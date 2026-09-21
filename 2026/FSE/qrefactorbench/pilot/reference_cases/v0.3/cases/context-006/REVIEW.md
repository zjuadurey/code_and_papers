# Context-006: optional component charges

**DRAFT / AI-ASSISTED PROPOSAL — NOT GROUND TRUTH.**

Functional need: explain the current bill and compare it with the attainable charge
floor under a catalogue of optional components, individual charges/credits and
pair adjustments. This is an **assessment**, not advice to remove needed features:
the contract permits all combinations and explicitly has no requirement to retain
functionality. Whether that simplification is useful is a human review issue.
See [request](example_request.json), [report](example_report.json), [program](program.py)
and [contract](public_task.json).

Example current charge is 103, while the attainable floor is 97 and the gap is 6.
The current component list is canonicalized to catalogue order. Two reversed
cache/telemetry adjustments are separate credits, so deduplication is wrong.
Removing base charge, adjusting when only one member is present, dropping duplicate
entries or sorting away adjustment indices changes required report fields.

Core `minimum_energy` is verbatim synthetic pilot-006. The named input compiles to
its coefficients; the context adds a constant and disallows self-pairs. The public
core still permits self-couplings. Independent named-subset [tests](test_program.py)
cover 231 bounded catalogues / 1,781 current-selection comparisons, signed and huge
integer charges, duplicate/reversed adjustments, input errors and missing-coupling
substitutes. Only a numeric minimum is required, so no hidden witness/tie demand exists.

Conditional research direction: the binary choice charge is already quadratic, so
the existing optimization family is a plausible analysis target. An explicit
coefficient correspondence and preserved constant are required; naming a family
alone is insufficient. Approximate low-energy samples do not certify the exact
minimum charge. Encoding range/precision, quantum resources, optimizer behavior
and an exactness strategy remain unresolved. No label or benefit is inferred.

Researcher decisions: keep the simplified charge-floor assessment, or require a
future separately versioned functional constraint? Is this sufficiently distinct
from MaxCut despite related quadratic algebra? It is not independent literature
provenance, and its direct formula may make HOW easy. No WHERE difficulty, practical
adoption or real application claim has been measured.
