You are analyzing an existing classical Python program for selective quantumization.
This is a single-response analysis/planning task, not code generation. Do not use
tools, retrieval, execution feedback, repair loops, or an agent workflow.

Analyze only the supplied program, software contract and execution assumptions.
An expensive computational hotspot is not automatically a quantumization opportunity.
Structural quantumizability is different from practical suitability. Data loading,
oracle construction, side effects, output requirements and scale can justify
REMAIN_CLASSICAL even when a structural formulation exists. Abstention is valid.
Unknown evidence should remain null; do not claim speedup or physical feasibility.

Only these migration families are supported:
- unstructured_search: a Grover-style predicate-search proposal;
- combinatorial_optimization: a QUBO/Ising proposal, possibly using QAOA.
Use null if neither applies or the family is unresolved. Do not add families.

T1 WHERE: identify candidate region(s), or [] if there is no supported candidate.
Coordinates refer to the supplied original files, 1-based and inclusive. If an
expensive region is merely a rejected hotspot, explain that distinction.
T2 WHETHER + WHAT: separately assess structural eligibility, practical suitability,
benchmark support, computational intent, family, contract applicability and risks.
T3 HOW: if proposing QUANTUMIZE, supply a structured migration plan. For a
structurally plausible but unsuitable region, you may include a conditional plan
while choosing REMAIN_CLASSICAL. Never weaken the software's exact semantics
without explicitly identifying the unresolved requirement.

The contract catalog is the same for every case. It is a DRAFT menu, not a claim
that any contract applies to this program. Assess applicability independently.
Reference intent IDs are withheld; describe intent in your own words. If you
provide a plan, choose your own descriptive computational_intent_id; this ID will
not be exact-matched to a private answer. Contract IDs come from the public menu.

Return exactly one JSON object, without markdown fences or commentary, with all
of the following fields (schema_version is the prediction format version):

{
  "schema_version": "0.2.0",
  "case_id": "pilot-004",
  "decision": "QUANTUMIZE or REMAIN_CLASSICAL",
  "candidate_regions": [{"file": "program.py", "function": null, "start_line": 1, "end_line": 1}],
  "structural_eligibility": null,
  "practical_suitability": null,
  "benchmark_supported": null,
  "computational_intent": "Your description of the computation and required outputs/effects",
  "migration_family": null,
  "contract_applicability": [{"contract_id": "ID from the shared menu", "applicable": null, "rationale": "Explain conditions and missing evidence"}],
  "assumptions": [],
  "risks": [],
  "rationale": "Explain the decision and uncertainties",
  "plan": null
}

Replace the illustrative decision with exactly one allowed value. Replace the
illustrative span with actual regions or []; do not copy its line numbers.
Each scientific label is true, false or null. computational_intent may be null
if unresolved; otherwise it is a nonempty description. Assess both catalog
contracts, or retain [] if you cannot assess applicability.

For QUANTUMIZE, candidate_regions must be nonempty and plan must be an object:
{
  "schema_version": "0.1.0",
  "contract_id": "grover-predicate-v0 or qubo-ising-v0",
  "computational_intent_id": "your_descriptive_slug",
  "migration_family": "unstructured_search or combinatorial_optimization",
  "formulation": "Concrete predicate or binary objective and required conditions",
  "input_encoding": "Candidate/data representation and how it is prepared",
  "quantum_algorithm_family": "grover_style or qaoa, consistent with selected contract",
  "output_decoding": "How results preserve the classical software contract",
  "assumptions": [],
  "risks": [],
  "expected_resource_characteristics": {"status": "unresolved unless justified"}
}
Top-level migration_family and plan.migration_family must agree when both are
known. Use only the enumerated family/decision strings, not the prose alternatives.
Do not generate code or self-reported correctness scores.

PUBLIC TASK
{
  "case_id": "pilot-004",
  "execution_assumptions": [
    "One invocation per process; at most eight codes already resident in classical memory.",
    "There is no reusable quantum state or oracle; setup and transfer costs count.",
    "No hypothetical larger-domain extrapolation is part of this case."
  ],
  "input_domain": "codes contains at most 8 integers; duplicates and empty input allowed; larger input raises ValueError.",
  "software_contract": "Return whether a target is present among at most eight resident integer codes.",
  "title": "Resident code request"
}


SHARED CANDIDATE CONTRACT MENU
{
  "catalog_version": "phase1-v0",
  "contracts": [
    {
      "algorithm_families": [
        "grover_style"
      ],
      "applicability_conditions": [
        "A finite domain and pure Boolean predicate can be explicitly represented.",
        "Preserve required classical effects and input/output semantics; demonstrate reversible predicate construction."
      ],
      "contract_id": "grover-predicate-v0",
      "formulation": "Grover-style marked-state predicate search; define success/no-solution handling explicitly.",
      "input_encoding": "Finite basis-state encoding of candidates; predicate data and workspace costs must be accounted for.",
      "known_limitations": [
        "Shared candidate contract for planning, not a validated implementation.",
        "No universal suitability or advantage claim; statistical semantics require human review."
      ],
      "output_decoding": "Classically verify decoded candidates; existence decisions also require a justified no-solution policy.",
      "resource_assumptions": [
        "No free data loading, oracle construction, workspace or coherent memory is assumed."
      ],
      "semantic_relation": "Preserve the classical task contract; probabilistic error policy is unresolved, not silently accepted.",
      "status": "DRAFT"
    },
    {
      "algorithm_families": [
        "qaoa"
      ],
      "applicability_conditions": [
        "The binary objective and any constraint penalties can be represented explicitly.",
        "Check coefficients, signs, penalty sufficiency and decoding against the original objective."
      ],
      "contract_id": "qubo-ising-v0",
      "formulation": "QUBO/Ising encoding; QAOA-style execution is a possible proposal, not an exactness guarantee.",
      "input_encoding": "Binary decision variables; document the x=(1-Z)/2 mapping, constants and coefficients if using Ising.",
      "known_limitations": [
        "No depth, parameter-optimization budget, approximation ratio or probability threshold is prescribed.",
        "Shared DRAFT planning contract; conformity and scientific admissibility remain unverified."
      ],
      "output_decoding": "Decode feasible assignments and recompute the classical objective.",
      "resource_assumptions": [
        "State preparation, classical optimization, measurement and decoding overheads must be stated."
      ],
      "semantic_relation": "Preserve the required solution quality and software interface. An exact optimum cannot be silently weakened to an approximate one.",
      "status": "DRAFT"
    }
  ],
  "notice": "Identical menu for all annotators and models. Inclusion is not per-case applicability or an admissibility judgment.",
  "status": "DRAFT"
}


ORIGINAL SOURCE FILES (line labels are not part of the source)
FILE: program.py
   1 | def has_code(codes: list[int], target: int) -> bool:
   2 |     if len(codes) > 8:
   3 |         raise ValueError("at most eight codes")
   4 |     for code in codes:
   5 |         if code == target:
   6 |             return True
   7 |     return False


Whenever structural quantumizability = YES, always provide a
conditional migration plan describing HOW the computation could be
quantumized, even if practical suitability = NO or UNCERTAIN.

The conditional migration plan describes a technically plausible
quantum reformulation under stated assumptions. It does NOT imply a
recommendation to deploy the quantum version.

Therefore:

    Structural = YES
    Practical = NO / UNCERTAIN
    Decision = REMAIN_CLASSICAL

is still compatible with:

    plan != null

Any unresolved semantic, exactness, resource, encoding, oracle,
certification, or feasibility requirement must remain explicitly
identified inside the plan rather than being silently assumed away.
