# Context-008: complete normalized exports

**DRAFT / AI-ASSISTED PROPOSAL — NOT GROUND TRUTH.**

Functional need: produce a fully materialized, labelled table for independent
downstream consumers. Rows are normalized by absolute-value sum, repeated, labelled
and summarized. Consumers may mutate their copies. See [request](example_request.json),
[report](example_report.json), [program](program.py) and [contract](public_task.json).

Example: three source rows and two copies give six rows. Signed [2,-2] becomes
[0.5,-0.5], while [0,0] remains zero. Source order and copy indices align with data;
all-zero IDs refer to source rows even if copies=0. Column totals use emitted order.
Aliasing copies produces exactly the same initial JSON values but breaks later
mutation behavior. Both value and object-identity checks are necessary.

Core `materialize` is verbatim synthetic pilot-008, whose valid domain also permits
ragged rows. The context's labelled table requires a fixed width. Independent
fraction-based [tests](test_program.py) cover 321 bounded table/copy combinations,
all-zero/empty/huge signed inputs, late malformed data even at copies=0, wrong value
and label substitutes, nonmutation and mutable aliasing.

Private design intention is a retention control: materializing all records and
preserving their identities cannot be replaced by reporting a sampled or aggregate
quantity. This does **not** prove universal quantum inapplicability. WHERE may
still nominate the loop and WHETHER reject a proposed mapping. No structural or
practical label is assigned. Missing workload scale is not evidence for a new
supported formulation. No encoding, hardware or advantage measurements are given.

Researcher decisions: is a complete editable export a useful contrasting workload?
Are Python alias semantics a relevant part of this interface? Should the control
be described as no supported candidate or candidate-but-reject under the future
WHERE policy? Do not settle that scoring question merely to label this example.
