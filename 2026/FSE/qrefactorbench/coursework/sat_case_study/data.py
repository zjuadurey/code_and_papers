"""Generate distinct CNF instances and exact labels from pilot-001's classical code."""

import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "cases/pilot/pilot-001/program.py"
spec = importlib.util.spec_from_file_location("original_sat", SOURCE)
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)


def canonical_formula(n: int, clauses: list[list[int]]) -> str:
    """Exact canonicalization for literal/clause ordering and variable renaming.

Enumerates <= 5! variable permutations. Does not claim to canonicalize arbitrary
logical equivalence or variable-polarity inversion. No labels are consulted.
"""
    variants = []
    for permutation in itertools.permutations(range(1, n + 1)):
        renamed = tuple(sorted(set(tuple(sorted(
            permutation[abs(x)-1] * (1 if x > 0 else -1) for x in clause))
            for clause in clauses)))
        variants.append(renamed)
    return json.dumps([n, min(variants)], separators=(",", ":"))


def features(n: int, clauses: list[list[int]]) -> dict[str, float]:
    """Cheap permutation-invariant syntax statistics; no solving, labels or timings."""
    widths = np.array([len(c) for c in clauses], dtype=float)
    occurrence = np.zeros(n);positive = np.zeros(n);negative = np.zeros(n)
    pair = np.zeros((n, n))
    for clause in clauses:
        for literal in clause:
            occurrence[abs(literal)-1] += 1
            (positive if literal > 0 else negative)[abs(literal)-1] += 1
        for a,b in itertools.combinations(sorted({abs(x)-1 for x in clause}),2):
            pair[a,b]+=1;pair[b,a]+=1
    balance = (positive-negative) / np.maximum(occurrence, 1)
    degree = (pair>0).sum(axis=1).astype(float)
    pairs = pair[np.triu_indices(n,1)]
    result = {
        "n_variables": n, "n_clauses": len(clauses), "clause_variable_ratio": len(clauses)/n,
        "total_literals": widths.sum(), "mean_clause_width": widths.mean(),
        "std_clause_width": widths.std(), "min_clause_width": widths.min(),
        "max_clause_width": widths.max(), "binary_fraction": float((widths==2).mean()),
        "ternary_fraction": float((widths==3).mean()),
        "positive_literal_fraction": positive.sum()/max(widths.sum(),1),
        "positive_occurrence_std": positive.std(), "negative_occurrence_std": negative.std(),
        "pair_edge_density": float((pairs>0).mean()), "pair_cooccurrence_mean": pairs.mean(),
        "pair_cooccurrence_std": pairs.std(), "pair_cooccurrence_max": pairs.max(),
    }
    for name, values in [("occurrence",occurrence),("polarity_balance",balance),("degree",degree)]:
        for stat, value in [("mean",values.mean()),("std",values.std()),("min",values.min()),("max",values.max())]:
            result[f"{name}_{stat}"]=value
    sets=[set(map(abs,c)) for c in clauses]
    result["mean_clause_variable_overlap"]=float(np.mean([len(a&b) for a,b in itertools.combinations(sets,2)])) if len(sets)>1 else 0.
    return {key:float(value) for key,value in result.items()}


FEATURES = list(features(4, [[1,2],[-2,3,4]]))
NONNEGATIVE = [name for name in FEATURES if not name.startswith("polarity_balance_")]


def generate(output: Path, count: int = 3000, seed: int = 2026) -> dict:
    """Uniform parameter sampling, label-independent duplicate rejection; no planting."""
    import pandas as pd
    if output.exists():
        raise FileExistsError("Dataset already exists; choose a new directory")
    output.mkdir(parents=True)
    rng=np.random.default_rng(seed);seen=set();rows=[];attempts=0
    pools={}
    for n in (4,5):
        for kind in ("2sat","3sat","mixed"):
            widths=[2,3] if kind=="mixed" else [2 if kind=="2sat" else 3]
            pools[n,kind]=[list(sign*variable for sign,variable in zip(signs,variables))
                for width in widths for variables in itertools.combinations(range(1,n+1),width)
                for signs in itertools.product([-1,1],repeat=width)]
    while len(rows)<count:
        attempts+=1
        n=int(rng.choice([4,5]));kind=str(rng.choice(["2sat","3sat","mixed"]))
        pool=pools[n,kind];m=int(rng.integers(n,min(7*n,len(pool))+1))
        clauses=[pool[int(i)] for i in rng.choice(len(pool),m,replace=False)]
        if len({abs(x) for c in clauses for x in c})!=n:continue
        canonical=canonical_formula(n,clauses)
        if canonical in seen:continue
        seen.add(canonical)
        digest=hashlib.sha256(canonical.encode()).hexdigest()
        rows.append({"instance_id":f"sat-{len(rows)+1:05d}","group_id":digest,
                     "family":kind,"n":n,"clauses_json":json.dumps(clauses,separators=(",",":")),
                     **features(n,clauses),"satisfiable":int(original.has_assignment(n,clauses))})
    frame=pd.DataFrame(rows);frame.to_csv(output/"instances.csv",index=False)
    provenance={"kind":"synthetic_coursework_instances_not_benchmark_cases","count":count,
        "seed":seed,"attempts":attempts,"variables":[4,5],"generator_families":["2sat","3sat","mixed"],
        "clauses":"uniform integer from n to min(7*n, number of possible distinct clauses)",
        "clauses_sampled_without_replacement":True,"label_balancing_or_planted_solutions":False,
        "exact_label":"Original pilot-001 has_assignment exhaustively checks every assignment",
        "source":"cases/pilot/pilot-001/program.py","source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "generator_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "dataset_sha256":hashlib.sha256((output/"instances.csv").read_bytes()).hexdigest(),
        "unique_canonical_groups":len(seen),"canonicalization":"literal/clause order + all variable renamings (<=5!)",
        "not_canonicalized":"arbitrary logical equivalence and polarity inversion",
        "features":FEATURES,"class_counts":frame.satisfiable.value_counts().sort_index().to_dict(),
        "provenance":"Researcher-requested synthetic generation; AI-assisted code. No external dataset, no expert quantum labels.",
        "license":"Repository licensing remains UNLICENSED / NOASSERTION; local coursework package, not a public benchmark release."}
    (output/"provenance.json").write_text(json.dumps(provenance,indent=2)+"\n")
    print(json.dumps({"rows":len(frame),"features":len(FEATURES),"classes":provenance["class_counts"],"attempts":attempts},indent=2))
    return provenance


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=HERE/"dataset")
    parser.add_argument("--count",type=int,default=3000)
    args=parser.parse_args();generate(args.output,args.count)
