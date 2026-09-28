# Conditional-plan diagnostic results

Date: 2026-09-20. **Controlled diagnostic; not an independent baseline, not reference-scored, not a publication-level capability result.**

**Interpretation: A. STRONGER SUPPORT FOR H1.** All eight diagnostic structural-YES responses now contain substantive conditional plans while still recommending REMAIN_CLASSICAL with practical NO or UNCERTAIN. The structural-NO controls retain null plans. This supports separating conditional HOW elicitation from practical adoption; it does not prove complete HOW competence or establish the original model's internal cause of abstention.

## Mechanical results and primary questions

The experiment actually ran with ChatGPT authentication, `codex-cli 0.154.0`, `gpt-5.6-sol`, high reasoning, fresh single-turn ephemeral read-only invocations, and the original Bubblewrap isolation and runner. All ten first attempts succeeded; ten predictions passed the existing collector/schema checks; zero malformed responses, repairs, operator retries or observed tool calls. One separate fixed-token smoke call is excluded from the ten. Raw bytes and logs are retained.

| Question | Observed result |
|---|---|
| Q1: Plans among diagnostic structural YES? | **8/8**, compared with 0/8 in the original run |
| Q2: Plans among structural YES + practical NO/UNCERTAIN + REMAIN_CLASSICAL? | **8/8**: six practical NO, two UNCERTAIN |
| Q3: Content beyond schema filling? | **8 SUBSTANTIVE, 0 PARTIAL, 0 SUPERFICIAL**; 2 null controls NOT APPLICABLE, under the descriptive rubric |
| Q4: Main judgments changed? | Structural, practical, final decision and selected family: **0/10 changes each**; intent wording changes in 10/10 but the main described computations remain recognizable |
| Q5: Structural-NO controls retain null? | **2/2**, pilot-002 and pilot-008 |

All ten still abstain. Across all cases practical NO remains 8 and UNCERTAIN remains 2; no practical YES was emitted. Selected families remain five search, three optimization and two null. Counts are generated from [paired_fields.json](paired_fields.json) and [SUMMARY.json](SUMMARY.json); content judgments are detailed in [PLAN_CONTENT_REVIEW.md](PLAN_CONTENT_REVIEW.md). Unknown suitability is not treated as a scientific failure.

## Paired comparison

YES/NO/UNCERTAIN render true/false/null. Both “Original” and “New” refer to model predictions, never reference labels. Candidate-coordinate changes below also refer only to predictions.

| Case | Original Structural | New Structural | Original Practical | New Practical | Original Decision | New Decision | Original Plan | New Plan | Main Observation |
|---|---|---|---|---|---|---|---|---|---|
| pilot-001 | YES | YES | NO | NO | REMAIN_CLASSICAL | REMAIN_CLASSICAL | null | present | Clause oracle/verification plan now explicit; same recommendation |
| pilot-002 | NO | NO | NO | NO | REMAIN_CLASSICAL | REMAIN_CLASSICAL | null | null | Sequential digest/audit retention remains |
| pilot-003 | YES | YES | NO | NO | REMAIN_CLASSICAL | REMAIN_CLASSICAL | null | present | Explicit cut QUBO/Ising; candidate starts at line 2 rather than 3 |
| pilot-004 | YES | YES | NO | NO | REMAIN_CLASSICAL | REMAIN_CLASSICAL | null | present | Bounded membership plan despite practical rejection |
| pilot-005 | YES | YES | UNCERTAIN | UNCERTAIN | REMAIN_CLASSICAL | REMAIN_CLASSICAL | null | present | Subset feasibility predicate and classical handler context |
| pilot-006 | YES | YES | NO | NO | REMAIN_CLASSICAL | REMAIN_CLASSICAL | null | present | Quadratic minimum plan; candidate ends at line 8 rather than 7 |
| pilot-007 | YES | YES | UNCERTAIN | UNCERTAIN | REMAIN_CLASSICAL | REMAIN_CLASSICAL | null | present | Signed subset-sum encoding and exact-absence caveat |
| pilot-008 | NO | NO | NO | NO | REMAIN_CLASSICAL | REMAIN_CLASSICAL | null | null | Full classical materialization retention remains |
| pilot-009 | YES | YES | NO | NO | REMAIN_CLASSICAL | REMAIN_CLASSICAL | null | present | Explicit placement-cost QUBO; candidate starts at line 5 rather than 4 |
| pilot-010 | YES | YES | NO | NO | REMAIN_CLASSICAL | REMAIN_CLASSICAL | null | present | Conditional record predicate after complete parsing |

## Diagnostic structural-YES subset

“Substantive” means observable case-specific formulation content, not validated correctness or complete execution design.

| Case | Practical | Final Decision | Plan Present? | Mapping Family | Conditional Plan Substantive? | Main Unresolved Requirement |
|---|---|---|---|---|---|---|
| pilot-001 | NO | REMAIN_CLASSICAL | YES | Search / Grover | SUBSTANTIVE | Exact absence certification and reversible clause-oracle cost |
| pilot-003 | NO | REMAIN_CLASSICAL | YES | Optimization / QUBO–Ising, QAOA | SUBSTANTIVE | Exact global-maximum certificate and coefficient/routing costs |
| pilot-004 | NO | REMAIN_CLASSICAL | YES | Search / Grover | SUBSTANTIVE | Exact absence and overhead for an at-most-eight domain |
| pilot-005 | UNCERTAIN | REMAIN_CLASSICAL | YES | Search / Grover | SUBSTANTIVE | Exact negative result, arithmetic encoding, unknown scale |
| pilot-006 | NO | REMAIN_CLASSICAL | YES | Optimization / QUBO–Ising, QAOA | SUBSTANTIVE | Exact global-minimum certificate and signed-coefficient fidelity |
| pilot-007 | UNCERTAIN | REMAIN_CLASSICAL | YES | Search / Grover | SUBSTANTIVE | Exact absence, signed accumulator, loading and magnitude costs |
| pilot-009 | NO | REMAIN_CLASSICAL | YES | Optimization / QUBO–Ising, QAOA | SUBSTANTIVE | Exact global minimum, constant offsets and coefficient precision |
| pilot-010 | NO | REMAIN_CLASSICAL | YES | Search / Grover | SUBSTANTIVE | Exact predicate semantics, fresh-batch loading and absence fallback |

## Other paired changes and limits of field stability

The requested main categorical fields do not change. Intent descriptions are **not text-identical** in any case; the following comparison is descriptive reading, not an intent-accuracy score or proof of semantic equivalence:

| Case | Main intent in both responses | New wording/emphasis |
|---|---|---|
| pilot-001 | Exact clause-satisfaction existence | Condenses assignment/edge-case wording |
| pilot-002 | Ordered rolling digest and observable callbacks | Makes completion/exception qualification more explicit |
| pilot-003 | Exact maximum weighted crossing score | Names weighted maximum cut and no side effects |
| pilot-004 | Exact bounded code membership with validation | Explicitly mentions duplicate handling |
| pilot-005 | Filter/sort offers, exact subset feasibility, response metadata | Condenses eligible-instance wording |
| pilot-006 | Exact binary quadratic minimum | Formula moves from top-level intent into the plan |
| pilot-007 | Exact positional subset-sum existence | Explicitly mentions negatives and duplicate positions |
| pilot-008 | Normalize rows and materialize distinct mutable copies | Explicit row/copy ordering |
| pilot-009 | Validate, minimize placement cost exactly, return report | Condenses explanation that placement need not be returned |
| pilot-010 | Parse all payloads, then exact predicate existence | Makes Python truthiness/equality wording explicit |

There are additional changes, so it would be inaccurate to say that **only the output plan field** changed:

- Candidate regions change in pilot-003, pilot-006 and pilot-009 as shown above; other seven region lists are identical.
- `benchmark_supported` changes in five cases: pilot-001 and pilot-007 NO → UNCERTAIN; pilot-003, pilot-005 and pilot-006 UNCERTAIN → NO. This field is separate from the unchanged structural/practical/family fields.
- Contract applicability labels change in four cases: pilot-003 Grover NO → UNCERTAIN; pilot-005 QUBO YES → UNCERTAIN; pilot-007 Grover and QUBO UNCERTAIN → YES; pilot-010 Grover UNCERTAIN → YES. All ten contract-applicability records differ textually, which includes rationale wording changes and must not be confused with ten categorical changes.

These are observed changes, not improvements or regressions. The two runs cannot determine whether each difference arose from the instruction, stochastic generation or unobserved service variation. No label adjudication or evaluator change was made to explain them away.

## Interpretation of H1 versus H2

The controlled instruction successfully elicits conditional plans without changing practical recommendations. Each of the eight plans contains a predicate/oracle or binary-objective construction rather than only naming Grover or QAOA. This is stronger support for **H1 at the conditional formulation/elicitation level** than the original all-null outputs alone provided. The structural-NO controls did not respond by inventing plans for every case.

This does not demonstrate that the model could supply a complete, exact, resource-feasible implementation. Search plans leave negative certification unresolved or invoke a potentially exhaustive fallback; optimization plans explicitly lack global-optimality certification. Exact encoding, circuit schedules, resource counts and feasibility remain incomplete. All eight resource objects are generic unresolved markers, although other fields discuss resource dimensions. These gaps may matter for later HOW evaluation, but were not tested as execution-capability failures here.

This is one paired rerun on ten synthetic pilot inputs with an unexposed model snapshot/seed. The content coding is AI-assisted and unblinded to experimental condition. There is no statistical-significance claim, independent human agreement result, quantum-advantage claim or general model-capability conclusion. No DRAFT/gold-reference correctness comparison was performed.

## Preservation, validation and deviations

- Original runner bytes and CLI path/configuration were retained. All ten recorded command arrays match the originals after replacing only fresh temporary directory names. Only the approved instruction was appended to scientific prompts; exact differences and hashes are retained.
- Immediately after execution/tests, **557 pre-existing files** matched their pre-run fingerprints, including **122 original baseline files** and **99 frozen pilot-v0.1 packet files**. Original responses, diagnosis, schemas, labels, programs and evaluator remained unchanged. Later project-memory updates are separately allowlisted in the final preservation check.
- Existing collector: **10 predictions, 0 repairs**, exit 0. Full pytest: **87 passed, 3 skipped in 3.61s**. Existing optional environment: **5 passed in 0.96s**. Dataset validation: **14 valid DRAFT cases**, including all ten pilot cases, with expected DRAFT warnings. JSON summary succeeded. See [validation/commands.json](validation/commands.json) for exact commands and raw outputs.
- Event audit: ten unique threads, one turn and one final message each; all raw/event contents match, all raw/parsed copies are byte-identical. No tool items, turn failures or observed reconnect/retry events; operator retry count is zero. No output was repaired or regenerated.
- No contamination or substantive protocol deviation was observed. Existing limitations remain: built-in harness descriptions, two preserved startup warnings per invocation, native bounded transport defaults, operator prior project context, and unexposed server/sampling details. The model's mount allowlist excludes repository/reference/previous-response content; the local harness inspection differs from the original only in message IDs/timestamps.
- No model-generated code, oracle, quantum circuit or benchmark accuracy evaluation was run. Existing tests ran only after the ten outputs were fixed, with no feedback to any model invocation. No dependencies were installed.

## Implications for Later QRefactor Design

These observations motivate questions, not implementation: should conditional HOW coverage be reported independently of adoption decisions; how should humans assess semantic obligations left unresolved inside a plan; and why are benchmark-support/secondary-contract judgments less stable than main family decisions? The next step is human review of the paired outputs and content coding, especially exactness/certification and resource placeholders. No agent, repair loop, extra model run or further system is proposed or implemented here.
