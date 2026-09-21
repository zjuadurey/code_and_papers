# Restricted Codex CLI single-turn pilot baseline

**PILOT · NON-FINAL · DRAFT-REFERENCE EVALUATION**

Executed 2026-09-20, 07:34:31–07:40:56 UTC (15:34:31–15:40:56 Asia/Shanghai).
ChatGPT-authenticated Codex CLI 0.154.0, requested gpt-5.6-sol, reasoning high.
No more specific server snapshot was exposed. This is not a raw GPT/API baseline.
Each case received one fresh isolated invocation and its unchanged pilot-v0.1
rendered prompt. See [protocol and evidence](README.md).

Every row below is a **prediction description**, not a new case annotation.
YES/NO/UNCERTAIN render JSON true/false/null. Candidate ranges are inclusive,
1-based, all in program.py. NONE renders an empty array. Intent is abbreviated
from the model's free text; approach denotes a family discussed, not an executed
migration or a structured plan. Every final decision is REMAIN_CLASSICAL and
every plan is null. Full originals are linked per case.

| Case | Candidate prediction | Structural | Practical | Intent | Approach | Parse status | Main observation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [001](raw/pilot-001.txt) | satisfies:1–6 + has_assignment:9–13 | YES | NO | Clause-satisfaction existence | Conditional Grover; abstain | Schema valid | Includes predicate helper; cites missing evidence but emits practical NO. |
| [002](raw/pilot-002.txt) | NONE | NO | NO | Ordered digest with audit effects | Remain Classical; no family | Schema valid | Describes ordered callbacks/exceptions and rejects both contracts. |
| [003](raw/pilot-003.txt) | best_partition_score:3–6 | YES | NO | Exact weighted partition maximum | QUBO/Ising discussion; abstain | Schema valid | Gives an objective expression; exact-optimum concern motivates rejection. |
| [004](raw/pilot-004.txt) | has_code:4–7 | YES | NO | Bounded-code membership | Conditional Grover; abstain | Schema valid | Uses the ≤8, one-shot workload; excludes the guard from its span. |
| [005](raw/pilot-005.txt) | feasible_bundle:4–12 | YES | UNCERTAIN | Budgeted exact-unit subset existence | Grover primary, QUBO alternative; abstain | Schema valid | Both contracts marked applicable at formulation level; no structured plan. |
| [006](raw/pilot-006.txt) | minimum_energy:2–7 | YES | NO | Exact binary-expression minimum | QUBO/Ising discussion; abstain | Schema valid | Separates sampled energy verification from global-optimum certification. |
| [007](raw/pilot-007.txt) | has_total:2–7 | YES | UNCERTAIN | Exact subset-total existence | Grover primary, QUBO alternative; abstain | Schema valid | Retains applicability uncertainty; discusses signed arithmetic and classical alternatives. |
| [008](raw/pilot-008.txt) | NONE | NO | NO | Full normalization and distinct copies | Remain Classical; no family | Schema valid | Emphasizes complete materialization and mutable-list identity. |
| [009](raw/pilot-009.txt) | best_cost:4–12 | YES | NO | Exact placement cost plus metadata | QUBO/Ising discussion; abstain | Schema valid | Writes the same-side cost expression; preserves validation/report obligations. |
| [010](raw/pilot-010.txt) | contains_record:4–8 | YES | NO | Active-record membership after full parse | Conditional Grover; abstain | Schema valid | Separates mandatory parsing from lookup; costs remain unquantified. |

## Mechanical Results

- Total cases attempted: **10**. Successful CLI executions: **10**. Failed: **0**.
- Valid JSON objects: **10**. Existing-schema/collector-valid predictions: **10**.
  Malformed or schema-invalid predictions: **0**. Collector repairs: **0**.
- Abstentions: **10**; QUANTUMIZE: **0**; structured non-null plans: **0**.
- Structural: YES **8**, NO **2**, UNCERTAIN **0**.
- Practical: YES **0**, NO **8**, UNCERTAIN **2** (005/007).
- Benchmark support: YES **0**, NO **2** (001/007), UNCERTAIN **8**.
- Operator retries: **0**; visible transport retry events: **0**; tool calls: **0**.
  CLI bounded internal transport defaults cannot be fully observed/disabled; do not
  equate no visible retries with a packet-level network guarantee.
- Ten distinct thread IDs, one turn and one final message per case. Each raw file
  matches its JSONL final message exactly; parsed copies match raw bytes exactly.
- One separate non-scientific smoke invocation passed. Read-only setup failures
  and fixed startup warnings are retained; they are not failed scientific cases.

Evidence: [SUMMARY.json](SUMMARY.json), [run audit](metadata/run-audit.json),
[collector](validation/collection.json), [raw responses](raw/), [logs](logs/).

### Existing evaluator diagnostics, against DRAFT references only

These describe the current provisional evaluator, not validated scientific accuracy.
No source labels or metrics were changed to accommodate the responses.

| Diagnostic | Recorded result | Interpretation limit |
| --- | --- | --- |
| Exact candidate-region micro precision / recall / F1 | 4/9 = 0.4444; 4/8 = 0.5; 8/17 = 0.4706 | Counts regions, not cases. Human boundary policy remains open. |
| Exact candidate-set matches by case | 5/10 (002, 005, 008, 009, 010) | Includes two empty-set matches; not a final WHERE correctness metric. |
| Structural labels | 10/10 resolved DRAFT pairs match | Draft agreement is not independent label validity or general capability. |
| Migration family | 8/8 resolved pairs match; 2 unresolved | Free-text intent and admissible alternatives are not scored by this number. |
| Practical labels | 4/4 resolved pairs match; 6 unresolved | Model NO on unknown references is not validated; UNCERTAIN is not automatically failure. |
| Decision / abstention | 4/4 scored decisions match; 6 unscored | All four known decisions are REMAIN_CLASSICAL. The apparent 1.0 conditional accuracy is not 10/10 task success. |
| False quantumization rate | 0/4 = 0 | All predictions abstain; QUANTUMIZE precision and recall are null. |
| Intent, contract conformity, benchmark support | Human coding required / unresolved | No automated semantic correctness inferred. |
| End-to-end quantumization success | 0 applicable cases | No quantum migration was generated or executed. |

All five exact-span mismatches still overlap the DRAFT span: 001 IoU 0.4545,
003/004 0.5714, 006 0.75, 007 0.8571. No overlap threshold was selected, and these
values do not resolve whether helper inclusion or smaller loop spans are acceptable.
Full output: [evaluation.DRAFT_REFERENCE.json](evaluation.DRAFT_REFERENCE.json),
with demonstration_only=true.

## Provisional Scientific Observations

The response set distinguishes structural formulation from a final migration
decision: eight structural YES judgments coexist with ten abstentions. It does
not force the digest or materialization tasks into either family. Whether this
is appropriate caution or excessive abstention requires reviewed assumptions
and labels; ten synthetic inputs cannot establish general model capability.

There are **no practical YES predictions**, so this run contains no instance of
the requested provisional flag “possible overconfident quantumization under
insufficient evidence.” No dedicated confidence field exists, and no high-confidence
count is inferred from prose. Instead, 001/003/006/009 give practical NO while
citing missing resources/benchmarks or exactness issues; 005/007 retain null amid
related unknowns. This asymmetry needs human interpretation, not automatic relabeling.

Exact-output obligations recur in the rationales. They motivate rejection even
when an algebraic formulation is written. Selecting a supported family or writing
an objective therefore remains distinct from establishing semantic preservation.

All plans are null, which is allowed on abstention by the frozen prompt/schema.
Some formulation reasoning appears in applicability/rationale fields, but this
run supplies no complete structured T3 plan. This is an observed measurement
limitation, not a schema violation or evidence of inability to plan.

## Candidate Failure Patterns

These are open-coded questions, not a finalized taxonomy or adjudicated failures.

- **Unknown evidence rendered as categorical rejection:** especially 001/003/006/009;
  compare with 005/007. Practical NO might reflect a semantic objection or a policy
  choice; the current evidence does not decide which is justified.
- **Support versus performance evidence:** 001/007 set benchmark_supported=false,
  while other rationales discuss lack of benchmark evidence. Review whether the
  model interprets current benchmark contract support as measured quantum advantage.
- **Boundary convention sensitivity:** helper inclusion in 001 and smaller spans
  in 003/004/006/007 change exact diagnostics without proving wrong localization.
- **Conditional planning not elicited on abstention:** all ten plan fields are null.
- **Formulation versus executable contract:** alternate formulations are discussed,
  but applicability and exactness are not independently verified.

Per-case evidence and review prompts: [FAILURE_NOTES.md](FAILURE_NOTES.md).

## Questions Raised for QRefactor Design

1. Should practical NO distinguish a demonstrated violation from missing evidence,
   while the operational decision may still be REMAIN_CLASSICAL?
2. How should benchmark_supported be explained without conflating contract coverage
   with measured advantage or availability of an implementation?
3. Should a future protocol request a conditional structured plan for structural
   YES cases even when the final action abstains, so T3 can be observed?
4. Which helper/guard/return boundaries are admissible for WHERE? The current
   exact/overlap contrast cannot establish that WHERE is the main bottleneck.
5. How should multiple supported formulations be judged independently of a single
   expected family and a model's binary applicability selection?
6. What reviewed exactness/certification and resource assumptions would make WHETHER
   meaningfully resolvable rather than consistently encouraging abstention?

No statistical significance, quantum advantage, final taxonomy, agent architecture
or benchmark-wide claim follows from this run.
