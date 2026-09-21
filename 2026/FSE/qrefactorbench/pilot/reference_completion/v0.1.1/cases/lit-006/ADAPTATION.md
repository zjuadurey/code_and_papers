# lit-006 — QuanBench task 05 → independent transfer windows

**PRIVATE · DRAFT / AI-ASSISTED PROPOSAL — NOT GROUND TRUTH.**

[Source task](../../../v0.1/sources/quanbench.jsonl) `05` specifies values `[3,3,1,1,5]`,
weights `[2,4,1,3,5]`, capacity `7`; MIT attribution and pinned bytes retained.
It asks for a QAOA circuit and contains a classical DP helper inside the canonical
solution. We **newly implement** a capacity-table classical solver and functional
window-review API; we do not claim this application is imported upstream code.

Important source inconsistency retained: its test expects a four-character outcome
`1001` despite five item variables, and the canonical top-level function has no return.
We do not adopt that bitstring as an answer or repair the archived source. Exhaustive
classical subsets for the stated numeric problem give value **8**, items **0 and 4**,
weight **7**, mask **17**. This is arithmetic evidence, not quantum reference validation.

New requirements: active filtering, independent windows, current report even if
infeasible, inspect/select branches, numeric-mask tie and ordered transfer offsets.
These are documented synthetic requirements. In particular, one window does not
consume stock needed by another; no general scheduling/resource-allocation claim.

WHERE is the capacity update in `kernel.choose`, supported by previous-row state,
item eligibility/order and capacities. The descriptor also sums weights/values but
has a reporting role, not selection. Selecting all items may improve raw value while
violating capacity; returning correct IDs with wrong offsets still breaks the API.
The DP is an efficient classical baseline for some inputs; no advantage assumption
is smuggled in from the QAOA source label.

[Tests](test_program.py): exact enumeration across 259 ordered item lists and five
capacities (1,295 kernel inputs), original numeric instance, ties, zero values,
inactive/current reporting, invalid late request and wrong-solver counterexample.
The maximum three-item bounded list checks are validation inputs, not benchmark cases.
QUBO/slack/penalty admissibility, exactness, resources and alternative boundaries await
review. Similarity to the older synthetic archive case is recorded, not independent
algorithmic diversity. All scientific judgments remain null/DRAFT.
