"""StaticPartitioner union/flush transcription; see notes/qdao_execution_model.md."""
import math
from .metrics import volume_metrics, exp2_safe


def partition(operands, m, t=2):
    if not 0 <= t < m:
        raise ValueError('Require 0 <= t < m')
    groups, start, qset = [], 0, set()
    for k, ids in enumerate(operands):
        qs = {q for q in ids if q >= t}
        if len(qs) > m-t:
            raise ValueError('Single instruction exceeds QDAO partition capacity')
        if len(qset | qs) <= m-t:
            qset |= qs
        else:
            groups.append((start, k))
            start, qset = k, qs
    if len(operands) > start:
        groups.append((start, len(operands)))
    return groups


def traffic_oracle(result, m, t=2):
    n = result['summary']['n']
    if m >= n or m <= t:
        raise ValueError('m must satisfy t < m < n')
    groups = partition([ids for _, ids, _ in result['operations']], m, t)
    q = [r['q_live'] for r in result['trace']]
    endpoints = [v for a, b in groups for v in (q[a], q[b])]
    metrics = volume_metrics(n, endpoints)
    if not endpoints:
        raise ValueError('Empty circuit')
    eager, thin = metrics['log2_eager_volume']+4, metrics['log2_lazy_volume']+4
    ends = volume_metrics(n, [q[b] for _, b in groups])
    return dict(m=m, fixed_t=t, subcircuits=len(groups), traversals=2*len(groups),
                log2_eager_bytes=eager, log2_thin_bytes=thin,
                eager_bytes_if_representable=exp2_safe(eager), thin_bytes_if_representable=exp2_safe(thin),
                log2_ideal_traffic_reduction=metrics['log2_reduction'],
                ideal_traffic_reduction=metrics['reduction_factor_if_representable'],
                ideal_traffic_reduction_end_end=ends['reduction_factor_if_representable'],
                measured=False, excludes_materialization_overhead=True)
