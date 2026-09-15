import _common
import json
import math
import gzip
from pathlib import Path
import numpy as np
import pandas as pd
from htp.loaders import sha256

verification=json.loads(Path('results/verification.json').read_text())
assert verification['status']=='PASS' and verification['false_known_violations']==0
for p,h in verification['validated_code_sha256'].items():
    assert sha256(p)==h, f'Code changed after exact validation: {p}'
summary=pd.read_csv('results/circuit_summary.csv')
discovery=json.loads(Path('results/manifests/discovery.json').read_text())
latest=json.loads(Path('results/manifests/latest_run.json').read_text())
for name in ['circuit_summary','q_trace','qubit_activation','materialization_events','parse_failures','unknown_gates','qdao_oracle','analysis_failures','layer_trace']:
    path=f'results/{name}.csv'
    assert sha256(path)==latest['outputs'][path],f'Output changed after characterization: {path}'
real=summary[~summary.source.isin(['generated','synthetic_control'])].copy()
primary=real[real.n<=64].copy()
focus=primary[primary.n.between(20,40)].copy()
semantic=primary[primary.representation=='semantic']
lowered=primary[primary.representation=='lowered']
assert not summary.duplicated(['workload_id','representation']).any()
assert (summary.groupby('workload_id').representation.nunique()==2).all()
assert (summary.q_peak<=summary.n).all()
assert (summary.q_peak==summary.q_final).all()
assert (summary.peak_storage_reduction_log2==summary.n-summary.q_peak).all()
assert np.allclose(summary.ideal_gate_reduction,summary.ideal_gate_hilbert_volume_reduction)

def stats(frame, groups):
    rows=[]
    for key,g in frame.groupby(groups):
        key=key if isinstance(key,tuple) else (key,)
        values=g.ideal_gate_reduction
        rows.append(dict(zip(groups,key),circuits=len(g),median=float(values.median()),
                         geometric_mean=float(2**g.log2_ideal_gate_reduction.mean()),p90=float(values.quantile(.9)),max=float(values.max()),
                         median_layer=float(g.ideal_layer_reduction.median()),ge4=int((values>=4-1e-9).sum()),
                         ge10=int((values>=10-1e-9).sum()),lt1_5=int((values<1.5).sum()),
                         peak_reduced=int((g.q_peak<g.n).sum()),all_basis=int((g.q_peak==0).sum())))
    return pd.DataFrame(rows)

family=stats(focus,['family','representation'])
family.to_csv('results/family_statistics_20_40.csv',index=False)
stats(primary,['source','family','representation']).to_csv('results/source_family_statistics.csv',index=False)
stats(summary[summary.source=='generated'],['family','representation']).to_csv('results/generated_family_statistics.csv',index=False)
family_all=stats(primary,['family','representation'])
family_all.to_csv('results/family_statistics_le64.csv',index=False)
stats(focus[focus.q_peak>0],['family','representation']).to_csv('results/family_statistics_nonzeroQ_20_40.csv',index=False)
nonzero_stats=stats(focus[focus.q_peak>0],['representation'])
nonzero_stats.to_csv('results/nonzeroQ_statistics_20_40.csv',index=False)
generated_arithmetic=summary[(summary.source=='generated')&(summary.family=='arithmetic')].copy()
generated_arithmetic['input_preparation']=np.where(generated_arithmetic.workload_id.str.endswith('_basis'),'basis','superposed_input')
generated_arithmetic['generator_kind']=generated_arithmetic.workload_id.str.replace(r'_\d+_(basis|superposed_input)$','',regex=True)
generated_arithmetic_stats=stats(generated_arithmetic,['generator_kind','input_preparation','representation'])
generated_arithmetic_stats.to_csv('results/generated_arithmetic_sensitivity.csv',index=False)

paired=primary.pivot(index='workload_id',columns='representation',values='log2_ideal_gate_reduction')
paired['lowered_minus_semantic']=paired.lowered-paired.semantic
paired.to_csv('results/representation_pairs.csv')
f=family[family.representation=='lowered']
robust=f[(f.family!='unknown')&(f.circuits>=3)&(f['median']>=4-1e-9)]
# Predeclared descriptive implementation of the user's informal stage thresholds.
if len(robust)>=2 and f.ge10.sum()>=3:
    classification='STRONG'
elif ((f.ge4.sum()>=3) or ((lowered.ideal_gate_reduction>=4).sum()>=5)):
    classification='MIXED'
else:
    classification='WEAK'
qdao=pd.read_csv('results/qdao_oracle.csv')
qo=qdao[(qdao.oracle_ok==True)&(~qdao.source.isin(['generated','synthetic_control']))&qdao.n.between(20,40)].copy()
oracle_stats=qo.groupby(['representation','m']).ideal_traffic_reduction.agg(['count','median','max']).reset_index()
oracle_stats['geometric_mean']=[float(np.exp(np.log(g.ideal_traffic_reduction).mean())) for _,g in qo.groupby(['representation','m'])]
oracle_stats.to_csv('results/qdao_statistics_20_40.csv',index=False)

def table(frame,cols=None):
    if frame.empty: return '_No eligible circuits._\n'
    frame=frame[cols] if cols else frame
    def fmt(v):
        if isinstance(v,(float,np.floating)): return f'{v:.5g}' if np.isfinite(v) else '—'
        return str(v).replace('|','\\|')
    return '| '+' | '.join(frame.columns)+' |\n| '+' | '.join(['---']*len(frame.columns))+' |\n'+'\n'.join('| '+' | '.join(fmt(v) for v in row)+' |' for row in frame.itertuples(index=False,name=None))+'\n'

shape=[]
for _,r in primary.iterrows():
    shape.append(dict(workload_id=r.workload_id,representation=r.representation,family=r.family,
                      shape='never_full' if r.never_full_materialization else ('immediate_10pct' if r.first_full_materialization_fraction<=.1 else ('late_after_50pct' if r.first_full_materialization_fraction>.5 else 'intermediate'))))
shapes=pd.DataFrame(shape)
shapes.to_csv('results/activation_shapes.csv',index=False)
timings=shapes.groupby(['representation','shape']).size().rename('circuits').reset_index()
event_details=[]
for r in primary.itertuples():
    with gzip.open(Path(latest['raw_directory'])/f'{r.workload_id}_{r.representation}.json.gz','rt') as f:
        data=json.load(f)
    counts={fraction:next((x['q_live']/r.n for x in reversed(data['trace']) if x['normalized_gate_position']<=fraction),0) for fraction in [.1,.5,.9]}
    events=data['events']
    burst=max((e['delta_q']/r.n for e in events),default=0)
    event_details.append(dict(workload_id=r.workload_id,representation=r.representation,family=r.family,
                              q_fraction_at_10pct=counts[.1],q_fraction_at_50pct=counts[.5],q_fraction_at_90pct=counts[.9],
                              max_event_fraction=burst,num_events=len(events),
                              event_pattern='no_activation' if not events else ('large_burst_ge25pct' if burst>=.25 else 'incremental'),
                              max_gap=r.max_materialization_gap,median_gap=r.median_materialization_gap))
event_details=pd.DataFrame(event_details)
event_details.to_csv('results/activation_event_statistics.csv',index=False)
event_patterns=event_details.groupby(['representation','event_pattern']).size().rename('circuits').reset_index()
trace_stats=event_details.groupby(['family','representation'])[['q_fraction_at_10pct','q_fraction_at_50pct','q_fraction_at_90pct']].median().reset_index()
trace_stats.to_csv('results/family_trace_statistics.csv',index=False)
source_counts=real[real.representation=='semantic'].groupby('source').agg(circuits=('workload_id','size'),families=('family','nunique')).reset_index()
big=real[(real.n>64)&(real.representation=='semantic')]
unknown=primary.groupby('representation').agg(unknown_gates=('unknown_gate_count','sum'),gates=('gates','sum'))
unknown['fraction']=unknown.unknown_gates/unknown.gates
benefits=primary.groupby('representation').apply(lambda g:pd.Series(dict(
    true_peak_reduction=int((g.q_peak<g.n).sum()),
    delayed_full_materialization=int((g.q_peak==g.n).sum()),
    all_basis=int((g.q_peak==0).sum()),
    historical_never_Q=int((g.never_quantum_count>0).sum())))).reset_index()
top=focus[focus.representation=='lowered'].sort_values('ideal_gate_reduction',ascending=False).head(12)
negative=family_all[(family_all.representation=='lowered')&(family_all['median']<1.5)]
notable=family_all[(family_all.representation=='lowered')&(family_all['median']>=4-1e-9)]
changes=int((paired.lowered_minus_semantic.abs()>1e-8).sum())
destroyed=int(((paired.semantic>=2-1e-9)&(paired.lowered<math.log2(1.5))).sum())
repo=pd.read_csv('results/manifests/external_repositories.csv')
failures=pd.read_csv('results/analysis_failures.csv')
failure_counts=failures.groupby(['error_type','unsupported_dynamic']).size().rename('count').reset_index() if len(failures) else pd.DataFrame()
global_stats=stats(focus,['representation'])
all_basis_focus=int(((focus.representation=='lowered')&(focus.q_peak==0)).sum())
decision=dict(classification=classification,primary_real_circuits=len(semantic),all_real_circuits=len(real)//2,
              focus_20_40_circuits=len(focus)//2,source_count=real.source.nunique(),family_count=semantic.family.nunique(),
              robust_focus_families=robust.family.tolist(),strong_pairs_destroyed_by_aer_lowering=destroyed,
              paired_metric_changed=changes,all_basis_focus_lowered=all_basis_focus)
Path('results/decision.json').write_text(json.dumps(decision,indent=2))

report=f'''# STATIC CHARACTERIZATION: {classification}

Real workloads analyzed: **{len(real)//2} distinct circuits**, of which **{len(semantic)} with n≤64** and **{len(focus)//2} with 20–40 qubits**.\n
Sources: **{real.source.nunique()}** public circuit repositories (QDAO source means its explicitly referenced QCS corpus).\n
Families: **{semantic.family.nunique()} labels** including `unknown`; **{semantic[semantic.family!='unknown'].family.nunique()} identified families** in primary n≤64 set.\n
Parse success rate: **{discovery['parse_success']}/{discovery['parse_success']+discovery['parse_failures']} = {discovery['parse_success']/(discovery['parse_success']+discovery['parse_failures']):.2%}** of attempted inputs; {discovery['metadata_skips']} metadata-only size skips.\n
Semantic/lowered pairs: **{len(summary)//2} total**, **{len(real)//2} external real**.\n
Tests passed: **{verification['tests_passed']}**.\n
Exact-validation cases: **{verification['exact_validation_cases']}**, **{verification['prefixes']} gate prefixes**, **{verification['known_claims']} single-qubit density-matrix claims**.\n
False-known violations: **{verification['false_known_violations']}**. Maximum density-matrix error **{verification['max_density_error']:.3g}**, tolerance 1e-10.\n
Prior local repository: **{discovery['prior_local_repository']}**.

**Interpretation warning:** large gate-volume ratios are not uniformly caused by late dependent quantum work. Basis-only reversible inputs and the serial order chosen for independent operations contribute strongly. For HEA/QAOA and several other families, lowering can increase the gate metric while layer-weighted reduction stays near 1. Inspect the 20–40 family table before using this stage label as a systems motivation.

## Scope and interpretation

This is CPU-only static characterization of the all-zero initial state followed by each circuit's explicit preparation. No workload-sized statevector, QDAO engine, SSD runtime, layout, extent allocator or m/t planner was run. Exact statevector checks are hard-limited to 8 qubits. Ideal ratios below are **not runtime speedups**; the QDAO oracle is **not measured SSD traffic**.

Primary aggregation excludes generated and synthetic controls and excludes n>64. The {len(big)} analyzed circuits with n>64 are structural evidence only. Counts are sampled coverage, not an estimate of how often these workloads occur in production. Pure basis-input reversible circuits can be simulated classically; their large ratios alone do not establish a need for an out-of-core quantum simulator.

{table(source_counts)}

## Q1. What does q(t) look like?

The curves include early full activation, incomplete activation, and delayed full activation. Classification by first full activation (≤10%, 10–50%, >50%, never full) is:

{table(timings)}

Activation event patterns (a large burst adds ≥25% of n at one gate; otherwise incremental):

{table(event_patterns)}

See Figure 1 and `q_trace.csv`; initial t=0 is stored but excluded from Hilbert-volume sums. Serial gate position depends on valid input gate order; independent gates may be reordered by lowering. The layer metric independently replays ASAP dependency layers to expose sensitivity to this choice. Q is absorbing except that SWAP transports labels without changing q; first-Q CDF is historical per logical wire, not the instantaneous q/n after swaps.

## Q2. Which families have substantial opportunity?

Families with lowered median R_gate≥4 in the n≤64 sampled set:

{table(notable,['family','circuits','median','geometric_mean','ge4','ge10','all_basis'])}

20–40-qubit lowered families with at least 3 circuits and median≥4: **{', '.join(robust.family) or 'none'}**. Large factors must be interpreted alongside all-basis and unused/never-quantumized qubits. No family was removed because its result was negative.

## Q3. Which families are negative controls?

Observed lowered family medians below 1.5 (n≤64):

{table(negative,['family','circuits','median','median_layer','lt1_5'])}

QFT, QAOA, HEA and random circuits were all included, but a proposed negative class is not forced to be negative. QFT on |0…0⟩ may introduce H gates progressively: controlled diagonal phases do not quantumize their known operands. Its observed opportunity is specific to this preparation and gate ordering; a QFT receiving an arbitrary quantum register starts with already-Q inputs and has no new basis-state virtualization opportunity.

## Q4. Where do the ratios come from?

{table(benefits)}

- `q_peak=0`: wholly classical basis evolution. There are **{all_basis_focus}** such lowered external circuits in the 20–40 range.
- `0<q_peak<n`: some proven basis dimensions remain virtual at peak; includes unused ancillas and basis-preserving control operands.
- `q_peak=n`: only allocation timing can improve; the eventual full state is still 16·2^n bytes.
- `materialization_events.csv` records individual/burst delta_q and gaps. Source traces and `activation_shapes.csv` separate timing from never-full behavior. No inferred automatic dematerialization is used.
- Generated arithmetic includes both basis and superposed input preparations, with exact Qiskit generator types recorded. These are sensitivity controls and never increase the external circuit count. Bare reversible modules on zero input are not evidence for arbitrary quantum input states.

Representative largest 20–40-qubit lowered external ratios, with provenance:

{table(top,['source','source_path','family','n','q_peak','ideal_gate_reduction','ideal_layer_reduction'])}

## Q5. Semantic versus execution-lowered

**{changes}/{len(paired)}** primary pairs change their log2 gate-volume metric by >1e-8. **{destroyed}** pairs move from semantic R≥4 to lowered R<1.5. Both are shown in Figure 4, including y=x.

The backend is Aer statevector/CPU, queried live and recorded in `results/manifests/backend.json`, with optimization_level=0. Current Aer retains CCX/MCX and many controlled gates. Thus this lowering is not equivalent to a hardware H/T/CX-only compiler. A separate unit test explicitly demonstrates loss of reversible proof after CCX decomposes into H/T/CX. The primary comparison answers the current QDAO/Aer entry-point question; it cannot establish robustness under every lower-level execution representation.

For static compilation only, Aer operation objects are copied into an unbounded Target, since its ordinary target advertises a RAM-derived width limit of 29 on this machine. The exact backend and memory limits are unchanged. Actual WSL-visible memory is approximately 15 GiB, less than the assumed host 32 GiB; no experiment needs a large statevector.

Semantic wrappers without trusted transfer rules are transparently expanded until supported primitives are reached. Exported QASM often already contains decompositions; original semantic blocks cannot be reconstructed by gate names alone. `original_gate_count`, `semantic_gate_count`, and `lowered_gate_count` make the counting domains explicit. When lowering changes the metric, changes can reflect scheduling and gate-count weighting as well as quantumization; they are not themselves proof of lost physical memory savings.

Unknown-gate coverage:

{table(unknown.reset_index())}

Details are in `unknown_gates.csv`. Unknown gates mark all operands Q; they can hide opportunity but cannot be credited with proving a basis state.

## Q6. Realistic 20–40-qubit statistics

External real circuits only; unweighted per circuit; no synthetic/generated circuits. Geometric mean uses mean log2 reduction. P90 is pandas linear quantile; these are descriptive statistics of the selected set, without population confidence claims.

{table(global_stats,['representation','circuits','median','geometric_mean','p90','max','median_layer'])}

{table(family,['family','representation','circuits','median','geometric_mean','p90','max','median_layer','all_basis'])}

`family_statistics_nonzeroQ_20_40.csv` additionally removes entirely basis-only circuits. This sensitivity table should guide any quantum simulation systems motivation.

Overall 20–40-qubit sensitivity after removing q_peak=0:

{table(nonzero_stats,['representation','circuits','median','geometric_mean','p90','max','median_layer'])}

Generated arithmetic preparation sensitivity (supplementary, excluded from external aggregates):

{table(generated_arithmetic_stats[generated_arithmetic_stats.representation=='lowered'],['generator_kind','input_preparation','circuits','median','geometric_mean','max','median_layer','all_basis'])}

## Q7. QDAO-aware static traffic oracle

**Static oracle — excludes materialization overhead. This ignores materialization overhead and is NOT measured SSD traffic.**

Boundaries reproduce current QDAO `StaticPartitioner` union/flush logic, checked against the extracted source class on 100 randomized circuits. Fixed t=2 (source default), m∈{{16,18,20,22,24}}, only t<m<n. There is no tuning or planner. Inputs are canonicalized to a single logical register to avoid QDAO's private register-local index aliasing. Oversized gates that the original partitioner cannot fit are explicitly rejected in `qdao_oracle.csv`.

For each subcircuit, eager bytes=32·2^n; thin bytes=16·(2^q_start+2^q_end). The second convention in the CSV charges both passes at q_end. Initial state-file creation, format overhead, repartitioning and materialization costs are excluded. These ratios are an ideal endpoint-volume model, not an implemented executor.

20–40-qubit external circuit statistics:

{table(oracle_stats)}

## Q8. Peak capacity or delayed allocation?

{table(benefits,['representation','true_peak_reduction','delayed_full_materialization','all_basis'])}

`peak_storage_reduction=2^(n-q_peak)` only represents a true peak reduction when q_peak<n. The other circuits eventually require the same 16·2^n-byte dense state. Historical never-Q count can differ from n-q_final because SWAP moves states between logical wires.

## Q9. Enter storage layout design?

**Stage decision: {classification}.** The operational decision uses the **lowered, external, 20–40-qubit** set: STRONG requires ≥2 families each with ≥3 circuits and median≥4, plus ≥3 circuits with ratio≥10; MIXED requires several substantial examples; otherwise WEAK. This is a transparent phase gate, not a final paper criterion.

{'The evidence warrants a scoped next-stage design study for the supported families and explicit input preparations. It does not establish broad simulator speedup or automatic benefit for circuits that already begin on quantum data. A no-full-rewrite materialization layout would be the next question, subject to actual materialization cost and backend semantics.' if classification!='WEAK' else 'The present evidence does not justify a broad storage-layout implementation. The retained traces and family-specific sensitivity results delimit any narrower motivation; no next-stage system has been implemented.'}

For scoping that decision: QFT on the benchmark's known initial state retains substantial **layer-weighted** opportunity; external basis-only adders/reversible circuits are weak evidence for needing a quantum storage system despite their enormous ratios. Generated VBE with an explicitly superposed data register is a useful nontrivial ancilla sensitivity control, while generated CDKM/modular addition is much weaker. QAOA's large lowered gate ratio is substantially schedule-dependent. The next study should preserve these distinctions rather than use the global geometric mean as its motivation. **No next-stage storage design is included in this project.**

## Coverage limitations and exclusions

- {discovery['scanned']} discovered input records; {discovery['metadata_skips']} files skipped before parsing for size. Every attempted parse failure is in `parse_failures.csv`, with source hash and exact error; no source files were edited.
- Deterministic stratification is by source/family/width/gate-count, with {latest['structural_duplicates']} further normalized-structure duplicates excluded. Existing `_transpiled` companions are not counted as independent circuits when their source exists. Repeated sizes/seeds are capped by stratum; the set is not a population sample.
- Unsupported dynamics and analysis limits are separate from parse failures. Terminal readout is removed; mid-circuit measurements, reset and classical control are not modeled.
- Numerical angle tolerance=1e-10 and matrix structure tolerance=1e-14 are documented in `notes/gate_semantics.md`. A cumulative operator-norm error budget of 5e-11 prevents repeated near-special gates from silently accumulating false-known claims; exhausted proofs use Q. Tests include 6,000 near-diagonal gates, repeated near-zero RX, and unreliable huge-angle reduction. Floating arithmetic itself remains numerical, rather than symbolic certification.
- Development validation exposed and fixed a multi-target controlled-gate false-known bug. All characterization was rerun after the correction; only the latest verified run is used here. See `notes/validation_audit.md` for the failure and regression test, rather than treating earlier debug artifacts as evidence.
- Reversible files containing conflicting repeated gate definitions remain parse failures. Missing unambiguous legacy `c3sx` and `mcx_gray` declarations are mapped to current Qiskit types; declared custom gate bodies are preserved.
- Generated arithmetic QPY stores its transparent semantic expansion because some current Qiskit OrGate wrappers fail to reload. Every saved generated input is immediately round-tripped. Optional generated Grover stops at 32 qubits because QPY cannot serialize closed MCX control masks above uint32; required QFT/QAOA/HEA/random controls still cover all eight sizes through 40. This package limitation does not limit static analysis of external larger circuits.
- No prior local repository was guessed or scanned without the configured path. QDAO and all external repositories remain clean and unmodified.

{table(failure_counts)}

## Reproduction and provenance

See `README.md` and `bash scripts/run_all.sh`. Raw per-circuit results and generated QPY inputs are stored under `{latest['raw_directory']}`; timestamps distinguish reruns. Exact tests and source/config/output hashes are recorded in the manifests. All figures are regenerated from CSV/raw records, not hand-edited.

{table(repo,['name','repository','git_commit','git_branch','dirty'])}

QDAO `v0.1.0` and `stable/0.1` exist; neither was checked out or run. See `notes/qdao_execution_model.md` for source locations. Primary references: [QDAO source](https://github.com/Zhaoyilunnn/qdao), [QASMBench](https://github.com/pnnl/QASMBench), [Veri-Q Benchmark](https://github.com/Veri-Q/Benchmark), [Qiskit QASM2 loader](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qasm2).
'''
Path('FINAL_REPORT.md').write_text(report)
print(json.dumps(decision,indent=2))
