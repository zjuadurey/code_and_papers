# pilot-002 — fresh source-grounded review proposal

**AI-ASSISTED PROPOSAL — NOT GROUND TRUTH**

Date: 2026-09-19. Status: advisory only; not an A/B submission, model-baseline
prediction, adjudication, or replacement for any existing annotation.
Evidence for this proposal is restricted to the supplied
[blinded source](../packets/annotator_a/pilot-002/program.py),
[public task](../packets/annotator_a/pilot-002/public_task.json),
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
| WHERE: smallest reasonable target | NONE under the two supported migration families. Rejected hotspot: program.py:7–9 in `ledger_digest`; it is not an eligible candidate proposal. |
| Structural quantumizability | NO within the current search/optimization task contracts; this is not a claim of physical impossibility. |
| Practical suitability | NO for supported selective migration of this unchanged task. This is a scope/contract rejection, not a latency comparison. |
| Computational intent | Other / Unsupported — sequential digest accumulation with observable ordered callbacks. |
| Proposed approach | Remain Classical. |
| Confidence by judgment | WHERE HIGH within the stated scope; structural HIGH scoped to the supported contracts; practical MEDIUM (scope judgment, no timing evidence); intent HIGH; approach HIGH. |

Structural YES here means a meaningful formulation within the two supplied
families, not verified reversible construction or complete semantic preservation.
Practical uncertainty must not be replaced by an invented cost or runtime assumption.

## Concrete evidence

All source line ranges below refer to the unmodified blinded files.

| Location | Observable behavior supporting the proposal |
| --- | --- |
| 6–8 | Each hash consumes the previous digest and the next event; every later step depends on earlier state. |
| 9 | audit(index, digest.hex()) is called once per processed event in order, exposing each intermediate state. |
| 9–10 | Callback exceptions are not caught; the function must stop and propagate them rather than always return a final digest. |
| public_task.json / execution_assumptions | Callbacks must occur on the classical host and the complete ordered ledger behavior is required. |

## Applicability conditions

SATISFIED/VIOLATED refer to the stated condition under the public task, not a
completed quantum implementation. UNKNOWN is retained when evidence is absent.

| Condition | Assessment | Evidence / limit |
| --- | --- | --- |
| An existential unknown witness/search result is the software objective | VIOLATED | The result is a prescribed digest and callback trace, not existence of a matching candidate. |
| A binary optimization objective defines the requested output | VIOLATED | No objective or alternative assignment to optimize is supplied. |
| Replacing the loop may omit/reorder callbacks | VIOLATED | The observable ordered callback contract forbids that transformation. |
| Observable exception/trace behavior can be preserved by the proposed supported mapping | UNKNOWN | No search/QUBO mapping demonstrating this is supplied. |
| Runtime, event sizes and classical/QPU timing comparison | UNKNOWN | Not provided; unnecessary to identify the present scope mismatch. |

## Formulation and boundary reasoning

High per-event cost or a long event list does not create a search opportunity. Quantum evaluation of a hash as an arithmetic subroutine would not by itself reformulate this task into either supported family. Retaining all required host callbacks while simply inserting a quantum subroutine is not evidence of useful selective quantumization.

## Missing information

Event-size/runtime distributions, callback semantics beyond order and possible exceptions, and any separately specified computational subtask. These omissions prevent performance analysis but do not turn the current ordered digest contract into search or optimization.

## Reasonable alternative interpretation

Searching for an event or input that produces a chosen digest would be a different program contract. It must not be substituted here. A researcher may annotate 7–9 as a rejected candidate during triage instead of using NONE; that changes the meaning of candidate_regions and needs an explicit benchmark convention.

## What the researcher should decide

Choose whether WHERE reports only supported eligible regions or also rejected hotspots. Scope the NO label to the current two families; do not turn it into a general no-quantumization theorem.

No quantum advantage, scientific label validity, or end-to-end migration success is
claimed. Keep this proposal outside independently distributed annotation packets.
