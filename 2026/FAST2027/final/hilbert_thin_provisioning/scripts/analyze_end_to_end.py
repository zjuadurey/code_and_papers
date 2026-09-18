"""Measured three-way summaries, audit and LaTeX tables; never writes Phase A."""
import _e2e_common
import datetime, hashlib, json, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from htp.e2e.tables import phase_a_tables, latex_table

root=Path('results/gbsa_comparison');a=Path('results/qdao_end_to_end')
checks={}
for name in ['phase_a_hashes.json','previous_results_hashes.json']:
    hashes=json.loads((a/name).read_text())
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items()),name
    checks[name]=len(hashes)
av=json.loads((a/'correctness.json').read_text());bv=json.loads((root/'correctness.json').read_text())
assert av['failures']==bv['failures']==0 and bv['validated']
source_hash=hashlib.sha256(Path('src/htp/e2e/gbsa.py').read_bytes()).hexdigest()
assert bv['source_sha256']==source_hash
raw=pd.read_csv(root/'raw_runs.csv');araw=pd.read_csv(a/'raw_runs.csv')
manifest=pd.read_csv('results/end_to_end_workloads.csv');required=manifest[manifest.n.isin([20,22,24])]
assert len(raw)==72 and len(araw)==144
assert set(raw.workload_id)==set(required.workload_id)
assert raw.groupby('workload_id').size().eq(3).all()
assert not raw.duplicated(['workload_id','repetition']).any()
assert set(raw.gbsa_sha256)=={source_hash}
assert set(raw.runtime_sha256)==set(araw.runtime_sha256), 'Common backend changed'
for r in manifest.itertuples():
    assert hashlib.sha256(Path(r.input_file).read_bytes()).hexdigest()==r.hash
    assert raw[raw.workload_id==r.workload_id].input_hash.eq(r.hash).all()
raw['algorithmic_total_bytes']=raw.algorithmic_read_bytes+raw.algorithmic_write_bytes
raw['proc_total_bytes']=raw.proc_read_bytes+raw.proc_write_bytes
raw['device_total_bytes']=raw.device_read_bytes+raw.device_write_bytes
raw['proc_write_minus_cancelled_bytes']=raw.proc_write_bytes-raw.proc_cancelled_write_bytes
assert np.all(raw.algorithmic_read_bytes==16*2.**raw.n*raw.state_traversals)
assert np.all(raw.algorithmic_write_bytes==16*2.**raw.n*(raw.state_traversals+1))
assert np.all(raw.state_traversals==raw.gbsa_gate_blocks+raw.gbsa_swap_passes)
assert np.all(raw.compute_unit_count==raw.state_traversals*2.**(raw.n-16))
columns=['wall_time_s','user_cpu_s','system_cpu_s','algorithmic_read_bytes',
    'algorithmic_write_bytes','algorithmic_total_bytes','proc_total_bytes','proc_read_bytes',
    'proc_write_bytes','proc_cancelled_write_bytes','proc_write_minus_cancelled_bytes',
    'device_total_bytes','device_read_bytes','device_write_bytes','peak_rss_bytes',
    'compute_unit_count','state_traversals','gbsa_gate_blocks','gbsa_swap_passes',
    'gbsa_swap_count','gbsa_search_s','gbsa_swap_s','sync_time_s']
rows=[]
for wid,g in raw.groupby('workload_id'):
    row=dict(workload_id=wid,family=g.family.iloc[0],n=int(g.n.iloc[0]),system='GBSA reproduction',repetitions=len(g))
    row.update({c:g[c].median() for c in columns})
    row.update(time_min_s=g.wall_time_s.min(),time_max_s=g.wall_time_s.max(),
        time_std_s=g.wall_time_s.std(ddof=1),time_cv=g.wall_time_s.std(ddof=1)/g.wall_time_s.mean())
    rows.append(row)
b=pd.DataFrame(rows).sort_values(['n','family']);b.to_csv(root/'summary.csv',index=False,na_rep='NA')
summary=pd.read_csv(a/'summary.csv')
prefixed=b.drop(columns=['system','family','n']).rename(columns={c:'gbsa_'+c for c in b.columns if c!='workload_id'})
combined=summary.merge(prefixed,on='workload_id',validate='one_to_one').sort_values(['n','family'])
combined['qthin_vs_gbsa']=combined.gbsa_wall_time_s/combined.qthin_wall_time_s
combined['gbsa_qthin_traffic_reduction']=combined.gbsa_algorithmic_total_bytes/combined.qthin_algorithmic_total_bytes
combined['gbsa_vs_qdao']=combined.qdao_wall_time_s/combined.gbsa_wall_time_s
combined['gbsa_status']='MEASURED_REPRODUCTION_COMMON_SUBSTRATE'
combined.to_csv('results/end_to_end_summary.csv',index=False,na_rep='NA')

fairness=[]
for r in required.itertuples():
    for method in ['QDAO','QThin','GBSA reproduction']:
        fairness.append(dict(workload_id=r.workload_id,system=method,input_file=r.input_file,
            input_hash=r.hash,representation=r.representation,precision='complex128',
            m=16,t=12,threads=1,io_mode='buffered_npy',sync='final surviving state fdatasync',
            batch='A' if method!='GBSA reproduction' else 'B',
            selector='published GBSA reproduction' if method=='GBSA reproduction' else 'upstream QDAO static',
            layout_swaps=method=='GBSA reproduction',status='MEASURED'))
pd.DataFrame(fairness).to_csv(root/'fairness_manifest.csv',index=False)
skips=[dict(workload_id=r.workload_id,n=26,system=method,repetition='ALL',reason='NOT_IN_REQUIRED_CORE_SEE_SCALING_SUBSET')
       for r in manifest[manifest.n==26].itertuples() for method in ['QDAO','QThin','GBSA reproduction']]
pd.DataFrame(skips).to_csv(root/'skipped_cases.csv',index=False)
env=json.loads((a/'environment.json').read_text())
env.update(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    phase_a_commit='79ab9a107b83346452bdbb96341a22076a533a44',
    benchmark_dir=str((root/'workdir').resolve()),gbsa_status='independent paper-policy reproduction',
    gbsa_sha256=source_hash,gbsa_artifact_commit=None,gbsa_author_license=None,
    gbsa_language='Python search and layout orchestration; shared Aer native kernels',chunk_bits=16)
(root/'environment.json').write_text(json.dumps(env,indent=2)+'\n')

runtime_columns=[('family','Workload'),('n','$n$'),('qdao_wall_time_s','QDAO (s)'),
    ('gbsa_wall_time_s','GBSA repr. (s)'),('qthin_wall_time_s','QThin (s)'),
    ('speedup','QDAO/QThin'),('qthin_vs_gbsa','GBSA/QThin')]
tex=phase_a_tables(summary)+'\n'+latex_table(combined,runtime_columns,
    'Measured runtime medians of three runs. GBSA is an independent policy reproduction on the common backend, not author software.',
    'tab:three-way-runtime')
for method in ['qdao','qthin','gbsa']:
    combined[method+'_gib']=combined[method+'_algorithmic_total_bytes']/2**30
tex+='\n'+latex_table(combined,[('family','Workload'),('n','$n$'),('qdao_gib','QDAO (GiB)'),
    ('gbsa_gib','GBSA repr. (GiB)'),('qthin_gib','QThin (GiB)'),
    ('algorithmic_traffic_reduction','QDAO/QThin'),('gbsa_qthin_traffic_reduction','GBSA/QThin')],
    'Instrumented state-payload read/write requests, including GBSA layout swaps; not physical SSD traffic.',
    'tab:three-way-traffic')
Path('results/end_to_end_tables.tex').write_text(tex)

def md(frame,columns):
    text='| '+' | '.join(title for _,title in columns)+' |\n|'+ '|'.join('---' for _ in columns)+'|\n'
    for r in frame.to_dict('records'):
        text+='| '+' | '.join(str(r[k]) if isinstance(r[k],str) else str(int(r[k])) if k=='n'
            else f'{r[k]:.3g}' if abs(r[k])<.001 else f'{r[k]:.3f}' for k,_ in columns)+' |\n'
    return text

table=md(combined,runtime_columns)
traffic=md(combined,[('family','Workload'),('n','n'),('qdao_gib','QDAO GiB'),('gbsa_gib','GBSA repr. GiB'),
    ('qthin_gib','QThin GiB'),('algorithmic_traffic_reduction','QDAO/QThin'),
    ('gbsa_qthin_traffic_reduction','GBSA/QThin')])
full=combined[combined.qthin_final_q_physical==combined.n]
family=combined.groupby('family')[['speedup','qthin_vs_gbsa','algorithmic_traffic_reduction','gbsa_qthin_traffic_reduction']].median().reset_index()
family_table=md(family,[('family','Variant'),('speedup','QDAO/QThin time'),('qthin_vs_gbsa','GBSA/QThin time'),
    ('algorithmic_traffic_reduction','QDAO/QThin bytes'),('gbsa_qthin_traffic_reduction','GBSA/QThin bytes')])
size=combined.groupby('n')[['speedup','qthin_vs_gbsa']].median().reset_index()
size_table=md(size,[('n','n'),('speedup','Median QDAO/QThin time'),('qthin_vs_gbsa','Median GBSA/QThin time')])
diagnostic=md(b,[('family','Variant'),('n','n'),('gbsa_gate_blocks','Gate blocks'),
    ('gbsa_swap_passes','Swap passes'),('gbsa_search_s','Search s'),('gbsa_swap_s','Swap s'),('time_cv','Time CV')])
wins=int((combined.qthin_vs_gbsa>1).sum());fullwins=int((full.qthin_vs_gbsa>1).sum())
result='PROMISING' if wins>=12 else 'MIXED'
gbsa_winners=', '.join(f'{r.family} {r.n}q' for r in combined[combined.qthin_vs_gbsa<1].itertuples()) or 'none'
strongest=', '.join(f'{r.family} ({r.qthin_vs_gbsa:.3f}x)' for r in family.sort_values('qthin_vs_gbsa',ascending=False).head(3).itertuples())
swap_fraction=(raw.gbsa_swap_s/raw.wall_time_s).median()
search_fraction=(raw.gbsa_search_s/raw.wall_time_s).median()
corr=spearmanr(full.algorithmic_traffic_reduction,full.speedup).statistic
negative=combined[combined.family.isin(['qaoa','hea'])]
common=f'''## Measurement contract and limitations

Small-scale **file-backed end-to-end** execution on WSL2/ext4 VHDX. These states
fit system RAM; no large-scale capacity/OOC claim. All methods: complex128,
fixed m=16/t=12, one thread, identical lowered u/cx QPY hashes, Aer 0.17.2/Qiskit
2.5.2, fusion disabled, buffered NPY, final surviving-state fdatasync. Phase A
uses QDAO upstream `fb360e6670b9818a3d4e106fb21cf605838be0a4` with the documented
shared modern-Aer state-injection adapter. It is not an untouched historical
author binary. Phase B shares the exact runtime source hash.

GBSA is an independent Algorithms 1/2 **policy reproduction on that substrate**,
with unrestricted C=16 chunk selection and charged physical layout swaps.
It is not the authors' optimized native SSDGBSA implementation. Algorithm 2 has
printed ambiguities resolved using Section 3.3 and tested against Figure 4.
See `notes/gbsa_reproduction.md` for exact decisions, omitted kernels and license.
No official artifact commit is available (NA).

Wall/CPU time, counter deltas, request counts and sync time are measured. Ratios,
medians, std/CV and correlations are derived. Request bytes count actual state
payload loads/stores, including initialization and layout swaps. They are not
native SSD bytes. Process read/write/cancelled-write counters and shared
guest-visible device counters remain separate in raw/summary CSV. Buffered reads
can hit cache and truncated writes can be cancelled. Device counters are not
uniquely attributable and do not measure native NVMe/NAND traffic.

Every required point has three repetitions; no slow sample was removed. Phase A
interleaved QDAO/QThin order. Phase B ran later, serially with shuffled workload
order; cross-phase background drift remains a limitation. Search, initialization,
swaps, execution and final sync are timed; QPY loading/import/cleanup are outside
all timing windows. No overlapping performance experiments were allowed.
Counts of wins refer only to sample medians, not statistical significance.
Near-unity ratios, especially differences of a few percent, should be read
alongside the individual samples and CV rather than as resolved superiority.
'''
answers=f'''## Answers and applicability

1. **QDAO runtime:** QThin median speedup across 24 points is {combined.speedup.median():.3f}x;
   among 21 eventually fully materialized points it is {full.speedup.median():.3f}x.
   Basis-only CDKM is separated because it never allocates an amplitude dimension.
2. **Traffic correlation:** strict-subset median requested-byte reduction is
   {full.algorithmic_traffic_reduction.median():.3f}x; descriptive Spearman correlation
   with runtime speedup is {corr:.3f}. This does not isolate SSD causality: fewer
   Aer compute units and staging operations also save CPU time.
3. **Families:** use the family table below. These 8 workload variants from 7
   families are small controlled instantiations of existing generators, not a
   rerun of the earlier 251-circuit corpus. Do not generalize a family-wide win
   from one size/variant or pool basis-only and eventually entangled inputs.
4. **Negative controls:** all QAOA/HEA Phase A median speedups lie between
   {negative.speedup.min():.3f}x and {negative.speedup.max():.3f}x, with no median
   slowdown. QFT also benefits here; the actual lowered ordering does not make it
   an immediate-full-materialization control. Noise/CV is retained in CSV.
5. **Published policy comparison:** QThin beats this GBSA reproduction at
   {wins}/24 points ({fullwins}/21 eventually fully materialized). Overall median
   GBSA/QThin runtime ratio is {combined.qthin_vs_gbsa.median():.3f}x; strict-subset
   median is {full.qthin_vs_gbsa.median():.3f}x. Ratios below one favor GBSA.
   This supports only the documented reproduction comparison, not superiority
   to the authors' full system.
6. **GBSA wins and costs:** GBSA wins at: {gbsa_winners}.
   QThin's largest median advantages over this reproduction are: {strongest}.
   Its gate-block reuse and QThin's delayed physicalization are different
   mechanisms. The diagnostic table separates search and layout-swap costs;
   median per-run layout-swap time fraction is {swap_fraction:.1%}, while search
   consumes {search_fraction:.3%}. These fractions are measured execution-time
   decompositions, not ablation results. Common-substrate swap overhead is not
   an inherent bound on native GBSA.
7. **Size consistency:** all required 20/22/24q points completed; see size table.
8. **26q:** not included in this required-core dataset. A separately authorized,
   preselected scaling subset is tracked in `results/end_to_end_scaling/`.
   Untimed full-suite planning predicted about 6.99 hours for QDAO alone at three
   repetitions; that extrapolation is not the cost of the smaller subset and
   is not a measured 26q result. Any scaling claims must cite the separate data.
9. **Measured vs derived:** see the measurement contract; paper-reported results
   and earlier trace-model reductions are not inserted into these tables.
10. **FAST claims:** a validated QThin integration reduces measured file-backed
    runtime and instrumented state traffic against the documented QDAO baseline;
    a separate, transparent GBSA policy reproduction supplies a qualified
    three-way comparison. Do not claim author-artifact reproduction, native SSD
    byte reduction, capacity-scale OOC speedup, or a universal family advantage.
'''
header=f'''# END-TO-END RESULT: {result}

QDAO integration status: completed; Phase A result **STRONG**; commit `79ab9a1`.
GBSA reproduction status: completed, independent paper-policy implementation.
Workloads completed: 24 points (8 variants × 20/22/24q), 216 timed runs total.
20q completed: yes. 22q completed: yes. 24q completed: yes.
26q: outside this required-core dataset; see the separate representative scaling extension.
Correctness: {av['cases']} Phase A cases + {bv['cases']} GBSA cases; **0 failures**.

## Primary runtime table

Times in seconds, medians of three repetitions. Ratios greater than one favor
QThin. GBSA columns are **GBSA reproduction**, not official author results.

{table}
## Instrumented requested state traffic

{traffic}
'''
Path('END_TO_END_EVALUATION_REPORT.md').write_text(header+common+answers+
    '\n## Median comparisons by variant\n\n'+family_table+'\n## By size\n\n'+size_table+
    '\n## GBSA execution diagnostics\n\n'+diagnostic+
    '\n## Artifacts\n\n`results/end_to_end_summary.csv`, `results/end_to_end_tables.tex`, '
    '`results/gbsa_comparison/{raw_runs,summary,fairness_manifest}.csv`. '
    'Four standalone LaTeX table environments; no paper source was edited.\n')
Path('GBSA_COMPARISON_REPORT.md').write_text('# GBSA REPRODUCTION: COMPLETED\n\n'+
    f'{bv["cases"]} exact cases, zero failures; 72 serial timed runs, all required sizes.\n\n'+
    table+'\n## Requested state traffic\n\n'+traffic+common+answers+
    '\n## Execution diagnostics\n\n'+diagnostic)
(root/'analysis_audit.json').write_text(json.dumps(dict(timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    frozen_hash_counts=checks,phase_a_runs=144,gbsa_runs=72,input_hashes_verified=True,
    gbsa_code_sha256=source_hash,common_runtime_hash_unchanged=True,
    requested_byte_identities_verified=True,correctness_failures=0,result=result),indent=2)+'\n')
print('END-TO-END RESULT:',result)
print(f'GBSA points={len(b)}; QThin wins={wins}/24; median GBSA/QThin={combined.qthin_vs_gbsa.median():.3f}')
