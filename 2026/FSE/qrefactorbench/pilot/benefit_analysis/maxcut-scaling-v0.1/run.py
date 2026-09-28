"""Bounded kernel scaling diagnostic; unknown quality/cost terms remain unknown."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import sys
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from qrefactorbench.resource_workflow import qdk_backend

SIZES = (8, 16, 24, 32, 48, 64)
SEEDS = (20260928, 20260929, 20260930)
DEPTHS = (1, 4, 16)


def save(path: Path, data: object) -> None:
    with path.open('x') as f:
        json.dump(data, f, indent=2, allow_nan=False)
        f.write('\n')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def graph(n: int, seed: int) -> list[tuple[int, int, int]]:
    rng = random.Random(seed + n)
    edges = {tuple(sorted((i, (i+1) % n))) for i in range(n)} | {(0, 2)}
    while len(edges) < 2*n:
        edges.add(tuple(sorted(rng.sample(range(n), 2))))
    return [(u, v, rng.randint(1, 5)) for u, v in sorted(edges)]


def value(mask: int, edges: list) -> int:
    return sum(w for u, v, w in edges if ((mask >> u) ^ (mask >> v)) & 1)


def enumerate_optimum(n: int, edges: list) -> tuple[int, int]:
    # Complement symmetry ensures the minimum mask has highest bit zero.
    return max(((value(m, edges), -m) for m in range(1 << (n-1))))


def solve(n: int, edges: list, limit: float = 3) -> dict:
    start = time.perf_counter()
    m = len(edges)
    a = lil_matrix((4*m, n+m))
    hi = np.zeros(4*m)
    for i, (u, v, _) in enumerate(edges):
        z = n+i
        for offset, terms, bound in (
            (0, ((z, 1), (u, -1), (v, -1)), 0),
            (1, ((z, 1), (u, 1), (v, 1)), 2),
            (2, ((z, -1), (u, 1), (v, -1)), 0),
            (3, ((z, -1), (u, -1), (v, 1)), 0)):
            for col, coefficient in terms:
                a[4*i+offset, col] = coefficient
            hi[4*i+offset] = bound
    constraints = [LinearConstraint(a.tocsc(), -np.inf, hi)]
    c = np.array([0]*n + [-w for _, _, w in edges], dtype=float)
    lower, upper = np.zeros(n+m), np.ones(n+m)
    upper[n-1] = 0
    records = []

    def invoke(objective):
        remaining = limit-(time.perf_counter()-start)
        if remaining <= 0:
            return None
        res = milp(objective, integrality=np.ones(n+m), bounds=Bounds(lower, upper),
                   constraints=constraints, options={'time_limit': remaining, 'mip_rel_gap': 0.0})
        records.append({'status': int(res.status), 'message': res.message,
                        'objective': float(res.fun) if res.fun is not None else None,
                        'gap': float(res.mip_gap) if getattr(res, 'mip_gap', None) is not None else None})
        return res

    result = invoke(c)
    optimum, mask = None, None
    if result is not None and result.status == 0:
        bits = np.rint(result.x).astype(int)
        assert np.max(np.abs(result.x-bits)) < 1e-5
        optimum = value(sum(int(bits[i]) << i for i in range(n)), edges)
        assert abs(result.fun+optimum) < 1e-5
        constraints.append(LinearConstraint(c.reshape(1, -1), -optimum, -optimum))
        # Minimize high-to-low bits while retaining globally maximal cut weight.
        for bit in reversed(range(n-1)):
            objective = np.zeros(n+m)
            objective[bit] = 1
            result = invoke(objective)
            if result is None or result.status != 0:
                break
            rounded = int(round(result.x[bit]))
            assert abs(result.x[bit]-rounded) < 1e-5
            lower[bit] = upper[bit] = rounded
        else:
            mask = sum(int(lower[i]) << i for i in range(n))
            assert value(mask, edges) == optimum
    elapsed = time.perf_counter()-start
    return {'n': n, 'edges': len(edges), 'complete': mask is not None,
            'elapsed_seconds': elapsed, 'optimum': optimum, 'minimum_mask': mask,
            'solver_calls': records, 'limit_seconds': limit,
            'scope': 'Kernel exact-value/minimum-mask target; floating solver status, not formal proof'}


def circuit(n: int, edges: list, depth: int) -> str:
    lines = ['OPENQASM 3.0;', 'include "stdgates.inc";', f'qubit[{n}] q;', f'bit[{n}] r;']
    lines += [f'h q[{i}];' for i in range(n)]
    for _ in range(depth):
        for u, v, w in edges:
            lines += [f'cx q[{u}], q[{v}];', f'rz(-{w}*pi/4) q[{v}];', f'cx q[{u}], q[{v}];']
        lines += [f'rx(pi/4) q[{i}];' for i in range(n)]
    lines += [f'r[{i}] = measure q[{i}];' for i in range(n)]
    return '\n'.join(lines)+'\n'


def envelope(classical: dict, row: dict) -> dict:
    if not classical['complete']:
        return {'status': 'unknown_classical_completion', 'shots_upper_bound': None}
    seconds = row['runtime_ns']*1e-9
    ratio = classical['elapsed_seconds']/seconds
    return {'status': 'necessary_budget_only', 'shots_upper_bound': ratio,
            'max_integer_shots_with_H_zero': max(0, math.ceil(ratio)-1),
            'remaining_seconds_for_all_overheads_at_64_shots': classical['elapsed_seconds']-64*seconds,
            'success_probability': None, 'exact_certificate_cost': None,
            'benefit_established': False}


def run(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=False)
    files = [Path(__file__), HERE/'README.md', ROOT/'qrefactorbench/resource_workflow.py',
             ROOT/'qrefactorbench/_qdk_resource_worker.py',
             ROOT/'pilot/source_adaptations/v0.1/cases/lit-001/program.py',
             ROOT/'pilot/source_adaptations/v0.1/cases/lit-001/kernel.py']
    bound = {str(p.relative_to(ROOT)): digest(p) for p in files}
    profile = {'id': 'hypothetical-100ns', 'gate_time_ns': 100,
               'measurement_time_ns': 500, 'error_rate': 1e-4,
               'source': 'Hypothetical scenario inherited from lit001 workflow; not hardware measurement'}
    save(output/'protocol.json', {'sizes': SIZES, 'seeds': SEEDS, 'depths': DEPTHS,
         'authorization': '2026-09-28 user asks to establish research effect and rejects tiny-instance no-benefit evidence; D-041 resource conditions.',
         'classical_limit_seconds': 3, 'qdk_timeout_seconds': 60, 'profile': profile,
         'qdk_max_error_per_circuit': .01, 'source_sha256': bound,
         'python': sys.version, 'scipy': scipy.__version__, 'platform': platform.platform(),
         'scope': 'Exploratory kernel scaling; no formal case/gold change; no positive benefit claim from zero-overhead envelope'})
    # Independent finite oracle check, not reference labels supplied by an LLM.
    checks = []
    for seed in range(8):
        edges = graph(8, seed)
        result = solve(8, edges, 10)
        expected_value, negative_mask = enumerate_optimum(8, edges)
        assert result['complete'] and (result['optimum'], result['minimum_mask']) == (expected_value, -negative_mask)
        checks.append({'seed': seed, 'passed': True})
    assert envelope({'complete': False}, {})['shots_upper_bound'] is None
    assert envelope({'complete': True, 'elapsed_seconds': 1}, {'runtime_ns': 1e9})['max_integer_shots_with_H_zero'] == 0
    save(output/'validation.json', {'finite_solver_checks': checks, 'timeout_and_strict_boundary_checks': True})
    rows = []
    for n in SIZES:
        classical = []
        for seed in SEEDS:
            edges = graph(n, seed)
            save(output/f'graph-{n}-{seed}.json', edges)
            result = solve(n, edges)
            save(output/f'classical-{n}-{seed}.json', result)
            classical.append(result)
            print(json.dumps({'n': n, 'seed': seed, 'complete': result['complete'], 'seconds': result['elapsed_seconds']}), flush=True)
        for depth in DEPTHS:
            source = circuit(n, graph(n, SEEDS[0]), depth)
            (output/f'qaoa-{n}-{depth}.qasm').write_text(source)
            request = {'application': {'source': source}, 'max_error': .01}
            raw = qdk_backend(request, profile, python=sys.executable, timeout=60)
            save(output/f'qdk-{n}-{depth}.json', raw)
            # Compare ONLY the same instance as the resource-estimated graph.
            entry = {'n': n, 'depth': depth, 'logical_qubits': n,
                     'gate_count': n+depth*(3*2*n+n), 'qdk_status': raw['status'],
                     'classical_seconds': classical[0]['elapsed_seconds'] if classical[0]['complete'] else None,
                     'points': [{**point, **envelope(classical[0], point)} for point in raw.get('rows', [])]}
            rows.append(entry)
            print(json.dumps({'n': n, 'depth': depth, 'qdk_status': raw['status']}), flush=True)
    assert all(digest(ROOT/p) == h for p, h in bound.items())
    save(output/'results.json', {'rows': rows, 'source_hashes_unchanged': True,
                               'benefit_established': False, 'quality_and_complete_overheads': 'unknown'})
    save(output/'manifest.json', {p.name: digest(p) for p in sorted(output.iterdir()) if p.is_file()})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args().output.resolve())
