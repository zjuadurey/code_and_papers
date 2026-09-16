import _e2e_common
import json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from htp.e2e.tables import phase_a_tables
root=Path('results/qdao_end_to_end')
raw=pd.read_csv(root/'raw_runs.csv')
required=pd.read_csv('results/end_to_end_workloads.csv').query('n in [20,22,24]')
assert set(required.workload_id)<=set(raw.workload_id), 'Required workload/size points are missing'
assert (raw.sync_barrier_count==1).all(), 'Completion policy differs between runs'
for r in raw.itertuples():
    assert r.algorithmic_write_bytes-r.algorithmic_read_bytes==16*(1<<r.final_q_physical)
    if r.system=='QDAO':
        assert r.algorithmic_read_bytes==r.state_traversals*16*(1<<r.n)
        assert r.compute_unit_count==r.state_traversals*(1<<(r.n-r.m))
    else:
        assert r.materialized_dimensions_total==r.final_q_physical
verification=json.loads((root/'correctness.json').read_text())
assert set(raw.runtime_sha256)=={verification['runtime_sha256']}
rows=[]
for workload,g in raw.groupby('workload_id',sort=False):
    base=dict(workload_id=workload,family=g.family.iloc[0],n=int(g.n.iloc[0]))
    for system in ['QDAO','QThin']:
        r=g[g.system==system]
        assert len(r)>=3,(workload,system,len(r))
        prefix=system.lower()
        base[prefix+'_repetitions']=len(r)
        for col in ['wall_time_s','user_cpu_s','system_cpu_s','algorithmic_read_bytes','algorithmic_write_bytes',
                    'proc_read_bytes','proc_write_bytes','proc_cancelled_write_bytes','device_read_bytes','device_write_bytes',
                    'final_q_physical','compute_unit_count','state_traversals','materialization_event_count',
                    'materialization_bytes_read','materialization_bytes_written','sync_time_s']:
            base[prefix+'_'+col]=r[col].median() if col in r else np.nan
        for metric,cols in [('algorithmic',['algorithmic_read_bytes','algorithmic_write_bytes']),
                            ('proc',['proc_read_bytes','proc_write_bytes']),
                            ('device',['device_read_bytes','device_write_bytes'])]:
            base[prefix+'_'+metric+'_total_bytes']=(r[cols].sum(axis=1,min_count=len(cols)).median()
                                                   if set(cols)<=set(r.columns) else np.nan)
        base[prefix+'_time_min_s']=r.wall_time_s.min();base[prefix+'_time_max_s']=r.wall_time_s.max()
        base[prefix+'_time_std_s']=r.wall_time_s.std()
        base[prefix+'_time_cv']=r.wall_time_s.std()/r.wall_time_s.mean()
        base[prefix+'_proc_write_minus_cancelled_bytes']=(r.proc_write_bytes-r.proc_cancelled_write_bytes).median()
    base['speedup']=base['qdao_wall_time_s']/base['qthin_wall_time_s']
    for metric in ['algorithmic','proc','device']:
        numerator=base['qdao_'+metric+'_total_bytes'];denominator=base['qthin_'+metric+'_total_bytes']
        base[metric+'_traffic_reduction']=numerator/denominator if denominator>0 else np.nan
    rows.append(base)
summary=pd.DataFrame(rows).sort_values(['n','family'])
summary.to_csv(root/'summary.csv',index=False,na_rep='NA')
Path('results/end_to_end_tables.tex').write_text(phase_a_tables(summary))
legacy_files=list((root/'legacy_api_calibration/raw').glob('*.json'))
if legacy_files:
    legacy=pd.DataFrame([json.loads(p.read_text()) for p in legacy_files])
    calibration=[]
    for (workload,system),old in legacy.groupby(['workload_id','system']):
        if system!='QDAO':continue  # QThin also changed intermediate-sync policy.
        new=raw[(raw.workload_id==workload)&(raw.system==system)]
        if len(new):
            calibration.append(dict(workload_id=workload,system=system,legacy_count=len(old),
                shared_adapter_count=len(new),legacy_median_s=old.wall_time_s.median(),
                shared_adapter_median_s=new.wall_time_s.median(),
                adapter_speedup=old.wall_time_s.median()/new.wall_time_s.median()))
    pd.DataFrame(calibration).to_csv(root/'legacy_interface_comparison.csv',index=False)
raw[['workload_id','system','repetition','compute_unit_count','state_traversals','algorithmic_read_bytes',
     'algorithmic_write_bytes','file_read_bytes','file_write_bytes','sync_time_s']].to_csv(root/'qdao_counters.csv',index=False)
correct=json.loads((root/'correctness.json').read_text())
negative=summary[summary.family.isin(['qaoa','hea'])]
positive=summary[~summary.family.isin(['qaoa','hea','qft'])]
full=summary[summary.qthin_final_q_physical==summary.n]
qualifying=positive.groupby('family').speedup.median()
status=('STRONG' if (qualifying>=1.3).sum()>=2 and (1/negative.speedup).max()<=1.05
        else 'PROMISING' if (summary.speedup>1.1).any() else 'MIXED')
table='| Workload | n | QDAO s | QThin s | Speedup | QDAO requested GiB | QThin requested GiB | Reduction |\n|---|---:|---:|---:|---:|---:|---:|---:|\n'
for r in summary.itertuples():
    thin_gib=r.qthin_algorithmic_total_bytes/2**30
    thin_text=f'{thin_gib:.2e}' if thin_gib<.0001 else f'{thin_gib:.4f}'
    table+=f'| {r.family} | {r.n} | {r.qdao_wall_time_s:.3f} | {r.qthin_wall_time_s:.3f} | {r.speedup:.3f}× | {r.qdao_algorithmic_total_bytes/2**30:.4f} | {thin_text} | {r.algorithmic_traffic_reduction:.3f}× |\n'
kernel_table='| 24q workload | QDAO process MiB | QThin process MiB | QDAO guest device MiB | QThin guest device MiB | Guest ratio |\n|---|---:|---:|---:|---:|---:|\n'
def counter_text(value, scale=1):
    return f'{value/scale:.3f}' if pd.notna(value) else 'NA'
for r in summary[summary.n==24].itertuples():
    values=[counter_text(getattr(r,key),2**20) for key in ['qdao_proc_total_bytes','qthin_proc_total_bytes','qdao_device_total_bytes','qthin_device_total_bytes']]
    kernel_table+='| '+r.family+' | '+' | '.join(values)+' | '+counter_text(r.device_traffic_reduction)+' |\n'
report=f'''# QDAO INTEGRATION RESULT: {status}

Small-scale file-backed end-to-end evaluation on WSL2/ext4 VHDX. This is not a
capacity-scale out-of-core experiment and does not measure host NVMe/NAND traffic.

- Common workloads completed: {len(summary)}; three repetitions per system.
- Correctness: {correct['cases']} three-way exact comparisons; {correct['failures']} failures.
- Maximum phase-aligned QThin amplitude error: {max(r['qthin_error'] for r in correct['comparisons']):.3e}.
- Fixed m=16, t=12, complex128, one CPU thread, buffered NPY files, final fdatasync.
- Median runtime speedup across workload/size points: {summary.speedup.median():.3f}×.
- Geometric mean runtime speedup: {np.exp(np.log(summary.speedup).mean()):.3f}×.
- Eventually fully materialized subset: {len(full)} points; median speedup {full.speedup.median():.3f}×.
- Negative-control (QAOA/HEA) maximum slowdown: {max(0,(1/negative.speedup-1).max())*100:.2f}%; minimum speedup {negative.speedup.min():.3f}×.

## Primary measured runtime and requested payload traffic

{table}

Times are measured medians; ratios are derived from medians. Requested amplitude
bytes are instrumented at actual upstream storage-unit reads/writes. NPY headers
are separately counted in raw_runs.csv. All slow repetitions remain in the data;
summary.csv includes min/max/sample standard deviation and coefficient of variation.

## Largest-size kernel counters

{kernel_table}

Process totals are read_bytes + write_bytes, including writes later cancelled.
The CSV separately preserves cancelled_write_bytes and write-minus-cancelled.
Guest counters are shared-device observation-window deltas, not uniquely
attributable physical NVMe/NAND traffic. These cache-sensitive quantities must
not be substituted for the instrumented state-payload requests above.

## Scope and interpretation

The adapter retains upstream StaticPartitioner, storage-unit gather/scatter and
Aer compute-unit execution. Once fully materialized, subsequent blocks use the
original Engine._run. Details and the exact compatibility patch are in
notes/qdao_integration.md and patches/qdao_current_qiskit.patch.

QDAO here means the upstream engine with a **shared current-Aer state-injection
adapter**, used identically by QThin. It replaces the old scalar-parameter
Initialize bridge with public set_statevector plus norm restoration. It does not
change partitioning or gates. This is not completely unmodified author software.
Original-bridge calibration samples remain in legacy_api_calibration; the main
matrix was restarted in full after independent correctness validation.

Basis-input arithmetic can remain virtual; report it separately from superposed
arithmetic. Although QFT on zero input has a product final state, its lowered CX
stream temporarily entangles and progressively materializes dimensions. It is
therefore not presumed to be a negative result. QAOA and HEA are the earlier
entangling controls. The exact lowered gate order is frozen in the common QPY
files; optimization level zero still reconstructs a dependency-respecting order.
These are requested-size instantiations of existing generators, not the entire
251-circuit corpus and not 24 independent benchmark families.

Application requests are not physical traffic. /proc read_bytes/write_bytes and
shared guest device counters are separately present in summary.csv. Buffered
cache reuse and overwrite coalescing are allowed by the real QDAO file path.
No global cache flush or artificial memory restriction was introduced. Background
guest traffic cannot be uniquely attributed to the benchmark from device counters.
Process write_bytes includes dirtied pages that may subsequently be cancelled by
NPY file truncation; cancelled_write_bytes and write-minus-cancelled are retained
separately. Neither process counter is a physical SSD byte measurement.
Wall time includes metadata planning, initialization, execution and final sync;
imports, shared circuit loading and cleanup are excluded. Reduced compute-unit
execution and smaller state sizes contribute alongside I/O reduction; the whole
speedup must not be attributed exclusively to the storage device.
The evaluated improvement is for the combined remapping/product/fusion mechanism,
not an ablation proving that fusion alone accounts for all end-to-end gains.

Materialization event counters cover fused partitions, including gates in that
partition. Their bytes/time are subsets of totals, not additive overhead terms.

## Reproduction

```bash
conda activate htp-static
python scripts/setup_qdao_integration.py
python scripts/prepare_end_to_end.py
pytest -q
python scripts/validate_qdao_integration.py
python scripts/run_qdao_end_to_end.py --sizes 20 22 24
python scripts/analyze_qdao_end_to_end.py
```

26q is deferred until required Phase B results are safely complete.
'''
Path('QDAO_INTEGRATION_REPORT.md').write_text(report)
frozen=json.loads((root/'previous_results_hashes.json').read_text())
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in frozen.items())
print(status,'completed',len(summary),'workload/size points; previous results unchanged')
