# pilot-009 — fresh source-grounded review proposal

**AI-ASSISTED PROPOSAL — NOT GROUND TRUTH**

Date: 2026-09-19. Status: advisory only; not an A/B submission, model-baseline
prediction, adjudication, or replacement for any existing annotation.
Evidence for this proposal is restricted to the supplied
[blinded source](../packets/annotator_a/pilot-009/program.py),
[public task](../packets/annotator_a/pilot-009/public_task.json) and [helper source](../packets/annotator_a/pilot-009/support.py),
and the [shared DRAFT contract menu](../packets/annotator_a/contracts.json).

**Independence limitation:** this assistant participated in earlier preparation and
the conversation retains that context; required startup governance documents also
summarize prior project state. This is a fresh source-based rationale, not a
demonstrably independent blind annotation. No case.json, curator notes, seed
manifest, or reference plan was consulted to generate this proposal. Confidence
below is an uncalibrated judgment about the reasoning, never correctness evidence.

## Judgments

| Dimension | Proposal |
| --- | --- |
| WHERE: smallest reasonable target | program.py:5–12 in `best_cost`. Keep `placement_report` (15–18) and support.py:1–6 classically; objective terms are program.py:7–10. |
| Structural quantumizability | YES — costs and same-side penalties yield a binary quadratic objective. |
| Practical suitability | UNCERTAIN — no size/cost/precision/implementation profile or exact-solver evidence. |
| Computational intent | Combinatorial Optimization — exact minimum cost of assigning every job to one of two placements. |
| Proposed approach | QUBO / Ising formulation; QAOA-style execution conditional on resolving exact outputs and resource assumptions. |
| Confidence by judgment | WHERE MEDIUM (kernel versus wrapper dependency rubric); structural HIGH algebraically; practical UNCERTAIN (HIGH confidence in missing evidence); intent HIGH; encoding HIGH / execution LOW. |

Structural YES here means a meaningful formulation within the two supplied
families, not verified reversible construction or complete semantic preservation.
Practical uncertainty must not be replaced by an invented cost or runtime assumption.

## Concrete evidence

All source line ranges below refer to the unmodified blinded files.

| Location | Observable behavior supporting the proposal |
| --- | --- |
| 6–8 | Each mask chooses either right_cost or left_cost for every job; no job is optional. |
| 9–10 | Each listed link adds a nonnegative penalty when the endpoint bits are equal. |
| 11–12 | The exact minimum is returned. |
| 15–18; support.py:2–6 | Validation runs before optimization; names/count are preserved and specified invalid inputs raise ValueError. |

## Applicability conditions

SATISFIED/VIOLATED refer to the stated condition under the public task, not a
completed quantum implementation. UNKNOWN is retained when evidence is absent.

| Condition | Assessment | Evidence / limit |
| --- | --- | --- |
| Complete binary assignment represents all source choices | SATISFIED | One bit per job; either placement is always chosen. |
| Quadratic representation of stated costs | SATISFIED | Equality of bits equals 1−x_a−x_b+2x_ax_b. |
| Treat every link as a hard constraint forbidding same-side placement | VIOLATED | The source permits it and merely adds its numeric penalty. |
| Preserve validation, name order and output metadata | SATISFIED as required obligation | The wrapper/helper make these behaviors explicit. |
| Exact optimum from QAOA-style execution | UNKNOWN | No permitted relaxation or certification method. |
| Job/link scale, coefficient precision and complete resource feasibility | UNKNOWN | No approved deployment/cost profile. |

## Formulation and boundary reasoning

Let x_i=1 mean right placement. The objective is E=Σ[L_i+(R_i−L_i)x_i]+Σ_(a,b,p)p(1−x_a−x_b+2x_ax_b). Every tuple contributes once; a self-link contributes the constant p, so dropping constants changes the returned cost. The word penalty here denotes an actual software cost, not an arbitrary enforcement multiplier. Raising penalties to prohibit same-side placement would alter the task. The public domain calls name an integer field while the source validator requires str; that input-domain inconsistency must be reviewed rather than silently normalized.

## Missing information

Job/link distributions, coefficient widths, desired cost/runtime objective, exactness/measurement policy and execution budgets. Also clarify the public_task wording 'name,left_cost,right_cost integer fields' against the explicit string-name check; determine whether invalid-domain behavior is graded.

## Reasonable alternative interpretation

A threshold-cost predicate could support a conditional search reformulation with additional exact-value recovery logic. Encoding the supplied same-side penalties as hard constraints is not a semantics-preserving alternative unless researchers explicitly change the task.

## What the researcher should decide

Resolve the public input-type contradiction, verify soft-cost rather than hard-constraint interpretation, and keep exact minimum plus validation/report obligations in any admissible execution contract.

No quantum advantage, scientific label validity, or end-to-end migration success is
claimed. Keep this proposal outside independently distributed annotation packets.
