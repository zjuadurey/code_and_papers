# Conditional-plan content review

## Observable rubric

This rubric was written before inspecting diagnostic scientific responses. Coding is an AI-assisted descriptive review of emitted text, not correctness validation, independent human annotation, reference agreement or proof of capability. Only completed predictions are used as substantive evidence.

- **SUBSTANTIVE:** a case-specific formulation path connects intent, family/contract, representation, quantum procedure and decoding/verification. For search, this includes a candidate domain and predicate/oracle role. For optimization, it includes variables, objective/QUBO/Ising construction and constraint handling where relevant. Assumptions, risks and unresolved semantic/resource requirements are meaningfully identified. Numerical resource estimates or resolved exactness are not prerequisites when explicitly unknown; this is content coverage, not feasibility certification.
- **PARTIAL:** some case-specific transformation detail exists, but one or more essential links in the formulation/encoding/procedure/decoding path are missing or too vague to follow.
- **SUPERFICIAL:** populated fields mostly repeat family names or generic instructions, without an actual case-specific formulation path.
- **NOT APPLICABLE:** no plan emitted. This does not imply an error, particularly for structural-NO controls.

A classification can be SUBSTANTIVE while exactness, optimality certification, resource feasibility or even scientific correctness remains unresolved. Claims and formulas below are attributed to model responses, not endorsed. The review does not solve cases or compare against DRAFT/gold annotations.

## Review summary

Eight plans are **SUBSTANTIVE**, zero PARTIAL, zero SUPERFICIAL; two null-plan cases are NOT APPLICABLE. All eight preserve unresolved requirements. All eight `expected_resource_characteristics` objects contain only an unresolved-status string; concrete resource considerations appear elsewhere in the plan. None supplies a complete resource estimate or verified implementation. This weakness is reported rather than hidden by the overall content classification.

| Case | Classification | Observable formulation evidence | Principal limitation |
|---|---|---|---|
| pilot-001 | SUBSTANTIVE | Assignment-bit domain; clause predicate; reversible OR/conjunction, marking and uncomputation | Exact absence certification and oracle costs unresolved |
| pilot-002 | NOT APPLICABLE | No plan; structural NO | No supported formulation claimed |
| pilot-003 | SUBSTANTIVE | Explicit cut objective, minimizing its negative, Ising substitution | Samples do not certify the exact maximum |
| pilot-004 | SUBSTANTIVE | Index predicate with padding, equality and exact fallback | Tiny domain, integer encoding costs, exact absence |
| pilot-005 | SUBSTANTIVE | Selection bits; unit equality plus budget inequality; reversible accumulators | Exact negative result and cost of coherent arithmetic |
| pilot-006 | SUBSTANTIVE | Explicit quadratic energy; repeated/self terms; Ising constants/signs | Exact minimum certification and coefficient precision |
| pilot-007 | SUBSTANTIVE | Positional subset bits; signed/offset accumulator and width bound | Unknown marked count, absence certification and input-dependent costs |
| pilot-008 | NOT APPLICABLE | No plan; structural NO | No supported formulation claimed |
| pilot-009 | SUBSTANTIVE | Placement bits, unary cost plus explicit same-side quadratic penalty | Exact optimality certification and coefficient fidelity |
| pilot-010 | SUBSTANTIVE | Record-index predicate; full classical parsing retained; reversible truthiness/equality | Exact Python semantics, loading and absence fallback |

## Per-plan evidence

### pilot-001 — SUBSTANTIVE

Evidence: [raw response](raw/pilot-001.txt), fields `plan.formulation`, `input_encoding`, `output_decoding`, `assumptions`, `risks`.

The intent ID is `exact_cnf_satisfiability_existence`; contract/family are `grover-predicate-v0` / `unstructured_search`, algorithm `grover_style`. The plan uses n assignment qubits, marks satisfaction of every clause, handles empty clauses/list, and describes computing literal truth, clause ORs and conjunction before phase marking and uncomputation. Measured assignments are checked with the classical predicate. It explicitly requires exact no-solution certification or an exhaustive classical fallback before returning false.

This is a formulation/encoding/verification path rather than a family name. Reversible construction, unknown-solution-count scheduling, workspace, loading and fallback cost remain assumptions or risks. The plan does not provide a concrete oracle circuit, complete search schedule or exact certification method. Its resource object is generic unresolved status, with qualitative qubit/workspace and gate considerations elsewhere.

### pilot-003 — SUBSTANTIVE

Evidence: [raw response](raw/pilot-003.txt), especially `plan.formulation` and `output_decoding`.

The intent ID is `exact_weighted_max_cut_value`; contract/family are `qubo-ising-v0` / `combinatorial_optimization`, algorithm `qaoa`. It introduces vertex bits and writes `C(x) = sum_(u,v,w) w*(x_u + x_v - 2*x_u*x_v)`, minimizes `-C(x)`, and gives an Ising substitution. It explicitly accounts for repeated edges, self loops, n partition qubits, coefficient preparation and the zero-vertex case. No separate feasibility constraints are claimed for the binary-partition representation. Decoding recomputes original edge-list scores.

The plan states that rescoring samples does not certify the global optimum. Precision, weighted interactions, routing, parameter optimization and sampling costs are unresolved. Its resource object remains generic; the plan supplies no depth/shot policy or exact optimum certificate. Those gaps limit migration completeness, not the observation that it contains a specific objective-to-Hamiltonian path.

### pilot-004 — SUBSTANTIVE

Evidence: [raw response](raw/pilot-004.txt), `plan.formulation`, `input_encoding`, `output_decoding` and `risks`.

The intent ID is `bounded_exact_code_membership`; Grover contract/search family/`grover_style` are selected. The plan keeps length validation classical, uses candidate indices, excludes invalid padded indices, and marks exact equality. Empty input and duplicates are addressed. It describes per-invocation signed-integer representation, reversible comparison and uncomputation, then bounds/equality verification after measurement.

The exact false result requires a certified procedure or complete scan; the length-over-eight exception is retained. The model calls out the at-most-eight domain and potentially redundant classical fallback. Integer widths, physical resources and oracle costs remain unknown. This is a concrete conditional mapping despite continued practical NO; no advantage conclusion is endorsed by this review.

### pilot-005 — SUBSTANTIVE

Evidence: [raw response](raw/pilot-005.txt), all substantive `plan` fields.

The intent ID is `exact_bundle_feasibility_existence`; Grover contract/search family/`grover_style` are selected. It specifies n subset-selection bits, `sum_i(x_i * units_i) == target` and `sum_i(x_i * price_i) <= budget`. Constraints are incorporated in the predicate through reversible accumulators and comparison flags, followed by marking and uncomputation. Filtering, copying and SKU sorting remain classical; the empty subset is included. Decoding verifies totals and preserves the Boolean plus count/target metadata interface.

The plan does not silently convert a failed search into false: exact absence, an explicitly approved error policy, or exact fallback remains necessary. Integer widths, loading, workspace, scale and oracle reuse are unresolved. The resource object only says unresolved. There is a specific constrained-feasibility-to-predicate path, but no completed exact decision procedure.

### pilot-006 — SUBSTANTIVE

Evidence: [raw response](raw/pilot-006.txt), `plan.formulation`, `input_encoding`, `output_decoding` and `risks`.

The intent ID is `exact_binary_quadratic_minimum_value`; QUBO contract/optimization family/`qaoa` are selected. It explicitly constructs `E(x)=sum_i b_i*x_i+sum_(i,j,w) w*x_i*x_j`, sums repeated tuples, folds self-couplings into linear terms and retains constants/signs under `x_i=(1-Z_i)/2`. One logical variable/qubit per bias entry and signed-coefficient Hamiltonian compilation are described. The objective is unconstrained over binary assignments rather than supplemented with invented penalties.

Decoding uses original-expression rescoring but permits returning the minimum only after a justified global certificate. Finite-depth sampling, coefficient precision/scaling, embedding and parameter optimization remain risks. Resource counts and certification are not resolved. This is detailed formulation content, not a verified exact minimizer.

### pilot-007 — SUBSTANTIVE

Evidence: [raw response](raw/pilot-007.txt), notably `plan.formulation`, `input_encoding` and `output_decoding`.

The intent ID is `exact_subset_sum_existence`; Grover contract/search family/`grover_style` are selected. Position-selection bits preserve duplicates; the predicate compares a controlled signed sum with the target. The plan handles the empty subset, describes a uniform candidate superposition and reversible accumulation/comparison/phase marking/uncomputation, and proposes an offset register bounded by `S=sum_i abs(values[i])`, with `ceil(log2(2*S+1))` value bits and an S=0 convention. These are claims in the response, not separately proved resource bounds.

Candidate sums are recomputed classically; failed samples cannot establish false. Unknown marked count, exact absence, overflow-free arithmetic, input-dependent compilation/loading and large integer widths are explicitly unresolved concerns. The resource object remains generic despite a more concrete encoding estimate in prose. No complete circuit or certification procedure is supplied.

### pilot-009 — SUBSTANTIVE

Evidence: [raw response](raw/pilot-009.txt), `plan.formulation`, `input_encoding`, `output_decoding` and `assumptions`.

The intent ID is `exact_binary_placement_cost_minimization`; QUBO contract/optimization family/`qaoa` are selected. The response defines x_i=0/1 for left/right, combines unary placement costs with `p*(1-x_a-x_b+2*x_a*x_b)`, discusses the constant self-link contribution and retains offsets when recovering integer cost. It gives the Ising substitution and keeps input validation/report construction classical. The formulation is over binary placements; links enter the objective, not an unexplained feasibility constraint.

Measured placements are rescored with exact integers, but best observed cost is not automatically returned as the optimum. Certification, coefficient fidelity, rescaling, circuit cost and performance evidence remain unresolved. Names/count and validation failures are explicitly preserved in the proposed interface. There is a substantive conditional cost formulation, not a certified replacement of the classical routine.

### pilot-010 — SUBSTANTIVE

Evidence: [raw response](raw/pilot-010.txt), `plan.formulation`, `input_encoding`, `output_decoding` and `assumptions`.

The intent ID is `exact_active_record_key_existence_after_full_json_parsing`; Grover contract/search family/`grover_style` are selected. Full JSON parsing stays classical before an index search. The predicate combines valid index, Python truthiness of active and key equality; padding is unmarked. The response proposes coherent field access and reversible equality/truthiness, explicitly charging fresh-batch representation and uncomputation costs. Candidates are verified classically, and parsing exceptions retain their ordering.

The plan requires a complete classical scan before false if no exact absence procedure is supplied. Exact reversible implementation of permitted Python/JSON value semantics is an assumption, not demonstrated. Resource feasibility, field sizes and loading costs remain unknown. The mapping is case-specific but its encoding/semantic obligations are substantial and unresolved.

## Structural-NO controls

[pilot-002](raw/pilot-002.txt) and [pilot-008](raw/pilot-008.txt) retain `plan: null`, structural NO and REMAIN_CLASSICAL. The first describes a sequential digest/callback computation; the second describes full normalization/materialization with independent mutable copies. Both reject the two supported families. They are NOT APPLICABLE under this content rubric, not failed plans. No reference-negative judgment is inferred.

## Limits and next human review

The eight plans expose an interpretable conditional formulation path. They do not resolve exact negative certification (search), global-optimum certification (optimization), concrete resource feasibility, or implementation correctness. All eight resource objects are generic unresolved markers, and Grover scheduling/QAOA depth and optimizer configuration are not complete execution designs. Human researchers should independently review formulas, representations, interface obligations and the SUBSTANTIVE coding before drawing capability conclusions. No further model run or implementation follows from this review.
