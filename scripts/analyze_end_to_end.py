"""Combine measured Phase A with explicitly unavailable GBSA results.

Never manufacture a published baseline from an unspecified blocking heuristic.
This script intentionally refuses to overwrite any future GBSA measurements.
"""
import _e2e_common
import datetime
import hashlib
import json
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from htp.e2e.tables import phase_a_tables, latex_table, number

root = Path('results/gbsa_comparison')
root.mkdir(exist_ok=True)
a = Path('results/qdao_end_to_end')
for manifest in ['phase_a_hashes.json', 'previous_results_hashes.json']:
    hashes = json.loads((a/manifest).read_text())
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h for p,h in hashes.items())
raw_path = root/'raw_runs.csv'
if raw_path.exists():
    assert pd.read_csv(raw_path).empty, 'GBSA measurements exist: implement measured combination explicitly'
summary = pd.read_csv(a/'summary.csv')
raw = pd.read_csv(a/'raw_runs.csv')
manifest = pd.read_csv('results/end_to_end_workloads.csv')
required = manifest[manifest.n.isin([20,22,24])]
assert len(summary)==24 and len(raw)==144
assert raw.groupby(['workload_id','system']).size().eq(3).all()
assert not raw.duplicated(['workload_id','system','repetition']).any()
for r in manifest.itertuples():
    assert hashlib.sha256(Path(r.input_file).read_bytes()).hexdigest()==r.hash

blocked = 'SOURCE_BLOCKED_NO_VERIFIABLE_GBSA_ALGORITHM_OR_ARTIFACT'
pd.DataFrame(columns=['workload_id','family','n','system','repetition','wall_time_s',
    'algorithmic_read_bytes','algorithmic_write_bytes','proc_read_bytes','proc_write_bytes',
    'device_read_bytes','device_write_bytes']).to_csv(raw_path,index=False)
b = required[['workload_id','family','n','hash']].copy()
b['system']='GBSA reproduction';b['status']=blocked;b['repetitions']=0
for col in ['wall_time_s','algorithmic_total_bytes','proc_total_bytes','device_total_bytes',
            'time_min_s','time_max_s','time_std_s','time_cv']:
    b[col]=np.nan
b.to_csv(root/'summary.csv',index=False,na_rep='NA')
verification=dict(status='NOT_RUN_SOURCE_BLOCKED',cases=0,failures=None,
    validated=False,reason=blocked,phase_a_correctness_cases=195,phase_a_failures=0)
(root/'correctness.json').write_text(json.dumps(verification,indent=2)+'\n')
env=json.loads((a/'environment.json').read_text())
env.update(phase_a_commit='79ab9a107b83346452bdbb96341a22076a533a44',
    gbsa_status=blocked,gbsa_commit=None,gbsa_language=None,gbsa_license=None,
    gbsa_backend=None,gbsa_runtime_versions=None,
    note='No GBSA timed run; environment is the intended common Phase A environment.')
(root/'environment.json').write_text(json.dumps(env,indent=2)+'\n')
fairness=[];skips=[]
for r in required.itertuples():
    for system in ['QDAO','QThin','GBSA reproduction']:
        available=system!='GBSA reproduction'
        fairness.append(dict(workload_id=r.workload_id,system=system,input_file=r.input_file,
            input_hash=r.hash,representation=r.representation,precision='complex128',
            m=16 if available else None,t=12 if available else None,threads=1 if available else None,
            io_mode='buffered_npy' if available else None,
            sync='final surviving state fdatasync' if available else None,
            status='MEASURED_PHASE_A' if available else blocked))
    for rep in range(3):
        skips.append(dict(workload_id=r.workload_id,n=r.n,system='GBSA reproduction',repetition=rep,reason=blocked))
for r in manifest[manifest.n==26].itertuples():
    for system in ['QDAO','QThin','GBSA reproduction']:
        skips.append(dict(workload_id=r.workload_id,n=26,system=system,repetition='ALL',reason='SKIPPED_TIME_BUDGET'))
pd.DataFrame(fairness).to_csv(root/'fairness_manifest.csv',index=False,na_rep='NA')
pd.DataFrame(skips).to_csv(root/'skipped_cases.csv',index=False)

# Untimed partition counts; extrapolation is a planning estimate, never a result.
counts={'cdkm_basis':7,'cdkm_superposed':7,'comparator':11,'qft':119,
        'qaoa':14,'hea':17,'grover_oracle':234,'mcx_oracle':198}
est=[]
for r in summary[summary.n==24].itertuples():
    units=counts[r.family]*1024
    est.append(dict(family=r.family,n=26,partition_count=counts[r.family],compute_units=units,
        qdao_seconds_extrapolated_per_run=r.qdao_wall_time_s*units/r.qdao_compute_unit_count,
        measured=False,method='24q median seconds per CU times untimed 26q CU count'))
est=pd.DataFrame(est);est.to_csv(root/'optional_26_planning.csv',index=False)
estimated_hours=est.qdao_seconds_extrapolated_per_run.sum()*3/3600

combined=summary.copy()
for col in ['gbsa_wall_time_s','gbsa_algorithmic_total_bytes','qthin_vs_gbsa']:
    combined[col]=np.nan
combined['gbsa_status']=blocked
combined.to_csv('results/end_to_end_summary.csv',index=False,na_rep='NA')
runtime_columns=[('family','Workload'),('n','$n$'),('qdao_wall_time_s','QDAO (s)'),
    ('gbsa_wall_time_s','GBSA repr. (s)'),('qthin_wall_time_s','QThin (s)'),
    ('speedup','QThin/QDAO speedup'),('qthin_vs_gbsa','QThin/GBSA speedup')]
tex=phase_a_tables(summary)+'\n'+latex_table(combined,runtime_columns,
    'Measured runtime medians. GBSA reproduction is source-blocked and NOT RUN; NA is not a performance result.',
    'tab:three-way-runtime')
for method in ['qdao','qthin','gbsa']:
    combined[method+'_gib']=combined[method+'_algorithmic_total_bytes']/2**30
tex+='\n'+latex_table(combined,[('family','Workload'),('n','$n$'),('qdao_gib','QDAO (GiB)'),
    ('gbsa_gib','GBSA repr. (GiB)'),('qthin_gib','QThin (GiB)'),
    ('algorithmic_traffic_reduction','QDAO/QThin'),('qthin_vs_gbsa','GBSA/QThin')],
    'Instrumented state-payload requests, not SSD traffic. GBSA reproduction was NOT RUN.',
    'tab:three-way-traffic')
Path('results/end_to_end_tables.tex').write_text(tex)

table='| Workload | n | QDAO s | GBSA repr. s | QThin s | QThin vs QDAO | QThin vs GBSA |\n|---|---:|---:|---:|---:|---:|---:|\n'
traffic='| Workload | n | QDAO requested GiB | GBSA requested GiB | QThin requested GiB | QDAO/QThin |\n|---|---:|---:|---:|---:|---:|\n'
for r in combined.itertuples():
    table+=f'| {r.family} | {r.n} | {r.qdao_wall_time_s:.3f} | NA | {r.qthin_wall_time_s:.3f} | {r.speedup:.3f}× | NA |\n'
    traffic+=f'| {r.family} | {r.n} | {r.qdao_gib:.4f} | NA | {r.qthin_gib:.4g} | {r.algorithmic_traffic_reduction:.3f}× |\n'
full=summary[summary.qthin_final_q_physical==summary.n]
negative=summary[summary.family.isin(['qaoa','hea'])]
corr=spearmanr(full.algorithmic_traffic_reduction,full.speedup).statistic
families=summary.groupby('family')[['speedup','algorithmic_traffic_reduction']].median().sort_values('speedup',ascending=False)
family_table='| Variant | Median runtime speedup | Median request reduction |\n|---|---:|---:|\n'
for name,r in families.iterrows():family_table+=f'| {name} | {r.speedup:.3f}× | {r.algorithmic_traffic_reduction:.3f}× |\n'
size_table='| n | Points | Median speedup | Fully materialized median |\n|---:|---:|---:|---:|\n'
for n,g in summary.groupby('n'):
    size_table+=f'| {n} | {len(g)} | {g.speedup.median():.3f}× | {g[g.qthin_final_q_physical==g.n].speedup.median():.3f}× |\n'

Path('GBSA_COMPARISON_REPORT.md').write_text(f'''# GBSA comparison: NOT COMPLETED — SOURCE_BLOCKED

Phase A checkpoint: `79ab9a1`. All Phase A performance processes finished before
GBSA source inspection. Phase A and older results remain hash-verified and frozen.

The requested published baseline could not be faithfully implemented because
the RACS paper's full algorithm and an official artifact were not obtained.
The DOI is [10.1145/3769002.3769982](https://doi.org/10.1145/3769002.3769982).
The [institution record](https://researchoutput.ncku.edu.tw/zh/publications/toward-efficient-quantum-circuit-simulation-with-memory-and-io-re/)
confirms the paper and abstract, but does not specify the selector/storage rules
needed for a fair reproduction. See `notes/gbsa_reproduction.md` and the source
audit for retrieval attempts and exact missing information.

GBSA correctness cases: 0; failures: **NA (not tested)**. GBSA performance runs:
0. All 72 required GBSA runs are explicitly skipped for the source blocker.
No official result, fabricated number or generic greedy proxy is substituted.
The following tables preserve only measured Phase A values. They are incomplete
three-way tables and cannot support a QThin-versus-GBSA claim.

## Runtime

{table}
## Requested state traffic

{traffic}
## Fairness and resumption

Common QPY files and SHA256s are frozen in `results/end_to_end_workloads.csv`.
`fairness_manifest.csv` maps those files to all three intended systems; GBSA
configuration fields remain NA. A later reproduction must validate correctness,
then run the same 24 required points with three repetitions. Reuse of Phase A
would introduce a sequential-batch timing limitation, which must be disclosed.

26q: SKIPPED_TIME_BUDGET. An untimed count-based extrapolation predicts roughly
{estimated_hours:.1f} hours for QDAO alone at 26q with three repetitions, before
QThin/GBSA and reporting. This is not a measured 26q runtime.
''')

Path('END_TO_END_EVALUATION_REPORT.md').write_text(f'''# END-TO-END RESULT: PROMISING

**Required task partially complete: Phase A is STRONG; Phase B is source-blocked.**
This label summarizes the available integration evidence, not an unmeasured
victory over GBSA. The requested published-baseline comparison is still missing.

- QDAO integration: completed, checkpoint `79ab9a1`.
- GBSA reproduction: NOT IMPLEMENTED / NOT RUN — missing verifiable algorithm/artifact.
- Workloads completed: 8 variants × 3 sizes = 24 points; 144 timed runs.
- 20q: completed QDAO/QThin; GBSA not run.
- 22q: completed QDAO/QThin; GBSA not run.
- 24q: completed QDAO/QThin; GBSA not run.
- 26q: SKIPPED_TIME_BUDGET.
- Correctness: 195 three-way exact cases, 0 QDAO/QThin failures; GBSA failures NA.
- Tests at Phase A freeze: 229 passed.
- Environment: WSL2/ext4 VHDX, buffered file-backed state, m=16/t=12,
  complex128, one CPU thread, shared current-Aer state-injection adapter.

## Primary runtime table: measured medians, seconds

{table}
## Requested state traffic: measured at actual manager calls

{traffic}
These are amplitude payload requests, not physical SSD traffic. NPY file bytes,
process counters and shared guest-device counters are separately retained in
Phase A CSVs. The sizes fit in available RAM; these are **small-scale file-backed
end-to-end integration results**, not capacity-scale out-of-core results.

## Q1–Q3: runtime, traffic and benefiting families

QThin is faster at all {len(summary)} measured workload/size medians. Overall
median speedup is {summary.speedup.median():.3f}×; the {len(full)} eventually fully
materialized points have median {full.speedup.median():.3f}× and median requested
traffic reduction {full.algorithmic_traffic_reduction.median():.3f}×. Basis-input
CDKM never materializes, so its much larger gains are shown separately.

Across the fully materialized points, Spearman correlation between request-byte
reduction and runtime speedup is {corr:.3f} (descriptive, not a causal estimate).
Lower backing width also reduces compute-unit execution and staging. This
combined experiment cannot attribute all speedup to storage or fusion alone.

{family_table}
## Q4: earlier-entangling controls

QAOA/HEA show no median-time slowdown in this set: speedups range from
{negative.speedup.min():.3f}× to {negative.speedup.max():.3f}×. This does not prove
zero overhead on every fully entangled circuit. Small exact tests exercise the
full-materialization fallback; they are correctness checks, not a performance
ablation. QFT is not assumed negative: on the frozen lowered zero-input stream,
dimensions activate progressively despite a product final state.

## Q5–Q6: comparison with GBSA

**Unanswered.** Neither QThin superiority nor GBSA superiority can be inferred.
The source audit is in `notes/gbsa_reproduction.md`; the unavailable baseline
cells deliberately remain NA. Do not put a GBSA win/loss claim in the paper.

## Q7: consistency across sizes

{size_table}
The sign is consistent, but magnitude is workload dependent. For example, 24q
Grover and MCX provide modest gains; they are retained alongside stronger cases.
All three repetitions, min/max, standard deviation and CV are available.

## Q8: optional 26q

Not run. Using actual 26q partition counts and measured 24q seconds per compute
unit predicts approximately {estimated_hours:.1f} hours for QDAO alone at three
repetitions, before QThin or GBSA. This exceeds the remaining approximate
seven-hour window. `optional_26_planning.csv` marks this explicitly as an
extrapolation, not a performance measurement. No fast-only 26q subset is
presented as completion of the common suite.

## Q9: evidence types

- Measured: wall/CPU/sync time, manager payload/file requests, /proc counters,
  shared guest-device deltas, correctness errors and per-run event counts.
- Derived: medians, CV, ratios, correlations and aggregates.
- Planning estimate: 26q extrapolation from compute-unit counts.
- Unavailable: GBSA timings/correctness; native physical NVMe/NAND traffic.

The final sync covers surviving files for both systems. Intermediate buffered
writes may be coalesced/cancelled; process cancelled_write_bytes is retained.
Shared guest-device deltas are not uniquely attributable to this process.

## Q10: defensible FAST claims

1. A minimal QThin runtime integrated with upstream QDAO's fixed partitions and
   compute-unit storage path is numerically correct on 195 small exact cases.
2. On this eight-variant 20/22/24q suite, with common current-Aer compatibility
   adaptation, it reduces median end-to-end time and requested state bytes.
   Quote the fully materialized subset ({full.speedup.median():.3f}× median
   runtime speedup) alongside the overall {summary.speedup.median():.3f}×.
3. These results demonstrate file-backed integration on WSL2, complementing
   the previous independently measured event-level storage prototype. They do
   not establish native-NVMe large-capacity speedup or superiority over GBSA.

QDAO baseline caveat: the upstream engine, partitioner, scheduling and
gather/scatter are retained, but both systems use a shared public Aer
set_statevector/norm-restoration bridge. It is not completely unmodified author
software. Original-API diagnostic samples are preserved and excluded from the
primary matrix. All previous stage results and Phase A files remain unchanged.

## Artifacts and remaining blocker

- `QDAO_INTEGRATION_REPORT.md`: complete Phase A analysis.
- `GBSA_COMPARISON_REPORT.md`: explicit missing baseline and resume requirements.
- `results/end_to_end_summary.csv`: measured A with unavailable B fields.
- `results/end_to_end_tables.tex`: four LaTeX table environments; GBSA cells NA.

A readable GBSA paper or verified author artifact is required to complete Phase
B fairly. No paper draft was edited and no results were pushed.
''')
print('Combined measured tables generated; GBSA remains explicitly NOT RUN.')
print('26q QDAO-only planning estimate, hours:',estimated_hours)
