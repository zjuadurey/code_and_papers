"""Pandas cleaning and real CPU neural-network training for the approved SAT study."""
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

from .data import HERE, FEATURES, NONNEGATIVE

SEED=42


def audit(frame):
    numeric=frame[FEATURES].apply(pd.to_numeric,errors="coerce")
    return {"rows":len(frame),"missing_feature_cells":int(frame[FEATURES].isna().sum().sum()),
            "duplicate_groups":int(frame.group_id.duplicated().sum()),
            "invalid_labels":int((~frame.satisfiable.isin([0,1])).sum()),
            "nonnumeric_cells":int((numeric.isna()&frame[FEATURES].notna()).sum().sum()),
            "infinite_cells":int(np.isinf(numeric.to_numpy()).sum()),
            "invalid_negative_cells":int((numeric[NONNEGATIVE]<0).sum().sum()),
            "impossible_literal_totals":int((numeric.total_literals>105).sum())}


def split_data(frame):
    """All canonical groups are unique before stratified 60/20/20 splitting."""
    if frame.group_id.duplicated().any():raise ValueError("Duplicate canonical groups before split")
    rng=np.random.default_rng(SEED);parts={k:[] for k in ["train","validation","test"]}
    for label in [0,1]:
        positions=rng.permutation(frame.index[frame.satisfiable==label])
        chunks=np.split(positions,[int(len(positions)*.6),int(len(positions)*.8)])
        for name,chunk in zip(parts,chunks):parts[name].extend(chunk.tolist())
    return {k:frame.loc[rng.permutation(v)].reset_index(drop=True).copy() for k,v in parts.items()}


def corrupt(train):
    dirty=train.astype({k:object for k in FEATURES}).copy();log=[]
    edits=[(i,FEATURES[i],np.nan,"missing") for i in range(8)]
    edits += [(8+i,FEATURES[i],"not_numeric","type_error") for i in range(3)]
    edits += [(11,"n_clauses",-10,"negative_count"),(12,"total_literals",-5,"negative_count"),
              (13,"occurrence_mean",float("inf"),"infinite"),(14,"total_literals",1e8,"impossible_outlier")]
    for i,col,value,kind in edits:
        dirty.at[i,col]=value
        log.append({"instance_id":dirty.at[i,"instance_id"],"feature":col,"error":kind,"value":str(value)})
    dirty=pd.concat([dirty,dirty.iloc[20:24].copy()],ignore_index=True)
    log.append({"error":"duplicate_rows","count":4})
    invalid=dirty.iloc[[25]].copy();invalid["group_id"]="synthetic-invalid-row";invalid["instance_id"]="synthetic-invalid-row";invalid["satisfiable"]=-1
    dirty=pd.concat([dirty,invalid],ignore_index=True);log.append({"error":"invalid_label","count":1})
    return dirty,log


def clean_rows(frame):
    rows=frame.drop_duplicates("group_id").copy()
    rows=rows[rows.satisfiable.isin([0,1])].copy()
    x=rows[FEATURES].apply(pd.to_numeric,errors="coerce").replace([np.inf,-np.inf],np.nan)
    x[NONNEGATIVE]=x[NONNEGATIVE].mask(x[NONNEGATIVE]<0)
    # Declared generator: at most 35 clauses, each at most 3 literals.
    # This is an impossible value under this dataset's definition, not tail clipping.
    x.loc[x.total_literals>105,"total_literals"]=np.nan
    return x,rows.satisfiable.astype(int),rows


def fit_preprocessor(x):
    median=x.median();filled=x.fillna(median)
    return {"median":median,"mean":filled.mean(),"std":filled.std(ddof=0).replace(0,1)}


def transform(x,prep):
    clean=x.fillna(prep["median"])
    scaled=((clean-prep["mean"])/prep["std"]).to_numpy(dtype=np.float32)
    if not np.isfinite(scaled).all():raise ValueError("Nonfinite cleaned features")
    return scaled,clean


class Network(nn.Module):
    def __init__(self,linear=False):
        super().__init__()
        self.layers=nn.Linear(len(FEATURES),1) if linear else nn.Sequential(
            nn.Linear(len(FEATURES),64),nn.ReLU(),nn.Linear(64,32),nn.ReLU(),nn.Linear(32,1))

    def forward(self,x):return self.layers(x).squeeze(-1)


def metrics(y,p):
    pred=p>=.5
    tp=int(((y==1)&pred).sum());tn=int(((y==0)&~pred).sum())
    fp=int(((y==0)&pred).sum());fn=int(((y==1)&~pred).sum())
    precision=tp/max(tp+fp,1);recall=tp/max(tp+fn,1)
    return {"n":len(y),"accuracy":(tp+tn)/len(y),"precision_sat":precision,"recall_sat":recall,
            "f1_sat":2*precision*recall/max(precision+recall,1e-12),
            "confusion_matrix":[[tn,fp],[fn,tp]],"threshold":.5}


def fit_model(tensors,linear=False):
    torch.manual_seed(SEED)
    net=Network(linear);opt=torch.optim.Adam(net.parameters(),lr=.001,weight_decay=.0001)
    loss_fn=nn.BCEWithLogitsLoss();history=[];best=float("inf");checkpoint=None;best_epoch=0
    for epoch in range(1,201):
        net.train()
        for batch in torch.randperm(len(tensors["train"][0])).split(64):
            opt.zero_grad();loss=loss_fn(net(tensors["train"][0][batch]),tensors["train"][1][batch]);loss.backward();opt.step()
        net.eval()
        with torch.no_grad():
            tr=float(loss_fn(net(tensors["train"][0]),tensors["train"][1]))
            val=float(loss_fn(net(tensors["validation"][0]),tensors["validation"][1]))
        history.append({"epoch":epoch,"train_loss":tr,"validation_loss":val})
        if val<best-1e-5:best=val;best_epoch=epoch;checkpoint=copy.deepcopy(net.state_dict())
        if epoch-best_epoch>=25:break
    net.load_state_dict(checkpoint);net.eval()
    return net,history,best_epoch


def charts(out,raw,train_clean,hist,result):
    plt.rcParams.update({"figure.dpi":150,"font.size":11,"axes.spines.top":False,
                         "axes.spines.right":False,"savefig.bbox":"tight"})
    colors=["#da9a39","#27a690"]
    fig,ax=plt.subplots(figsize=(6,3.5));counts=raw.satisfiable.value_counts().reindex([0,1])
    ax.bar(["UNSAT (0)","SAT (1)"],counts,color=colors)
    for i,v in enumerate(counts):ax.text(i,v+20,str(v),ha="center")
    ax.set(ylabel="Generated instances",title="Observed class balance (not forced)",ylim=(0,counts.max()*1.2));fig.savefig(out/"class_balance.png");plt.close(fig)
    fig,ax=plt.subplots(figsize=(6,3.5))
    for label,color in zip([0,1],colors):
        sub=train_clean[train_clean.satisfiable==label]
        ax.hist(sub.clause_variable_ratio,bins=np.arange(.75,7.51,.5),alpha=.6,color=color,label="SAT" if label else "UNSAT")
    ax.set(xlabel="Clauses / variables",ylabel="Training instances",title="Training-only clause density distribution");ax.legend();fig.savefig(out/"density_distribution.png");plt.close(fig)
    fig,ax=plt.subplots(figsize=(6.5,3.5));h=pd.DataFrame(hist)
    ax.plot(h.epoch,h.train_loss,label="Train BCE",color=colors[1]);ax.plot(h.epoch,h.validation_loss,label="Validation BCE",color=colors[0]);ax.axvline(result["best_epoch"],ls="--",color="#657790",label="Selected epoch")
    ax.set(xlabel="Epoch",ylabel="BCE loss",title="Actual MLP training");ax.legend();fig.savefig(out/"training_curve.png");plt.close(fig)
    fig,ax=plt.subplots(figsize=(5,3.8));cm=np.array(result["mlp"]["test"]["confusion_matrix"])
    ax.imshow(cm,cmap="Blues");ax.set(xticks=[0,1],yticks=[0,1],xticklabels=["UNSAT","SAT"],yticklabels=["UNSAT","SAT"],xlabel="Predicted",ylabel="Exact label",title="Held-out MLP confusion matrix")
    for i in range(2):
        for j in range(2):ax.text(j,i,str(cm[i,j]),fontsize=22,ha="center",va="center",color="white" if cm[i,j]>cm.max()/2 else "#142d3c")
    fig.savefig(out/"confusion_matrix.png");plt.close(fig)


def run(output: Path,dataset: Path=HERE/"dataset/instances.csv"):
    if output.exists():raise FileExistsError("Choose a new output directory; preserve previous run")
    output.mkdir(parents=True)
    random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED);torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    raw=pd.read_csv(dataset);before=audit(raw)
    if any(v for k,v in before.items() if k!="rows"):raise ValueError(f"Unexpected source defect: {before}")
    splits=split_data(raw);dirty,log=corrupt(splits["train"])
    dirty.to_csv(output/"training_dirty.csv",index=False)
    (output/"error_injection_log.json").write_text(json.dumps(log,indent=2)+"\n")
    x,y,rows=clean_rows(dirty);prep=fit_preprocessor(x);scaled,clean=transform(x,prep)
    clean_table=rows.copy();clean_table[FEATURES]=clean
    clean_table.to_csv(output/"training_cleaned.csv",index=False)
    pd.DataFrame(prep).to_csv(output/"preprocessing.csv")
    raw[FEATURES].describe().T.assign(variance=raw[FEATURES].var(ddof=1)).to_csv(output/"raw_statistics.csv")
    clean.describe().T.assign(variance=clean.var(ddof=1)).to_csv(output/"training_statistics.csv")
    ids={k:v.group_id.tolist() for k,v in splits.items()}
    assert all(not set(ids[a])&set(ids[b]) for a,b in [("train","validation"),("train","test"),("validation","test")])
    (output/"split_groups.json").write_text(json.dumps(ids,indent=2)+"\n")
    tensors={"train":(torch.from_numpy(scaled),torch.tensor(y.to_numpy(),dtype=torch.float32))}
    for name in ["validation","test"]:
        nx,ny,_=clean_rows(splits[name]);sx,_=transform(nx,prep)
        tensors[name]=(torch.from_numpy(sx),torch.tensor(ny.to_numpy(),dtype=torch.float32))
    # Both configurations are predeclared; validation selects epochs only.
    mlp,history,best_epoch=fit_model(tensors)
    linear,linear_history,linear_epoch=fit_model(tensors,linear=True)
    results={};test_probabilities={}
    for name,model in [("mlp",mlp),("linear",linear)]:
        results[name]={}
        with torch.no_grad():
            for part,(tx,ty) in tensors.items():
                probabilities=torch.sigmoid(model(tx)).numpy()
                results[name][part]=metrics(ty.numpy().astype(int),probabilities)
                if part=="test":test_probabilities[name]=probabilities
    labels=tensors["test"][1].numpy().astype(int);majority=int(y.mean()>=.5)
    predictions=splits["test"][["instance_id","group_id","n","clauses_json","satisfiable"]].copy()
    for name,prob in test_probabilities.items():predictions[name+"_probability"]=prob;predictions[name+"_prediction"]=(prob>=.5).astype(int)
    predictions.to_csv(output/"test_predictions.csv",index=False)
    result={"study":"CA6000 SAT prediction, not quantumization classification","seed":SEED,
        "source_audit":before,"dirty_training_audit":audit(dirty),"cleaned_training_audit":audit(clean_table),
        "imputed_cells":int(x.isna().sum().sum()),"split_counts":{k:len(v) for k,v in splits.items()},
        "features":FEATURES,"architecture":[len(FEATURES),64,32,1],"parameters":sum(p.numel() for p in mlp.parameters()),
        "best_epoch":best_epoch,"epochs_run":len(history),"linear_best_epoch":linear_epoch,
        "linear_epochs_run":len(linear_history),"majority_baseline_accuracy":float((labels==majority).mean()),
        **results,"optimizer":"Adam","learning_rate":.001,"batch_size":64,"weight_decay":.0001,
        "early_stopping":{"monitor":"validation BCE","patience":25,"max_epochs":200,"min_delta":1e-5},
        "test_used_for_selection":False,"device":"CPU",
        "versions":{"python":platform.python_version(),"torch":torch.__version__,"pandas":pd.__version__,"numpy":np.__version__,"matplotlib":matplotlib.__version__},
        "dataset_sha256":hashlib.sha256(dataset.read_bytes()).hexdigest(),
        "training_code_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "limitations":["Synthetic small-CNF generator, 4 or 5 variables, same-distribution holdout.",
            "Canonicalization handles variable renaming and clause/literal order, not all logical equivalence.",
            "Aggregate features discard structural information; no solver replacement or speedup claim.",
            "No quantum suitability labels used or created; predictions may be wrong."]}
    (output/"metrics.json").write_text(json.dumps(result,indent=2)+"\n")
    pd.DataFrame(history).to_csv(output/"training_history.csv",index=False)
    pd.DataFrame(linear_history).to_csv(output/"linear_history.csv",index=False)
    torch.save(mlp.state_dict(),output/"model_state.pt")
    torch.save(linear.state_dict(),output/"linear_state.pt")
    charts(output,raw,clean_table,history,result)
    print(json.dumps({"split":result["split_counts"],"mlp_test":results["mlp"]["test"],
        "linear_test":results["linear"]["test"],"majority":result["majority_baseline_accuracy"],"best_epoch":best_epoch},indent=2))
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=HERE/"results")
    parser.add_argument("--dataset",type=Path,default=HERE/"dataset/instances.csv")
    args=parser.parse_args();run(args.output,args.dataset)
