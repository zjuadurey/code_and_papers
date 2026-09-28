"""Checks for split isolation, actual cleaning, preprocessing, and saved inference."""
import json

import numpy as np

from .train import (HERE, audit, clean_rows, fit_preprocessor, inject_errors,
                    load_data, metrics, split_data, transform)
from .predict import predict


def test_stratified_split_is_disjoint_and_complete():
    raw = load_data()
    splits = split_data(raw)
    groups = [set(frame.id) for frame in splits.values()]
    assert set.union(*groups) == set(raw.id)
    assert sum(map(len, groups)) == len(raw) == 569
    assert all(not groups[i] & groups[j] for i in range(3) for j in range(i+1, 3))
    assert all(set(frame.diagnosis) == {"B", "M"} for frame in splits.values())


def test_teaching_errors_repaired_without_source_mutation():
    raw = load_data();splits = split_data(raw);train = splits["train"]
    before = train.copy(deep=True)
    dirty, log = inject_errors(train)
    assert train.equals(before)
    found = audit(dirty)
    assert found["missing_cells"] == 8 and found["duplicate_ids"] == 4
    assert found["nonnumeric_feature_cells"] == 3 and found["negative_feature_cells"] == 2
    numeric, labels, ids = clean_rows(dirty)
    prep = fit_preprocessor(numeric);scaled, cleaned = transform(numeric, prep)
    assert len(scaled) == len(train) == 341 and len(labels) == len(ids)
    assert np.isfinite(scaled).all() and not cleaned.isna().any().any()
    assert float(cleaned.radius_mean.max()) < 1e8
    assert len(log) == 17


def test_transform_does_not_fit_on_validation_data():
    splits = split_data(load_data())
    train, _, _ = clean_rows(splits["train"])
    prep = fit_preprocessor(train)
    saved = {k: v.copy() for k, v in prep.items()}
    val, _, _ = clean_rows(splits["validation"])
    changed = val.copy();changed.iloc[0, 0] = 1e12
    normal, _ = transform(val, prep);extreme, _ = transform(changed, prep)
    assert np.array_equal(normal[1:], extreme[1:])
    assert all(saved[k].equals(prep[k]) for k in prep)


def test_metrics_use_malignant_positive_and_original_predictions():
    score = metrics(np.array([0,0,1,1]), np.array([.1,.8,.2,.9]))
    assert score["accuracy"] == .5 and score["confusion_matrix"] == [[1,1],[1,1]]
    result = json.loads((HERE / "results/metrics.json").read_text())
    raw = load_data();split = json.loads((HERE / "results/split_ids.json").read_text())
    selected = raw.set_index("id").loc[split["test"]].reset_index()
    inference = predict(selected)
    probabilities = inference.probability_malignant.to_numpy()
    computed = metrics(selected.diagnosis.map({"B":0,"M":1}).to_numpy(), probabilities)
    assert computed == result["test"]
