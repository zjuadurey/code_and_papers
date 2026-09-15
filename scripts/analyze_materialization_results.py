import _materialization_common as common
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
from htp.materialization_policy import POLICIES
from htp.loaders import sha256

out=common.OUT
verification=json.loads((out/'verification.json').read_text())
assert verification['status']=='PASS' and verification['false_virtual']==0 and verification['fused_correctness_cases']>=1000
common.check_frozen()
s=pd.read_csv(out/'workload_policy_results.csv')
p=s[s.primary].copy()
primary_ids=set(p.workload_id)
wide=p.pivot(index='workload_id',columns='policy',values='predicted_total_bytes')
assert wide.notna().all().all()
comparisons=pd.DataFrame(index=wide.index)
for policy in POLICIES:
    comparisons['eager_to_'+policy.lower()]=wide.EAGER_FULL/wide[policy]
comparisons['basis_thin_to_product_fused']=wide.BASIS_THIN/wide.PRODUCT_FUSED
extras=p[p.policy=='PRODUCT_FUSED'].set_index('workload_id')
comparisons=comparisons.join(extras[['family','n','q_peak','materialization_events','median_physicalization_delay','median_observed_virtual_window']])
writes=p.pivot(index='workload_id',columns='policy',values='materialization_write_bytes').astype(float)
comparisons['materialization_write_reduction']=np.where(writes.PRODUCT_FUSED>0,writes.BASIS_REWRITE/writes.PRODUCT_FUSED,
                                                       np.where(writes.BASIS_REWRITE>0,np.inf,1.))
comparisons['basis_materialization_write_bytes']=writes.BASIS_REWRITE
comparisons['product_materialization_write_bytes']=writes.PRODUCT_FUSED
comparisons.to_csv(out/'paired_comparisons.csv')
policy=[]
for name,g in p.groupby('policy'):
    policy.append(dict(policy=name,circuits=len(g),median_reduction=g.reduction_vs_eager.median(),
        geometric_mean_reduction=float(np.exp(np.log(g.reduction_vs_eager.astype(float)).mean())),
        p90_reduction=g.reduction_vs_eager.quantile(.9),max_reduction=g.reduction_vs_eager.max(),
        median_boundary_fused_reduction=g.reduction_boundary_fused.median(),
        median_resident_optimistic_reduction=g.reduction_resident_lower_bound.median(),
        median_peak_bytes=g.peak_bytes.astype(float).median(),median_q_peak=g.q_peak.median(),
        median_materialization_read_bytes=g.materialization_read_bytes.astype(float).median(),
        median_materialization_write_bytes=g.materialization_write_bytes.astype(float).median(),
        total_materialization_events=g.materialization_events.sum(),
        median_materialization_events=g.materialization_events.median()))
policy=pd.DataFrame(policy).set_index('policy').loc[list(POLICIES)].reset_index()
policy.to_csv(out/'policy_summary.csv',index=False)
diagnostics=[]
for name,g in p.groupby('policy'):
    diagnostics.append(dict(policy=name,
        median_traversal_only_reduction=float(np.median(wide.EAGER_FULL.reindex(g.workload_id).to_numpy()/g.predicted_qdao_bytes.astype(float).to_numpy())),
        median_materialization_fraction=float((g.predicted_materialization_bytes.astype(float)/g.predicted_total_bytes.astype(float)).median()),
        median_total_over_traversal_bytes=float((g.predicted_total_bytes.astype(float)/g.predicted_qdao_bytes.astype(float)).median()),
        capacity_reduced_circuits=int((g.q_peak<g.n).sum()),eventually_full_circuits=int((g.q_peak==g.n).sum()),
        explicit_resize_copies_avoided=int(g.full_state_rewrites_avoided.sum())))
diagnostics=pd.DataFrame(diagnostics)
diagnostics.to_csv(out/'accounting_diagnostics.csv',index=False)
family=p[p.policy=='PRODUCT_FUSED'].groupby('family').agg(circuits=('workload_id','size'),median_reduction=('reduction_vs_eager','median'),
    p90_reduction=('reduction_vs_eager',lambda x:x.quantile(.9)),median_q_peak=('q_peak','median'),
    median_window=('median_observed_virtual_window','median'),zero_physical_dimensions=('q_peak',lambda x:int((x==0).sum()))).reset_index()
family.to_csv(out/'family_summary.csv',index=False)
life=pd.read_csv(out/'qubit_lifetimes.csv')
l=life[(life.representation=='lowered')&life.workload_id.isin(primary_ids)&(~life.never_quantumized)]
completed=l[~l.never_physicalized]
events=pd.read_csv(out/'physicalization_events.csv')
ep=events[(events.representation=='lowered')&events.workload_id.isin(primary_ids)]
trigger=ep[ep.policy=='PRODUCT_FUSED'].groupby(['gate_name','trigger_reason']).agg(events=('gate_index','size'),
    dimensions=('materialization_batch_size','sum'),median_batch=('materialization_batch_size','median')).reset_index().sort_values('events',ascending=False)
trigger.to_csv(out/'trigger_summary.csv',index=False)
batch=ep.groupby(['policy','materialization_batch_size']).size().rename('events').reset_index()
batch.to_csv(out/'batch_distribution.csv',index=False)
strong=family[(family.family!='unknown')&(family.circuits>=3)&(family.median_reduction>=5)]
med=policy.set_index('policy').median_reduction
delay=float(l.observed_window_lower_bound_fraction.median())
writered=float(comparisons.materialization_write_reduction.median())
if med.PRODUCT_FUSED>=3 and len(strong)>=2 and (delay>0 or writered>1):
    decision='PROMISING'
elif ((med.PRODUCT_FUSED<1.5) and (med.BASIS_THIN<1.5) and delay<.001 and len(strong)==0):
    decision='WEAK'
else:
    decision='NEEDS_REFINEMENT'
nontrivial=comparisons[comparisons.materialization_events>0]
nonzero=nontrivial[['eager_to_product_fused','basis_thin_to_product_fused']].agg(['count','median','min','max']).reset_index(names='statistic')
nonzero.to_csv(out/'nontrivial_event_sensitivity.csv',index=False)
nopeak=comparisons[comparisons.q_peak==comparisons.n]
nopeak[['eager_to_product_fused','basis_thin_to_product_fused']].agg(['count','median','min','max']).to_csv(out/'eventual_full_capacity_sensitivity.csv')
# Trace-backed examples use actual frozen gate operands, not inferred family stories.
chosen=[]
for family_name in ['state_preparation','grover_oracle','qaoa','random']:
    g=completed[(completed.family==family_name)&(completed.virtual_product_window_gates>0)]
    if len(g): chosen.append(g.sort_values(['virtual_product_window_fraction','workload_id','qubit']).iloc[len(g)//2])
chosen_ids={r.workload_id for r in chosen}
small_trace=pd.concat([c[(c.representation=='lowered')&c.workload_id.isin(chosen_ids)]
                       for c in pd.read_csv(out/'gate_event_trace.csv',chunksize=100000,dtype={'physical_backing_bytes':str})],ignore_index=True)
examples=[]
for r in chosen:
    g=small_trace[(small_trace.workload_id==r.workload_id)&small_trace.gate_index.between(r.first_quantum_gate,r.first_physical_gate)]
    on_wire=g[g.qubits.map(lambda value:int(r.qubit) in json.loads(value))]
    sequence=[f'{int(x.gate_index)}:{x.gate_name}' for x in on_wire.itertuples()]
    abbreviated=sequence if len(sequence)<=10 else sequence[:5]+['…']+sequence[-4:]
    examples.append(dict(workload_id=r.workload_id,family=r.family,qubit=r.qubit,
                         quantum_gate=int(r.first_quantum_gate),physical_gate=int(r.first_physical_gate),
                         delay_gates=int(r.virtual_product_window_gates),delay_fraction=r.virtual_product_window_fraction,
                         gates_on_wire=' → '.join(abbreviated)))
example_table=pd.DataFrame(examples)
example_table.to_csv(out/'lifetime_examples.csv',index=False)
ms=s[(s.primary_eligible)&(s.oracle_valid)].groupby(['m','policy']).reduction_vs_eager.agg(['count','median']).reset_index()
ms.to_csv(out/'m_sensitivity.csv',index=False)
secondary=s[(~s.source.isin(['generated','synthetic_control']))&(s.m==16)&s.oracle_valid]
secondary_stats=secondary.groupby(['representation','policy']).reduction_vs_eager.agg(['count','median']).reset_index()
secondary_stats.to_csv(out/'secondary_summary.csv',index=False)
paired_rep=secondary[secondary.policy=='PRODUCT_FUSED'].pivot(index='workload_id',columns='representation',values='reduction_vs_eager').dropna()
paired_rep['lowered_over_semantic']=paired_rep.lowered/paired_rep.semantic
paired_rep.to_csv(out/'semantic_lowered_pairs.csv')
control=s[(s.source.isin(['generated','synthetic_control']))&(s.m==16)&s.oracle_valid]
control.groupby(['source','family','representation','policy']).reduction_vs_eager.agg(['count','median']).to_csv(out/'control_summary.csv')
sensitivity=pd.read_csv(out/'sensitivity.csv')
sens=sensitivity.groupby(['policy','amplitude_bytes','chunk_bytes']).reduction_vs_eager.median().reset_index()
sens.to_csv(out/'sensitivity_summary.csv',index=False)
# No result depends on changing the data precision without chunk rounding.
unrounded=sensitivity[sensitivity.chunk_bytes==1].pivot(index=['workload_id','policy'],columns='amplitude_bytes',values='predicted_total_bytes')
assert np.allclose(unrounded[16].astype(float),2*unrounded[8].astype(float),rtol=1e-14)
assert (p.predicted_total_bytes.astype(float)>=0).all()
assert np.allclose(wide.BASIS_REWRITE.astype(float),wide.BASIS_THIN.astype(float))
micro=pd.read_csv(out/'microbenchmark.csv') if (out/'microbenchmark.csv').exists() else pd.DataFrame()
micro_summary=micro.groupby(['q','policy']).agg(trials=('q','size'),median_wall_seconds=('wall_seconds','median'),
    median_peak_rss_bytes=('peak_rss_bytes','median'),output_allocation_bytes=('bytes_allocated_for_outputs','median'),
    implementation_copy_volume_estimate=('implementation_copy_volume_estimate','median')).reset_index() if len(micro) else pd.DataFrame()
micro_summary.to_csv(out/'microbenchmark_summary.csv',index=False)

def table(frame,columns=None):
    if frame.empty:return '_No eligible entries._\n'
    frame=frame[columns] if columns else frame
    def fmt(x):
        if isinstance(x,(float,np.floating)):
            if math.isinf(x):return '∞'
            if math.isnan(x):return '—'
            return f'{x:.6g}'
        return str(x).replace('|','\\|')
    return '| '+' | '.join(map(str,frame.columns))+' |\n| '+' | '.join(['---']*len(frame.columns))+' |\n'+'\n'.join('| '+' | '.join(fmt(x) for x in row)+' |' for row in frame.itertuples(index=False,name=None))+'\n'

details=dict(mechanism_result=decision,primary_candidates=90,primary_common_valid=len(wide),excluded_m16=90-len(wide),
    real_circuits=251,median_eager_to_basis_rewrite=float(med.BASIS_REWRITE),median_eager_to_basis_thin=float(med.BASIS_THIN),
    median_eager_to_product_fused=float(med.PRODUCT_FUSED),median_basis_thin_to_product_fused=float(comparisons.basis_thin_to_product_fused.median()),
    median_observed_virtual_window_fraction=delay,median_completed_physicalization_delay_fraction=float(completed.virtual_product_window_fraction.median()),
    never_physicalized_quantum_qubits=int(l.never_physicalized.sum()),quantum_qubits=len(l),median_materialization_write_reduction=writered,
    median_event_bearing_product_reduction=float(nontrivial.eager_to_product_fused.median()),
    minimum_next_mechanisms=['A. logical/physical qubit remapping','C. product-state metadata','D. fused first-entangler materialization'])
(out/'decision.json').write_text(json.dumps(details,indent=2))
report=f'''# MECHANISM RESULT: {decision}

Primary real lowered workloads: **the frozen external 20–40q set**.\n
20–40q workload count: **90 analyzed; {len(wide)} common-valid at preregistered m=16**; {90-len(wide)} excluded only from this oracle aggregate because a single gate exceeds QDAO capacity.\n
false_virtual violations: **{verification['false_virtual']}** across **{verification['product_validation_cases']} circuits**, **{verification['prefixes']} prefixes**, **{verification['virtual_claims']} virtual-factor assertions**.\n
Fused correctness cases: **{verification['fused_correctness_cases']}**, maximum infidelity **{verification['max_fused_infidelity']:.3g}**.\n
Tests passed: **{verification['tests_passed']}**, including all 154 prior tests.\n
Median eager→basis-rewrite reduction: **{med.BASIS_REWRITE:.4g}×**.\n
Median eager→basis-thin reduction: **{med.BASIS_THIN:.4g}×**.\n
Median eager→product-fused reduction: **{med.PRODUCT_FUSED:.4g}×**.\n
Median basis-thin→product-fused improvement: **{details['median_basis_thin_to_product_fused']:.4g}×**.\n
Median physicalization delay: **{details['median_completed_physicalization_delay_fraction']:.4g} of G** among completed quantum→physical lifetimes; **{delay:.4g} of G** pooled observed lower-bound windows including right-censoring.\n
Median materialization write reduction, BASIS_REWRITE/PRODUCT_FUSED: **{writered:.4g}×** (0/0 counted as 1, positive/0 as ∞).\n
**trace-driven static model — NOT measured SSD traffic.** All byte ratios above use conservative additive checkpoint accounting, not measured I/O or speedup.

**Scope of the positive result:** excluding circuits with no PRODUCT physicalization event leaves {len(nontrivial)} circuits with median **{nontrivial.eager_to_product_fused.median():.4g}×**. The {len(nopeak)} circuits that eventually fully materialize have median **{nopeak.eager_to_product_fused.median():.4g}×**, and only **{nopeak.basis_thin_to_product_fused.median():.4g}×** incremental improvement over BASIS_THIN. The overall threshold is met, but a broad SSD benefit for eventually dense circuits is not established.

## Main answer: when does a quantum qubit actually require amplitude storage?

A mathematically quantum single-qubit state does **not** need a backing dimension while its state remains a separable factor. H, RX, RY, RZ and other one-qubit unitaries update its two scalar amplitudes. Physicalization is required when the next interaction cannot be proved to preserve that factor for the current virtual states and **every possible state of the affected backing wires**. In particular, a P-control CX usually forces physicalization, but a known-zero control or an X-eigenstate target can avoid it. Controlled diagonal gates may entangle P/P or P/M while preserving a known basis operand. SWAP only remaps logical wires and physical slots.

The model's M label is conservative: failure of a local proof may physicalize more than necessary. It is not an exact entanglement-minimization algorithm. Unknown gates and matrices above 3 local qubits are not expanded into giant statevectors. P→K canonicalization is allowed, M→virtual dematerialization is not.

## Accounting definitions and capacity versus traffic

Logical q_logical replays the frozen basis analyzer. Product physical dimensions obey q_physical≤q_logical≤n. EAGER_FULL is explicitly an exception to that lazy-policy inequality: it fixes q_physical=n at t=0. BASIS_THIN has the same post-gate dimension counts as BASIS_REWRITE in the conservative dense-output envelope.

Append-only new address bits preserve existing amplitude indices. A ZERO descriptor adds no amplitude allocation at insertion; known |1⟩ selects the corresponding nonzero branch. A first H still has to generate both output branches. PRODUCT_FUSED instead holds the local vector until the first unproved entangler, then contracts compact backing plus local factors directly into post-gate output.

For each checkpoint: REWRITE charges old read + expanded write; THIN charges actual output generation after zero insertion; PRODUCT charges the fused first-entangler output generation. Each equals B_old+B_new for its own event. **The primary additive model also retains the ordinary partition traversal pair. This deliberately overcharges overlap for THIN/PRODUCT; it is a conservative composition, not a claim that an eventual fused implementation must issue both passes.** Boundary fusion only credits coincident entry reads/exit writes once. The resident convention absorbs all THIN/PRODUCT event passes and is an optimistic bound.

The standalone kernel comparison is different: expand-then-gate reads/writes B_old+3B_new versus ideal fused B_old+B_new. We do not add those saved passes a second time to the QDAO ratio. BASIS_THIN and BASIS_REWRITE matching in the primary table is a consequence of the dense-output checkpoint envelope, **not empirical proof that ZERO extents have no implementation value**.

Persistent backing peak excludes simultaneous old/new working buffers. P metadata costs 2×amplitude_bytes per product wire and is separately reported as metadata_peak_bytes. Huge scalar-backing ratios should not be mistaken for total-process RSS reductions.

{table(policy)}

## Q1. What remains of the previous 8.50× gate-volume opportunity?

The frozen 8.50× figure was gate weighted and is not a byte-traffic baseline. At common-valid m=16, including naive materialization checkpoints reduces the new predicted median to **{med.BASIS_REWRITE:.4g}×**. Delaying physicalization to an unproved entangler recovers **{med.PRODUCT_FUSED:.4g}×** under the same conservative accounting. We never subtract or divide unmatched aggregate medians as if they were paired measurements. `paired_comparisons.csv` contains paired ratios for the same circuits.

There are {len(nontrivial)} primary circuits with at least one PRODUCT physicalization event. Removing circuits with no such event gives:

{table(nonzero)}

This sensitivity is essential: many QFT/Bernstein–Vazirani/basis-only inputs remain entirely product states. They establish a physical boundary opportunity but can often be handled by simpler classical/product-state simulation and do not themselves justify an SSD kernel.

## Q2. How much does naive resize cost?

For k new dimensions, explicit resize reads B_old and writes 2^k B_old before a subsequent gate pass. `physicalization_events.csv` records each batch, insertion bytes, output bytes and standalone fusion bound. Compared with unchanged partition traversal-only accounting, resize bytes can dominate short circuits. Results can legitimately be below 1×; no clipping of negative opportunity is used.

Per-circuit medians and counts on the same common-valid set:

{table(diagnostics)}

## Q3. What does implicit ZERO avoid?

It avoids all amplitude reads/writes **at the insertion step**, including copying the existing branch and initializing the absent branch. In our dense post-quantumizing-gate output envelope, the ensuing kernel still emits B_new bytes; thus THIN and REWRITE have equal conservative checkpoint totals. The boundary-fused and resident columns quantify how much integration might change this conclusion. Actual chunk sparsity and filesystem sparse-file behavior are not assumed free.

The primary set has **{int(diagnostics.set_index('policy').loc['BASIS_THIN','explicit_resize_copies_avoided'])} explicit resize copies avoided** by the implicit insertion model. This counts eliminated copy operations, not eliminated output-generation bytes. PRODUCT executes **{int(policy.set_index('policy').loc['PRODUCT_FUSED','total_materialization_events'])} output-generation events**, versus **{int(policy.set_index('policy').loc['BASIS_REWRITE','total_materialization_events'])}** BASIS events.

## Q4. How long does P delay physicalization?

Among {len(l)} primary quantumized logical qubits, **{int(l.never_physicalized.sum())} never physicalize** in the analyzed trace. Completed lifetimes have median **{completed.virtual_product_window_fraction.median():.5g} G**, p90 **{completed.virtual_product_window_fraction.quantile(.9):.5g} G**, max **{completed.virtual_product_window_fraction.max():.5g} G**. Including censored qubits via their observed lower bounds gives median **{delay:.5g} G**. Missing physical timestamps remain missing; never-physicalized wires are not incorrectly assigned a physical event at circuit end.

First timestamps are historical per logical wire. A SWAP can transfer M to a new wire without adding a dimension; its lifetime timestamp records mapping arrival, not a new allocation. `gate_event_trace.csv` includes q_logical, each policy's dimensions, current virtual-basis/product counts, and backing bytes at every original gate position. No gate reordering is introduced by this study.

These are first-quantum-to-first-physical intervals, as requested. They may include P→K returns and mapping changes; they do not assert continuous residence in label P throughout every interval.

## Q5. Where does PRODUCT improve over THIN?

One-qubit sequences such as H→RZ→RX keep two scalar amplitudes until a later CX/controlled-phase interaction. Product invariants can also survive interactions: CX into |+⟩, known controls, and factor-preserving local isometries. These cases delay or eliminate physical output generation entirely. Batching several new dimensions at the first entangler additionally removes intermediate expansion checkpoints.

QFT on the frozen zero-state workloads often remains a product state throughout. A QFT receiving already-entangled quantum input would not inherit that saving. QAOA/random/VQE generally encounter unproved entanglers earlier and show weaker effects. The report keeps the original preparations; no workload was reinitialized to improve the answer.

Actual lowered gate sequences touching representative logical wires (median completed positive window in each listed family; positions are one-based):

{table(example_table)}

## Q6. What forces physicalization?

{table(trigger.head(20))}

Batch sizes:

{table(batch)}

## Q7. Strong and weak workload families

Primary lowered, m=16, all individual points retained in the figures:

{table(family.sort_values('median_reduction',ascending=False))}

No-event/all-product cases are explicit in this table. There are **{len(nopeak)}** primary circuits that eventually reach q_physical=n, versus **{len(wide)-len(nopeak)}** with a smaller product backing peak. Delayed allocation is not called peak capacity reduction for those reaching n. The supplementary `eventual_full_capacity_sensitivity.csv` isolates eventual-full cases.

## Q8. Semantic versus lowered and partition sensitivity

All 251 external real circuits are analyzed in both views; generated/synthetic inputs from the prior stage are secondary controls only. Below are common-legal results at m=16, including the explicitly labeled whole-circuit in-memory extension when n≤m:

{table(secondary_stats)}

There are {len(paired_rep)} external semantic/lowered pairs with legal oracle results. Their median lowered/semantic PRODUCT reduction ratio is **{paired_rep.lowered_over_semantic.median():.5g}**. `semantic_lowered_pairs.csv` retains every pair. We do not optimize ordering or choose whichever representation looks best.

m sensitivity (fixed t=2; no planner/tuning):

{table(ms)}

## Chunk size, precision and materialization batches

`sensitivity.csv` sweeps complex64/complex128 and 4 KiB, 64 KiB, 1 MiB and 4 MiB chunks on the same primary traces. Without chunk rounding, all bytes scale exactly by two and ratios are equal (asserted). With rounding, small/scalar buffers pay at least one chunk and precision can change padding fractions. ZERO branches themselves allocate no chunks, while conservatively dense outputs allocate all rounded chunks. This is a buffer/extent rounding model, not a simulation of filesystem extents or unstructured sparse patterns.

{table(sens[sens.policy=='PRODUCT_FUSED'])}

`batch_sensitivity.csv` explicitly evaluates k=1..8 for q=8/16/24. Larger batches grow output exponentially but avoid intervening copies. The fused/naive standalone byte ratio approaches three as k grows; this algebraic bound is not a measured storage gain.

## Exact validation and in-memory mechanism sanity check

Virtual labels are checked after every gate: purity Tr(rho²)≈1 and the stored local-vector projector must match rho. Maximum impurity **{verification['max_impurity']:.3g}**, maximum projector-entry error **{verification['max_vector_projector_error']:.3g}**. Random product-heavy prefixes, basis-heavy controls, entangled-rest cases and every eligible frozen n≤8 workload are included. Symbolic local gates are verified structurally in unit tests; unbound symbolic statevectors are not numerically simulated.

Fused contraction uses random compact backing states and local factors; CX in both directions, CZ, generic 2q unitaries, and batches are compared with independent Qiskit eager expansion. **{verification['fused_correctness_cases']}** cases pass with maximum amplitude error **{verification['max_fused_amplitude_error']:.3g}**. Correctness kernels enforce n≤12. No performance inference is drawn from these tiny correctness cases.

Optional NumPy microbenchmark, separate process per trial, three repetitions, setup and norm check outside the kernel timer:

{table(micro_summary)}

This is CPU RAM behavior only. The NumPy fused kernel reads compact input twice in its vectorized loops (array-pass estimate 4B_old including output writes), whereas the abstract ideal fused bound reads it once (3B_old). The naive implementation's output copy/permutation yields an estimated 10B_old in array passes. These estimates are neither hardware memory counters nor SSD traffic. Peak RSS includes the Python/Qiskit process and live buffers. No cache flush, hardware-specific optimization or simulator speedup claim is made.

## Q9. Minimum next-stage mechanism set

**{decision}: choose A + C + D — logical/physical remapping, product-state metadata, and fused first-entangler materialization.** Remapping preserves old indices and handles SWAP; metadata is what delays physicalization beyond H; the fused output kernel avoids creating and rereading an intermediate expanded vector. The numerical prototype validates this contraction. ZERO extents (B) alone are not selected as the main mechanism based on this conservative comparison; general alias/COW (E) adds no benefit for a single still-product factor beyond its two coefficients.

This selection is a design recommendation, not an implementation of any SSD component. Broad benefit remains conditional on input preparation, how long factors survive, materialization batches, and integration with traversal boundaries. The no-event and eventual-full sensitivity tables should guide which circuits justify a physical-storage prototype. No real extent store, filesystem benchmark, QDAO runtime modification, GPU kernel or m/t planner is included.

## Reproduction and immutable prior artifacts

```
conda activate htp-static
pytest -q
python scripts/run_materialization_model.py
python scripts/validate_product_virtualization.py
python scripts/benchmark_fused_materialization.py
python scripts/analyze_materialization_results.py
python scripts/plot_materialization_results.py
```

The parent commit, current commit, conda environment, package versions, seed, input CSV hashes and all external SHAs are in `results/materialization_model/reproducibility.txt`. The full prior-results hash inventory is checked before and after each stage. Per-run raw records and manifests live only in the new directory. Parse results and original figures are never regenerated or overwritten.

All model/validation outputs are numerical evidence at the stated abstraction. The same mathematical product-vector alias can be written as two scaled references to one backing extent, but no chunk-level COW store was built. **trace-driven static model — NOT measured SSD traffic.**
'''
Path('MATERIALIZATION_REPORT.md').write_text(report)
print(json.dumps(details,indent=2))
