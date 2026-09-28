# lit-003: agenda inspection and completion

**DRAFT / AI-ASSISTED PROPOSAL — NOT GROUND TRUTH.**

Source: C2|Q> pinned records **97 and 98**, preserved in
[original preview](../../sources/row-97.decoded.py) and
[original completion](../../sources/row-98.decoded.py). See [source audit](../../SOURCES.md).
The application requirements are new synthetic requirements; no real calendar
product, deployed repository or original-author application claim is made.

The user's functional task is to inspect an agenda or complete it while retaining
an already feasible arrangement. Shared participants create conflicting pairs;
slot labels and session identities must survive decoding. Partial current assignments
are not mandatory constraints on a new proposal. No participant availability, durations
or room capacities are silently assumed.

Changes: rename source's color/node variables to slot/session roles, preserve the
two algorithms and ordered result behavior, make error wording unspecified, and
integrate them under inspection/current-retention/preview/completion paths. Source
functions remain unchanged in the core view. [Exact diff](../../source_diffs/agenda.diff).
The adapted and original algorithms agree on all 76 simple graphs through four
vertices with slot counts 0–3; full reports are independently checked from participant
records, not the production graph compiler. This is bounded evidence, not a proof
of all inputs or a model difficulty measurement.

## Why WHERE is more than a function name here

The [example](example_request.json) encodes the path 0–2–3–1 through shared participants.
With two slots, first-available preview blocks, while full completion returns
`[morning, afternoon, afternoon, morning]`. See [actual report](example_report.json).

| Region / role | What must be understood | Consequence of an incorrect boundary |
|---|---|---|
| `catalog.relations` | Derives constraints from participant overlap | An oracle over the wrong relation solves a different problem |
| `agenda.preview` | One ordered, non-backtracking attempt; its status is visible | Replacing it with a full solver changes preview/status even with the same final proposal |
| `agenda.complete`, including nested `available`/`place` and closed-over state | Complete assignment under all conflicts, prescribed order, no-solution behavior | Isolating `available` alone omits the assignment domain and search; omitting rollback changes behavior |
| `program.review_agenda` | Inspect and retained-current paths bypass both algorithms; ready preview bypasses completion | Always offloading or rebuilding a valid current assignment violates observable behavior |
| `catalog.describe` / move report | Exact named outputs, conflicts and changes | Valid slot indices alone are not a full replacement |

The provisional nomination is `agenda.complete` with its nested predicate and state;
input relation construction is a required dependency, not automatically part of a
quantum kernel. Broad nomination followed by rejection remains allowed under D-016.
No unique accepted source span or overlap threshold is declared.

## Conditional HOW / remaining science

A finite slot-vector domain and participant-conflict predicate provide a candidate
search formulation to review. Coloring also admits other formulations; the new case
does not force a single correct algorithm or add a third quantum family. Encoding
non-power-of-two slot counts, constructing/uncomputing a predicate, exact absence,
lexicographic output and runtime/resource assumptions remain explicit obligations.
The need to preserve a preview does not prove its underlying computation can never
be quantumized; it rules out substituting a differently specified full solver.

Review functional realism, output ordering and practical evidence. All scientific
fields remain null. Stronger WHERE is a design hypothesis supported by boundary
counterexamples, not an already observed LLM failure or hardness result.
