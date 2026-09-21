"""Saved MLP inference with exact classical verification; never treat prediction as proof."""
import argparse
import json

import numpy as np
import pandas as pd
import torch

from .data import HERE, FEATURES, features, original
from .train import Network, transform


def validate(n,clauses):
    if type(n) is not int or n not in [4,5] or type(clauses) is not list or not n<=len(clauses)<=7*n:
        raise ValueError("Use 4 or 5 variables and n to 7*n clauses, matching the dataset domain")
    for clause in clauses:
        if type(clause) is not list or len(clause) not in [2,3]:
            raise ValueError("Each clause must have 2 or 3 literals")
        if any(type(x) is not int or not 1<=abs(x)<=n for x in clause):
            raise ValueError("Literals must be nonzero integers with abs(literal) <= n")
        if len({abs(x) for x in clause})!=len(clause):raise ValueError("Each variable appears at most once per clause")
    if len({tuple(sorted(c)) for c in clauses})!=len(clauses):raise ValueError("Duplicate clauses are outside the generator domain")
    if len({abs(x) for c in clauses for x in c})!=n:raise ValueError("Every declared variable must appear")


def predict(n,clauses,model_dir=HERE/"results"):
    validate(n,clauses)
    prep_frame=pd.read_csv(model_dir/"preprocessing.csv",index_col=0)
    prep={k:prep_frame[k] for k in prep_frame}
    row=pd.DataFrame([features(n,clauses)],columns=FEATURES);scaled,_=transform(row,prep)
    model=Network();model.load_state_dict(torch.load(model_dir/"model_state.pt",map_location="cpu",weights_only=True));model.eval()
    with torch.no_grad():probability=float(torch.sigmoid(model(torch.from_numpy(scaled)))[0])
    exact=bool(original.has_assignment(n,clauses));prediction=probability>=.5
    return {"probability_sat":probability,"predicted":"SAT" if prediction else "UNSAT",
            "exact":"SAT" if exact else "UNSAT","matches_exact":prediction==exact,
            "features":row.iloc[0].to_dict(),"neural_prediction_is_not_a_proof":True}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n",type=int,required=True);parser.add_argument("--clauses",required=True)
    args=parser.parse_args();print(json.dumps(predict(args.n,json.loads(args.clauses)),indent=2))
