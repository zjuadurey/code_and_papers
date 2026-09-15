# STATIC CHARACTERIZATION: STRONG

Real workloads analyzed: **251 distinct circuits**, of which **211 with n≤64** and **90 with 20–40 qubits**.

Sources: **3** public circuit repositories (QDAO source means its explicitly referenced QCS corpus).

Families: **22 labels** including `unknown`; **21 identified families** in primary n≤64 set.

Parse success rate: **1240/1369 = 90.58%** of attempted inputs; 11 metadata-only size skips.

Semantic/lowered pairs: **359 total**, **251 external real**.

Tests passed: **154**.

Exact-validation cases: **1112**, **72665 gate prefixes**, **195810 single-qubit density-matrix claims**.

False-known violations: **0**. Maximum density-matrix error **5.64e-14**, tolerance 1e-10.

Prior local repository: **not provided**.

**Interpretation warning:** large gate-volume ratios are not uniformly caused by late dependent quantum work. Basis-only reversible inputs and the serial order chosen for independent operations contribute strongly. For HEA/QAOA and several other families, lowering can increase the gate metric while layer-weighted reduction stays near 1. Inspect the 20–40 family table before using this stage label as a systems motivation.

## Scope and interpretation

This is CPU-only static characterization of the all-zero initial state followed by each circuit's explicit preparation. No workload-sized statevector, QDAO engine, SSD runtime, layout, extent allocator or m/t planner was run. Exact statevector checks are hard-limited to 8 qubits. Ideal ratios below are **not runtime speedups**; the QDAO oracle is **not measured SSD traffic**.

Primary aggregation excludes generated and synthetic controls and excludes n>64. The 40 analyzed circuits with n>64 are structural evidence only. Counts are sampled coverage, not an estimate of how often these workloads occur in production. Pure basis-input reversible circuits can be simulated classically; their large ratios alone do not establish a need for an out-of-core quantum simulator.

| source | circuits | families |
| --- | --- | --- |
| qasmbench | 67 | 17 |
| qdao | 51 | 10 |
| veriq | 133 | 13 |


## Q1. What does q(t) look like?

The curves include early full activation, incomplete activation, and delayed full activation. Classification by first full activation (≤10%, 10–50%, >50%, never full) is:

| representation | shape | circuits |
| --- | --- | --- |
| lowered | immediate_10pct | 9 |
| lowered | intermediate | 54 |
| lowered | late_after_50pct | 93 |
| lowered | never_full | 55 |
| semantic | immediate_10pct | 39 |
| semantic | intermediate | 50 |
| semantic | late_after_50pct | 65 |
| semantic | never_full | 57 |


Activation event patterns (a large burst adds ≥25% of n at one gate; otherwise incremental):

| representation | event_pattern | circuits |
| --- | --- | --- |
| lowered | incremental | 150 |
| lowered | large_burst_ge25pct | 31 |
| lowered | no_activation | 30 |
| semantic | incremental | 153 |
| semantic | large_burst_ge25pct | 28 |
| semantic | no_activation | 30 |


See Figure 1 and `q_trace.csv`; initial t=0 is stored but excluded from Hilbert-volume sums. Serial gate position depends on valid input gate order; independent gates may be reordered by lowering. The layer metric independently replays ASAP dependency layers to expose sensitivity to this choice. Q is absorbing except that SWAP transports labels without changing q; first-Q CDF is historical per logical wire, not the instantaneous q/n after swaps.

## Q2. Which families have substantial opportunity?

Families with lowered median R_gate≥4 in the n≤64 sampled set:

| family | circuits | median | geometric_mean | ge4 | ge10 | all_basis |
| --- | --- | --- | --- | --- | --- | --- |
| arithmetic | 22 | 2.3593e+06 | 4.1775e+07 | 21 | 17 | 17 |
| hidden_linear_function | 4 | 7.204 | 7.497 | 4 | 0 | 0 |
| iqp | 4 | 4.4679 | 4.4842 | 4 | 0 | 0 |
| ising | 4 | 10.452 | 6.9465 | 3 | 2 | 0 |
| mapping | 12 | 1.6353e+05 | 7.6733e+06 | 12 | 12 | 2 |
| qaoa | 12 | 10.364 | 7.6733 | 9 | 6 | 0 |
| qft | 16 | 13.832 | 11.511 | 13 | 12 | 0 |
| qram | 1 | 1.0486e+06 | 1.0486e+06 | 1 | 1 | 1 |
| quantum_ml | 9 | 45.359 | 14.404 | 6 | 6 | 0 |
| reversible | 17 | 2.6214e+05 | 1.2907e+06 | 12 | 9 | 10 |
| state_preparation | 11 | 9.3492 | 5.6639 | 7 | 5 | 0 |
| swap_test | 2 | 10 | 9.7082 | 2 | 1 | 0 |
| unknown | 20 | 5.133 | 4.2697 | 10 | 7 | 0 |


20–40-qubit lowered families with at least 3 circuits and median≥4: **arithmetic, hidden_linear_function, iqp, mapping, qaoa, qft, quantum_ml, reversible, state_preparation, vqe**. Large factors must be interpreted alongside all-basis and unused/never-quantumized qubits. No family was removed because its result was negative.

## Q3. Which families are negative controls?

Observed lowered family medians below 1.5 (n≤64):

| family | circuits | median | median_layer | lt1_5 |
| --- | --- | --- | --- | --- |
| bernstein_vazirani | 15 | 1.4579 | 1.0233 | 14 |
| clifford | 4 | 1.4848 | 1.414 | 2 |
| grover_oracle | 17 | 1.2662 | 1.2335 | 13 |
| qec | 2 | 1.4878 | 1.0033 | 1 |
| quantum_walk | 1 | 1.0476 | 1 | 1 |


QFT, QAOA, HEA and random circuits were all included, but a proposed negative class is not forced to be negative. QFT on |0…0⟩ may introduce H gates progressively: controlled diagonal phases do not quantumize their known operands. Its observed opportunity is specific to this preparation and gate ordering; a QFT receiving an arbitrary quantum register starts with already-Q inputs and has no new basis-state virtualization opportunity.

## Q4. Where do the ratios come from?

| representation | true_peak_reduction | delayed_full_materialization | all_basis | historical_never_Q |
| --- | --- | --- | --- | --- |
| lowered | 55 | 156 | 30 | 54 |
| semantic | 57 | 154 | 30 | 56 |


- `q_peak=0`: wholly classical basis evolution. There are **10** such lowered external circuits in the 20–40 range.
- `0<q_peak<n`: some proven basis dimensions remain virtual at peak; includes unused ancillas and basis-preserving control operands.
- `q_peak=n`: only allocation timing can improve; the eventual full state is still 16·2^n bytes.
- `materialization_events.csv` records individual/burst delta_q and gaps. Source traces and `activation_shapes.csv` separate timing from never-full behavior. No inferred automatic dematerialization is used.
- Generated arithmetic includes both basis and superposed input preparations, with exact Qiskit generator types recorded. These are sensitivity controls and never increase the external circuit count. Bare reversible modules on zero input are not evidence for arbitrary quantum input states.

Representative largest 20–40-qubit lowered external ratios, with provenance:

| source | source_path | family | n | q_peak | ideal_gate_reduction | ideal_layer_reduction |
| --- | --- | --- | --- | --- | --- | --- |
| veriq | combinational/adder/adder_n40.qasm | arithmetic | 40 | 0 | 1.0995e+12 | 1.0995e+12 |
| veriq | combinational/rev_circuit/gf2^13mult_205_881.qasm | reversible | 39 | 0 | 5.4976e+11 | 5.4976e+11 |
| veriq | combinational/adder/adder_n34.qasm | arithmetic | 34 | 0 | 1.718e+10 | 1.718e+10 |
| veriq | combinational/rev_circuit/gf2^10mult_109_509.qasm | reversible | 30 | 0 | 1.0737e+09 | 1.0737e+09 |
| qasmbench | large/adder_n28/adder_n28.qasm | arithmetic | 28 | 0 | 2.6844e+08 | 2.6844e+08 |
| veriq | combinational/adder/adder_n28.qasm | arithmetic | 28 | 0 | 2.6844e+08 | 2.6844e+08 |
| veriq | combinational/rev_circuit/gf2^8mult_85_341.qasm | reversible | 24 | 0 | 1.6777e+07 | 1.6777e+07 |
| veriq | combinational/adder/adder_n22.qasm | arithmetic | 22 | 0 | 4.1943e+06 | 4.1943e+06 |
| veriq | combinational/rev_circuit/permanent3x3p3.qasm | reversible | 20 | 0 | 1.0486e+06 | 1.0486e+06 |
| qasmbench | medium/qram_n20/qram_n20.qasm | qram | 20 | 0 | 1.0486e+06 | 1.0486e+06 |
| veriq | combinational/qubit_mapping/Tokyo/20QBT_4CYC_8GN_1.0P2_0.qasm | mapping | 20 | 2 | 4.1943e+05 | 2.9959e+05 |
| veriq | combinational/qubit_mapping/Tokyo/20QBT_8CYC_16GN_1.0P2_0.qasm | mapping | 20 | 3 | 2.3967e+05 | 3.2264e+05 |


## Q5. Semantic versus execution-lowered

**108/211** primary pairs change their log2 gate-volume metric by >1e-8. **2** pairs move from semantic R≥4 to lowered R<1.5. Both are shown in Figure 4, including y=x.

The backend is Aer statevector/CPU, queried live and recorded in `results/manifests/backend.json`, with optimization_level=0. Current Aer retains CCX/MCX and many controlled gates. Thus this lowering is not equivalent to a hardware H/T/CX-only compiler. A separate unit test explicitly demonstrates loss of reversible proof after CCX decomposes into H/T/CX. The primary comparison answers the current QDAO/Aer entry-point question; it cannot establish robustness under every lower-level execution representation.

For static compilation only, Aer operation objects are copied into an unbounded Target, since its ordinary target advertises a RAM-derived width limit of 29 on this machine. The exact backend and memory limits are unchanged. Actual WSL-visible memory is approximately 15 GiB, less than the assumed host 32 GiB; no experiment needs a large statevector.

Semantic wrappers without trusted transfer rules are transparently expanded until supported primitives are reached. Exported QASM often already contains decompositions; original semantic blocks cannot be reconstructed by gate names alone. `original_gate_count`, `semantic_gate_count`, and `lowered_gate_count` make the counting domains explicit. When lowering changes the metric, changes can reflect scheduling and gate-count weighting as well as quantumization; they are not themselves proof of lost physical memory savings.

Unknown-gate coverage:

| representation | unknown_gates | gates | fraction |
| --- | --- | --- | --- |
| lowered | 197 | 113314 | 0.0017385 |
| semantic | 62 | 121496 | 0.0005103 |


Details are in `unknown_gates.csv`. Unknown gates mark all operands Q; they can hide opportunity but cannot be credited with proving a basis state.

## Q6. Realistic 20–40-qubit statistics

External real circuits only; unweighted per circuit; no synthetic/generated circuits. Geometric mean uses mean log2 reduction. P90 is pandas linear quantile; these are descriptive statistics of the selected set, without population confidence claims.

| representation | circuits | median | geometric_mean | p90 | max | median_layer |
| --- | --- | --- | --- | --- | --- | --- |
| lowered | 90 | 8.4969 | 60.743 | 1.0486e+06 | 1.0995e+12 | 1.0133 |
| semantic | 90 | 2.3472 | 37.374 | 1.0486e+06 | 1.0995e+12 | 1.0133 |


| family | representation | circuits | median | geometric_mean | p90 | max | median_layer | all_basis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| arithmetic | lowered | 9 | 4.1943e+06 | 3.1054e+05 | 2.3365e+11 | 1.0995e+12 | 4.1943e+06 | 5 |
| arithmetic | semantic | 9 | 4.1943e+06 | 3.1054e+05 | 2.3365e+11 | 1.0995e+12 | 4.1943e+06 | 5 |
| bernstein_vazirani | lowered | 5 | 1.4667 | 1.483 | 1.5344 | 1.5758 | 1.0182 | 0 |
| bernstein_vazirani | semantic | 5 | 1.4667 | 1.483 | 1.5344 | 1.5758 | 1.0182 | 0 |
| grover_oracle | lowered | 8 | 1.5537 | 1.526 | 1.8533 | 1.8592 | 1.1597 | 0 |
| grover_oracle | semantic | 8 | 1.2848 | 1.2819 | 1.3058 | 1.3069 | 1.1597 | 0 |
| hidden_linear_function | lowered | 4 | 7.204 | 7.497 | 8.9422 | 9.5581 | 1 | 0 |
| hidden_linear_function | semantic | 4 | 1.4531 | 1.4529 | 1.4564 | 1.4571 | 1 | 0 |
| iqp | lowered | 4 | 4.4679 | 4.4842 | 4.7718 | 4.8023 | 1 | 0 |
| iqp | semantic | 4 | 4.4679 | 4.4842 | 4.7718 | 4.8023 | 1 | 0 |
| ising | lowered | 2 | 10.452 | 10.355 | 11.587 | 11.871 | 1 | 0 |
| ising | semantic | 2 | 1.0945 | 1.0945 | 1.0951 | 1.0952 | 1 | 0 |
| mapping | lowered | 4 | 1.6353e+05 | 32285 | 3.655e+05 | 4.1943e+05 | 1.9013e+05 | 0 |
| mapping | semantic | 4 | 2.2462e+05 | 34129 | 4.2682e+05 | 4.5344e+05 | 1.9013e+05 | 0 |
| phase_estimation | lowered | 1 | 2.1611 | 2.1611 | 2.1611 | 2.1611 | 2 | 0 |
| phase_estimation | semantic | 1 | 2.1611 | 2.1611 | 2.1611 | 2.1611 | 2 | 0 |
| qaoa | lowered | 5 | 15.519 | 11.633 | 22.114 | 23.355 | 1 | 0 |
| qaoa | semantic | 5 | 1.0432 | 1.0425 | 1.0434 | 1.0435 | 1 | 0 |
| qft | lowered | 6 | 13.032 | 12.853 | 14.631 | 15.029 | 15.5 | 0 |
| qft | semantic | 6 | 26.232 | 26.778 | 40.822 | 52.501 | 15.5 | 0 |
| qram | lowered | 1 | 1.0486e+06 | 1.0486e+06 | 1.0486e+06 | 1.0486e+06 | 1.0486e+06 | 1 |
| qram | semantic | 1 | 1.0486e+06 | 1.0486e+06 | 1.0486e+06 | 1.0486e+06 | 1.0486e+06 | 1 |
| quantum_ml | lowered | 5 | 45.359 | 44.428 | 51.464 | 52.988 | 1 | 0 |
| quantum_ml | semantic | 5 | 46.557 | 36.565 | 52.663 | 54.187 | 1 | 0 |
| random | lowered | 8 | 1.5266 | 1.5559 | 2.3371 | 2.3456 | 1.2156 | 0 |
| random | semantic | 8 | 1.4573 | 1.5048 | 2.324 | 3.1947 | 1.2156 | 0 |
| reversible | lowered | 4 | 5.4526e+08 | 3.1923e+08 | 3.8515e+11 | 5.4976e+11 | 5.4526e+08 | 4 |
| reversible | semantic | 4 | 5.4526e+08 | 3.1923e+08 | 3.8515e+11 | 5.4976e+11 | 5.4526e+08 | 4 |
| state_preparation | lowered | 8 | 10.496 | 8.8144 | 14.05 | 20 | 1.0192 | 0 |
| state_preparation | semantic | 8 | 2.762 | 4.3063 | 14.05 | 20 | 1.0192 | 0 |
| swap_test | lowered | 1 | 7.6007 | 7.6007 | 7.6007 | 7.6007 | 1 | 0 |
| swap_test | semantic | 1 | 2.5333 | 2.5333 | 2.5333 | 2.5333 | 1 | 0 |
| unknown | lowered | 11 | 9.4001 | 5.6932 | 13.441 | 16.238 | 1 | 0 |
| unknown | semantic | 11 | 1.0283 | 1.3596 | 2.5333 | 2.6111 | 1 | 0 |
| vqe | lowered | 4 | 8.4051 | 8.4596 | 9.1038 | 9.2785 | 1 | 0 |
| vqe | semantic | 4 | 8.4051 | 8.4596 | 9.1038 | 9.2785 | 1 | 0 |


`family_statistics_nonzeroQ_20_40.csv` additionally removes entirely basis-only circuits. This sensitivity table should guide any quantum simulation systems motivation.

Overall 20–40-qubit sensitivity after removing q_peak=0:

| representation | circuits | median | geometric_mean | p90 | max | median_layer |
| --- | --- | --- | --- | --- | --- | --- |
| lowered | 80 | 7.9684 | 8.5904 | 33.592 | 4.1943e+05 | 1 |
| semantic | 80 | 1.8983 | 4.9742 | 46.557 | 4.5344e+05 | 1 |


Generated arithmetic preparation sensitivity (supplementary, excluded from external aggregates):

| generator_kind | input_preparation | circuits | median | geometric_mean | max | median_layer | all_basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cdkm | basis | 6 | 5.5706e+05 | 2.6214e+05 | 2.6844e+08 | 5.5706e+05 | 6 |
| cdkm | superposed_input | 6 | 2.0695 | 2.0326 | 2.1628 | 1.3193 | 0 |
| comparator | basis | 6 | 1.3926e+05 | 65536 | 6.7109e+07 | 1.3926e+05 | 6 |
| comparator | superposed_input | 6 | 2.5426 | 2.4127 | 2.8114 | 1.6282 | 0 |
| draper | basis | 6 | 438.01 | 344.87 | 11511 | 471.64 | 0 |
| draper | superposed_input | 6 | 1.4623 | 1.4606 | 1.4718 | 1.4602 | 0 |
| modular_adder | basis | 6 | 3.2389 | 3.1693 | 3.3443 | 3.302 | 0 |
| modular_adder | superposed_input | 6 | 1.1181 | 1.1184 | 1.1203 | 1.0832 | 0 |
| multiplier | basis | 4 | 2491.7 | 1237.4 | 72529 | 2494.2 | 0 |
| multiplier | superposed_input | 4 | 4.0737 | 3.9485 | 5.962 | 4.1059 | 0 |
| vbe | basis | 6 | 1.3631e+08 | 3.3554e+07 | 1.0995e+12 | 1.3631e+08 | 6 |
| vbe | superposed_input | 6 | 35.461 | 31.558 | 57.998 | 24.888 | 0 |


## Q7. QDAO-aware static traffic oracle

**Static oracle — excludes materialization overhead. This ignores materialization overhead and is NOT measured SSD traffic.**

Boundaries reproduce current QDAO `StaticPartitioner` union/flush logic, checked against the extracted source class on 100 randomized circuits. Fixed t=2 (source default), m∈{16,18,20,22,24}, only t<m<n. There is no tuning or planner. Inputs are canonicalized to a single logical register to avoid QDAO's private register-local index aliasing. Oversized gates that the original partitioner cannot fit are explicitly rejected in `qdao_oracle.csv`.

For each subcircuit, eager bytes=32·2^n; thin bytes=16·(2^q_start+2^q_end). The second convention in the CSV charges both passes at q_end. Initial state-file creation, format overhead, repartitioning and materialization costs are excluded. These ratios are an ideal endpoint-volume model, not an implemented executor.

20–40-qubit external circuit statistics:

| representation | m | count | median | max | geometric_mean |
| --- | --- | --- | --- | --- | --- |
| lowered | 16 | 86 | 4.7988 | 1.0995e+12 | 46.993 |
| lowered | 18 | 86 | 3.9922 | 1.0995e+12 | 42.995 |
| lowered | 20 | 74 | 3.9767 | 1.0995e+12 | 29.188 |
| lowered | 22 | 71 | 3.8788 | 1.0995e+12 | 24.604 |
| lowered | 24 | 68 | 3.6601 | 1.0995e+12 | 20.988 |
| semantic | 16 | 86 | 1.8089 | 1.0995e+12 | 33.227 |
| semantic | 18 | 86 | 1.9669 | 1.0995e+12 | 32.12 |
| semantic | 20 | 74 | 1.9948 | 1.0995e+12 | 20.842 |
| semantic | 22 | 71 | 1.9794 | 1.0995e+12 | 18.48 |
| semantic | 24 | 68 | 1.9794 | 1.0995e+12 | 15.948 |


## Q8. Peak capacity or delayed allocation?

| representation | true_peak_reduction | delayed_full_materialization | all_basis |
| --- | --- | --- | --- |
| lowered | 55 | 156 | 30 |
| semantic | 57 | 154 | 30 |


`peak_storage_reduction=2^(n-q_peak)` only represents a true peak reduction when q_peak<n. The other circuits eventually require the same 16·2^n-byte dense state. Historical never-Q count can differ from n-q_final because SWAP moves states between logical wires.

## Q9. Enter storage layout design?

**Stage decision: STRONG.** The operational decision uses the **lowered, external, 20–40-qubit** set: STRONG requires ≥2 families each with ≥3 circuits and median≥4, plus ≥3 circuits with ratio≥10; MIXED requires several substantial examples; otherwise WEAK. This is a transparent phase gate, not a final paper criterion.

The evidence warrants a scoped next-stage design study for the supported families and explicit input preparations. It does not establish broad simulator speedup or automatic benefit for circuits that already begin on quantum data. A no-full-rewrite materialization layout would be the next question, subject to actual materialization cost and backend semantics.

For scoping that decision: QFT on the benchmark's known initial state retains substantial **layer-weighted** opportunity; external basis-only adders/reversible circuits are weak evidence for needing a quantum storage system despite their enormous ratios. Generated VBE with an explicitly superposed data register is a useful nontrivial ancilla sensitivity control, while generated CDKM/modular addition is much weaker. QAOA's large lowered gate ratio is substantially schedule-dependent. The next study should preserve these distinctions rather than use the global geometric mean as its motivation. **No next-stage storage design is included in this project.**

## Coverage limitations and exclusions

- 1380 discovered input records; 11 files skipped before parsing for size. Every attempted parse failure is in `parse_failures.csv`, with source hash and exact error; no source files were edited.
- Deterministic stratification is by source/family/width/gate-count, with 0 further normalized-structure duplicates excluded. Existing `_transpiled` companions are not counted as independent circuits when their source exists. Repeated sizes/seeds are capped by stratum; the set is not a population sample.
- Unsupported dynamics and analysis limits are separate from parse failures. Terminal readout is removed; mid-circuit measurements, reset and classical control are not modeled.
- Numerical angle tolerance=1e-10 and matrix structure tolerance=1e-14 are documented in `notes/gate_semantics.md`. A cumulative operator-norm error budget of 5e-11 prevents repeated near-special gates from silently accumulating false-known claims; exhausted proofs use Q. Tests include 6,000 near-diagonal gates, repeated near-zero RX, and unreliable huge-angle reduction. Floating arithmetic itself remains numerical, rather than symbolic certification.
- Development validation exposed and fixed a multi-target controlled-gate false-known bug. All characterization was rerun after the correction; only the latest verified run is used here. See `notes/validation_audit.md` for the failure and regression test, rather than treating earlier debug artifacts as evidence.
- Reversible files containing conflicting repeated gate definitions remain parse failures. Missing unambiguous legacy `c3sx` and `mcx_gray` declarations are mapped to current Qiskit types; declared custom gate bodies are preserved.
- Generated arithmetic QPY stores its transparent semantic expansion because some current Qiskit OrGate wrappers fail to reload. Every saved generated input is immediately round-tripped. Optional generated Grover stops at 32 qubits because QPY cannot serialize closed MCX control masks above uint32; required QFT/QAOA/HEA/random controls still cover all eight sizes through 40. This package limitation does not limit static analysis of external larger circuits.
- No prior local repository was guessed or scanned without the configured path. QDAO and all external repositories remain clean and unmodified.

| error_type | unsupported_dynamic | count |
| --- | --- | --- |
| UnsupportedDynamic | True | 40 |


## Reproduction and provenance

See `README.md` and `bash scripts/run_all.sh`. Raw per-circuit results and generated QPY inputs are stored under `results/raw/20260915T141040.945114Z`; timestamps distinguish reruns. Exact tests and source/config/output hashes are recorded in the manifests. All figures are regenerated from CSV/raw records, not hand-edited.

| name | repository | git_commit | git_branch | dirty |
| --- | --- | --- | --- | --- |
| qdao | https://github.com/Zhaoyilunnn/qdao.git | fb360e6670b9818a3d4e106fb21cf605838be0a4 | main | False |
| QASMBench | https://github.com/pnnl/QASMBench.git | 357b942396d5c2b7cbc1c229c585a6ef5ccaebac | master | False |
| veriq-benchmark | https://github.com/Veri-Q/Benchmark.git | 1c03e45371e5701f62c123943dec1cace4d46767 | main | False |
| qcs | https://github.com/Zhaoyilunnn/quantum-computing-resources.git | c03dfa056ab2f765847b536494480081daa8caad | main | False |


QDAO `v0.1.0` and `stable/0.1` exist; neither was checked out or run. See `notes/qdao_execution_model.md` for source locations. Primary references: [QDAO source](https://github.com/Zhaoyilunnn/qdao), [QASMBench](https://github.com/pnnl/QASMBench), [Veri-Q Benchmark](https://github.com/Veri-Q/Benchmark), [Qiskit QASM2 loader](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qasm2).
