# MECHANISM RESULT: PROMISING

Primary real lowered workloads: **the frozen external 20–40q set**.

20–40q workload count: **90 analyzed; 86 common-valid at preregistered m=16**; 4 excluded only from this oracle aggregate because a single gate exceeds QDAO capacity.

false_virtual violations: **0** across **1216 circuits**, **58665 prefixes**, **136965 virtual-factor assertions**.

Fused correctness cases: **1600**, maximum infidelity **4.44e-16**.

Tests passed: **194**, including all 154 prior tests.

Median eager→basis-rewrite reduction: **1.489×**.

Median eager→basis-thin reduction: **1.489×**.

Median eager→product-fused reduction: **5.243×**.

Median basis-thin→product-fused improvement: **1.296×**.

Median physicalization delay: **0.0074 of G** among completed quantum→physical lifetimes; **0.0119 of G** pooled observed lower-bound windows including right-censoring.

Median materialization write reduction, BASIS_REWRITE/PRODUCT_FUSED: **1.5×** (0/0 counted as 1, positive/0 as ∞).

**trace-driven static model — NOT measured SSD traffic.** All byte ratios above use conservative additive checkpoint accounting, not measured I/O or speedup.

**Scope of the positive result:** excluding circuits with no PRODUCT physicalization event leaves 59 circuits with median **1.994×**. The 40 circuits that eventually fully materialize have median **1.491×**, and only **1.034×** incremental improvement over BASIS_THIN. The overall threshold is met, but a broad SSD benefit for eventually dense circuits is not established.

## Main answer: when does a quantum qubit actually require amplitude storage?

A mathematically quantum single-qubit state does **not** need a backing dimension while its state remains a separable factor. H, RX, RY, RZ and other one-qubit unitaries update its two scalar amplitudes. Physicalization is required when the next interaction cannot be proved to preserve that factor for the current virtual states and **every possible state of the affected backing wires**. In particular, a P-control CX usually forces physicalization, but a known-zero control or an X-eigenstate target can avoid it. Controlled diagonal gates may entangle P/P or P/M while preserving a known basis operand. SWAP only remaps logical wires and physical slots.

The model's M label is conservative: failure of a local proof may physicalize more than necessary. It is not an exact entanglement-minimization algorithm. Unknown gates and matrices above 3 local qubits are not expanded into giant statevectors. P→K canonicalization is allowed, M→virtual dematerialization is not.

## Accounting definitions and capacity versus traffic

Logical q_logical replays the frozen basis analyzer. Product physical dimensions obey q_physical≤q_logical≤n. EAGER_FULL is explicitly an exception to that lazy-policy inequality: it fixes q_physical=n at t=0. BASIS_THIN has the same post-gate dimension counts as BASIS_REWRITE in the conservative dense-output envelope.

Append-only new address bits preserve existing amplitude indices. A ZERO descriptor adds no amplitude allocation at insertion; known |1⟩ selects the corresponding nonzero branch. A first H still has to generate both output branches. PRODUCT_FUSED instead holds the local vector until the first unproved entangler, then contracts compact backing plus local factors directly into post-gate output.

For each checkpoint: REWRITE charges old read + expanded write; THIN charges actual output generation after zero insertion; PRODUCT charges the fused first-entangler output generation. Each equals B_old+B_new for its own event. **The primary additive model also retains the ordinary partition traversal pair. This deliberately overcharges overlap for THIN/PRODUCT; it is a conservative composition, not a claim that an eventual fused implementation must issue both passes.** Boundary fusion only credits coincident entry reads/exit writes once. The resident convention absorbs all THIN/PRODUCT event passes and is an optimistic bound.

The standalone kernel comparison is different: expand-then-gate reads/writes B_old+3B_new versus ideal fused B_old+B_new. We do not add those saved passes a second time to the QDAO ratio. BASIS_THIN and BASIS_REWRITE matching in the primary table is a consequence of the dense-output checkpoint envelope, **not empirical proof that ZERO extents have no implementation value**.

Persistent backing peak excludes simultaneous old/new working buffers. P metadata costs 2×amplitude_bytes per product wire and is separately reported as metadata_peak_bytes. Huge scalar-backing ratios should not be mistaken for total-process RSS reductions.

| policy | circuits | median_reduction | geometric_mean_reduction | p90_reduction | max_reduction | median_boundary_fused_reduction | median_resident_optimistic_reduction | median_peak_bytes | median_q_peak | median_materialization_read_bytes | median_materialization_write_bytes | total_materialization_events | median_materialization_events |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EAGER_FULL | 86 | 1 | 1 | 1 | 1 | 1 | 1 | 6.44245e+09 | 28.5 | 0 | 0 | 0 | 0 |
| BASIS_REWRITE | 86 | 1.48904 | 24.2881 | 1.04858e+06 | 1.09951e+12 | 1.48904 | 1.48904 | 4.29497e+09 | 28 | 4.29497e+09 | 8.58993e+09 | 2123 | 28 |
| BASIS_THIN | 86 | 1.48904 | 24.2881 | 1.04858e+06 | 1.09951e+12 | 1.49193 | 4.79883 | 4.29497e+09 | 28 | 4.29497e+09 | 8.58993e+09 | 2123 | 28 |
| PRODUCT_FUSED | 86 | 5.24342 | 1438.41 | 2.68435e+09 | 1.09951e+12 | 5.265 | 8.31747 | 5.36871e+08 | 25 | 3.12584e+08 | 8.27348e+08 | 1234 | 16 |


## Q1. What remains of the previous 8.50× gate-volume opportunity?

The frozen 8.50× figure was gate weighted and is not a byte-traffic baseline. At common-valid m=16, including naive materialization checkpoints reduces the new predicted median to **1.489×**. Delaying physicalization to an unproved entangler recovers **5.243×** under the same conservative accounting. We never subtract or divide unmatched aggregate medians as if they were paired measurements. `paired_comparisons.csv` contains paired ratios for the same circuits.

There are 59 primary circuits with at least one PRODUCT physicalization event. Removing circuits with no such event gives:

| statistic | eager_to_product_fused | basis_thin_to_product_fused |
| --- | --- | --- |
| count | 59 | 59 |
| median | 1.99367 | 1.17749 |
| min | 0.992248 | 1 |
| max | 209715 | 122.852 |


This sensitivity is essential: many QFT/Bernstein–Vazirani/basis-only inputs remain entirely product states. They establish a physical boundary opportunity but can often be handled by simpler classical/product-state simulation and do not themselves justify an SSD kernel.

## Q2. How much does naive resize cost?

For k new dimensions, explicit resize reads B_old and writes 2^k B_old before a subsequent gate pass. `physicalization_events.csv` records each batch, insertion bytes, output bytes and standalone fusion bound. Compared with unchanged partition traversal-only accounting, resize bytes can dominate short circuits. Results can legitimately be below 1×; no clipping of negative opportunity is used.

Per-circuit medians and counts on the same common-valid set:

| policy | median_traversal_only_reduction | median_materialization_fraction | median_total_over_traversal_bytes | capacity_reduced_circuits | eventually_full_circuits | explicit_resize_copies_avoided |
| --- | --- | --- | --- | --- | --- | --- |
| BASIS_REWRITE | 4.79883 | 0.369272 | 1.5856 | 19 | 67 | 0 |
| BASIS_THIN | 4.79883 | 0.369272 | 1.5856 | 19 | 67 | 2123 |
| EAGER_FULL | 1 | 0 | 1 | 0 | 86 | 0 |
| PRODUCT_FUSED | 8.31747 | 0.282813 | 1.39434 | 46 | 40 | 2123 |


## Q3. What does implicit ZERO avoid?

It avoids all amplitude reads/writes **at the insertion step**, including copying the existing branch and initializing the absent branch. In our dense post-quantumizing-gate output envelope, the ensuing kernel still emits B_new bytes; thus THIN and REWRITE have equal conservative checkpoint totals. The boundary-fused and resident columns quantify how much integration might change this conclusion. Actual chunk sparsity and filesystem sparse-file behavior are not assumed free.

The primary set has **2123 explicit resize copies avoided** by the implicit insertion model. This counts eliminated copy operations, not eliminated output-generation bytes. PRODUCT executes **1234 output-generation events**, versus **2123** BASIS events.

## Q4. How long does P delay physicalization?

Among 2123 primary quantumized logical qubits, **510 never physicalize** in the analyzed trace. Completed lifetimes have median **0.0073996 G**, p90 **0.17944 G**, max **0.9322 G**. Including censored qubits via their observed lower bounds gives median **0.011905 G**. Missing physical timestamps remain missing; never-physicalized wires are not incorrectly assigned a physical event at circuit end.

First timestamps are historical per logical wire. A SWAP can transfer M to a new wire without adding a dimension; its lifetime timestamp records mapping arrival, not a new allocation. `gate_event_trace.csv` includes q_logical, each policy's dimensions, current virtual-basis/product counts, and backing bytes at every original gate position. No gate reordering is introduced by this study.

These are first-quantum-to-first-physical intervals, as requested. They may include P→K returns and mapping changes; they do not assert continuous residence in label P throughout every interval.

## Q5. Where does PRODUCT improve over THIN?

One-qubit sequences such as H→RZ→RX keep two scalar amplitudes until a later CX/controlled-phase interaction. Product invariants can also survive interactions: CX into |+⟩, known controls, and factor-preserving local isometries. These cases delay or eliminate physical output generation entirely. Batching several new dimensions at the first entangler additionally removes intermediate expansion checkpoints.

QFT on the frozen zero-state workloads often remains a product state throughout. A QFT receiving already-entangled quantum input would not inherit that saving. QAOA/random/VQE generally encounter unproved entanglers earlier and show weaker effects. The report keeps the original preparations; no workload was reinitialized to improve the answer.

Actual lowered gate sequences touching representative logical wires (median completed positive window in each listed family; positions are one-based):

| workload_id | family | qubit | quantum_gate | physical_gate | delay_gates | delay_fraction | gates_on_wire |
| --- | --- | --- | --- | --- | --- | --- | --- |
| qdao_b55d2dd9bf5b66fa_0 | state_preparation | 25 | 48 | 49 | 1 | 0.0181818 | 48:h → 49:cz |
| veriq_caf4f6fd0033a07b_0 | grover_oracle | 9 | 10 | 26 | 16 | 0.107383 | 10:h → 26:ccx |
| veriq_1e3f14dad487dc42_0 | qaoa | 15 | 311 | 314 | 3 | 0.00443787 | 311:h → 312:rz → 313:u3 → 314:cx |
| qdao_f582b0405134801e_0 | random | 0 | 1 | 6 | 5 | 0.013624 | 1:u2 → 6:cx |


## Q6. What forces physicalization?

| gate_name | trigger_reason | events | dimensions | median_batch |
| --- | --- | --- | --- | --- |
| cx | cx_materialized_control | 462 | 462 | 1 |
| cx | cx_product_control | 244 | 448 | 2 |
| cz | controlled_diagonal_backing | 156 | 156 | 1 |
| cp | controlled_diagonal_backing | 114 | 114 | 1 |
| cswap | multi_qubit_gate | 111 | 158 | 1 |
| cz | cz_product_pair | 55 | 110 | 2 |
| ccx | multi_qubit_gate | 54 | 112 | 2 |
| cy | controlled_rotation | 24 | 29 | 1 |
| ryy | generic_entangler | 6 | 12 | 2 |
| cp | cz_product_pair | 4 | 8 | 2 |
| rzz | controlled_diagonal_backing | 4 | 4 | 1 |


Batch sizes:

| policy | materialization_batch_size | events |
| --- | --- | --- |
| BASIS_REWRITE | 1 | 2123 |
| BASIS_THIN | 1 | 2123 |
| PRODUCT_FUSED | 1 | 862 |
| PRODUCT_FUSED | 2 | 365 |
| PRODUCT_FUSED | 3 | 7 |


## Q7. Strong and weak workload families

Primary lowered, m=16, all individual points retained in the figures:

| family | circuits | median_reduction | p90_reduction | median_q_peak | median_window | zero_physical_dimensions |
| --- | --- | --- | --- | --- | --- | --- |
| arithmetic | 9 | 1.07374e+09 | 2.33646e+11 | 0 | 0 | 9 |
| bernstein_vazirani | 5 | 1.07374e+09 | 6.63143e+11 | 0 | 0.826923 | 5 |
| qft | 6 | 8.05306e+08 | 1.07374e+10 | 0 | 0.733854 | 6 |
| reversible | 4 | 5.4526e+08 | 3.85151e+11 | 0 | 0 | 4 |
| qram | 1 | 1.04858e+06 | 1.04858e+06 | 0 | 0 | 1 |
| phase_estimation | 1 | 1.04858e+06 | 1.04858e+06 | 0 | 0.95614 | 1 |
| mapping | 4 | 128159 | 796918 | 3 | 0.171875 | 1 |
| hidden_linear_function | 4 | 33.8545 | 138.282 | 26.5 | 0.0142857 | 0 |
| state_preparation | 8 | 10.9727 | 25.9191 | 26 | 0.0162871 | 0 |
| grover_oracle | 4 | 5.24342 | 5.48838 | 28 | 0.10697 | 0 |
| iqp | 4 | 3.52346 | 4.59354 | 30 | 0.00240892 | 0 |
| swap_test | 1 | 2.14925 | 2.14925 | 25 | 0.342105 | 0 |
| unknown | 11 | 1.99367 | 5.9978 | 28 | 0.0058651 | 0 |
| qaoa | 5 | 1.98425 | 2.7554 | 29 | 0.00443787 | 0 |
| ising | 2 | 1.86142 | 2.15143 | 30 | 0.0125776 | 0 |
| quantum_ml | 5 | 1.48833 | 1.7679 | 29 | 0.00440529 | 0 |
| random | 8 | 1.47786 | 2.10767 | 29 | 0.0257044 | 0 |
| vqe | 4 | 1.3058 | 1.45736 | 29 | 0.00753917 | 0 |


No-event/all-product cases are explicit in this table. There are **40** primary circuits that eventually reach q_physical=n, versus **46** with a smaller product backing peak. Delayed allocation is not called peak capacity reduction for those reaching n. The supplementary `eventual_full_capacity_sensitivity.csv` isolates eventual-full cases.

## Q8. Semantic versus lowered and partition sensitivity

All 251 external real circuits are analyzed in both views; generated/synthetic inputs from the prior stage are secondary controls only. Below are common-legal results at m=16, including the explicitly labeled whole-circuit in-memory extension when n≤m:

| representation | policy | count | median |
| --- | --- | --- | --- |
| lowered | BASIS_REWRITE | 247 | 1.48828 |
| lowered | BASIS_THIN | 247 | 1.48828 |
| lowered | EAGER_FULL | 247 | 1 |
| lowered | PRODUCT_FUSED | 247 | 5.59219 |
| semantic | BASIS_REWRITE | 247 | 1.19988 |
| semantic | BASIS_THIN | 247 | 1.19988 |
| semantic | EAGER_FULL | 247 | 1 |
| semantic | PRODUCT_FUSED | 247 | 5.41473 |


There are 247 external semantic/lowered pairs with legal oracle results. Their median lowered/semantic PRODUCT reduction ratio is **1**. `semantic_lowered_pairs.csv` retains every pair. We do not optimize ordering or choose whichever representation looks best.

m sensitivity (fixed t=2; no planner/tuning):

| m | policy | count | median |
| --- | --- | --- | --- |
| 16 | BASIS_REWRITE | 86 | 1.48904 |
| 16 | BASIS_THIN | 86 | 1.48904 |
| 16 | EAGER_FULL | 86 | 1 |
| 16 | PRODUCT_FUSED | 86 | 5.24342 |
| 18 | BASIS_REWRITE | 86 | 1.37168 |
| 18 | BASIS_THIN | 86 | 1.37168 |
| 18 | EAGER_FULL | 86 | 1 |
| 18 | PRODUCT_FUSED | 86 | 4.85356 |
| 20 | BASIS_REWRITE | 86 | 1.19533 |
| 20 | BASIS_THIN | 86 | 1.19533 |
| 20 | EAGER_FULL | 86 | 1 |
| 20 | PRODUCT_FUSED | 86 | 4.70449 |
| 22 | BASIS_REWRITE | 86 | 1.07824 |
| 22 | BASIS_THIN | 86 | 1.07824 |
| 22 | EAGER_FULL | 86 | 1 |
| 22 | PRODUCT_FUSED | 86 | 4.69416 |
| 24 | BASIS_REWRITE | 86 | 0.999512 |
| 24 | BASIS_THIN | 86 | 0.999512 |
| 24 | EAGER_FULL | 86 | 1 |
| 24 | PRODUCT_FUSED | 86 | 4.58257 |


## Chunk size, precision and materialization batches

`sensitivity.csv` sweeps complex64/complex128 and 4 KiB, 64 KiB, 1 MiB and 4 MiB chunks on the same primary traces. Without chunk rounding, all bytes scale exactly by two and ratios are equal (asserted). With rounding, small/scalar buffers pay at least one chunk and precision can change padding fractions. ZERO branches themselves allocate no chunks, while conservatively dense outputs allocate all rounded chunks. This is a buffer/extent rounding model, not a simulation of filesystem extents or unstructured sparse patterns.

| policy | amplitude_bytes | chunk_bytes | reduction_vs_eager |
| --- | --- | --- | --- |
| PRODUCT_FUSED | 8 | 1 | 5.24342 |
| PRODUCT_FUSED | 8 | 4096 | 5.24339 |
| PRODUCT_FUSED | 8 | 65536 | 5.24261 |
| PRODUCT_FUSED | 8 | 1048576 | 3.97 |
| PRODUCT_FUSED | 8 | 4194304 | 2.32353 |
| PRODUCT_FUSED | 16 | 1 | 5.24342 |
| PRODUCT_FUSED | 16 | 4096 | 5.24341 |
| PRODUCT_FUSED | 16 | 65536 | 5.24304 |
| PRODUCT_FUSED | 16 | 1048576 | 5.05174 |
| PRODUCT_FUSED | 16 | 4194304 | 3.51709 |


`batch_sensitivity.csv` explicitly evaluates k=1..8 for q=8/16/24. Larger batches grow output exponentially but avoid intervening copies. The fused/naive standalone byte ratio approaches three as k grows; this algebraic bound is not a measured storage gain.

## Exact validation and in-memory mechanism sanity check

Virtual labels are checked after every gate: purity Tr(rho²)≈1 and the stored local-vector projector must match rho. Maximum impurity **1.25e-13**, maximum projector-entry error **6.25e-14**. Random product-heavy prefixes, basis-heavy controls, entangled-rest cases and every eligible frozen n≤8 workload are included. Symbolic local gates are verified structurally in unit tests; unbound symbolic statevectors are not numerically simulated.

Fused contraction uses random compact backing states and local factors; CX in both directions, CZ, generic 2q unitaries, and batches are compared with independent Qiskit eager expansion. **1600** cases pass with maximum amplitude error **2.24e-16**. Correctness kernels enforce n≤12. No performance inference is drawn from these tiny correctness cases.

Optional NumPy microbenchmark, separate process per trial, three repetitions, setup and norm check outside the kernel timer:

| q | policy | trials | median_wall_seconds | median_peak_rss_bytes | output_allocation_bytes | implementation_copy_volume_estimate |
| --- | --- | --- | --- | --- | --- | --- |
| 18 | fused | 3 | 0.00315855 | 1.47976e+08 | 8.38861e+06 | 1.67772e+07 |
| 18 | naive | 3 | 0.00737061 | 1.56156e+08 | 1.67772e+07 | 4.1943e+07 |
| 20 | fused | 3 | 0.0144323 | 1.85692e+08 | 3.35544e+07 | 6.71089e+07 |
| 20 | naive | 3 | 0.0329642 | 2.19144e+08 | 6.71089e+07 | 1.67772e+08 |
| 22 | fused | 3 | 0.0543664 | 3.36708e+08 | 1.34218e+08 | 2.68435e+08 |
| 22 | naive | 3 | 0.0838993 | 4.70852e+08 | 2.68435e+08 | 6.71089e+08 |
| 24 | fused | 3 | 0.131929 | 9.4063e+08 | 5.36871e+08 | 1.07374e+09 |
| 24 | naive | 3 | 0.350631 | 1.47738e+09 | 1.07374e+09 | 2.68435e+09 |


This is CPU RAM behavior only. The NumPy fused kernel reads compact input twice in its vectorized loops (array-pass estimate 4B_old including output writes), whereas the abstract ideal fused bound reads it once (3B_old). The naive implementation's output copy/permutation yields an estimated 10B_old in array passes. These estimates are neither hardware memory counters nor SSD traffic. Peak RSS includes the Python/Qiskit process and live buffers. No cache flush, hardware-specific optimization or simulator speedup claim is made.

## Q9. Minimum next-stage mechanism set

**PROMISING: choose A + C + D — logical/physical remapping, product-state metadata, and fused first-entangler materialization.** Remapping preserves old indices and handles SWAP; metadata is what delays physicalization beyond H; the fused output kernel avoids creating and rereading an intermediate expanded vector. The numerical prototype validates this contraction. ZERO extents (B) alone are not selected as the main mechanism based on this conservative comparison; general alias/COW (E) adds no benefit for a single still-product factor beyond its two coefficients.

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
