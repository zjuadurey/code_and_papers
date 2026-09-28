# pilot-005 — fresh source-grounded review proposal

**AI-ASSISTED PROPOSAL — NOT GROUND TRUTH**

Date: 2026-09-19. Status: advisory only; not an A/B submission, model-baseline
prediction, adjudication, or replacement for any existing annotation.
Evidence for this proposal is restricted to the supplied
[blinded source](../packets/annotator_a/pilot-005/program.py),
[public task](../packets/annotator_a/pilot-005/public_task.json) and [helper source](../packets/annotator_a/pilot-005/support.py),
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
| WHERE: smallest reasonable target | program.py:5–12 in `feasible_bundle`. Context dependencies that should remain classical: program.py:16–18 and support.py:1–3. |
| Structural quantumizability | YES — finite subset feasibility is an explicit pure predicate after preprocessing. |
| Practical suitability | UNCERTAIN — preprocessing, encoding, data scale and reuse costs are unsettled. |
| Computational intent | Unstructured / Predicate Search as the direct intent; a Combinatorial Optimization reformulation is also plausible and should be reviewed. |
| Proposed approach | Grover-style feasibility search, conditionally; QUBO/Ising is an alternative requiring a separately reviewed contract. |
| Confidence by judgment | WHERE MEDIUM; structural HIGH at formulation level; practical UNCERTAIN (HIGH confidence in missing evidence); intent MEDIUM because formulations differ; approach MEDIUM. |

Structural YES here means a meaningful formulation within the two supplied
families, not verified reversible construction or complete semantic preservation.
Practical uncertainty must not be replaced by an invented cost or runtime assumption.

## Concrete evidence

All source line ranges below refer to the unmodified blinded files.

| Location | Observable behavior supporting the proposal |
| --- | --- |
| program.py:5–9 | Each mask selects offers and produces total units and price. |
| program.py:10–12 | The result is existence of exact-target units at price≤budget, not the minimum price or a chosen subset. |
| program.py:16–18 | The wrapper preserves the count of eligible offers and the original target in its response. |
| support.py:2–3 | Unavailable offers are filtered; dictionaries are copied and sorted by sku without mutating the input list. |

## Applicability conditions

SATISFIED/VIOLATED refer to the stated condition under the public task, not a
completed quantum implementation. UNKNOWN is retained when evidence is absent.

| Condition | Assessment | Evidence / limit |
| --- | --- | --- |
| Finite Boolean selection variables | SATISFIED | One selection bit per prepared offer. |
| Pure arithmetic/equality/inequality predicate inside the target | SATISFIED on the stated domain | The loop only reads offers/target/budget. |
| Preservation of filtering, ordering, nonmutation and response fields | SATISFIED as visible obligations | Their behavior is explicit; a migration must retain it. |
| Reversible sums/comparisons with bounded registers and cost | UNKNOWN | Integer widths and a construction are absent. |
| Direct claim that an arbitrary penalty/QAOA approximation preserves feasibility | UNKNOWN | No penalty encoding or exact decision/certification protocol is supplied. |
| End-to-end practical cost including preprocessing | UNKNOWN | Neither offer distribution nor cost/reuse budget is supplied. |

## Formulation and boundary reasoning

The direct predicate is P(x)=[Σu_ix_i=target] ∧ [Σp_ix_i≤budget]. A possible alternative introduces a nonnegative integer slack s and energy E=(Σu_ix_i−target)^2+(Σp_ix_i+s−budget)^2. With an adequate finite binary slack encoding, a zero energy corresponds to feasibility on the nonnegative input domain. This is an algebraic proposal only: encoding, bit ranges, exact zero detection and a supported solver remain human review items. Choosing a sampled low-energy state is not sufficient to conclude infeasibility.

## Missing information

Offer counts/distributions and price/unit widths, comparable sku types for sorting, permitted behavior outside the stated domain, reversible arithmetic/data loading, classical alternatives, repeated use, and probabilistic or exact decision policy.

## Reasonable alternative interpretation

The same Boolean intent can be implemented by search or by deciding whether a constructed objective has zero minimum. A family mismatch alone may reject a valid alternative. Marking the whole wrapper would also be defensible under an interface-level rubric, but it would hide localization of the expensive enumeration.

## What the researcher should decide

Decide whether the admissible set can contain strategies from both current families, how feasibility differs from optimization intent, and whether WHERE includes preprocessing/interface dependencies.

No quantum advantage, scientific label validity, or end-to-end migration success is
claimed. Keep this proposal outside independently distributed annotation packets.
