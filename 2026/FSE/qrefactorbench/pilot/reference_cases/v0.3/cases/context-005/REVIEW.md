# Context-005: indivisible capacity requests

**DRAFT / AI-ASSISTED PROPOSAL — NOT GROUND TRUTH.**

Functional need: a planner checks alternative capacity requests against a snapshot
of indivisible lots. Eligibility depends on site and reservation state. Requests
are independent what-if questions, not simultaneous allocations. See the concrete
[request](example_request.json), [report](example_report.json), [program](program.py)
and [public contract](public_task.json).

Example: eligible west lots have capacities 4 and 6. Two independent requests for
6 both succeed; a request for 5 fails despite total capacity 10. A held west lot of
5 and available east lot of 5 cannot change that answer. Empty demand succeeds.
Removing filtering, using a total-capacity shortcut, or consuming stock between
requests changes observable decisions. Reports expose inventory count, eligibility,
available capacity and request-order IDs; no irrelevant context is added.

Core `has_total` is verbatim synthetic pilot-007; it supports signed integers too.
The context uses positive lot sizes and nonnegative demand for its functional need.
[Tests](test_program.py) independently enumerate subsets of the raw eligible lot
records for 259 bounded inventories, all listed target/site queries, and check
nonmutation, large exact integers, malformed later records and bad substitutes.

Conditional research direction, not an assigned label: finite subset choices and
an exact integer-sum predicate may support the current search family. A concrete
reversible arithmetic oracle, index/data encoding, workspace/uncomputation, unknown
number of witnesses and certified false result remain obligations. The boolean
API does not require a witness but still requires **exact absence**, which a failed
sample does not certify. Dynamic programming and meet-in-the-middle are relevant
classical alternatives; exhaustive source code does not establish a benefit.

Researcher decisions: is independent capacity feasibility a useful task? Are positive
indivisible lots/site/hold rules natural enough? Should another future case request
an actual allocation (a changed contract)? Missing scale, numeric-bit-width distribution,
preparation cost and hardware prevent a practical-suitability conclusion. No fixed
uncertainty, family or eligibility label is supplied.
