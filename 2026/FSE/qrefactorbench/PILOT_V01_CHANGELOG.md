# QRefactorBench pilot-v0.1 — public-input revision

2026-09-20. Researcher-approved specification/prose fixes only. **All ten cases
remain DRAFT; no labels were assigned, promoted or rescored. No LLM baseline ran.**

## Current and preserved versions

- Use [pilot/packets-v0.1/](pilot/packets-v0.1/) for the next baseline/annotation
  distribution; give each recipient only their role directory.
- [pilot/packets/](pilot/packets/) remains the unchanged original snapshot.
- All ten original public task files are preserved byte for byte in
  [original_public_tasks/](pilot/revisions/pilot-v0.1/original_public_tasks/).
- [Exact diff](pilot/revisions/pilot-v0.1/public-task-changes.diff) and
  [revision manifest](pilot/revisions/pilot-v0.1/manifest.json) record every changed
  field and old/new hashes, plus the four new packet-manifest hashes.

pilot-v0.1 names this input revision, not a frozen benchmark or a schema upgrade.
The exporter's existing packet format marker remains phase1-v0; software/prediction
version remains 0.2.0. Identify this revision by directory and manifest hashes.

## Ten-case prose audit

| Case | Changed / cue removed | Functional information retained |
| --- | --- | --- |
| 001 | Clause satisfaction → Clause interface; replaced Boolean-domain exploration and pure-predicate/reversible-construction coaching with input growth and representation-cost facts. | Exact satisfaction Boolean, literal domain, empty cases, classical clauses, unknown benefit. |
| 002 | Removed “no hidden existential query” and one-pass prescription; stated observable outputs instead. | Final digest, every ordered audit call, callback effects/exceptions. |
| 003 | Weighted partition score → Graph interface; replaced “Analyze the family” with a graph-size assumption. | Exact maximum crossing weight, weights, repeated edges, self-loops and encoding cost. |
| 004 | Small resident lookup → Resident code request. | ≤8 resident integers, duplicates/empty input, ValueError, one invocation, no state/oracle reuse, complete costs. |
| 005 | Removed “remain classical; analyze the subset enumeration”; replaced feasibility/witness jargon with returned Boolean/no-subset behavior. | Exact units/budget condition, filtering, sorting, metadata and classical data arrival; no location or migration partition prescribed. |
| 006 | Binary quadratic energy → Coefficient interface; expressed the exact 0/1 minimum via the supplied expression rather than naming its formulation; removed QAOA-depth/optimizer hint. | Exact result, coefficient signs, repeated/self terms, growing inputs; no approximation threshold or execution budget supplied. |
| 007 | Subset total decision → Integer list interface; replaced subset-domain coaching with list growth and removed reversible-arithmetic coaching. | Exact existence result, signed/duplicate inputs, empty subset, widths/arithmetic/workspace costs and classical comparison. |
| 008 | Removed “not a summary, sample or optimum” and “no search predicate or optimization objective”. | Complete ordered output, distinct mutable copies, zero-row behavior and workload growth. |
| 009 | Corrected name from integer to string; kept integer left_cost/right_cost. Documented existing ValueError behavior for non-string names, invalid indices and negative penalties. No extra family/location cue was found to remove. | Existing program/tests, exact placement cost, metadata and validation. |
| 010 | Fresh-data record membership → Fresh-data record request; “One membership query” → “One invocation”. | Full parse before result, active/key condition, malformed-JSON exceptions, fresh one-use batches, no QRAM/reuse and full-operation costs. |

Exact minima/maxima, existence Booleans and complete-output requirements necessarily
convey functional meaning. They remain because removing them would change the task.
Source identifiers/algorithms, generic T1/T2/T3 instructions and the identical shared
two-family contract menu are unchanged. No per-case recommended quantum family or
positive/negative annotation is exported. This is a prose-leakage audit, not an
empirical claim that recognition has become difficult or free of all possible cues.

## Verification

- Focused pilot/revision tests: **23 passed**. Full pytest: **87 passed, 3 skipped**
  (Qiskit/PyYAML absent in the core environment); optional suite: **5 passed**.
- All **10 pilot cases validate**; full dataset: **14 valid DRAFT** cases with
  expected DRAFT warnings. Summary counts and scientific labels are unchanged.
- New tests execute pilot-009's valid string-name case and invalid-name/link cases;
  specification and executable checks agree. Source programs are unchanged.
- Fresh exports reproduce all four new role packets byte for byte. Existing
  private-sentinel export tests pass; public field allowlisting, blank A/B forms,
  absence of populated private answer fields, IDs and hashes pass inspection.
- Temporary dummy collection/schema/evaluation passes for all ten IDs and both
  decisions, including null labels, default DRAFT rejection and malformed-input
  rejection. No scores or dummy responses are retained as baseline results.

Commands and raw outputs: [validation record](artifacts/pilot_v01_validation/README.md).
The existing workflow audit now accepts --packets and defaults to packets-v0.1;
its earlier saved outputs remain historical. No production exporter, evaluator,
schema, source algorithm, contract menu or suitability scoring changed.

## Still scientifically unresolved

Practical suitability and its cost model; structural evidence requirements;
candidate boundaries/rejected hotspots and overlap scoring; exact versus
probabilistic semantics; alternate admissible families/contracts; unknown versus
abstention; independent annotation/adjudication, licensing and final splits.
Only Q17's input-type conflict is resolved. Q18's explicit prose cues were addressed
as approved; the influence of necessary specifications remains unmeasured.

Next: record the new baseline packet hash in run metadata and, when separately
authorized, follow the existing one-response direct-LLM protocol. Distribute no
curator files, archived packets, AI proposals or changelog to the model operator.
