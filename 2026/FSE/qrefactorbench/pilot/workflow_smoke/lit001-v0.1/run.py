"""Direct MaxCut -> QAOA -> simulation -> actual resource-backend smoke."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import sys
import time

os.environ['QDK_PYTHON_TELEMETRY'] = 'none'
os.environ['QSHARP_PYTHON_TELEMETRY'] = 'none'
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CASE = ROOT / 'pilot/source_adaptations/v0.1/cases/lit-001'
sys.path[:0] = [str(ROOT), str(CASE)]
import program
from qrefactorbench.resource_workflow import analyze_resources

INSTANCE = {'equipment': ['A', 'B', 'C', 'D'], 'requirements': [
    {'first': a, 'second': b, 'weight': 1}
    for a, b in [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')]]}
GAMMA, BETA, SHOTS, SEED = math.pi / 4, math.pi / 8, 32, 20260928


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def circuit(request):
    names, matrix = program.prepare_request(request)
    n = len(names)
    gates = [('h', (i,), None) for i in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i][j]:
                # C_ij = w(1-Z_i Z_j)/2; global phase omitted.
                gates += [('cx', (i, j), None), ('rz', (j,), -GAMMA * matrix[i][j]),
                          ('cx', (i, j), None)]
    gates += [('rx', (i,), 2 * BETA) for i in range(n)]
    lines = ['OPENQASM 3.0;', 'include "stdgates.inc";', f'qubit[{n}] q;', f'bit[{n}] result;']
    for name, indices, angle in gates:
        gate = name if angle is None else f'{name}({angle:.17g})'
        lines.append(gate + ' ' + ', '.join(f'q[{i}]' for i in indices) + ';')
    lines += [f'result[{i}] = measure q[{i}];' for i in range(n)]
    return '\n'.join(lines) + '\n', gates, matrix


def probabilities(gates, n):
    """Independent small state vector for gate/sign/order verification."""
    import numpy as np
    state = np.zeros(1 << n, dtype=complex)
    state[0] = 1
    for name, indices, angle in gates:
        if name == 'cx':
            control, target = indices
            for bits in range(1 << n):
                if bits & (1 << control) and not bits & (1 << target):
                    other = bits | (1 << target)
                    state[bits], state[other] = state[other], state[bits]
        else:
            target = indices[0]
            for bits in range(1 << n):
                if bits & (1 << target):
                    continue
                other = bits | (1 << target)
                a, b = state[bits], state[other]
                if name == 'h':
                    state[bits], state[other] = (a + b) / math.sqrt(2), (a - b) / math.sqrt(2)
                elif name == 'rz':
                    state[bits] = a * np.exp(-1j * angle / 2)
                    state[other] = b * np.exp(1j * angle / 2)
                elif name == 'rx':
                    c, s = math.cos(angle / 2), -1j * math.sin(angle / 2)
                    state[bits], state[other] = c * a + s * b, s * a + c * b
                else:
                    raise ValueError(name)
    result = [float(abs(a) ** 2) for a in state]
    assert abs(sum(result) - 1) < 1e-10
    return result


def score(mask, matrix):
    return sum(matrix[i][j] for i in range(len(matrix)) for j in range(i + 1, len(matrix))
               if bool(mask & (1 << i)) != bool(mask & (1 << j)))


def finish_cycle(request, measured_masks):
    """Exact certificate for this 4-cycle only, else use original solver.

    This is an instance-specific engineering wrapper, not a general QAOA solver.
    """
    names, matrix = program.prepare_request(request)
    if request != INSTANCE or not measured_masks:
        return program.schedule(request), True
    if any(type(m) is not int or not 0 <= m < 16 for m in measured_masks):
        return program.schedule(request), True
    canonical = [min(mask, mask ^ 15) for mask in measured_masks]
    best = min(canonical, key=lambda mask: (-score(mask, matrix), mask))
    weight_sum = sum(matrix[i][j] for i in range(4) for j in range(i + 1, 4))
    if score(best, matrix) != weight_sum:
        return program.schedule(request), True
    return {'separated_weight': weight_sum,
            'windows': [[names[i] for i in range(4) if best & (1 << i)],
                        [names[i] for i in range(4) if not best & (1 << i)]],
            'equipment_count': 4}, False


def measure(fn):
    values = []
    fn()
    for _ in range(7):
        start = time.perf_counter()
        for _ in range(1000):
            fn()
        values.append((time.perf_counter() - start) / 1000)
    return {'lower': min(values), 'upper': max(values),
            'source': '7x1000 local perf_counter calls; descriptive range, not confidence bound',
            'batch_means': values}


def run(output, python):
    from qdk import openqasm
    output.mkdir(parents=True, exist_ok=False)
    def save(name, data):
        with (output / name).open('x') as f:
            json.dump(data, f, indent=2, sort_keys=True, allow_nan=False)
            f.write('\n')
    inputs = [CASE / x for x in ('program.py', 'kernel.py', 'public_task.json')]
    inputs += [Path(__file__), HERE / 'protocol.json', ROOT / 'qrefactorbench/resource_workflow.py',
               ROOT / 'qrefactorbench/_qdk_resource_worker.py']
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in inputs}
    save('input-manifest.json', hashes)
    save('instance.json', INSTANCE)
    before = deepcopy(INSTANCE)
    source, gates, matrix = circuit(INSTANCE)
    (output / 'application.qasm').write_text(source)
    expected = program.schedule(INSTANCE)
    ideal = probabilities(gates, 4)
    # Calibrate the actual SDK bitstring convention instead of guessing endianness.
    probe = 'OPENQASM 3.0; include "stdgates.inc"; qubit[4] q; bit[4] r; x q[0]; r=measure q;'
    observed = openqasm.run(probe, shots=1, as_bitstring=True, seed=SEED)[0]
    if observed not in ('1000', '0001'):
        raise ValueError(f'Unexpected QDK bitstring output: {observed!r}')
    little = observed == '1000'
    raw = openqasm.run(source, shots=SHOTS, as_bitstring=True, seed=SEED)
    masks = [int(bits[::-1] if little else bits, 2) for bits in raw]
    actual, used_fallback = finish_cycle(INSTANCE, masks)
    assert actual == expected and INSTANCE == before
    assert all(ideal[m] > 1e-12 for m in masks)
    # Check every possible one-shot outcome, including hardware-corrupted candidates.
    for mask in range(16):
        assert finish_cycle(INSTANCE, [mask])[0] == expected
    assert finish_cycle(INSTANCE, [])[0] == expected
    optimal_probability = sum(p for mask, p in enumerate(ideal) if score(mask, matrix) == 4)
    simulation = {'sdk': 'qdk.openqasm.run', 'shots': SHOTS, 'seed': SEED,
        'q0_probe_bitstring': observed, 'raw_bitstrings': raw, 'decoded_masks': masks,
        'histogram_masks': dict(Counter(masks)), 'ideal_statevector_probabilities': ideal,
        'expected_cut_random': 2, 'expected_cut_qaoa': sum(p * score(m, matrix) for m, p in enumerate(ideal)),
        'ideal_single_shot_optimal_probability': optimal_probability,
        'ideal_32_shot_at_least_one_optimal_probability': 1 - (1 - optimal_probability) ** SHOTS,
        'classical_output': expected, 'hybrid_output': actual, 'fallback_used': used_fallback,
        'all_16_single_samples_and_absent_sample_correct': True,
        'noise_note': 'Ideal local simulation; independent-shot probability is an ideal-model statement only'}
    save('simulation.json', simulation)
    timing = {'classical_full_schedule': measure(lambda: program.schedule(INSTANCE)),
              'circuit_preparation': measure(lambda: circuit(INSTANCE)),
              'decode_validate_observed_batch': measure(lambda: finish_cycle(INSTANCE, masks))}
    save('host-timings.json', timing)
    interval = lambda x: {k: x[k] for k in ('lower', 'upper', 'source')}
    request = {'version': 'resource-workflow-v0.1', 'plan_id': 'lit001-qaoa-p1-cycle4',
        'application': {'format': 'openqasm3', 'source': source,
            'coverage': 'one QAOA p=1 shot including uniform initialization, edge cost phases, mixers, measurement'},
        'profiles': [{'id': f'hypothetical-{ns}ns', 'gate_time_ns': ns,
            'measurement_time_ns': ns * 5, 'error_rate': 1e-4,
            'source': 'hypothetical gate-based configuration; not calibrated physical device'} for ns in (100, 1000)],
        'max_error': 0.01}
    context = {'application_sha256': hashlib.sha256(source.encode()).hexdigest(),
        'comparison_id': 'lit001-four-cycle-exact-task',
        'evidence_source': 'simulation.json and host-timings.json; finite engineering checks only',
        'same_task': True, 'classical_seconds': interval(timing['classical_full_schedule']),
        'overheads_seconds': {'preparation': interval(timing['circuit_preparation']),
            'classical_control': None, 'communication': None, 'readout_decode': None,
            'validation_fallback': None, 'compilation_amortized': None},
        'quantum_executions': SHOTS, 'max_failure_probability': 0, 'algorithm_failure_bound': 0}
    save('resource-request.json', request)
    save('controller-context.json', context)
    result = analyze_resources(request, context, python=python, timeout=60)
    save('resource-analysis.json', result)
    rows = result['points']
    ok = all(r['status'] == 'ok' for r in result['estimation_runs']) and bool(rows)
    # Preserve missing deployment terms; a known quantum subtotal can still be a lower bound.
    excluded = [r['profile_id'] for r in rows
                if r['quantum_seconds_total'] >= timing['classical_full_schedule']['upper']]
    summary = {'workflow_status': 'completed' if ok else 'backend_incomplete',
        'case': 'lit-001', 'instance': 'four-node unit cycle', 'quantum_path': 'QAOA p=1',
        'quantum_implementation_verified': True, 'fallback_used_in_actual_run': used_fallback,
        'logical_qubits': 4, 'unitary_gates': len(gates), 'shots': SHOTS,
        'correct_output': actual, 'resource_points': len(rows),
        'profiles_with_quantum_subtotal_above_observed_classical_range': excluded,
        'full_cost_status': 'complete ledger; unavailable deployment costs remain null',
        'decision': 'positive quantum implementation smoke passed; practical benefit not established on this tiny instance',
        'limitations': ['Current-session authored workflow, not autonomous or held-out LLM evaluation.',
                       'Finite instance certificate; QAOA is not generally an exact MaxCut solver.',
                       'A cycle also has a linear-time classical solution; enumeration is not a competitive general baseline.',
                       'QDK failure union bound does not model classical certificate/fallback recovery.',
                       'Simulator wall time is not quantum device time.'],
        'environment': {'python': sys.version, 'platform': platform.platform(),
                        'qdk': importlib.metadata.version('qdk'), 'pyqir': importlib.metadata.version('pyqir')}}
    assert all(digest(ROOT / p) == h for p, h in hashes.items()), 'Source/adapter changed during run'
    save('summary.json', summary)
    save('output-manifest.json', {p.name: digest(p) for p in sorted(output.iterdir()) if p.is_file()})
    print(json.dumps(summary, indent=2))
    return 0 if ok else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--qdk-python', default=sys.executable)
    args = parser.parse_args()
    raise SystemExit(run(args.output, args.qdk_python))
