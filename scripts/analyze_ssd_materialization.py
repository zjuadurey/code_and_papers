import _ssd_common as common
import json,math,subprocess,datetime,shutil
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import pandas as pd
from htp.storage.analysis import summarize
from htp.storage.environment_probe import host_free

out=common.OUT
status=json.loads((out/'execution_status.json').read_text());assert status['status']=='PASS'
correct=json.loads((out/'correctness.json').read_text());assert correct['status']=='PASS' and correct['incorrect_cases']==0
assert correct['binary_sha256']==common.digest(common.BINARY)
for path,digest in correct['code_sha256'].items():
    if path.startswith('native/') or path=='scripts/validate_ssd_materialization.py':
        assert common.digest(common.ROOT/path)==digest,('Correctness evidence stale',path)
tests=ET.parse(out/'logs/pytest.xml').getroot()
test_failures=sum(int(x.get('failures',0))+int(x.get('errors',0)) for x in tests.iter('testsuite'))
tests_passed=sum(int(x.get('tests',0))-int(x.get('failures',0))-int(x.get('errors',0))-int(x.get('skipped',0)) for x in tests.iter('testsuite'))
assert test_failures==0 and tests_passed>=214
env=json.loads((out/'environment.json').read_text());raw=pd.read_csv(out/'raw_runs.csv');manifest=pd.read_csv(out/'benchmark_manifest.csv')
capacity_after=dict(timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    guest_free_bytes=shutil.disk_usage(common.bench_dir()).free,
    host_free_bytes=host_free((env.get('host_volume') or {}).get('DriveLetter')))
(out/'capacity_after.json').write_text(json.dumps(capacity_after,indent=2))
skip=pd.read_csv(out/'skipped_cases.csv')
assert raw.config_id.is_unique and len(raw)==status['completed_runs']
assert set(manifest.config_id)==set(raw.config_id)|set(skip.config_id)
assert (raw.sample_max_abs_error<=1e-12).all()
assert (raw.configured_buffer_bytes<=256*1024**2).all()
assert set(raw.binary_sha256)=={correct['binary_sha256']}
for row in raw.itertuples():
    assert int(row.old_state_bytes)==16<<int(row.q_old)
    assert int(row.new_state_bytes)==2*int(row.old_state_bytes) and row.q_new==row.q_old+1
    assert row.logical_output_bytes==row.new_state_bytes
    assert abs(row.total_elapsed_s-row.operation_elapsed_s-row.sync_elapsed_s)<1e-7
    chunks=int(row.old_state_bytes)//int(row.effective_chunk_bytes)
    expected_calls={'NAIVE_PRODUCT':(3,4),'NAIVE_BASIS':(3,4),'THIN_BASIS':(3,3),'PRODUCT_FUSED':(1,2),'FUSED_BASIS':(1,2)}
    reads,writes=expected_calls[row.policy]
    assert row.pread_calls==reads*chunks and row.pwrite_calls==writes*chunks
summary,statistics=summarize(raw)
summary.to_csv(out/'summary.csv',index=False,na_rep='NA');statistics.to_csv(out/'run_statistics.csv',index=False,na_rep='NA')
allocation=raw[raw.scenario=='basis'][['config_id','q_old','policy','gate','io_mode','repetition','logical_output_bytes',
    'allocated_output_bytes_before_gate','allocated_output_bytes_after_gate']]
allocation['before_allocation_fraction']=allocation.allocated_output_bytes_before_gate/allocation.logical_output_bytes
allocation['after_allocation_fraction']=allocation.allocated_output_bytes_after_gate/allocation.logical_output_bytes
allocation.to_csv(out/'allocation_behavior.csv',index=False,na_rep='NA')
chunk=statistics[(statistics.study.isin(['main','chunk']))&statistics.q_old.isin(common.config()['chunk_sensitivity_q'])&
                 (statistics.product_state=='plus')&(statistics.gate=='cx_product_control')&(statistics.target==3)]
chunk.to_csv(out/'chunk_sensitivity.csv',index=False,na_rep='NA')
buffered=statistics[(statistics.study.isin(['main','buffered']))&statistics.q_old.isin(common.config()['buffered_sensitivity_q'])&
                    (statistics.product_state=='plus')&(statistics.gate=='cx_product_control')&(statistics.target==3)]
buffered.to_csv(out/'direct_vs_buffered.csv',index=False,na_rep='NA')
mode='direct' if env['direct_io']['supported'] and 'direct' in common.config()['io_modes'] else 'buffered'
main=summary[(summary.study=='main')&(summary.io_mode==mode)&summary.interpretation_eligible].copy()
eligible=main[~((main.gate=='cx_product_target')&(main.product_state=='plus'))]
large=eligible[eligible.q_old>=28]
fallback=False
if not len(large):large=eligible[eligible.q_old>=26];fallback=True
assert len(large),'No storage-size results available to interpret'
device_available=large.device_traffic_reduction.notna().all()
counter_domain='device' if device_available else 'proc' if large.proc_traffic_reduction.notna().all() else 'algorithmic'
traffic=float(large[counter_domain+'_traffic_reduction'].median());speed=float(large.latency_speedup.median())
median_policy_cv=float(np.maximum(large.baseline_latency_cv,large.fused_latency_cv).median())
unstable=median_policy_cv>.3
if traffic>=2 and speed>=1.5 and mode=='direct' and counter_domain!='algorithmic' and not unstable and not fallback:decision='STRONG'
elif speed<=1.2 or unstable:decision='MIXED' if traffic>=1.5 else 'WEAK'
elif traffic>=1.5 and speed>=1.2:decision='PROMISING'
else:decision='WEAK'
next_step='INTEGRATE_QDAO' if counter_domain!='algorithmic' and traffic>=1.5 and (speed>=1.2 or traffic>=2) else 'REFINE_SSD_MECHANISM'
largest=int(raw.q_old.max())
def finite_or_none(value):
    return float(value) if pd.notna(value) and math.isfinite(value) else None

def metric_text(value):
    return 'NA' if value is None else f'{value:.5g}'

publication_ready=env['storage_environment_class']=='native_linux' and mode=='direct' and device_available
decision_record=dict(result=decision,next_step=next_step,largest_completed_q=largest,decision_q_values=sorted(map(int,large.q_old.unique())),
    smaller_size_fallback=fallback,decision_configurations=len(large),median_algorithmic_traffic_reduction=float(large.algorithmic_traffic_reduction.median()),
    median_proc_traffic_reduction=finite_or_none(large.proc_traffic_reduction.median()),median_device_traffic_reduction=finite_or_none(large.device_traffic_reduction.median()),
    median_latency_speedup=speed,median_max_policy_cv=median_policy_cv,
    measured_counter_domain=counter_domain,correctness_cases=correct['correctness_cases'],correctness_failures=0,
    native_publication_prerequisites=publication_ready)
(out/'decision.json').write_text(json.dumps(decision_record,indent=2))

def table(df):
    if df.empty:return '_No completed configurations._'
    def fmt(v):
        if isinstance(v,(float,np.floating)):
            return 'NA' if not math.isfinite(v) else f'{v:.5g}'
        return str(v).replace('|','\\|')
    return '| '+' | '.join(df.columns)+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+'\n'.join('| '+' | '.join(fmt(v) for v in r)+' |' for r in df.itertuples(index=False,name=None))

show=main[(main.q_old>=max(26,largest-1))&(main.product_state=='random_seeded')].copy()
columns=['q_old','old_size_GiB','gate','algorithmic_traffic_reduction','proc_traffic_reduction','device_traffic_reduction','baseline_latency_s','fused_latency_s','latency_speedup']
byte_table=show[['q_old','gate']].copy()
for c in ['baseline_algorithmic_traffic_bytes','fused_algorithmic_traffic_bytes','baseline_proc_traffic_bytes','fused_proc_traffic_bytes','baseline_device_traffic_bytes','fused_device_traffic_bytes']:
    byte_table[c.replace('_bytes','_GiB')]=show[c]/1024**3
size_table=eligible.groupby('q_old')[['algorithmic_traffic_reduction','proc_traffic_reduction','device_traffic_reduction','latency_speedup']].median().reset_index()
chunk_table=summary[(summary.study.isin(['main','chunk']))&summary.q_old.isin(common.config()['chunk_sensitivity_q'])&
                  (summary.product_state=='plus')&(summary.gate=='cx_product_control')&(summary.target==3)]
mode_table=summary[(summary.study.isin(['main','buffered']))&summary.q_old.isin(common.config()['buffered_sensitivity_q'])&
                  (summary.product_state=='plus')&(summary.gate=='cx_product_control')&(summary.target==3)]
allocation_table=allocation.groupby(['q_old','policy'])[['logical_output_bytes','allocated_output_bytes_before_gate','allocated_output_bytes_after_gate','before_allocation_fraction','after_allocation_fraction']].median().reset_index()
target_table=summary[(summary.study.isin(['main','target']))&(summary.q_old==28)&(summary.product_state=='plus')&(summary.gate=='cx_product_control')]
git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip()
host_identity='Host physical-device identity is unavailable.'
host_budget_text='Host-volume capacity is unavailable or not applicable.'
host_volume=env.get('host_volume') or {}
if host_volume.get('Size'):
    host_budget_text=(f"At the initial audit the host volume had {host_volume['SizeRemaining']/1024**3:.3f} GiB free "
        f"of {host_volume['Size']/1024**3:.3f} GiB ({100*host_volume['SizeRemaining']/host_volume['Size']:.2f}% free). "
        'This is a volume-level capacity observation, not an SSD-internal free-block or garbage-collection measurement.')
supplement=out/'host_device_supplement.json'
if supplement.exists():
    for query in json.loads(supplement.read_text()).get('queries',[]):
        if query['returncode']==0 and 'Get-Partition' in ' '.join(query['command']):
            identity=json.loads(query['stdout'])
            host_identity=f"The supplementary Windows query maps the VHDX host volume to {identity['FriendlyName']}, BusType {identity['BusType']}."
        elif query['returncode']!=0:
            host_identity+=' The supplemental reliability query failed; its exact error is retained in host_device_supplement.json.'
temporal_rows=[]
for (q,policy),group in raw[raw.study=='main'].groupby(['q_old','policy']):
    group=group.sort_values('actual_order');window=max(1,len(group)//4)
    temporal_rows.append(dict(q_old=q,policy=policy,window_runs=window,
        first_quarter_latency_median_s=group.total_elapsed_s.iloc[:window].median(),
        last_quarter_latency_median_s=group.total_elapsed_s.iloc[-window:].median()))
temporal=pd.DataFrame(temporal_rows)
skip_table=skip.groupby('q_old')[['required_bytes','budget_bytes']].first().reset_index()
for column in ['required_bytes','budget_bytes']:
    skip_table[column.replace('_bytes','_GiB')]=skip_table.pop(column)/1024**3
report=f'''# SSD MECHANISM RESULT: {decision}

Git commit: `{git_commit}` (execution provenance; final delivery commit is its descendant).  
Branch: `{branch}`  
Storage environment: **{env['storage_environment_class']}**  
Filesystem: **{env['filesystem']}**, mount `{env['mount_source']}`  
Direct I/O supported: **{env['direct_io']['supported']}**, tested with 4096-byte aligned read/write.  
Largest completed q: **{largest}**, old backing **{(16<<largest)/1024**3:g} GiB**, output **{(32<<largest)/1024**3:g} GiB**.  
Correctness cases: **{correct['correctness_cases']}**, native executions **{correct['native_executions']}**.  
Correctness failures: **0**.  
Tests passed: **{tests_passed}**, including all 194 predecessor tests.  
Performance runs: **{len(raw)} completed**, **{len(skip)} capacity skips** from {len(manifest)} planned configurations.  

Primary PRODUCT_FUSED versus NAIVE_PRODUCT, random pure product states, largest completed sizes; latency includes fdatasync and ratios use configuration medians:

{table(show[columns])}

**Counter terminology:** algorithmic=requested pread/pwrite bytes; proc=Linux process-accounted bytes; device={env['device_counter_scope']} bytes. Device counters are shared with other guest activity. **These are actual regular-file storage-path measurements, not proven native physical NVMe/NAND traffic.**

Decision aggregate: q={decision_record['decision_q_values']}, {len(large)} gate/state configurations, median measured {counter_domain} traffic reduction **{traffic:.4g}×**, median latency speedup **{speed:.4g}×**. The forced CX target-|+⟩ control is excluded from this aggregate because that factor does not mathematically need physicalization. All requested controls remain in raw data and summary.csv. No timing outliers were removed.

Only comparisons with at least three completed repetitions for both methods enter the decision aggregate. Any interrupted-by-capacity partial group remains identifiable by repetition counts and `interpretation_eligible` in summary.csv.

## Q1. Does native fused materialization produce the same state?

Yes at double-precision tolerance: {correct['correctness_cases']} normalized random cross-file cases (q≤12 old dimensions), {correct['native_executions']} native processes, compared with independent Qiskit eager statevector evolution. Cases include CX(v,p), CX(p,v), CZ, random general 2q unitary, known |0⟩/|1⟩ sparse/basis cases, and supported DIRECT file cases. Maximum elementwise error **{correct['max_abs_error']:.4g}**, maximum infidelity **{correct['max_infidelity']:.4g}**, threshold 1e-12. Every completed large run additionally checks 32 deterministic amplitudes outside timing and counter windows; maximum error **{raw.sample_max_abs_error.max():.4g}**.

The backing file has no header and is flat complex128. New virtual wire v becomes the highest physical address bit q, preserving old physical indices. The local vector is separate metadata. Existing backing may be arbitrarily entangled; the native transformation does not assume it is product. This is a standalone one-event prototype, not a full state simulator or a general logical-wire runtime.

## Q2. What bytes were measured?

Traffic values below are **GiB (2^30 bytes)**; the CSV retains exact byte counts per run:

{table(byte_table)}

Raw process counters also retain rchar, wchar, read_bytes, write_bytes and cancelled_write_bytes. All successful syscall sizes and call counts are instrumented. Device sectors are converted using the Linux stat ABI's 512-byte sectors. When a counter is unavailable its field is NA; no application count substitutes for it.

The accounting boundaries follow the [Linux process-I/O documentation](https://docs.kernel.org/filesystems/proc.html): rchar/wchar count syscall bytes, while read_bytes/write_bytes account storage-layer work with different read/write update points. Sector units and completed-I/O fields follow the [block-stat ABI](https://docs.kernel.org/block/stat.html). Neither counter interface identifies host NAND traffic through a virtual disk.

## Q3. Does 7B → 3B appear at application level?

Every completed run is asserted against the implemented pass count: NAIVE_PRODUCT reads 3B and writes 4B; PRODUCT_FUSED reads B and writes 2B. The resulting theoretical and observed requested-byte reduction is **7/3 = 2.333333×**, with **2× write reduction**. THIN_BASIS reads 3B and writes 3B (6B total) because it omits the initial zero-branch write. It still reads the logical hole during the gate pass and writes the final full output. Sparse-hole reads can consume fewer process/device bytes than requested bytes, which the counters expose.

This one-event ratio has a different denominator and purpose from the previous whole-trace predicted 5.243×. No claim of reproducing that trace aggregate is made.

The baseline is the specified **full expanded-state traversal**. It reads/writes both branches even when a controlled gate acts identically on one branch. A specialized branch-selective baseline for CX(v,p) or CZ could omit that branch in the gate pass, giving an analytical 5B baseline and 5/3 ratio instead; that variant is **not measured here**. Therefore 7/3 is a property of the requested expand-then-full-pass comparison, not a universal lower bound against every optimized controlled-gate implementation. QDAO integration must compare against the actual traversal behavior it replaces.

## Q4. Does traffic reduction survive below the application?

On the decision subset, process-accounted reduction median is **{metric_text(decision_record['median_proc_traffic_reduction'])}×**; {env['device_counter_scope']} reduction median is **{metric_text(decision_record['median_device_traffic_reduction'])}×**. Extra filesystem reads/writes and background activity are left in the observed counters. The block source is `{env['mount_source']}`, model `{env['device_model']}`, rotational flag `{env['rotational_flag']}`. Under WSL these describe a virtual disk and do not establish actual SSD/HDD media.

Write amplification is explicitly defined as device bytes written / final logically necessary output bytes (2B). `summary.csv` stores baseline/fused device write amplification and all three write-reduction ratios. It is guest-path amplification under WSL, not NAND FTL write amplification.

## Q5. How much latency is reduced?

Decision-set median speedup is **{speed:.5g}×**. Every operation uses the same I/O mode, target, chunk, native kernel family and product vector as its comparison. The baseline syncs the intermediate file and the final output; fused only needs the final output sync. Those completion points are part of the design difference. `operation_elapsed_s` excludes fdatasync call durations; `total_elapsed_s` includes them.

`run_statistics.csv` records median, minimum, maximum, sample standard deviation and coefficient of variation for latency, CPU time, throughput, counters, call counts and RSS. Median larger policy CV across the decision set is **{decision_record['median_max_policy_cv']:.5g}**. CPU time is measured separately: tensor expansion plus a permutation/phase pass is more CPU/memory work than their combined contraction, so all timing benefit is not attributed solely to SSD transfers. The input generator, file open, buffer setup and post-run sample checks are not timed; ftruncate and both computational passes are timed.

For these configuration medians, CPU/wall-time median is **{(large.baseline_cpu_s/large.baseline_latency_s).median():.4g}** for naive and **{(large.fused_cpu_s/large.fused_latency_s).median():.4g}** for fused. The remaining wall time includes I/O waiting and scheduling; it does not identify a specific host-device bottleneck.

The individual primary configurations make the nonuniform variability explicit:

{table(large[['gate','product_state','baseline_latency_cv','fused_latency_cv','latency_speedup']])}

## Q6. Dependence on backing size

Per-size medians over the five nontrivial gate/product-state combinations:

{table(size_table)}

The requested-byte ratio is size-independent at 7/3. The measured per-size median latency speedups span **{size_table.latency_speedup.min():.4g}–{size_table.latency_speedup.max():.4g}×**. This is a descriptive size comparison; sequential size order and changing storage-path latency prevent attributing its trend to size alone.

q=24 is a sanity size; q=26/27 are smaller storage-path microbenchmarks. DIRECT bypasses the guest page cache but cannot prove Windows or device caches are cold. These measurements are not end-to-end out-of-core quantum circuit runs. The skipped sizes below exceeded the conservative guest/host free-space budget. Required capacity includes input+working output and a 256 MiB margin; q=29 needs 24.25 GiB and q=30 needs 48.25 GiB. No performance values are imputed for skipped configurations. The full explicit skip list is `skipped_cases.csv` ({len(skip)} rows).

{table(skip_table)}

`capacity_after.json` records free space after cleanup. Ordinary benchmark input/output files are removed, but this does not guarantee that a dynamically growing host VHDX immediately returns its allocated host space. Host free-space changes can also include other activity. No explicit discard/TRIM or VHDX compaction is performed to force reclamation.

## Q7. Chunk sensitivity and target-bit sensitivity

{table(chunk_table[['q_old','chunk_bytes','io_mode','baseline_latency_s','fused_latency_s','latency_speedup','device_traffic_reduction']])}

Across completed chunk configurations, measured speedup spans **{chunk_table.latency_speedup.min():.4g}–{chunk_table.latency_speedup.max():.4g}×**. Changing chunk size does not change the requested 7B/3B pass counts. Its observed latency effect is entangled with measurement time because the chunk blocks are sequential; no best-chunk tuning claim is made.

Chunk-level repetitions are at least three. Main 16 MiB rows reuse the main repetitions. `chunk_sensitivity.csv` also includes I/O call count, peak RSS and device bytes. The configured native workspace is four chunks, bounded by 256 MiB; observed maximum RSS across performance runs is **{raw.peak_rss_bytes.max()/1024**2:.4g} MiB**. Neither baseline nor fused loads the whole file into RAM.

RSS here is the unmodified RUSAGE_SELF ru_maxrss watermark. [getrusage(2)](https://man7.org/linux/man-pages/man2/getrusage.2.html) preserves resource history across exec, so a Python launcher's earlier watermark can dominate smaller native buffers. An ancillary live `/proc/PID/status` observation is retained in `memory_snapshot.json` when available; it is not substituted for per-run RSS. Buffer bytes are separately asserted and reported, so small-chunk RSS plateaus are not interpreted as kernel workspace growth.

Primary target is bit 3; higher-bit sensitivity uses bit 18, still inside a 16 MiB chunk:

{table(target_table[['q_old','target','baseline_latency_s','fused_latency_s','latency_speedup','device_traffic_reduction']])}

An inter-chunk high-bit gate would need a different I/O access pattern and is not covered by this prototype.

## Q8. DIRECT versus BUFFERED + fdatasync

{table(mode_table[['q_old','io_mode','baseline_latency_s','fused_latency_s','latency_speedup','proc_traffic_reduction','device_traffic_reduction']])}

The completed mode/configuration comparisons show speedups of **{mode_table.latency_speedup.min():.4g}–{mode_table.latency_speedup.max():.4g}×**. {'Both recorded modes retain a >1.2× latency benefit in these comparisons.' if mode_table.io_mode.nunique()==2 and (mode_table.latency_speedup>1.2).all() else 'The mode results must be read individually; a uniform >1.2× benefit across two modes is not established.'}

BUFFERED uses POSIX_FADV_DONTNEED after input generation and before measurement; the baseline also advises its synchronized intermediate file before rereading it. Advice return codes are recorded. No root cache-drop command is used. O_DIRECT support is probed, not assumed; all records retain their actual mode. Host/device caching remains possible in both modes.

Modes are measured in separate blocks, with randomized policy order inside each block. The mode contrast also includes possible temporal/thermal/background effects and is a secondary sensitivity, not an isolated causal estimate of caching.

The [Linux open(2) manual](https://man7.org/linux/man-pages/man2/open.2.html) distinguishes O_DIRECT from synchronous completion guarantees; this experiment therefore explicitly calls fdatasync and reports its duration. No direct I/O is outstanding when the native process exits, and buffered sample reads occur after that process has completed.

## Q9. Does THIN_BASIS save actual file allocation?

Allocation is stat.st_blocks×512, sampled after expansion+sync and after the entangler+sync:

{table(allocation_table)}

The thin path uses ftruncate and writes only the known branch; the other branch is a real filesystem hole until the gate output is written. Allocated blocks describe guest filesystem allocation, not the physical size of the host VHDX or NAND usage. The dense final write deliberately writes every output byte, even amplitudes that are mathematically zero. This prototype does not perform content sparsification or filesystem COW.

## Q10. Is this environment suitable for publication-grade native SSD claims?

**{'Yes, the native/direct/device-counter prerequisites are present; device identity and shared-system noise must still accompany any publication claim.' if publication_ready else 'No: this is useful measured prototype evidence, but a native Linux/NVMe rerun is required for native SSD claims.'}** The path is {env['storage_environment_class']}, filesystem {env['filesystem']}. The host-volume audit is {(env.get('host_volume') or {}).get('DriveLetter','not applicable/unknown')}:/{(env.get('host_volume') or {}).get('FileSystem','not applicable/unknown')}. In WSL, guest O_DIRECT and guest block counters establish elimination of guest-visible storage-path work, not elimination of a particular physical NVMe/controller/NAND traversal.

{host_identity} That identity does not turn guest counters into host/controller counters. Temperature and device-internal behavior remain unavailable.

{host_budget_text}

The raw data distinguishes possible distortions: operation versus sync time, CPU time, mode sensitivity, chunk sensitivity, block-versus-process bytes, allocation and repetition CV. It does not provide SSD temperatures, FTL garbage-collection counters, host cache misses or bandwidth saturation proof, so those causal explanations remain hypotheses rather than fabricated measurements. Device counters are shared; no background-system tuning was performed. Load averages and available memory were recorded before every run.

Sizes are processed sequentially in increasing q to bound disk occupancy, and policies are shuffled within each configuration/repetition block. First-versus-last-quarter main-run medians expose temporal variation (the quarters also contain different gate/state groups, so this is descriptive):

{table(temporal)}

The size trend and cross-block sensitivities therefore do not isolate size or time as a cause. Every slow sample is retained; actual order and timestamps allow this variation to be audited.

## Scope, recommendation and reproduction

**NEXT STEP: {next_step}**

{'Correctness is clean and the measured storage-path traffic benefit supports integrating this bounded mechanism with QDAO; the measured timing variability and native-device validation limitation still apply.' if next_step=='INTEGRATE_QDAO' else 'The current storage-path evidence requires refinement before integration; retain the same QThin research direction.'} This stage validates remapping + product metadata + fused first-entangler only. It establishes no whole-program QDAO speedup. QDAO runtime and partition code were not modified, m/t were not tuned, and no workload corpus was expanded.

```
conda activate htp-static
bash scripts/run_ssd_materialization_all.sh
```

The script builds Release C++17 with compiler-recorded flags, runs all tests and file correctness first, then safely runs and summarizes the configured matrix. `HTP_SSD_BENCH_DIR` overrides the ordinary-file directory. Existing output files are never opened for truncation; each benchmark output is newly created. Temporary input/output files are deleted after results are safely journaled. A manifest records planned order; each raw row records actual order, parameters, product-state seed, modes, counters and binary hash. `input_generation.csv` separately records the input seed, generation ID and size. `execution_plan_consistency.json` verifies the final orchestration source regenerates the measured manifest. No raw block write, mount/format, explicit discard/TRIM or privileged cache-drop operation is performed.

`reproducibility.txt`, `build.json`, `environment.json`, `benchmark_manifest.csv` and per-run command logs provide execution provenance. All earlier characterization and materialization-model artifacts are hash checked and left immutable. Numerical values above are measured or ratios of measured medians except the explicitly labeled 7B/3B theoretical pass count. No publication plots were generated.
'''
(common.ROOT/'SSD_MATERIALIZATION_REPORT.md').write_text(report)
count=common.frozen_check()
audit=dict(status='PASS',timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_files_unchanged=count,
    planned_runs=len(manifest),measured_runs=len(raw),skipped_runs=len(skip),correctness_cases=correct['correctness_cases'],
    incorrect_cases=0,tests_passed=tests_passed,test_failures=test_failures,workdir_empty=not any(common.bench_dir().iterdir()),binary_sha256=common.digest(common.BINARY),
    code_sha256=common.code_hashes(),artifact_sha256={str(p.relative_to(common.ROOT)):common.digest(p) for p in out.iterdir() if p.is_file() and p.name!='artifact_audit.json'},
    report_sha256=common.digest(common.ROOT/'SSD_MATERIALIZATION_REPORT.md'))
(out/'artifact_audit.json').write_text(json.dumps(audit,indent=2))
print(json.dumps(decision_record,indent=2))
