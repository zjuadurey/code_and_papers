"""Reproducible CPU MLP classification with explicit data cleaning and held-out test.

No scikit-learn dependency. Pandas does cleaning; PyTorch trains a real neural net.
Only the training partition receives documented synthetic data-quality errors.
"""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import platform
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from torch import nn

HERE = Path(__file__).resolve().parent
BASE_FEATURES = ["radius", "texture", "perimeter", "area", "smoothness", "compactness",
                 "concavity", "concave_points", "symmetry", "fractal_dimension"]
FEATURES = [f"{name}_{group}" for group in ("mean", "se", "worst") for name in BASE_FEATURES]
SEED = 42


def load_data() -> pd.DataFrame:
    return pd.read_csv(HERE / "data/wdbc.data", header=None,
                       names=["id", "diagnosis"] + FEATURES, dtype={"id": str})


def audit(df: pd.DataFrame) -> dict:
    numeric = df[FEATURES].apply(pd.to_numeric, errors="coerce")
    return {
        "rows": len(df), "columns": len(df.columns), "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()), "duplicate_ids": int(df.id.duplicated().sum()),
        "invalid_labels": int((~df.diagnosis.isin(["B", "M"])).sum()),
        "nonnumeric_feature_cells": int((numeric.isna() & df[FEATURES].notna()).sum().sum()),
        "infinite_feature_cells": int(np.isinf(numeric.to_numpy()).sum()),
        "negative_feature_cells": int((numeric < 0).sum().sum()),
    }


def split_data(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Stratify by label, never include ID as a predictor; split before fitting anything."""
    rng = np.random.default_rng(SEED)
    partitions = {"train": [], "validation": [], "test": []}
    for label in ("B", "M"):
        positions = rng.permutation(df.index[df.diagnosis == label])
        first, second = int(len(positions)*.6), int(len(positions)*.8)
        for name, chunk in zip(partitions, np.split(positions, [first, second])):
            partitions[name].extend(chunk.tolist())
    return {name: df.loc[rng.permutation(indices)].copy().reset_index(drop=True)
            for name, indices in partitions.items()}


def inject_errors(train: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Teaching corruption only; preserve raw source and validation/test untouched."""
    dirty = train.copy().astype({c: object for c in FEATURES})
    log = []
    edits = [(i, FEATURES[i], np.nan, "missing") for i in range(8)]
    edits += [(8+i, FEATURES[i], "not_numeric", "type_error") for i in range(3)]
    edits += [(11, "area_mean", -50, "negative_measurement"),
              (12, "radius_mean", -2, "negative_measurement"),
              (13, "perimeter_mean", float("inf"), "nonfinite"),
              (14, "radius_mean", 1e8, "extreme_value")]
    for row, feature, value, kind in edits:
        dirty.at[row, feature] = value
        log.append({"id": str(dirty.at[row, "id"]), "feature": feature, "error": kind,
                    "injected_value": str(value)})
    dirty = pd.concat([dirty, dirty.iloc[20:24].copy()], ignore_index=True)
    log.append({"error": "duplicate_rows", "count": 4,
                "ids": dirty.iloc[-4:].id.tolist()})
    invalid = dirty.iloc[[25]].copy()
    invalid["id"] = "synthetic_invalid_label_row"
    invalid["diagnosis"] = "UNKNOWN"
    dirty = pd.concat([dirty, invalid], ignore_index=True)
    log.append({"error": "invalid_label", "count": 1, "id": "synthetic_invalid_label_row"})
    return dirty, log


def clean_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Fixed type/domain checks, before learned preprocessing; no repair from originals."""
    rows = df.drop_duplicates(subset="id", keep="first").copy()
    rows = rows[rows.diagnosis.isin(["B", "M"])].copy()
    numeric = rows[FEATURES].apply(pd.to_numeric, errors="coerce")
    numeric = numeric.replace([np.inf, -np.inf], np.nan).mask(lambda x: x < 0)
    return numeric, rows.diagnosis.map({"B": 0, "M": 1}).astype(int), rows.id


def fit_preprocessor(x: pd.DataFrame) -> dict[str, pd.Series]:
    """Fit medians, winsorization bounds, means and scales using training data only."""
    median = x.median()
    filled = x.fillna(median)
    lower, upper = filled.quantile(.01), filled.quantile(.99)
    clipped = filled.clip(lower, upper, axis=1)
    return {"median": median, "lower": lower, "upper": upper,
            "mean": clipped.mean(), "std": clipped.std(ddof=0).replace(0, 1)}


def transform(x: pd.DataFrame, prep: dict) -> tuple[np.ndarray, pd.DataFrame]:
    cleaned = x.fillna(prep["median"]).clip(prep["lower"], prep["upper"], axis=1)
    scaled = ((cleaned - prep["mean"]) / prep["std"]).to_numpy(dtype=np.float32)
    if not np.isfinite(scaled).all():
        raise ValueError("Non-finite values after cleaning")
    return scaled, cleaned


class MLP(nn.Module):
    """30 -> 32 -> 16 -> 1 logit; sigmoid is applied only for predictions."""
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(nn.Linear(30, 32), nn.ReLU(), nn.Linear(32, 16),
                                     nn.ReLU(), nn.Linear(16, 1))

    def forward(self, x):
        return self.network(x).squeeze(-1)


def metrics(y: np.ndarray, probabilities: np.ndarray) -> dict:
    predicted = (probabilities >= .5).astype(int)
    tp, tn = int(((predicted == 1) & (y == 1)).sum()), int(((predicted == 0) & (y == 0)).sum())
    fp, fn = int(((predicted == 1) & (y == 0)).sum()), int(((predicted == 0) & (y == 1)).sum())
    precision, recall = tp / max(tp+fp, 1), tp / max(tp+fn, 1)
    return {"accuracy": (tp+tn)/len(y), "precision_malignant": precision,
            "recall_malignant": recall, "f1_malignant": 2*precision*recall/max(precision+recall, 1e-12),
            "confusion_matrix": [[tn, fp], [fn, tp]], "n": len(y), "threshold": .5}


def charts(out: Path, raw, train_clean, history, result):
    plt.rcParams.update({"figure.dpi": 150, "font.size": 11, "axes.spines.top": False,
                         "axes.spines.right": False, "savefig.bbox": "tight"})
    colors=["#29a690", "#e6a149"]
    fig, ax=plt.subplots(figsize=(6,3.4));counts=raw.diagnosis.value_counts().reindex(["B","M"])
    ax.bar(["Benign (B)","Malignant (M)"],counts,color=colors)
    for i,v in enumerate(counts):ax.text(i,v+5,str(v),ha="center")
    ax.set(ylabel="Samples",title="Original dataset: class distribution",ylim=(0,410));fig.savefig(out/"class_balance.png");plt.close(fig)
    # Exploratory plot uses only the training partition, not held-out outcome inspection.
    fig,ax=plt.subplots(figsize=(6,3.4))
    for label,color in zip(["B","M"],colors):
        rows=train_clean[train_clean.diagnosis==label]
        ax.scatter(rows.radius_mean,rows.texture_mean,s=18,alpha=.6,label=label,color=color)
    ax.set(xlabel="Mean radius",ylabel="Mean texture",title="Cleaned training data only");ax.legend();fig.savefig(out/"training_scatter.png");plt.close(fig)
    hist=pd.DataFrame(history);fig,ax=plt.subplots(figsize=(6.5,3.5))
    ax.plot(hist.epoch,hist.train_loss,label="Train BCE",color=colors[0]);ax.plot(hist.epoch,hist.validation_loss,label="Validation BCE",color=colors[1])
    ax.axvline(result["best_epoch"],color="#596b84",ls="--",label="Selected epoch")
    ax.set(xlabel="Epoch",ylabel="BCE loss",title="Actual neural-network training");ax.legend();fig.savefig(out/"training_curve.png");plt.close(fig)
    cm=np.array(result["test"]["confusion_matrix"]);fig,ax=plt.subplots(figsize=(4.8,3.7))
    ax.imshow(cm,cmap="Blues");ax.set(xticks=[0,1],yticks=[0,1],xticklabels=["B","M"],yticklabels=["B","M"],xlabel="Predicted",ylabel="Actual",title="Held-out test confusion matrix")
    for i in range(2):
        for j in range(2):ax.text(j,i,str(cm[i,j]),ha="center",va="center",fontsize=22,color="white" if cm[i,j]>cm.max()/2 else "#12263c")
    fig.savefig(out/"confusion_matrix.png");plt.close(fig)


def run(out: Path) -> dict:
    if out.exists():
        raise FileExistsError("Choose a new output directory; previous runs are preserved")
    out.mkdir(parents=True)
    random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED)
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    raw=load_data();before=audit(raw)
    if before["duplicate_ids"] or before["invalid_labels"]:
        raise ValueError("Unexpected source identity/label issue; inspect before splitting")
    splits=split_data(raw)
    dirty,errors=inject_errors(splits["train"]);dirty.to_csv(out/"training_dirty_demo.csv",index=False)
    (out/"error_injection_log.json").write_text(json.dumps(errors,indent=2)+"\n")
    numeric,y_train,ids=clean_rows(dirty);prep=fit_preprocessor(numeric)
    train_x,train_clean=transform(numeric,prep)
    cleaned_table=train_clean.copy();cleaned_table.insert(0,"diagnosis",y_train.map({0:"B",1:"M"}));cleaned_table.insert(0,"id",ids)
    cleaned_table.to_csv(out/"training_cleaned.csv",index=False)
    raw[FEATURES].describe().T.assign(variance=raw[FEATURES].var(ddof=1)).to_csv(out/"raw_descriptive_statistics.csv")
    train_clean.describe().T.assign(variance=train_clean.var(ddof=1)).to_csv(out/"training_descriptive_statistics.csv")
    medians=train_clean.median();medians.to_csv(out/"training_medians.csv",header=["median"])
    pd.DataFrame(prep).to_csv(out/"preprocessing_parameters.csv")
    split_ids={name:frame.id.tolist() for name,frame in splits.items()}
    assert all(not set(split_ids[a]) & set(split_ids[b]) for a,b in [("train","validation"),("train","test"),("validation","test")])
    (out/"split_ids.json").write_text(json.dumps(split_ids,indent=2)+"\n")
    tensors={"train":(torch.from_numpy(train_x),torch.tensor(y_train.to_numpy(),dtype=torch.float32))}
    for name in ["validation","test"]:
        x,y,_=clean_rows(splits[name]);scaled,_=transform(x,prep)
        tensors[name]=(torch.from_numpy(scaled),torch.tensor(y.to_numpy(),dtype=torch.float32))
    model=MLP();optimizer=torch.optim.Adam(model.parameters(),lr=.001,weight_decay=.0001)
    loss_fn=nn.BCEWithLogitsLoss();history=[];best_loss=float("inf");best_state=None;best_epoch=0
    # Test tensors are not evaluated until the best validation-loss checkpoint is fixed.
    for epoch in range(1,301):
        model.train();order=torch.randperm(len(train_x))
        for batch in order.split(32):
            optimizer.zero_grad();loss=loss_fn(model(tensors["train"][0][batch]),tensors["train"][1][batch]);loss.backward();optimizer.step()
        model.eval()
        with torch.no_grad():
            train_loss=float(loss_fn(model(tensors["train"][0]),tensors["train"][1]))
            val_loss=float(loss_fn(model(tensors["validation"][0]),tensors["validation"][1]))
        history.append({"epoch":epoch,"train_loss":train_loss,"validation_loss":val_loss})
        if val_loss < best_loss-1e-5:
            best_loss=val_loss;best_state=copy.deepcopy(model.state_dict());best_epoch=epoch
        if epoch-best_epoch>=30:break
    model.load_state_dict(best_state);model.eval()
    evaluated={}
    with torch.no_grad():
        for name,(x,y) in tensors.items():
            probabilities=torch.sigmoid(model(x)).numpy();evaluated[name]=metrics(y.numpy().astype(int),probabilities)
            if name=="test":
                pd.DataFrame({"id":splits[name].id,"actual":y.numpy().astype(int),"probability_malignant":probabilities,"predicted":(probabilities>=.5).astype(int)}).to_csv(out/"test_predictions.csv",index=False)
    labels=tensors["test"][1].numpy().astype(int);majority=int(y_train.mean()>=.5)
    result={"task":"UCI WDBC neural-network classification coursework", "seed":SEED,
        "source_audit":before,"dirty_training_audit":audit(dirty),"cleaned_training_audit":audit(cleaned_table),
        "imputed_training_cells":int(numeric.isna().sum().sum()),
        "clipped_training_cells":int(((numeric.fillna(prep['median'])<prep['lower'])|(numeric.fillna(prep['median'])>prep['upper'])).sum().sum()),
        "split_counts":{k:len(v) for k,v in splits.items()},"best_epoch":best_epoch,"epochs_run":epoch,
        "architecture":[30,32,16,1],"parameters":sum(p.numel() for p in model.parameters()),
        "optimizer":"Adam", "learning_rate":.001,"batch_size":32,"weight_decay":.0001,
        "early_stopping":"validation BCE, patience=30, min_delta=1e-5, max_epochs=300",
        "test_evaluated_after_checkpoint_selection":True,"majority_baseline_accuracy":float((labels==majority).mean()),
        **evaluated,"versions":{"python":platform.python_version(),"torch":torch.__version__,"pandas":pd.__version__,"numpy":np.__version__,"matplotlib":matplotlib.__version__},
        "device":"CPU","source_sha256":hashlib.sha256((HERE/'data/wdbc.data').read_bytes()).hexdigest(),
        "training_source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "limitations":["One fixed split and seed; no significance or clinical-use claim.","Winsorization can suppress legitimate extreme observations; raw data retained.","Synthetic corruption affects training only; test set is original held-out data.","ID excluded from features; all preprocessing statistics fit only on training."]}
    (out/"metrics.json").write_text(json.dumps(result,indent=2)+"\n")
    pd.DataFrame(history).to_csv(out/"history.csv",index=False)
    torch.save(model.state_dict(),out/"model_state.pt")
    charts(out,raw,cleaned_table,history,result)
    print(json.dumps({"best_epoch":best_epoch,"epochs_run":epoch,"test":result['test'],"baseline":result['majority_baseline_accuracy']},indent=2))
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=HERE/"results")
    run(parser.parse_args().output)
