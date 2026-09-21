# Independent annotation packet

You receive only this packet: neutral software facts, source files, a shared DRAFT
contract menu and blank forms. Do not inspect the repository, case manifests,
curator category list, reference plans, other annotators' forms or baseline outputs
before submitting your independent annotations. The coordinator must distribute
only your role's directory, not the common parent containing other roles.

For each case, inspect the unmodified source and public_task.json. Complete
annotation.json independently, using your real researcher ID only when submitting.
The supplied roles A/B are empty workflow slots, not claims of completed review.

- candidate_regions: null means unfilled/unresolved; [] means an explicit judgment
  of no candidate. Otherwise give file, inclusive 1-based start/end and optional
  function. Distinguish supported candidates from rejected computational hotspots
  in uncertainty/rationale. Do not assume every expensive loop is a candidate.
- structural_eligibility: true/false/null, with supporting reasoning.
- practical_suitability: true/false/null under the explicit workload and data assumptions.
- benchmark_supported: true/false/null; presence in the shared menu is not support evidence.
- computational_intent: your description (or {id, description} if you propose an ID).
- migration_family: unstructured_search, combinatorial_optimization, or null.
- contract_applicability: consider each shared contract; record ID, applicable
  true/false/null, conditions and rationale. Other scientific alternatives can be
  noted as out-of-scope questions; do not expand the benchmark's family list.
- expected_decision: QUANTUMIZE, REMAIN_CLASSICAL, or null when unresolved.
- assumptions: identify which provided facts matter and which additional assumptions
  a migration would need. Do not replace provided workload facts silently.
- semantic_oracle: propose observable correctness criteria, including exactness,
  inputs, effects, exceptions and output quality. No statistical threshold is prescribed.
- uncertainty and annotation_rationale: record evidence, doubts and alternatives.

All forms remain annotation_status=DRAFT. completion_status=SUBMITTED records that
you finished your independent pass, not scientific review or adjudication. Keep
unknown judgments null and explain them. Do not copy the example spans in the LLM
prompt; human packets contain no model predictions or reference answers.

The catalog describes possible strategies, not established applicability. A
structural formulation need not be practical, and executable code would not prove
semantics. You may abstain. Do not infer ground truth from presumed case counts.

Return the complete directory or the original-named annotation files to the
coordinator. The coordinator preserves both submissions and compares them only
after both independent passes are complete. No automatic adjudication occurs.
