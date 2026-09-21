"""Evidence checks for canonical isolation, source-derived labels and model artifacts."""
import itertools
import json

import numpy as np
import pandas as pd
import pytest
import torch

from .data import HERE, FEATURES, canonical_formula, features, original
from .predict import predict, validate
from .train import Network, audit, clean_rows, corrupt, fit_preprocessor, metrics, split_data, transform


def test_canonicalization_and_features_ignore_renaming_and_order():
    clauses=[[1,-2],[2,3,-4],[-1,4],[1,3]]
    permutation=[3,1,4,2]
    renamed=[[permutation[abs(x)-1]*(1 if x>0 else -1) for x in reversed(c)]
             for c in reversed(clauses)]
    assert canonical_formula(4,clauses)==canonical_formula(4,renamed)
    assert features(4,clauses)==features(4,renamed)


def test_all_labels_against_independent_boolean_evaluation():
    frame=pd.read_csv(HERE/"dataset/instances.csv")
    assert len(frame)==3000 and frame.group_id.nunique()==3000
    for row in frame.itertuples():
        clauses=json.loads(row.clauses_json)
        expected=any(all(any(values[abs(x)-1]==(x>0) for x in clause) for clause in clauses)
                     for values in itertools.product([False,True],repeat=row.n))
        assert expected==bool(row.satisfiable)
        assert expected==original.has_assignment(row.n,clauses)


def test_no_canonical_group_overlap():
    frame=pd.read_csv(HERE/"dataset/instances.csv");split=split_data(frame)
    groups=[set(part.group_id) for part in split.values()]
    assert sum(map(len,groups))==len(set.union(*groups))==len(frame)
    recorded=json.loads((HERE/"results/split_groups.json").read_text())
    assert all(part.group_id.tolist()==recorded[name] for name,part in split.items())


def test_cleaning_and_training_only_statistics():
    train=split_data(pd.read_csv(HERE/"dataset/instances.csv"))["train"]
    saved=train.copy(deep=True);dirty,log=corrupt(train)
    assert train.equals(saved)
    assert audit(dirty)["duplicate_groups"]==4 and audit(dirty)["invalid_labels"]==1
    x,y,_=clean_rows(dirty);prep=fit_preprocessor(x);before={k:v.copy() for k,v in prep.items()}
    scaled,clean=transform(x,prep)
    assert np.isfinite(scaled).all() and len(y)==len(train)
    assert int(x.isna().sum().sum())==15 and clean.total_literals.max()<=105
    heldout=x.iloc[:2].copy();heldout.iloc[0,0]=1e9;transform(heldout,prep)
    assert all(before[k].equals(prep[k]) for k in prep)


def test_loaded_model_reproduces_test_metrics():
    source=pd.read_csv(HERE/"dataset/instances.csv")
    frame=split_data(source)["test"]
    params=pd.read_csv(HERE/"results/preprocessing.csv",index_col=0)
    prep={k:params[k] for k in params};x,y,_=clean_rows(frame);scaled,_=transform(x,prep)
    model=Network();model.load_state_dict(torch.load(HERE/"results/model_state.pt",weights_only=True));model.eval()
    with torch.no_grad():p=torch.sigmoid(model(torch.from_numpy(scaled))).numpy()
    reported=json.loads((HERE/"results/metrics.json").read_text())
    assert metrics(y.to_numpy(),p)==reported["mlp"]["test"]


def test_prediction_is_compared_with_solver_and_rejects_invalid_input():
    row=pd.read_csv(HERE/"results/test_predictions.csv").iloc[0]
    result=predict(int(row.n),json.loads(row.clauses_json))
    assert result["exact"]==("SAT" if row.satisfiable else "UNSAT")
    assert result["neural_prediction_is_not_a_proof"]
    with pytest.raises(ValueError):validate(100,[[1,2]])
    with pytest.raises(ValueError):validate(4,[[1,99]]*4)
