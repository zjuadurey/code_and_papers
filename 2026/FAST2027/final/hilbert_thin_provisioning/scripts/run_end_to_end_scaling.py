"""Deadline-limited, serial common-subset extension; frozen primary data stay read-only."""
import _e2e_common
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import time

import pandas as pd
from htp.storage.environment_probe import host_free, host_volume
from htp.e2e.capacity import scaling_capacity_bytes


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=int, choices=[26, 28], default=26)
    parser.add_argument('--families', nargs='+', default=['cdkm_superposed', 'qaoa'])
    parser.add_argument('--latest-group-start', default='2026-09-16T16:00:00+08:00')
    args = parser.parse_args()
    assert set(args.families) <= {'cdkm_superposed', 'qaoa', 'comparator'}
    root = Path('results/end_to_end_scaling')
    (root / 'raw').mkdir(parents=True, exist_ok=True)
    lock = open('build/e2e-performance.lock', 'a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    audit = json.loads(Path('results/gbsa_comparison/analysis_audit.json').read_text())
    assert audit['gbsa_runs'] == 72 and audit['correctness_failures'] == 0
    final_audit = json.loads(Path('results/gbsa_comparison/final_audit.json').read_text())
    assert final_audit['gbsa_measured_runs'] == 72 and final_audit['tests_passed'] >= 243
    for name in ['phase_a_hashes.json', 'previous_results_hashes.json']:
        for path, sha in json.loads((Path('results/qdao_end_to_end') / name).read_text()).items():
            assert digest(path) == sha, path
    verification = json.loads(Path('results/gbsa_comparison/correctness.json').read_text())
    assert verification['validated'] and verification['failures'] == 0
    assert verification['source_sha256'] == digest('src/htp/e2e/gbsa.py')
    manifest = pd.read_csv('results/end_to_end_workloads.csv')
    selected = manifest[(manifest.n == args.size) & manifest.family.isin(args.families)]
    assert len(selected) == len(set(args.families))
    selected_path = root / 'selected_workloads.csv'
    recorded = pd.read_csv(selected_path) if selected_path.exists() else selected.iloc[:0]
    pd.concat([recorded, selected]).drop_duplicates('workload_id').to_csv(selected_path, index=False)
    sources = {p: digest(p) for p in [
        'src/htp/e2e/runtime.py', 'src/htp/e2e/gbsa.py',
        'src/htp/e2e/capacity.py',
        'scripts/run_end_to_end_scaling.py',
        'scripts/run_e2e_case.py', 'scripts/run_gbsa_case.py',
        'results/end_to_end_workloads.csv', 'patches/qdao_current_qiskit.patch']}
    stamp = dt.datetime.now(dt.timezone.utc).isoformat().replace(':', '-')
    plan = dict(timestamp=stamp, families=args.families, n=args.size, repetitions=3,
        systems=['QDAO', 'QThin', 'GBSA reproduction'], seed=20260916,
        rationale='Preselected superposed arithmetic positive and early-physicalization control; comparator optional.',
        latest_group_start=args.latest_group_start, source_sha256=sources,
        parent_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        scope='Representative scaling subset; not a full larger-size corpus or capacity-scale OOC test.')
    (root / f'plan_{stamp}.json').write_text(json.dumps(plan, indent=2) + '\n')
    if not (root / 'environment.json').exists():
        environment = json.loads(Path('results/gbsa_comparison/environment.json').read_text())
        environment.update(benchmark_dir=str((root / 'workdir').resolve()),
                           git_commit=plan['parent_commit'], scope=plan['scope'])
        (root / 'environment.json').write_text(json.dumps(environment, indent=2) + '\n')
    cutoff = dt.datetime.fromisoformat(args.latest_group_start)
    host = host_volume() if 'microsoft' in os.uname().release.lower() else None
    skips = []
    rng = random.Random(20260916)
    for family in args.families:
        row = selected[selected.family == family].iloc[0]
        if dt.datetime.now(dt.timezone.utc) >= cutoff:
            skips.append(dict(workload_id=row.workload_id, reason='SKIPPED_TIME_BUDGET'))
            continue
        assert digest(row.input_file) == row['hash']
        for repetition in range(3):
            methods = ['QDAO', 'QThin', 'GBSA reproduction']
            rng.shuffle(methods)
            for method in methods:
                tag = 'GBSA' if method == 'GBSA reproduction' else method
                output = root / 'raw' / f'{row.workload_id}_{tag}_{repetition}.json'
                if output.exists():
                    old = json.loads(output.read_text())
                    assert old['input_hash'] == row['hash'] and old['system'] == method
                    assert old['runtime_sha256'] == sources['src/htp/e2e/runtime.py']
                    continue
                free = shutil.disk_usage(root).free
                host_capacity = host_free(host['DriveLetter']) if host else None
                if host_capacity is not None:
                    free = min(free, host_capacity)
                required = scaling_capacity_bytes(args.size, os.statvfs(root).f_frsize)
                if required > .7 * free:
                    with (root / 'capacity_stops.jsonl').open('a') as handle:
                        handle.write(json.dumps(dict(workload_id=row.workload_id, system=method,
                            repetition=repetition, free_bytes=free, required_bytes=required,
                            time_unix=time.time())) + '\n')
                    raise RuntimeError('Insufficient safe disk capacity; do not run an incomplete comparison silently')
                assert all(digest(p) == sha for p, sha in sources.items())
                command = [sys.executable,
                    'scripts/run_gbsa_case.py' if tag == 'GBSA' else 'scripts/run_e2e_case.py',
                    '--workload', row.workload_id, '--repetition', str(repetition), '--output', str(output)]
                if tag != 'GBSA':
                    command += ['--system', method]
                with (root / 'execution_order.jsonl').open('a') as handle:
                    handle.write(json.dumps(dict(command=command, start_unix=time.time(),
                        free_bytes=free, required_capacity_bytes=required, load_average=os.getloadavg())) + '\n')
                print('START', row.workload_id, method, repetition, flush=True)
                subprocess.run(command, check=True, env=dict(os.environ,
                    OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1'))
                records = [json.loads(p.read_text()) for p in sorted((root / 'raw').glob('*.json'))]
                pd.DataFrame([{k: v for k, v in r.items() if k != 'events'} for r in records]).to_csv(
                    root / 'raw_runs.csv', index=False)
    pd.DataFrame(skips, columns=['workload_id', 'reason']).to_csv(root / 'skipped_cases.csv', index=False)
    print('SCALING BATCH COMPLETE', flush=True)


if __name__ == '__main__':
    main()
