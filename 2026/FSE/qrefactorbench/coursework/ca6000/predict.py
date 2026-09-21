"""Predict UCI-style feature rows using the saved coursework model; no retraining."""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .train import FEATURES, HERE, MLP, transform


def predict(frame: pd.DataFrame, model_dir: Path = HERE / "results") -> pd.DataFrame:
    missing = set(FEATURES) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing feature columns: {sorted(missing)}")
    prep_frame = pd.read_csv(model_dir / "preprocessing_parameters.csv", index_col=0)
    prep = {name: prep_frame[name] for name in prep_frame}
    numeric = frame[FEATURES].apply(pd.to_numeric, errors="coerce")
    numeric = numeric.replace([np.inf, -np.inf], np.nan).mask(lambda x: x < 0)
    scaled, _ = transform(numeric, prep)
    model = MLP()
    model.load_state_dict(torch.load(model_dir / "model_state.pt", map_location="cpu", weights_only=True))
    model.eval()
    with torch.no_grad():
        probability = torch.sigmoid(model(torch.from_numpy(scaled))).numpy()
    result = pd.DataFrame({"probability_malignant": probability,
                           "predicted_label": np.where(probability >= .5, "M", "B")})
    if "id" in frame:
        result.insert(0, "id", frame.id.to_numpy())
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--model-dir", type=Path, default=HERE / "results")
    args = parser.parse_args()
    print(predict(pd.read_csv(args.input_csv), args.model_dir).to_csv(index=False), end="")
