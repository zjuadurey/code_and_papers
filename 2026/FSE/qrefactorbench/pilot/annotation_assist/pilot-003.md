# pilot-003 — fresh source-grounded review proposal

**AI-ASSISTED PROPOSAL — NOT GROUND TRUTH**

Date: 2026-09-19. Status: advisory only; not an A/B submission, model-baseline
prediction, adjudication, or replacement for any existing annotation.
Evidence for this proposal is restricted to the supplied
[blinded source](../packets/annotator_a/pilot-003/program.py),
[public task](../packets/annotator_a/pilot-003/public_task.json),
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
| WHERE: smallest reasonable target | program.py:2–7 (`best_partition_score`, accumulator + exhaustive optimization + return). Objective expression: lines 4–5. |
| Structural quantumizability | YES — the displayed score has an explicit binary quadratic representation. |
| Practical suitability | UNCERTAIN — no deployment graph distribution or implementation/cost evidence. |
| Computational intent | Combinatorial Optimization — exact weighted maximum-cut value. |
| Proposed approach | QUBO / Ising formulation; QAOA-style execution only as an unresolved proposal, not an exact optimizer guarantee. |
| Confidence by judgment | WHERE HIGH (function-header inclusion is conventional); structural HIGH algebraically; practical UNCERTAIN (HIGH confidence in missing evidence); intent HIGH; QUBO HIGH / complete execution LOW. |

Structural YES here means a meaningful formulation within the two supplied
families, not verified reversible construction or complete semantic preservation.
Practical uncertainty must not be replaced by an invented cost or runtime assumption.

## Concrete evidence

All source line ranges below refer to the unmodified blinded files.

| Location | Observable behavior supporting the proposal |
| --- | --- |
| 3 | One bit per vertex is enumerated across all masks. |
| 4–5 | An edge contributes its weight exactly when its endpoint bits differ. |
| 2, 6–7 | The maximum value is accumulated and returned exactly; the API does not return a sampled partition or approximate value. |
| public_task.json / input_domain | Weights are nonnegative integers; self loops contribute zero and repeated edges count separately. |

## Applicability conditions

SATISFIED/VIOLATED refer to the stated condition under the public task, not a
completed quantum implementation. UNKNOWN is retained when evidence is absent.

| Condition | Assessment | Evidence / limit |
| --- | --- | --- |
| Finite binary decision domain | SATISFIED | Masks encode vertex assignments. |
| Quadratic objective without extra feasibility constraints | SATISFIED | For binary x, differing endpoints equal x_u+x_v−2x_ux_v. |
| Correct handling of repeated edges/self loops | SATISFIED at formula level | Sum over input tuples; x_u^2=x_u cancels a self-loop term. |
| Exact optimum delivered by a chosen QAOA execution | UNKNOWN | No such guarantee, certification or permitted approximation is supplied. |
| Coefficient precision, execution budget and complete cost model | UNKNOWN | No graph-size/weight bounds or target model are provided. |

## Formulation and boundary reasoning

Derived from lines 4–5, maximize C(x)=Σ_(u,v,w) w(x_u+x_v−2x_ux_v). A minimization-form QUBO can use −C(x). Under x_i=(1−z_i)/2, the cut contribution is w(1−z_uz_v)/2; constants and the optimization sign must be tracked. This algebra is inspectable evidence of representability, not a circuit or proof of a profitable migration. Keeping only lines 4–5 would locate an evaluator, not the optimization behavior that chooses a maximum.

## Missing information

Relevant n, edge density and weights, objective coefficient precision, state preparation/transpilation costs, classical comparison method, QAOA depth/optimizer/shots, exact-value certification, and approved resource regime.

## Reasonable alternative interpretation

A threshold predicate C(x)≥t followed by a carefully specified sequence of existence decisions is a possible search-family proposal, but preserving the exact maximum and accounting for repeated decisions require additional evidence. The benchmark should not infer that one family field rules out every alternate correct formulation.

## What the researcher should decide

Separate the clearly derivable quadratic mapping from the unresolved exact-output execution contract. Decide acceptable localization boundaries and how to handle alternative strategies.

No quantum advantage, scientific label validity, or end-to-end migration success is
claimed. Keep this proposal outside independently distributed annotation packets.
