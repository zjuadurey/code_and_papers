from collections import Counter
import json
import numpy as np
from .abstract_state import initial, K0, K1, Q
from .gate_semantics import transfer
from .metrics import volume_metrics, exp2_safe


def scheduled_operations(circuit):
    levels = [0] * circuit.num_qubits
    operations = []
    for inst in circuit.data:
        ids = [circuit.find_bit(q).index for q in inst.qubits]
        if inst.operation.name in {'barrier', 'delay'}:
            fence = max((levels[i] for i in ids), default=0)
            for i in ids:
                levels[i] = fence
            continue
        d = 1 + max((levels[i] for i in ids), default=0)
        for i in ids:
            levels[i] = d
        operations.append((inst.operation, ids, d))
    return operations


def analyze(circuit, angle_tol=1e-10):
    n = circuit.num_qubits
    ops = scheduled_operations(circuit)
    g = len(ops)
    state = initial(n)
    activations = [dict(qubit=i, first_quantum_gate=None, first_quantum_fraction=None,
                        first_quantum_depth=None, trigger_gate='', trigger_reason='', never_quantum=True) for i in range(n)]
    trace, events, unknown = [], [], Counter()

    def row(k, depth):
        q = state.count(Q)
        return dict(gate_index=k, normalized_gate_position=k / g if g else 0, depth=depth,
                    n=n, q_live=q, known_zero=state.count(K0), known_one=state.count(K1),
                    state_reduction_log2=n-q, state_reduction_factor=exp2_safe(n-q))

    trace.append(row(0, 0))
    previous_event = 0
    for k, (op, ids, depth) in enumerate(ops, 1):
        old_q = state.count(Q)
        reason, unrecognized = transfer(state, op, ids, angle_tol)
        if unrecognized:
            unknown[op.name] += 1
        new_q = state.count(Q)
        assert new_q >= old_q, 'Unexpected dematerialization'
        for i in ids:
            if state[i] == Q and activations[i]['never_quantum']:
                activations[i].update(first_quantum_gate=k, first_quantum_fraction=k/g,
                                      first_quantum_depth=depth, trigger_gate=op.name,
                                      trigger_reason=reason, never_quantum=False)
        if new_q > old_q:
            events.append(dict(gate_index=k, gate_name=op.name, qubits=json.dumps(ids),
                               old_q=old_q, new_q=new_q, delta_q=new_q-old_q,
                               trigger_reason=reason, gap_from_previous_event=k-previous_event))
            previous_event = k
        trace.append(row(k, depth))
    # Replay in dependency-layer order: serial prefixes do not represent layer ends.
    layer_state = initial(n)
    layer_qs, layer_rows = [], []
    by_layer = sorted(enumerate(ops), key=lambda x: (x[1][2], x[0]))
    for index, (_, (op, ids, d)) in enumerate(by_layer):
        transfer(layer_state, op, ids, angle_tol)
        if index + 1 == len(by_layer) or by_layer[index + 1][1][2] != d:
            layer_qs.append(layer_state.count(Q))
            layer_rows.append(dict(depth=d, q_live=layer_state.count(Q)))
    gate_metrics = volume_metrics(n, [r['q_live'] for r in trace[1:]])
    layer_metrics = volume_metrics(n, layer_qs)
    full = next((r['normalized_gate_position'] for r in trace[1:] if r['q_live'] == n), None)
    gaps = [e['gap_from_previous_event'] for e in events]
    peak = max(r['q_live'] for r in trace)
    never = sum(a['never_quantum'] for a in activations)
    summary = dict(n=n, gates=g, depth=max((o[2] for o in ops), default=0), q_final=state.count(Q),
                   q_peak=peak, never_quantum_count=never, never_quantum_fraction=never/n if n else 0,
                   full_materialization_reached=full is not None, never_full_materialization=full is None,
                   first_full_materialization_fraction=full, num_materialization_events=len(events),
                   median_materialization_gap=float(np.median(gaps)) if gaps else 0,
                   max_materialization_gap=max(gaps, default=0), peak_storage_reduction_log2=n-peak,
                   peak_storage_reduction=exp2_safe(n-peak), unknown_gate_count=sum(unknown.values()),
                   unsupported_dynamic=False, parse_ok=True, **gate_metrics)
    for kind, met in [('gate', gate_metrics), ('layer', layer_metrics)]:
        summary[f'log2_ideal_{kind}_reduction'] = met['log2_reduction']
        summary[f'ideal_{kind}_reduction'] = met['reduction_factor_if_representable']
        summary[f'ideal_{kind}_hilbert_volume_reduction'] = met['reduction_factor_if_representable']
    return dict(summary=summary, trace=trace, activations=activations, events=events,
                unknown=dict(unknown), operations=ops, layers=layer_rows)
