# pilot-007 — fresh source-grounded review proposal

**AI-ASSISTED PROPOSAL — NOT GROUND TRUTH**

Date: 2026-09-19. Status: advisory only; not an A/B submission, model-baseline
prediction, adjudication, or replacement for any existing annotation.
Evidence for this proposal is restricted to the supplied
[blinded source](../packets/annotator_a/pilot-007/program.py),
[public task](../packets/annotator_a/pilot-007/public_task.json),
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
| WHERE: smallest reasonable target | program.py:2–7 in `has_total`; lines 3–5 define the subset predicate. |
| Structural quantumizability | YES — finite subset predicate, with explicit signed integer semantics. |
| Practical suitability | UNCERTAIN — input sizes/widths and complete arithmetic/oracle costs are unknown. |
| Computational intent | Unstructured / Predicate Search as the software intent: existence of a target-sum subset. Optimization is an alternative formulation, not the returned quantity. |
| Proposed approach | Grover-style search conditionally; a squared-residual QUBO is also a reviewable alternative. |
| Confidence by judgment | WHERE HIGH; structural HIGH at formulation level; practical UNCERTAIN (HIGH confidence in missing evidence); intent HIGH / uniqueness of family LOW; approach MEDIUM. |

Structural YES here means a meaningful formulation within the two supplied
families, not verified reversible construction or complete semantic preservation.
Practical uncertainty must not be replaced by an invented cost or runtime assumption.

## Concrete evidence

All source line ranges below refer to the unmodified blinded files.

| Location | Observable behavior supporting the proposal |
| --- | --- |
| 2–4 | All masks over list positions are enumerated and selected integer values summed. |
| 5–7 | Equality to target returns True; exhaustion returns False. |
| public_task.json / input_domain | Negative values, duplicates and the empty subset are allowed; positional duplicates cannot be collapsed indiscriminately. |

## Applicability conditions

SATISFIED/VIOLATED refer to the stated condition under the public task, not a
completed quantum implementation. UNKNOWN is retained when evidence is absent.

| Condition | Assessment | Evidence / limit |
| --- | --- | --- |
| Finite candidate domain and pure predicate | SATISFIED | One bit per list position; equality to a sum is explicit. |
| Representability by a binary quadratic residual | SATISFIED algebraically | (Σv_ix_i−t)² has degree two after x_i²=x_i. |
| Unsigned-only arithmetic or removal of duplicate entries preserves all inputs | VIOLATED | Negative values and repeated equal entries are part of the domain. |
| Signed reversible sum width, overflow policy and cleanup | UNKNOWN | No bounded implementation is supplied. |
| Exact no-solution or zero-minimum decision under quantum output | UNKNOWN | The source is exact, while no probabilistic policy is given. |
| Practical comparison against suitable classical alternatives | UNKNOWN | No value-width/target/size distributions or cost model. |

## Formulation and boundary reasoning

For the alternative energy, expand E=t²+Σ(v_i²−2tv_i)x_i+2Σ_(i<j)v_iv_jx_ix_j. E=0 exactly when some subset reaches the target. This follows from the code's equality check and does not by itself supply an exact optimizing quantum implementation. For a finite instance a signed sum range can be derived from the input values; that does not authorize assuming one fixed small-width quantum register across all Python integers.

## Missing information

Number and widths/distribution of values, target distribution, exact arithmetic encoding, oracle cost, success/no-solution handling, execution budgets and classical reference methods.

## Reasonable alternative interpretation

Search and quadratic minimization can both address the same Boolean result. The program does not itself ask for an optimum, so intent classification and permitted migration family should not be treated as identical labels. A special target=0 instance returns True through the empty subset immediately; workload distribution affects suitability.

## What the researcher should decide

Decide whether both supported families can be admissible for one intent, how signed arithmetic is specified, and whether an exact Boolean no-instance can be validated under the eventual execution contract.

No quantum advantage, scientific label validity, or end-to-end migration success is
claimed. Keep this proposal outside independently distributed annotation packets.
