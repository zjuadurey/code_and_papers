"""Validate small instances and evaluate large resource conditions, without large statevectors."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import formulas as f

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from qrefactorbench.resource_workflow import qdk_backend


def save(path: Path, value: object) -> None:
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=False)
    protected = {str(p.relative_to(ROOT)): sha(p)
                 for directory in (HERE, HERE.parent/'maxcut-scaling-v0.1',
                                   ROOT/'pilot/llm_workflow/lit001-v0.1', ROOT/'qrefactorbench')
                 for p in directory.rglob('*') if p.is_file()
                 and '__pycache__' not in p.parts and not p.is_relative_to(output)}
    small = list(itertools.product((4, 6, 8, 10, 12), (20260928, 20260929, 20260930), (1, 2, 4)))
    large = [(n, p, 100) for n, p in itertools.product((100, 200, 500), (1, 4, 16))]
    large += [(100, 1, 10), (100, 1, 1000)]
    save(output/'protocol.json', {'created_utc': datetime.now(timezone.utc).isoformat(),
        'authorization': 'User requests small-scale validation and formula-derived potential advantage beyond simulation; then 照这个情况推进下; no requirement to own large QPU.',
        'small_validation_grid': small, 'large_resource_grid': large,
        'physical_error_rate': 1e-4, 'measurement_time_over_gate_time': 5,
        'max_error_per_shot': .01, 'qdk_timeout_seconds': 60,
        'condition_grid': {'classical_seconds': [.1, 1, 10, 100], 'fixed_seconds': [0, .01, .1],
                           'per_shot_seconds': [0, .0001, .001], 'shots': [1, 4, 16, 64, 256, 1024]},
        'cost_interpretation': 'All large classical/host costs are explicit condition coordinates, not extrapolated measurements.',
        'protected_before': protected, 'python': sys.version, 'numpy': np.__version__, 'platform': platform.platform()})
    observations = []
    for n, seed, depth in small:
        edges = f.graph(n, seed)
        structure = f.verify_structure(n, edges, depth)
        a, b = f.hamiltonian_state(n, edges, depth), f.gate_state(n, edges, depth)
        fidelity = float(abs(np.vdot(a, b))**2)
        assert abs(fidelity-1) < 1e-10
        assert abs(float(np.vdot(a, a).real)-1) < 1e-10
        score = f.costs(n, edges)
        optimum = int(score.max())
        mask = int(np.flatnonzero(score == optimum)[0])
        probs = np.abs(a)**2
        pair = {mask, mask ^ ((1 << n)-1)}
        r_exact = float(sum(probs[i] for i in pair))
        r_any = float(probs[score == optimum].sum())
        assert r_exact <= r_any+1e-12
        observations.append({'n': n, 'seed': seed, 'depth': depth, 'edges': edges,
            'fidelity_up_to_global_phase': fidelity, 'resources': structure,
            'optimal_cut': optimum, 'minimum_mask': mask,
            'ideal_any_optimum_probability': r_any,
            'ideal_canonical_pair_probability': r_exact,
            'iid_64_shot_contains_canonical_pair_probability': f.batch_success(r_exact, 64),
            'usable_certified_success_probability': None})
    save(output/'small-validation.json', observations)
    print(json.dumps({'small_instances': len(observations), 'state_validation': 'passed'}), flush=True)
    estimates, grid = [], []
    for n, depth, ns in large:
        label = f'n{n}-p{depth}-g{ns}'
        edges = f.graph(n, 20260928)
        structure = f.verify_structure(n, edges, depth)
        source = f.qasm(n, edges, depth)
        (output/f'{label}.qasm').write_text(source)
        profile = {'id': label, 'gate_time_ns': ns, 'measurement_time_ns': 5*ns,
                   'error_rate': 1e-4, 'source': 'Hypothetical physical model; fixed physical error rate, not real-device calibration'}
        request = {'application': {'source': source}, 'max_error': .01}
        started = time.perf_counter()
        raw = qdk_backend(request, profile, python=sys.executable, timeout=60)
        elapsed = time.perf_counter()-started
        save(output/f'{label}-qdk.json', raw)
        row = {'label': label, 'n': n, 'depth': depth, 'profile': profile, 'resources': structure,
               'application_sha256': hashlib.sha256(source.encode()).hexdigest(),
               'status': raw['status'], 'points': raw.get('rows', []), 'estimator_wall_seconds': elapsed,
               'large_state_simulation_performed': False}
        estimates.append(row)
        for index, point in enumerate(row['points']):
            for classical, fixed, per_shot, shots in itertools.product(
                    (.1, 1, 10, 100), (0, .01, .1), (0, .0001, .001), (1, 4, 16, 64, 256, 1024)):
                answer = f.required_success(shots, point['runtime_ns']*1e-9, fixed, per_shot, classical)
                grid.append({'label': label, 'point_index': index,
                    'classical_seconds_assumed': classical, 'fixed_seconds_assumed': fixed,
                    'per_shot_seconds_assumed': per_shot, 'fallback_seconds_assumed': classical,
                    'shots': shots, 'condition': answer})
        print(json.dumps({'label': label, 'status': row['status'], 'wall_seconds': elapsed,
                          'points': len(row['points'])}), flush=True)
    save(output/'large-resources.json', estimates)
    save(output/'conditions.json', grid)
    changed = [name for name, digest in protected.items() if sha(ROOT/name) != digest]
    assert not changed, changed
    save(output/'validation.json', {'small_instances_passed': len(observations),
        'qdk_attempts': len(estimates), 'qdk_successes': sum(x['status'] == 'ok' for x in estimates),
        'conditional_points': len(grid), 'large_state_simulations': 0,
        'protected_files_unchanged': len(protected), 'model_calls': 0, 'qpu_calls': 0})
    save(output/'manifest.json', {p.name: sha(p) for p in output.iterdir() if p.is_file()})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args().output.resolve())
