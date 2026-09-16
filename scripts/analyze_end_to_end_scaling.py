"""Summarize the common scaling subset separately from the frozen 20/22/24q core."""
import _e2e_common
import hashlib
import json
import re
from pathlib import Path
import datetime
import platform
import subprocess
import sys

import pandas as pd
from htp.e2e.tables import latex_table

root = Path('results/end_to_end_scaling')
raw = pd.read_csv(root / 'raw_runs.csv')
assert not raw.duplicated(['workload_id', 'system', 'repetition']).any()
assert raw.groupby(['workload_id', 'system']).size().eq(3).all()
assert raw.groupby('workload_id').system.nunique().eq(3).all()
manifest = pd.read_csv('results/end_to_end_workloads.csv').set_index('workload_id')
runtime_hash = hashlib.sha256(Path('src/htp/e2e/runtime.py').read_bytes()).hexdigest()
assert raw.runtime_sha256.eq(runtime_hash).all()
gbsa_hash = hashlib.sha256(Path('src/htp/e2e/gbsa.py').read_bytes()).hexdigest()
assert raw[raw.system == 'GBSA reproduction'].gbsa_sha256.eq(gbsa_hash).all()
for wid in raw.workload_id.unique():
    entry = manifest.loc[wid]
    assert hashlib.sha256(Path(entry.input_file).read_bytes()).hexdigest() == entry['hash']
    assert raw[raw.workload_id == wid].input_hash.eq(entry['hash']).all()
assert raw.m.eq(16).all() and raw.t.eq(12).all() and raw.threads.eq(1).all()
raw['algorithmic_total_bytes'] = raw.algorithmic_read_bytes + raw.algorithmic_write_bytes
raw['proc_total_bytes'] = raw.proc_read_bytes + raw.proc_write_bytes
raw['device_total_bytes'] = raw.device_read_bytes + raw.device_write_bytes
metrics = ['wall_time_s', 'user_cpu_s', 'system_cpu_s', 'algorithmic_total_bytes',
           'proc_total_bytes', 'device_total_bytes', 'peak_rss_bytes', 'compute_unit_count',
           'state_traversals', 'sync_time_s', 'algorithmic_read_bytes', 'algorithmic_write_bytes',
           'proc_read_bytes', 'proc_write_bytes', 'proc_cancelled_write_bytes',
           'device_read_bytes', 'device_write_bytes', 'fdatasync_calls']
summaries = []
for (wid, system), group in raw.groupby(['workload_id', 'system']):
    result = dict(workload_id=wid, system=system, family=group.family.iloc[0],
                  n=int(group.n.iloc[0]), repetitions=len(group))
    result.update({c: group[c].median() for c in metrics})
    result.update(time_min_s=group.wall_time_s.min(), time_max_s=group.wall_time_s.max(),
                  time_std_s=group.wall_time_s.std(),
                  time_cv=group.wall_time_s.std() / group.wall_time_s.mean())
    summaries.append(result)
summary = pd.DataFrame(summaries).sort_values(['n', 'family', 'system'])
summary.to_csv(root / 'system_summary.csv', index=False)
rows = []
for wid, group in summary.groupby('workload_id'):
    row = dict(workload_id=wid, family=group.family.iloc[0], n=int(group.n.iloc[0]))
    for system, prefix in [('QDAO', 'qdao'), ('QThin', 'qthin'), ('GBSA reproduction', 'gbsa')]:
        r = group[group.system == system].iloc[0]
        row.update({prefix + '_' + c: r[c] for c in metrics + ['time_cv']})
        row[prefix + '_gib'] = r.algorithmic_total_bytes / 2**30
    row['qdao_qthin_speedup'] = row['qdao_wall_time_s'] / row['qthin_wall_time_s']
    row['gbsa_qthin_speedup'] = row['gbsa_wall_time_s'] / row['qthin_wall_time_s']
    row['qdao_qthin_byte_reduction'] = row['qdao_gib'] / row['qthin_gib']
    row['gbsa_qthin_byte_reduction'] = row['gbsa_gib'] / row['qthin_gib']
    rows.append(row)
comparison = pd.DataFrame(rows).sort_values(['n', 'family'])
comparison.to_csv(root / 'summary.csv', index=False)
core_runs = pd.concat([pd.read_csv('results/qdao_end_to_end/raw_runs.csv'),
                      pd.read_csv('results/gbsa_comparison/raw_runs.csv')], ignore_index=True)
all_runs = pd.concat([core_runs, raw], ignore_index=True)
coverage = []
for family in sorted(core_runs.family.unique()):
    for n in [20, 22, 24, 26, 28]:
        group = all_runs[(all_runs.family == family) & (all_runs.n == n)]
        complete = len(group) == 9 and group.groupby('system').size().eq(3).all()
        assert complete or len(group) == 0
        coverage.append(dict(workload_id=f'{family}_{n}', family=family, n=n,
            status='COMPLETED' if complete else 'NOT_SELECTED_TIME_BUDGET',
            measured_runs=len(group), systems=group.system.nunique(),
            scope='required core' if n <= 24 else 'representative scaling subset'))
coverage = pd.DataFrame(coverage)
coverage.to_csv(root / 'coverage.csv', index=False)
coverage[coverage.status != 'COMPLETED'].assign(reason='NOT_SELECTED_TIME_BUDGET').to_csv(root / 'skipped_cases.csv', index=False)
trends = all_runs[all_runs.family.isin(['cdkm_superposed', 'qaoa'])].copy()
trends['algorithmic_total_bytes'] = trends.algorithmic_read_bytes + trends.algorithmic_write_bytes
trends.groupby(['family', 'n', 'system'])[['wall_time_s', 'algorithmic_total_bytes']].median().reset_index().to_csv(
    root / 'combined_size_trends.csv', index=False)
timecols = [('family', 'Workload'), ('n', '$n$'), ('qdao_wall_time_s', 'QDAO (s)'),
            ('gbsa_wall_time_s', 'GBSA repr. (s)'), ('qthin_wall_time_s', 'QThin (s)'),
            ('qdao_qthin_speedup', 'QDAO/QThin'), ('gbsa_qthin_speedup', 'GBSA/QThin')]
bytecols = [('family', 'Workload'), ('n', '$n$'), ('qdao_gib', 'QDAO (GiB)'),
            ('gbsa_gib', 'GBSA repr. (GiB)'), ('qthin_gib', 'QThin (GiB)'),
            ('qdao_qthin_byte_reduction', 'QDAO/QThin'), ('gbsa_qthin_byte_reduction', 'GBSA/QThin')]
tex = latex_table(comparison, timecols,
    'Representative scaling subset, three measured repetitions per system. GBSA is a policy reproduction on the common backend.',
    'tab:scaling-runtime') + '\n' + latex_table(comparison, bytecols,
    'Scaling subset: instrumented state-payload read/write requests, not physical SSD bytes.', 'tab:scaling-traffic')
(root / 'tables.tex').write_text(tex)


def markdown(columns):
    lines = ['| ' + ' | '.join(title for _, title in columns) + ' |',
             '|' + '|'.join('---' for _ in columns) + '|']
    for row in comparison.to_dict('records'):
        lines.append('| ' + ' | '.join(str(row[c]) if c == 'family' else str(int(row[c])) if c == 'n'
                                      else f'{row[c]:.3f}' for c, _ in columns) + ' |')
    return '\n'.join(lines)


report = f'''# Representative end-to-end scaling subset

{len(comparison)} common workload-size points; {len(raw)} measured runs; three repetitions per system.
Selected before timing: superposed CDKM arithmetic and QAOA early-physicalization control.
28q, if present, covers only the arithmetic point; QAOA at 28q was not measured.
This is not the full workload matrix. Exact coverage and unselected points are in `coverage.csv`.

## Runtime medians

{markdown(timecols)}

## Requested state-payload traffic

{markdown(bytecols)}

All three systems use identical QPY hashes, fixed m=16/t=12 (GBSA C=16), complex128,
one thread, buffered NPY and the same final-state synchronization policy.
The case runners and runtime source are unchanged from the core experiments.
Correctness evidence is the existing 195 Phase A and 195 GBSA small exact cases,
with zero failures and unchanged validated runtime hashes; the large scaling runs
are not new exact-state validation cases.
Methods rotate in seeded shuffled order within each repetition; timed runs are serial.
Individual samples, min/max/std/CV, CPU time and process/device counters are retained.
No slow samples are discarded. Ratios are derived from sample medians, not significance tests.

This remains a file-backed WSL2/ext4 VHDX experiment. Full states are 1 GiB at 26q and 4 GiB at 28q;
these data establish size trends rather than exceeding-memory capacity capability.
GBSA is an independent published-policy reproduction on the common QDAO/Aer substrate,
not the authors' native SSDGBSA artifact. Shared guest-device counters are not uniquely
attributable, and requested payload bytes are not native SSD/NAND bytes.

The earlier 28q SSD result is a single materialization event, not a full-circuit run.
See execution-order records and pre-run plans for actual coverage and selection.
'''
if (summary.n == 28).any():
    report += '\n## 28q storage-path diagnostics\n\n'
    report += '| System | Wall s | User + system CPU s | Final sync s | Process read GiB | Process write GiB | Cancelled write GiB | Guest-device write GiB |\n'
    report += '|---|---:|---:|---:|---:|---:|---:|---:|\n'
    for r in summary[summary.n == 28].itertuples():
        report += (f'| {r.system} | {r.wall_time_s:.3f} | {r.user_cpu_s+r.system_cpu_s:.3f} | '
            f'{r.sync_time_s:.3f} | {r.proc_read_bytes/2**30:.6f} | {r.proc_write_bytes/2**30:.3f} | '
            f'{r.proc_cancelled_write_bytes/2**30:.3f} | {r.device_write_bytes/2**30:.3f} |\n')
    report += ('\nThese are per-column medians, not a causal runtime decomposition. '
        'Small process-accounted read volumes indicate that most payload reads hit the page cache. '
        'Final sync is timed for every method; these runs also incur writeback during execution. '
        'CPU work and storage stalls both affect wall time. Guest-device counters are shared, '
        'and process write counters must be read alongside cancelled writes. '
        'No native NVMe/NAND or capacity-scale OOC claim follows from this table.\n')
Path('END_TO_END_SCALING_REPORT.md').write_text(report)
if (root / 'capacity_revision.json').exists():
    report += ('\n## Capacity-safety pause\n\n'
        'After four completed 28q samples the original uniform 3B (12 GiB) preflight reserve '
        'exceeded 70% of host free space. Temporary state files were already removed. '
        'Execution paused before the next timed run; incomplete-set analysis correctly refused to proceed. '
        'Source inspection bounded simultaneous source/destination amplitude banks by 1.5B, '
        'and the revised conservative guard reserves 2B + 1 GiB (9 GiB at 28q), '
        'including NPY file allocation and metadata allowance for fixed t=12 and 4 KiB blocks. '
        'Six capacity tests passed; the 70% free-space limit was retained. '
        'Only the pre-run capacity estimator changed; timed case runners, kernels, inputs and parameters '
        'remained unchanged. No completed sample was discarded. The pause and changing host-space '
        'conditions are part of this small-sample experiment, not controlled native-device conditions. '
        'See `capacity_revision.json` and the preserved performance log.\n')
    Path('END_TO_END_SCALING_REPORT.md').write_text(report)
combined_report = Path('END_TO_END_EVALUATION_REPORT.md')
marker = '<!-- representative-scaling-extension -->'
core = combined_report.read_text().split(marker)[0].rstrip()
core = re.sub(r'<!-- scaling-coverage -->.*?<!-- /scaling-coverage -->\s*', '', core, flags=re.S)
core = core.replace('216 timed runs total.', '216 core timed runs.')
core = core.replace('Four standalone LaTeX table environments;',
                    'Four core LaTeX table environments plus two scaling tables;')
count26 = int((comparison.n == 26).sum())
count28 = int((comparison.n == 28).sum())
coverage_header = (f'<!-- scaling-coverage -->\n'
    f'Representative 26q extension: {"completed" if count26 else "not run"} ({count26} workload-size points).\n'
    f'Representative 28q extension: {"completed" if count28 else "not run"} ({count28} arithmetic point); other 28q workloads were not measured.\n'
    f'Core plus extension: **{len(all_runs)} measured runs**, three repetitions per system at every completed point.\n'
    '<!-- /scaling-coverage -->\n\n')
core = core.replace('## Primary runtime table', coverage_header + '## Primary runtime table', 1)
combined_report.write_text(core + '\n\n' + marker + '\n\n## Completed representative scaling extension\n\n'
    + f'{len(comparison)} additional common points, {len(raw)} measured runs; three repetitions per system. '
    + 'These are a preselected subset, not the full larger-size workload matrix.\n\n'
    + markdown(timecols) + '\n\nSee `END_TO_END_SCALING_REPORT.md` for traffic, coverage and limitations.\n')
combined_tables = Path('results/end_to_end_tables.tex')
tex_marker = '% representative-scaling-extension'
core_tex = combined_tables.read_text().split(tex_marker)[0].rstrip()
combined_tables.write_text(core_tex + '\n\n' + tex_marker + '\n' + tex)
(root / 'analysis_audit.json').write_text(json.dumps(dict(runs=len(raw), points=len(comparison),
    input_hashes_verified=True, repetitions_per_system=3, common_runtime_sha256=runtime_hash,
    gbsa_sha256=gbsa_hash, all_three_systems_at_every_point=True), indent=2) + '\n')
repro = dict(timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    branch=subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip(),
    git_status_at_analysis=subprocess.check_output(['git', 'status', '--short'], text=True),
    python=sys.version, kernel=platform.release(), seed=20260916,
    core_environment='results/gbsa_comparison/environment.json',
    measured_execution_order='results/end_to_end_scaling/execution_order.jsonl',
    plans=[str(p) for p in sorted(root.glob('plan_*.json'))],
    source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in
        [Path('src/htp/e2e/runtime.py'), Path('src/htp/e2e/gbsa.py'), Path('src/htp/e2e/capacity.py'),
         Path('scripts/run_end_to_end_scaling.py'), Path('scripts/run_e2e_case.py'),
         Path('scripts/run_gbsa_case.py'), Path('results/end_to_end_workloads.csv')]},
    commands=['python scripts/run_end_to_end_scaling.py --size 26 --families cdkm_superposed qaoa',
              'python scripts/prepare_end_to_end_scaling.py --size 28 --families cdkm_superposed',
              'python scripts/run_end_to_end_scaling.py --size 28 --families cdkm_superposed',
              'python scripts/analyze_end_to_end_scaling.py', 'python scripts/audit_end_to_end_scaling.py'])
(root / 'reproducibility.txt').write_text(json.dumps(repro, indent=2) + '\n')
print(comparison[['family', 'n', 'qdao_qthin_speedup', 'gbsa_qthin_speedup']].to_string(index=False))
