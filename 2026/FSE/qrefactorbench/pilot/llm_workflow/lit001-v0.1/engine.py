"""Trusted tools for one model-generated, four-qubit migration candidate."""
from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
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


def save(path: Path, value: object) -> None:
    with path.open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write('\n')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score(mask: int, matrix: list[list[int]]) -> int:
    return sum(matrix[i][j] for i in range(len(matrix)) for j in range(i + 1, len(matrix))
               if ((mask >> i) & 1) != ((mask >> j) & 1))


def certificate(request: dict, masks: list[int]) -> dict | None:
    """All positive edges cut in a connected graph -> exactly two optima.

    Canonicalize the complementary masks to match the source's first-mask tie.
    This helper never solves for a partition; it checks the measured candidates.
    """
    names, matrix = program.prepare_request(request)
    n = len(names)
    if not n or not masks or any(type(m) is not int or not 0 <= m < 1 << n for m in masks):
        return None
    seen, todo = {0}, [0]
    while todo:
        u = todo.pop()
        for v in range(n):
            if matrix[u][v] > 0 and v not in seen:
                seen.add(v)
                todo.append(v)
    if len(seen) != n:
        return None
    bound = sum(matrix[i][j] for i in range(n) for j in range(i + 1, n))
    candidates = [min(m, m ^ ((1 << n) - 1)) for m in masks if score(m, matrix) == bound]
    if not candidates:
        return None
    best = min(candidates)
    return {'separated_weight': bound, 'windows': [
        [names[i] for i in range(n) if best & (1 << i)],
        [names[i] for i in range(n) if not best & (1 << i)]], 'equipment_count': n}


def finish(request: dict, masks: list[int]) -> tuple[dict, bool]:
    result = certificate(request, masks)
    return (result, False) if result is not None else (program.schedule(request), True)


def strong_classical(request: dict) -> dict:
    """Bipartite graph coloring, with original solver on non-bipartite inputs."""
    names, matrix = program.prepare_request(request)
    colors: dict[int, int] = {}
    mask = 0
    for root in range(len(names)):
        if root in colors:
            continue
        colors[root] = 0
        todo, component = [root], []
        while todo:
            u = todo.pop()
            component.append(u)
            for v in range(len(names)):
                if matrix[u][v] <= 0:
                    continue
                if v in colors:
                    if colors[v] == colors[u]:
                        return program.schedule(request)
                else:
                    colors[v] = 1 - colors[u]
                    todo.append(v)
        a = sum(1 << v for v in component if colors[v])
        b = sum(1 << v for v in component if not colors[v])
        mask |= min(a, b)
    return {'separated_weight': score(mask, matrix), 'windows': [
        [name for i, name in enumerate(names) if mask & (1 << i)],
        [name for i, name in enumerate(names) if not mask & (1 << i)]], 'equipment_count': len(names)}


def angle(text: str) -> float:
    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.Name) and node.id == 'pi':
            return math.pi
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            return visit(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            a, b = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add): return a + b
            if isinstance(node.op, ast.Sub): return a - b
            if isinstance(node.op, ast.Mult): return a * b
            return a / b
        raise ValueError('Only finite arithmetic angles using pi are accepted')
    value = float(visit(ast.parse(text, mode='eval').body))
    if not math.isfinite(value) or abs(value) > 1e6:
        raise ValueError('Angle out of bounds')
    return value


def parse_qasm(source: str) -> list[tuple]:
    """Accept a bounded straight-line gate language; no arbitrary code execution."""
    if not isinstance(source, str) or len(source) > 16000:
        raise ValueError('Expected at most 16 KB OpenQASM')
    source = re.sub(r'//[^\n]*', '', source)
    statements = [s.strip() for s in source.split(';') if s.strip()]
    if statements[:4] != ['OPENQASM 3.0', 'include "stdgates.inc"', 'qubit[4] q', 'bit[4] r']:
        raise ValueError('Use exact header: OPENQASM 3.0; include "stdgates.inc"; qubit[4] q; bit[4] r;')
    gates, measured = [], set()
    for s in statements[4:]:
        m = re.fullmatch(r'r\[([0-3])\]\s*=\s*measure q\[([0-3])\]', s)
        if m:
            a, b = map(int, m.groups())
            if a != b or a in measured:
                raise ValueError('Measure each qubit once into its same-index bit')
            measured.add(a)
            continue
        if measured:
            raise ValueError('All measurements must be last')
        m = re.fullmatch(r'(h|x) q\[([0-3])\]', s)
        if m:
            gates.append((m[1], (int(m[2]),), None))
            continue
        m = re.fullmatch(r'cx q\[([0-3])\],\s*q\[([0-3])\]', s)
        if m and m[1] != m[2]:
            gates.append(('cx', (int(m[1]), int(m[2])), None))
            continue
        m = re.fullmatch(r'(rx|rz)\((.+)\) q\[([0-3])\]', s)
        if m:
            gates.append((m[1], (int(m[3]),), angle(m[2])))
            continue
        raise ValueError(f'Unsupported QASM statement: {s}')
    if measured != set(range(4)) or not 1 <= len(gates) <= 200:
        raise ValueError('Need 1..200 gates and four measurements')
    return gates


def probabilities(gates: list[tuple]) -> list[float]:
    import numpy as np
    state = np.zeros(16, dtype=complex)
    state[0] = 1
    for name, indices, theta in gates:
        if name == 'cx':
            c, t = indices
            for i in range(16):
                if i & (1 << c) and not i & (1 << t):
                    j = i | (1 << t)
                    state[i], state[j] = state[j], state[i]
        else:
            t = indices[0]
            for i in range(16):
                if i & (1 << t): continue
                j = i | (1 << t)
                a, b = state[i], state[j]
                if name == 'h': state[i], state[j] = (a+b)/math.sqrt(2), (a-b)/math.sqrt(2)
                elif name == 'x': state[i], state[j] = b, a
                elif name == 'rz': state[i], state[j] = a*np.exp(-1j*theta/2), b*np.exp(1j*theta/2)
                elif name == 'rx':
                    c, s = math.cos(theta/2), -1j*math.sin(theta/2)
                    state[i], state[j] = c*a+s*b, s*a+c*b
    return [float(abs(a)**2) for a in state]


def verify(candidate: dict, folder: Path) -> dict:
    from qdk import openqasm
    if set(candidate) != {'plan', 'qasm', 'shots', 'decoder'}:
        raise ValueError('Candidate needs exactly plan, qasm, shots, decoder')
    if not isinstance(candidate['plan'], str) or not candidate['plan'].strip():
        raise ValueError('Plan explanation required')
    if candidate['decoder'] != 'connected_all_edges_certificate_else_original':
        raise ValueError('Unsupported decoder')
    if type(candidate['shots']) is not int or not 1 <= candidate['shots'] <= 64:
        raise ValueError('shots must be 1..64')
    gates = parse_qasm(candidate['qasm'])
    if not {'h', 'cx', 'rx', 'rz'} <= {g[0] for g in gates}:
        raise ValueError('This smoke requests a QAOA circuit, not a precomputed answer state')
    (folder / 'application.qasm').write_text(candidate['qasm'])
    probs = probabilities(gates)
    probe = 'OPENQASM 3.0; include "stdgates.inc"; qubit[4] q; bit[4] r; x q[0]; r=measure q;'
    order = openqasm.run(probe, shots=1, as_bitstring=True, seed=20260928)[0]
    if order not in ('1000', '0001'): raise ValueError('Unsupported QDK bit convention')
    raw = openqasm.run(candidate['qasm'], shots=candidate['shots'], as_bitstring=True, seed=20260928)
    masks = [int(s[::-1] if order == '1000' else s, 2) for s in raw]
    original = deepcopy(INSTANCE)
    expected = program.schedule(INSTANCE)
    actual, fallback = finish(INSTANCE, masks)
    sample_sets = [[m] for m in range(16)] + [[], [16], [-1], [True], ['bad']]
    checks = [finish(INSTANCE, ms)[0] == expected for ms in sample_sets]
    _, matrix = program.prepare_request(INSTANCE)
    p = sum(probs[m] for m in range(16) if certificate(INSTANCE, [m]) is not None)
    output = {'status': 'passed' if actual == expected and all(checks) and original == INSTANCE else 'failed',
        'application_sha256': hashlib.sha256(candidate['qasm'].encode()).hexdigest(),
        'logical_qubits': 4, 'gate_count': len(gates), 'shots': candidate['shots'],
        'actual_output': actual, 'classical_output': expected, 'fallback_used': fallback,
        'raw_bitstrings': raw, 'q0_probe': order, 'masks': masks, 'probabilities': probs,
        'measurement_cases_passed': sum(checks), 'measurement_cases_total': len(checks),
        'ideal_expected_cut': sum(probs[m]*score(m, matrix) for m in range(16)),
        'ideal_certificate_probability_per_shot': p,
        'ideal_batch_fallback_probability': (1-p)**candidate['shots'],
        'quality': 'Exact trusted certificate or original classical fallback; QAOA itself need not be exact.',
        'scope': 'Generated circuit for supplied four-node instance; other requests retain original schedule.'}
    save(folder / 'verification.json', output)
    return output


def timing(fn) -> dict:
    fn()
    batches = []
    for _ in range(7):
        start = time.perf_counter()
        for _ in range(500): fn()
        batches.append((time.perf_counter()-start)/500)
    return {'lower': min(batches), 'upper': max(batches),
            'source': 'Local 7x500 perf_counter batch means; descriptive interval, not confidence bound'}


def compare(candidate: dict, verified: dict, folder: Path) -> dict:
    if verified['status'] != 'passed': raise ValueError('Behavior verification required')
    source = candidate['qasm']
    if hashlib.sha256(source.encode()).hexdigest() != verified['application_sha256']:
        raise ValueError('Candidate changed since verification')
    classical = timing(lambda: program.schedule(INSTANCE))
    strong = timing(lambda: strong_classical(INSTANCE))
    prep = timing(lambda: json.dumps(program.prepare_request(INSTANCE)))
    decode = timing(lambda: [int(s[::-1] if verified['q0_probe'] == '1000' else s, 2)
                             for s in verified['raw_bitstrings']])
    # Include BOTH successful certification and the most conservative fallback path.
    good = timing(lambda: finish(INSTANCE, [5] * candidate['shots']))
    bad = timing(lambda: finish(INSTANCE, [0] * candidate['shots']))
    validation = {'lower': min(good['lower'], bad['lower']), 'upper': max(good['upper'], bad['upper']),
                  'source': 'Observed certificate and always-fallback paths; no ideal success-rate discount'}
    assumed = lambda v, reason: {'lower': v, 'upper': v, 'source': 'SCENARIO ASSUMPTION: ' + reason}
    costs = {'preparation': prep, 'readout_decode': decode, 'validation_fallback': validation,
        'classical_control': assumed(1e-6, 'one microsecond dispatch per batch'),
        'communication': assumed(1e-6, 'one microsecond total transfer per batch'),
        'compilation_amortized': assumed(0, 'steady-state fixed circuit, compiled offline; cold-start cost excluded')}
    request = {'version': 'resource-workflow-v0.1', 'plan_id': 'llm-lit001',
        'application': {'format': 'openqasm3', 'source': source,
                        'coverage': 'One complete model-generated shot including preparation and measurement'},
        'profiles': [{'id': f'hypothetical-{ns}ns', 'gate_time_ns': ns, 'measurement_time_ns': 5*ns,
                      'error_rate': 1e-4, 'source': 'Hypothetical architecture, not a calibrated QPU'} for ns in (100, 1000)],
        'max_error': 0.01}
    context = {'application_sha256': verified['application_sha256'], 'comparison_id': 'lit001-exact-steady-state',
        'evidence_source': 'verification.json plus local timing and explicit scenario assumptions',
        'same_task': True, 'classical_seconds': strong, 'overheads_seconds': costs,
        'quantum_executions': candidate['shots'], 'max_failure_probability': 0, 'algorithm_failure_bound': 0}
    save(folder / 'resource-request.json', request)
    save(folder / 'controller-context.json', context)
    resource = analyze_resources(request, context, python=sys.executable, timeout=60)
    save(folder / 'resource-analysis.json', resource)
    if not resource['points'] or any(r['status'] != 'ok' for r in resource['estimation_runs']):
        raise ValueError('QDK did not produce both resource estimates; inspect resource-analysis.json')
    host = [sum(v[k] for v in costs.values()) for k in ('lower', 'upper')]
    result = {'status': 'completed', 'classical_original_seconds': classical,
        'classical_strong_seconds': strong, 'complete_cost_ledger_seconds': costs,
        'host_seconds': host, 'points': resource['points'],
        'break_even': {'formula': 'S*t_shot + H < T_classical; physical_qubits >= estimated requirement',
            'S': candidate['shots'], 'H_seconds': host,
            'optimistic_max_shot_seconds_vs_original': (classical['upper']-host[0])/candidate['shots'],
            'optimistic_max_shot_seconds_vs_strong': (strong['upper']-host[0])/candidate['shots'],
            'guaranteed_max_shot_seconds_vs_strong': (strong['lower']-host[1])/candidate['shots'],
            'interpretation': 'Nonpositive time budget means no feasible faster shot under this host-cost scenario; not a global impossibility.'},
        'quality_composition': 'Raw QDK decision conservatively counts shot errors. Exact certificate/fallback separately preserves output for every measurement; hardware availability/host faults outside scope.',
        'cost_scope': 'Steady-state per request, serial shots; offline LLM development and compilation not charged per invocation.',
        'scenario': 'Measured local host terms plus explicitly assumed dispatch/transfer and offline compilation.'}
    save(folder / 'comparison.json', result)
    return result
