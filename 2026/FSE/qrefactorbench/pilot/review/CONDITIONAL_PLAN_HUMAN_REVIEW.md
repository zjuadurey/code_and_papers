# Conditional-plan diagnostic — human review record

**COORDINATOR ONLY — contains links to model outputs. NOT GROUND TRUTH.**

Prepared by Codex on 2026-09-20 for N-001. All human fields are intentionally blank;
no human review, agreement, adjudication or protocol adoption is recorded here.
Do not give this record to blind A/B annotators or prediction processes. This is
an output-aware coordinator review, not independent benchmark annotation.

## How to use this record

Review the frozen input/specification and the original/diagnostic responses linked
below. Inspect the diagnostic response's `plan`, with its top-level judgments kept
separate. Fill reviewer identity, actual review date, free-text judgment and concrete
evidence references for each reviewed case. A blank means unreviewed, not agreement,
incorrectness or a scientific UNCERTAIN label. Leave unknowns explicit in your notes.

Distinguish formulation content, technical correctness, unresolved semantic/resource
obligations, and deployment recommendation. A plan can be detailed while those
obligations remain open. The prompts/results are frozen; record concerns here rather
than editing an answer or case. Preserve this blank original and save completed
copies separately with actual reviewer/date identifiers; do not overwrite earlier
submissions or merge disagreements automatically. This Markdown is a review record,
not a case/prediction schema object and not input to the evaluator.

Existing analyses are available without being copied into the human judgment cells:
[AI-assisted content review](../baseline-v0.1/conditional-plan-diagnostic/PLAN_CONTENT_REVIEW.md)
and [paired results](../baseline-v0.1/conditional-plan-diagnostic/CONDITIONAL_PLAN_DIAGNOSTIC_RESULTS.md).
Their classifications are proposals, not prescribed answers. No new rubric or score
is introduced. If needed, record detailed observations separately using the existing
[observation template](../failure_analysis/observation_template.json); do not infer
reference correctness or finalize a failure taxonomy before independent annotation.

## Case review

The questions below are taken from the existing review/results, not new findings.
“Control” refers only to the diagnostic model's structural-NO/null-plan responses;
it is not a researcher-assigned negative label. Rows 001/003/004/005/006/007/009/010
link the eight non-null plans; rows 002/008 link the two controls. Evidence entries
should identify source lines or JSON fields and explain which claim they support.

| Case | Frozen input and responses | Previously recorded question to examine | Reviewer | Review date | Human judgment | Evidence / unresolved notes |
|---|---|---|---|---|---|---|
| pilot-001 | [Input](../packets-v0.1/baseline/prompts/pilot-001.md) · [Original](../baseline-v0.1/restricted-codex/raw/pilot-001.txt) · [Diagnostic](../baseline-v0.1/conditional-plan-diagnostic/raw/pilot-001.txt) | What remains open for exact absence certification and reversible clause-oracle cost? | | | | |
| pilot-002 | [Input](../packets-v0.1/baseline/prompts/pilot-002.md) · [Original](../baseline-v0.1/restricted-codex/raw/pilot-002.txt) · [Diagnostic](../baseline-v0.1/conditional-plan-diagnostic/raw/pilot-002.txt) | Control: how does the sequential digest/ordered callback rationale support retaining a null plan? | | | | |
| pilot-003 | [Input](../packets-v0.1/baseline/prompts/pilot-003.md) · [Original](../baseline-v0.1/restricted-codex/raw/pilot-003.txt) · [Diagnostic](../baseline-v0.1/conditional-plan-diagnostic/raw/pilot-003.txt) | What separates the stated objective mapping from an exact global-maximum certificate, including coefficient/routing costs? | | | | |
| pilot-004 | [Input](../packets-v0.1/baseline/prompts/pilot-004.md) · [Original](../baseline-v0.1/restricted-codex/raw/pilot-004.txt) · [Diagnostic](../baseline-v0.1/conditional-plan-diagnostic/raw/pilot-004.txt) | How are exact absence and encoding/fallback overhead handled for the at-most-eight domain? | | | | |
| pilot-005 | [Input](../packets-v0.1/baseline/prompts/pilot-005.md) · [Original](../baseline-v0.1/restricted-codex/raw/pilot-005.txt) · [Diagnostic](../baseline-v0.1/conditional-plan-diagnostic/raw/pilot-005.txt) | What remains open for an exact negative result, reversible arithmetic and unknown input scale? | | | | |
| pilot-006 | [Input](../packets-v0.1/baseline/prompts/pilot-006.md) · [Original](../baseline-v0.1/restricted-codex/raw/pilot-006.txt) · [Diagnostic](../baseline-v0.1/conditional-plan-diagnostic/raw/pilot-006.txt) | What remains open for an exact global-minimum certificate and signed-coefficient fidelity? | | | | |
| pilot-007 | [Input](../packets-v0.1/baseline/prompts/pilot-007.md) · [Original](../baseline-v0.1/restricted-codex/raw/pilot-007.txt) · [Diagnostic](../baseline-v0.1/conditional-plan-diagnostic/raw/pilot-007.txt) | Are signed-accumulator, magnitude/loading and exact-absence obligations explicitly retained? | | | | |
| pilot-008 | [Input](../packets-v0.1/baseline/prompts/pilot-008.md) · [Original](../baseline-v0.1/restricted-codex/raw/pilot-008.txt) · [Diagnostic](../baseline-v0.1/conditional-plan-diagnostic/raw/pilot-008.txt) | Control: how do full materialization and independent mutable copies support the null-plan rationale? | | | | |
| pilot-009 | [Input](../packets-v0.1/baseline/prompts/pilot-009.md) · [Original](../baseline-v0.1/restricted-codex/raw/pilot-009.txt) · [Diagnostic](../baseline-v0.1/conditional-plan-diagnostic/raw/pilot-009.txt) | What remains open for exact optimality, constant offsets and coefficient precision while preserving the report? | | | | |
| pilot-010 | [Input](../packets-v0.1/baseline/prompts/pilot-010.md) · [Original](../baseline-v0.1/restricted-codex/raw/pilot-010.txt) · [Diagnostic](../baseline-v0.1/conditional-plan-diagnostic/raw/pilot-010.txt) | What remains open for exact Python predicate semantics, fresh-batch loading and absence fallback? | | | | |

## Cross-case human review and Q19

Use this section only after recording what was actually reviewed. The existing
results identify generic unresolved resource objects, exactness/certification gaps,
and changes in support/applicability/localization despite stable main judgments.
Reference those observations where relevant; do not assume they settle correctness.
The proposed policy question is whether a **future** protocol should require
conditional plans for structural YES independently of practical adoption. A comment
here does not automatically approve that policy, modify a label, or authorize a run.

| Human-completed field | Entry |
|---|---|
| Reviewer(s) and actual review date(s) | |
| Cases/fields actually reviewed; exclusions or expertise limits | |
| Assessment of formulation content versus technical correctness | |
| Remaining semantic/exactness/oracle/certification obligations | |
| Remaining encoding/resource/feasibility obligations | |
| Interpretation of changed support/applicability/candidate judgments | |
| Evidence references, disagreements and alternative interpretations | |
| Q19 recommendation and rationale; unresolved evidence needed | |
| Explicit coordinator decision, decision date and ledger ID, if later supplied | |

No scientific decision is preselected. Preserve uncertainty. Return the completed
record to the coordinator; keep independent benchmark annotations separate. Further
protocol adoption requires an explicit recorded human decision; original experiment
artifacts and DRAFT labels remain unchanged. [Current queue](../../NEXT_ACTIONS.md).
