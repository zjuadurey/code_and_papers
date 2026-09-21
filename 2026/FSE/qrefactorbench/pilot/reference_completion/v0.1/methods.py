"""Reference-inspired descriptive checks, separate from the existing evaluator.

No default scientific acceptance threshold. No model, network or hardware calls.
"""
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from numbers import Real


def pass_at_k(n: int, c: int, k: int) -> float:
    """HumanEval/QuanBench sampling estimator; requires n actual attempts of one task."""
    if any(type(v) is not int for v in (n,c,k)) or not (0 <= c <= n and 1 <= k <= n):
        raise ValueError("require integer counts 0<=c<=n and 1<=k<=n")
    return 1.0 - (math.comb(n-c,k) / math.comb(n,k) if n-c >= k else 0.0)


def probabilities(values: Mapping[str, float]) -> dict[str,float]:
    """Normalize nonnegative count/mass maps; keys are already decoded, not reversed."""
    if not values or any(not isinstance(k,str) or not isinstance(v,Real)
                         or isinstance(v,bool) for k,v in values.items()):
        raise ValueError("finite nonnegative keyed masses required")
    try:
        converted={str(k):float(v) for k,v in values.items()}
    except (OverflowError,ValueError) as exc:
        raise ValueError("mass outside float range") from exc
    if any(not math.isfinite(v) or v<0 for v in converted.values()):
        raise ValueError("finite nonnegative keyed masses required")
    total=sum(converted.values())
    if not math.isfinite(total) or total <= 0:
        raise ValueError("positive finite total required")
    return {k:v/total for k,v in converted.items()}


def distribution_report(reference: Mapping[str,float], observed: Mapping[str,float]) -> dict:
    """TV, Hellinger fidelity and directional KL; singular KL is explicit JSON null."""
    p,q=probabilities(reference),probabilities(observed)
    keys=sorted(set(p)|set(q))
    infinite=any(p.get(k,0)>0 and q.get(k,0)==0 for k in keys)
    kl=None if infinite else sum(p.get(k,0)*math.log(p[k]/q[k]) for k in keys if p.get(k,0)>0)
    return {"total_variation":sum(abs(p.get(k,0)-q.get(k,0)) for k in keys)/2,
            "hellinger_fidelity":sum(math.sqrt(p.get(k,0)*q.get(k,0)) for k in keys)**2,
            "kl_reference_to_observed":kl,"kl_is_infinite":infinite,
            "smoothing":None,"acceptance":None}


def objective_report(reference: Mapping[str,float], observed: Mapping[str,float], values: Mapping[str,float]) -> dict:
    """Task quality distinct from distribution/circuit validity; avoid signed ratios."""
    p,q=probabilities(reference),probabilities(observed)
    if not (set(p)|set(q)) <= set(values) or any(not isinstance(v,Real) or isinstance(v,bool) or not math.isfinite(v) for v in values.values()):
        raise ValueError("finite objective value for every outcome required")
    ideal=sum(v*values[k] for k,v in p.items()); actual=sum(v*values[k] for k,v in q.items())
    if not math.isfinite(ideal) or not math.isfinite(actual):raise ValueError("nonfinite expectation")
    return {"reference_expectation":ideal,"observed_expectation":actual,
            "absolute_expectation_gap":abs(ideal-actual),"acceptance":None}


def structural_signature(circuit) -> dict:
    """PQID-inspired count-map signature; cannot certify ordering, operands or semantics."""
    counts={str(k).lower():int(v) for k,v in circuit.count_ops().items()}
    return {"num_qubits":circuit.num_qubits,"num_clbits":circuit.num_clbits,
            "gate_count":sum(v for k,v in counts.items() if k!='barrier'),"gate_types":counts}


def process_overlap(reference, candidate) -> float:
    """Small unitary-only diagnostic; never strip measurements/initialization silently."""
    from qiskit.quantum_info import Operator, process_fidelity
    from qiskit.circuit import Gate
    if reference.num_qubits != candidate.num_qubits:
        raise ValueError("matching dimensions required")
    for circuit in (reference,candidate):
        if circuit.num_clbits or any(not isinstance(item.operation,Gate) for item in circuit.data):
            raise ValueError("only gate-only unitary circuits accepted")
    return float(process_fidelity(Operator(reference),Operator(candidate)))


def backward_error(matrix: Sequence[Sequence[float]], rhs: Sequence[float], x: Sequence[float], epsilon: float) -> dict:
    """HPL's infinity-norm normalization, descriptive and explicitly parameterized."""
    n=len(rhs)
    if len(matrix)!=n or len(x)!=n or any(len(row)!=n for row in matrix):raise ValueError("dimensions")
    if not math.isfinite(epsilon) or epsilon<=0:raise ValueError("positive epsilon")
    if any(not math.isfinite(v) for v in list(rhs)+list(x)+[a for row in matrix for a in row]):raise ValueError("finite values")
    norm=max((abs(sum(a*v for a,v in zip(row,x))-b) for row,b in zip(matrix,rhs)),default=0.0)
    scale=epsilon*(max((sum(map(abs,row)) for row in matrix),default=0.0)*max(map(abs,x),default=0.0)+max(map(abs,rhs),default=0.0))*n
    if not math.isfinite(norm) or not math.isfinite(scale):raise ValueError("overflow")
    result=norm/scale if scale else (0.0 if norm==0 else None)
    return {"residual_infinity_norm":norm,"scaled_backward_error":result,"acceptance":None}


def symmetry_defect(matrix: Sequence[Sequence[float]], x: Sequence[float], y: Sequence[float]) -> float:
    """HPCG-inspired bilinear identity check, raw defect without adopting its cutoff."""
    n=len(x)
    if len(y)!=n or len(matrix)!=n or any(len(r)!=n for r in matrix):raise ValueError("dimensions")
    if any(not math.isfinite(v) for v in list(x)+list(y)+[v for r in matrix for v in r]):raise ValueError("finite values")
    ax=[sum(a*v for a,v in zip(row,x)) for row in matrix]
    ay=[sum(a*v for a,v in zip(row,y)) for row in matrix]
    result=abs(sum(a*b for a,b in zip(x,ay))-sum(a*b for a,b in zip(y,ax)))
    if not math.isfinite(result):raise ValueError("overflow")
    return result
