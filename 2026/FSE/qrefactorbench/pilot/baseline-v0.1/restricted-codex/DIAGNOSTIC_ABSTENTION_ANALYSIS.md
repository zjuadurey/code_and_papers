# Abstention Diagnostic Analysis

Date: 2026-09-20. Retrospective, descriptive diagnosis of the completed Restricted Codex CLI single-turn pilot baseline. No rerun was performed. This document does not establish scientific labels or evaluate agreement with reference annotations.

## 1. Question

Why did the model abstain and emit `plan: null`?

- **H1 — DECISION-COUPLING EFFECT:** the response contains a structural quantum mapping, but a negative or uncertain practical recommendation leads the model to omit a conditional migration plan.
- **H2 — TRUE HOW FAILURE:** the model cannot identify an appropriate quantum formulation despite reporting structural eligibility.

The recorded aggregate observation is ten successful, schema-valid responses, ten `REMAIN_CLASSICAL` decisions and ten null plans; eight structural YES responses; practical suitability eight NO and two UNCERTAIN. These counts describe output behavior, not correctness. Here `true`, `false`, and `null` are rendered as YES, NO, and UNCERTAIN.

Evidence is limited to the completed raw responses, parsed predictions, run metadata, descriptive portions of [BASELINE_RESULTS.md](BASELINE_RESULTS.md) and [FAILURE_NOTES.md](FAILURE_NOTES.md), the [experiment README](README.md), and the frozen prompt/schema audit requested below. Reference comparisons in the reports are not used. No reference case annotations, annotation-assist proposals, or DRAFT-reference evaluation artifact were consulted to judge correctness. “Reasoning” below means the explanation present in the final response, not access to the model's internal reasoning or a proven causal account.

## 2. Selected Cases

Exactly three cases were selected using a transparent post hoc rule: the lowest case ID in each requested prediction stratum. Selection uses model-reported fields, not benchmark labels or whether the narrative supports either hypothesis.

| Case | Selection stratum | Why informative |
|------|-------------------|-----------------|
| pilot-001 | First structural YES with `unstructured_search` | Explicit predicate/domain discussion and reasons for rejecting practical migration. |
| pilot-003 | First structural YES with `combinatorial_optimization` | Explicit binary objective and a distinction between formulation and exact-optimum guarantees. |
| pilot-002 | First structural NO with no selected family and `REMAIN_CLASSICAL` | Explains retention through unsupported structure and observable sequential effects. |

This selection is not preregistered or statistically representative. “Classical-retention case” refers to pilot-002's prediction, not an independently verified negative label. All three selected responses report practical NO; this sample does **not** directly diagnose the two practical-UNCERTAIN responses.

## 3. Case-by-Case Analysis

### pilot-001 — Search prediction

Sources: [raw response](raw/pilot-001.txt), [parsed prediction](parsed/pilot-001.json), [metadata](metadata/pilot-001.json). Relevant response fields: `computational_intent`, the `grover-predicate-v0` entry of `contract_applicability`, `assumptions`, `risks`, and `rationale`.

**A. Structural recognition — CLEAR YES.** The response reports `structural_eligibility: true` and identifies `program.py` lines 1–6 (`satisfies`) plus 9–13 (`has_assignment`). It explains:

> Assignments form a finite basis-state domain and satisfies is a pure Boolean predicate, so the exhaustive loop has a structural Grover-style formulation.

This is evidence of an articulated supported structure, not just an unsupported YES label. Candidate coordinates are reported predictions; their correctness is not assessed here.

**B. Intent recognition — Search.** The model describes deciding whether any of the `2^n` Boolean assignments satisfies all supplied clauses, with an exact Boolean result and explicit empty-input edge cases. It selects `unstructured_search`.

**C. Conditional quantum mapping — EXPLICIT.** It names Grover, marks `grover-predicate-v0` applicable, and discusses a reversible clause predicate, coherent clause encoding, workspace, uncomputation, and classical verification of measured assignments. It also mentions a possible QUBO alternative but leaves that contract's applicability unknown; the primary mapping is not ambiguous in this response.

**D. Reasons for practical rejection.** The response cites classical variable-sized clause data; potentially dominant coherent-representation and reversible-predicate costs; missing resource estimates, implementation, scale distribution, benchmark evidence, and measured end-to-end benefit; unknown solution count for amplification scheduling; and the inability to treat unsuccessful probabilistic search as an exact proof of unsatisfiability. It states that no preloaded quantum memory, fault-tolerant resource budget, or error policy is available. These are the model's stated premises, not independently verified facts. It does **not** say the search-space formula is unknown or that the instance is necessarily small.

**E. Why `plan = null`? — COUPLED_DECISION (inferred, moderate confidence).** Its final rationale directly separates the two judgments:

> That establishes structural eligibility but not practical suitability.

It then concludes that the hotspot is a rejected quantumization candidate rather than sufficient evidence for migration. Together with the explicit mapping, this favors withholding a plan after rejecting adoption over inability to identify a formulation. The optional-plan wording in Section 5 is a plausible contributing interpretation. The response never explicitly says that it set null because of the schema; that stronger causal claim is unsupported.

**F. Counterfactual — LIKELY YES, for a conditional high-level plan.** The response already supplies a candidate domain, predicate, algorithm family, encoding concerns, verification outline, and unresolved semantic/resource requirements. Those ingredients could support the current plan fields with conditions made explicit. It does not demonstrate a concrete reversible oracle or a semantics-preserving exact no-solution procedure. A non-null conditional plan would therefore not by itself demonstrate a complete correct migration.

### pilot-003 — Optimization prediction

Sources: [raw response](raw/pilot-003.txt), [parsed prediction](parsed/pilot-003.json), [metadata](metadata/pilot-003.json). Relevant fields: `computational_intent`, the `qubo-ising-v0` entry of `contract_applicability`, `assumptions`, `risks`, and `rationale`.

**A. Structural recognition — CLEAR YES.** The model reports `structural_eligibility: true` and identifies `program.py` lines 3–6 in `best_partition_score`. It calls the computation a weighted Max-Cut QUBO formulation and marks `qubo-ising-v0` applicable.

**B. Intent recognition — Optimization.** It describes enumeration of binary vertex partitions to return the exact maximum crossing weight, counting repeated edges independently and excluding self-loop contributions. It selects `combinatorial_optimization`.

**C. Conditional quantum mapping — EXPLICIT.** The contract rationale goes beyond naming an algorithm:

> With one binary variable x_u per vertex, the crossing-weight objective is explicitly representable as sum over edges of w_uv*(x_u+x_v-2*x_u*x_v), with repeated edges included separately and self-loop terms cancelling.

It discusses decoded-assignment checking, QAOA sampling, weight precision, interaction-graph routing, parameter optimization, and measurement overhead. This is explicit formulation content outside the null `plan` field. It is not an implemented or validated quantum method.

**D. Reasons for practical rejection.** The response emphasizes exact-optimum semantics: recomputing a sampled partition's score cannot certify global optimality, and it identifies no exactness guarantee for the proposed QAOA execution. It also cites unknown edge-data encoding/hardware costs, coefficient precision, embedding/routing, and unquantified preparation, optimization, measurement, and verification overhead. It states that scale data and quantum benchmark evidence are absent. A classical exact fallback is mentioned as a possible semantics-preserving route with unsupported advantage, not as an implemented solution.

**E. Why `plan = null`? — COUPLED_DECISION (inferred, moderate confidence), with an unresolved semantic gap.** The rationale says:

> They are nevertheless a rejected practical migration target under the supplied assumptions: the interface requires the exact optimum, while the catalog's QAOA-style proposal supplies no exactness or optimality-certificate guarantee.

The mapping is present; the rejection concerns whether adopting the mapped execution preserves the required result and is justified. This supports H1 at the formulation level. However, the response does not supply a complete exact-optimum quantum procedure. That missing step limits claims about full HOW competence; it does not establish that the model was unable to identify a formulation. Optional planning during abstention could also explain omission, but is not explicitly acknowledged by the response.

**F. Counterfactual — LIKELY YES, for a conditional high-level plan.** Binary variables, an explicit objective, an algorithm family, decoding/checking considerations, and resource risks are already articulated. A conditional plan could state the unresolved exactness requirement instead of silently relaxing it. The existing reasoning is insufficient to certify a deployable, exact replacement; emitting a populated plan would not resolve that requirement.

### pilot-002 — Classical-retention prediction

Sources: [raw response](raw/pilot-002.txt), [parsed prediction](parsed/pilot-002.json), [metadata](metadata/pilot-002.json). Relevant fields: `computational_intent`, both `contract_applicability` entries, `risks`, and `rationale`.

**A. Structural recognition — NO.** It reports structural NO, `candidate_regions: []`, and `migration_family: null`. Its explanation is specific:

> Lines 7-9 may be a runtime hotspot for a long event list, but they are a mandatory sequential recurrence with an observable classical side effect after every update, not a supported quantumization candidate.

**B. Intent recognition — Other.** The model describes a rolling SHA-256 digest recurrence with ordered per-event audit callbacks, observable intermediate digests, exception propagation, and an exact final digest.

**C. Conditional quantum mapping — ABSENT.** Grover and QUBO/QAOA appear only in arguments rejecting applicability: no candidate-domain predicate and no optimization objective/decision variables. Mentioning a family to reject it is not a positive conditional mapping.

**D. Reasons for retention.** The response cites dependence on the preceding digest, required callback order and count, exception behavior, exact output, and absence of either supported problem structure. It also cites unquantified quantum preparation/hash-construction overhead without a supported formulation. It does not rest its decision on an identified mapping being too small or too expensive.

**E. Why `plan = null`? — OTHER: no supported mapping claimed.** Its final rationale explicitly states that neither supported family matches the computation. That explains abstention and omission on the response's own terms. H1 and H2, as hypotheses about structurally eligible computations, are not discriminated by this case. No reference judgment about this rejection is made.

**F. Counterfactual — LIKELY NO.** The proposed instruction applies only when the model reports structural YES. This response reports NO and provides no positive mapping; continued null would be consistent with the instruction. This is not evidence of a HOW failure on an eligible case.

## 4. Cross-Case Comparison

| Case | Structural recognized? | Intent | Quantum mapping mentioned? | Practical reason | Why plan=null? | H1/H2 indication |
|------|-------------------------|--------|----------------------------|------------------|----------------|------------------|
| pilot-001 | CLEAR YES | Search | EXPLICIT: domain, predicate, Grover, verification conditions | Encoding/oracle costs and scale evidence unresolved; exact no-solution semantics | COUPLED_DECISION, inferred | Favors H1 at formulation level; complete HOW untested |
| pilot-003 | CLEAR YES | Optimization | EXPLICIT: binary objective, QUBO, QAOA, decoding concerns | Exact-optimum guarantee missing; costs and scale evidence unresolved | COUPLED_DECISION, inferred | Favors H1 at formulation level; exact execution gap remains |
| pilot-002 | NO | Other | ABSENT; family names only rejected | Unsupported structure and observable sequential effects | OTHER: no supported mapping claimed | Neither; classical-retention comparison |

1. **Evidence of practical/planning coupling?** Yes: both structural-YES responses articulate a mapping, reject adoption, and omit the plan. The prompt makes detailed planning mandatory only for QUANTUMIZE. This is compatible with a measurement confound between recommending migration and demonstrating conditional HOW. The data do not establish whether that coupling was unintended by the protocol authors or the model's internal reason for omission.
2. **Evidence of actual HOW incapability?** Not for the narrow ability to identify a formulation in these two responses. Both contain concrete mapping content. Neither demonstrates a complete semantics-preserving quantum replacement; exactness and oracle/certification details remain unresolved. Failure to demonstrate those details under optional planning is not proof of inability to produce them under a different instruction.
3. **Capability, prompt, schema, or combination?** The strongest observable explanation combines recommendation-focused prompt wording, a schema that permits null during abstention, and explicit semantic/resource reservations. The schema does not prohibit conditional plans. Capability limitations may contribute to unresolved execution details but cannot be isolated by `plan=null` alone. Example anchoring and CLI instruction effects remain hypotheses, not observed causes.
4. **Is a conditional-planning rerun justified?** Yes, as a controlled diagnostic of what the current output requirement elicits. It would not retrospectively establish correctness, practical suitability, or general capability. Section 7 specifies a proposal only.

## 5. Prompt / Schema Coupling Evidence

The following wording comes from the actual [frozen pilot-001 prompt](../../packets-v0.1/baseline/prompts/pilot-001.md), not a newly composed prompt. Its SHA-256 matches the recorded `prompt_sha256` and `input_sha256`; the same check passes for the other two selected prompts. The scientific instruction header is shared across cases, apart from the illustrative case ID.

**Recommendation and planning are asymmetrically required.** Lines 7–10 say:

> Structural quantumizability is different from practical suitability. Data loading,
> oracle construction, side effects, output requirements and scale can justify
> REMAIN_CLASSICAL even when a structural formulation exists. Abstention is valid.
> Unknown evidence should remain null; do not claim speedup or physical feasibility.

Lines 22–25 are the most direct evidence:

> T3 HOW: if proposing QUANTUMIZE, supply a structured migration plan. For a
> structurally plausible but unsuitable region, you may include a conditional plan
> while choosing REMAIN_CLASSICAL. Never weaken the software's exact semantics
> without explicitly identifying the unresolved requirement.

Thus planning during abstention is explicitly **allowed but optional**. A null plan is compatible with following this instruction even when the model has formulation knowledge. The exact-semantics caution also provides a reason to distinguish a tentative mapping from a migration recommendation; it does not ban a conditional plan documenting the unresolved requirement.

The illustrative top-level response has `"plan": null` at line 50. Line 59 introduces the populated example with:

> For QUANTUMIZE, candidate_regions must be nonempty and plan must be an object:

These choices may reinforce an abstain/null association, but this experiment cannot establish an example-anchoring effect. Conversely, the prompt explicitly asks for separate scientific assessments and permits a conditional plan, which is evidence **against** claiming that it instructed all abstentions to use null.

**Schema constraints are permissive, not a forced-null rule.** The frozen [Phase-1 schema](../../packets-v0.1/baseline/schemas/phase1_prediction.schema.json), version 0.2.0, has:

- `/required`: includes `plan`, requiring the field to be present, not necessarily non-null.
- `/properties/structural_eligibility` and `/properties/practical_suitability`: `"type": ["boolean", "null"]`.
- `/properties/plan`: a reference to the legacy prediction schema's `/properties/plan`.
- `/allOf/0`: a reference to the legacy prediction schema's `/allOf/0`.

In the frozen [legacy prediction schema](../../packets-v0.1/baseline/schemas/prediction.schema.json), `/properties/plan/anyOf` accepts a migration-plan object or null. `/allOf/0` states, in structural form:

```text
if decision == QUANTUMIZE:
    candidate_regions.minItems = 1
    plan.type = object
    require plan
```

There is no corresponding `else` requiring null for REMAIN_CLASSICAL, and no structural-YES condition requiring a plan. No practical-NO/UNCERTAIN constraint forbids one. Therefore `REMAIN_CLASSICAL` plus a schema-conforming conditional plan is representable without changing the schema.

The frozen [migration-plan schema](../../packets-v0.1/baseline/schemas/migration_plan.schema.json) requires a contract ID, intent ID, family, formulation, encoding, algorithm family, decoding, assumptions, risks, and `expected_resource_characteristics`. The last field is an object without mandatory numeric estimates; the frozen prompt itself illustrates `{"status": "unresolved unless justified"}`. Missing cost numbers do not mechanically force null. Schema conformance nevertheless does not validate scientific adequacy or semantic preservation.

**Execution and collection do not explain away the nulls.** Selected run metadata record `codex-cli 0.154.0`, model argument `gpt-5.6-sol`, reasoning `high`, exit code 0, `parse_status: json_object`, zero retries, and no tool items. The effective server snapshot is not exposed. The fixed CLI wrapper requires one final response without tools or clarification; it adds no rule relating practical suitability to `plan`. There was no `--output-schema` forced decoding. For all three selected cases the raw response and parsed prediction are byte-identical, and their hashes match the existing artifact manifest; null was present in the model's original answer, not introduced by collection or evaluation.

## 6. Diagnostic Conclusion

**Evidence mainly supports H1.** This is a limited descriptive conclusion about the selected responses and the task's elicitation of conditional plans, not a publication-level causal or capability claim.

The two structural-YES responses contain explicit quantum mappings and tie rejection to practical evidence and exact-result requirements. The prompt makes a conditional plan optional after that rejection. Consequently, ten null plans cannot be read directly as ten failures to identify HOW. The schema permits this behavior but does not force it.

The remaining uncertainty matters: neither eligible response demonstrates a complete correct migration, and neither explicitly explains the choice of JSON null. Exact search/optimality guarantees, detailed implementation competence, and the behavior of practical-UNCERTAIN responses remain untested by this three-case diagnosis. Confidence in the proposed mechanism must not be confused with correctness of the model's scientific judgments.

Diagnostic checks: selected raw/parsed/metadata hashes match the existing manifest; raw and parsed bytes match for all three; all three frozen prompt hashes match run metadata. Only this document was added. No baseline invocation, test of a new prediction, scientific scoring, or reference-label comparison was performed. Original experiment artifacts and their historical manifest were retained unchanged.

## 7. Recommended Next Experiment

**Proposed only — do not execute without a later explicit request.** Use the same ten frozen cases, model argument `gpt-5.6-sol`, reasoning level `high`, isolation, fresh single-turn/single-shot invocations, fixed CLI wrapper, no tools or feedback, and no repair/retry based on answer quality. Preserve the original experiment and every new first-attempt output separately. Keep the CLI version/configuration constant where technically available; the unexposed server snapshot and unspecified sampling seed limit exact reproducibility.

Make only one controlled instruction addition to a separately versioned copy of each frozen prompt:

> Whenever structural quantumizability = YES, always provide a conditional migration plan describing HOW the computation could be quantumized, even if practical suitability = NO or UNCERTAIN. The conditional plan does not imply a recommendation to deploy the quantum version.

This addition makes the previously optional conditional plan mandatory when the response reports structural YES. It does not change the schema, evaluation semantics, adoption decision, or requirement to expose unresolved semantic conditions. Do not supply previous responses, this diagnosis, or reference annotations as model input. Include the structural-NO cases as controls rather than selecting only cases that previously suggested a mapping.

Compare plan presence and structured content separately from the decision and practical-suitability fields. A substantive conditional formulation alongside continued abstention would support H1; merely filling fields would not demonstrate HOW quality. Continued null could indicate instruction-following or interpretation problems and would not, by itself, prove H2. An attempted plan with unresolved or missing formulation logic would require human review before attributing a capability failure. Preserve semantic gaps as gaps; do not require invented exactness or resource evidence to obtain a non-null plan.

The paired diagnostic would test sensitivity to this instruction, not establish statistical significance or general ability from ten synthetic cases. No rerun, prompt edit, schema change, label change, or system design is part of the present task.
