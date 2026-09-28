Analyze the supplied existing classical Python software for selective quantumization.
Use only the supplied material. Return one response; do not use tools, execute code,
browse, retrieve other material, or request feedback. Do not generate a patch.

Identify candidate region(s) for further analysis, or [] if none is justified.
Coordinates are 1-based, inclusive, in the supplied source files. A nomination may
subsequently be rejected: it is not a recommendation to deploy. Explain the source
evidence, required input/predicate/state dependencies, activation conditions, and
surrounding behavior that must remain intact in rationale. Multiple defensible
regions are possible; a supplied location cue is a starting point, not an exhaustive
answer or proof of eligibility. Do not infer that every input has a suitable candidate.

Assess structural eligibility, practical suitability and benchmark support separately.
An expensive hotspot is not automatically a quantumization opportunity. Supported
families are only unstructured_search (Grover-style) and combinatorial_optimization
(QUBO/Ising, potentially QAOA). Unknown evidence stays null. REMAIN_CLASSICAL is valid.
Do not assume quantum advantage or relax exactness, exceptions, ordering or effects.

Whenever structural_eligibility is true, provide a conditional migration plan even
if practical suitability is false/null or decision is REMAIN_CLASSICAL. State the
formulation and unresolved encoding, oracle, exactness, feasibility and resource
obligations. A conditional plan does not recommend adoption or certify correctness.

Return exactly one JSON object conforming to the supplied phase1_prediction schema
(schema_version 0.2.0); use the public_task case_id. Use true/false/null for labels,
the existing candidate_regions field for spans and rationale for boundary/dependency
evidence. Do not invent extra fields or private intent identifiers. Use your own
descriptive computational intent. The shared contract menu is DRAFT: independently
assess applicability, rather than treating inclusion as approval. No human review
judgments or correctness scores are requested from you.
