# Tomorrow review — QRefactorBench Phase 1

**AI-ASSISTED PROPOSAL — NOT GROUND TRUTH** · 2026-09-19 · Coordinator/reviewer copy.

| Case | Candidate region | Structural | Practical | Intent | Proposed approach | Confidence (W/S/P/A) | Main thing researcher must decide |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [001](pilot-001.md) | program.py:10–13; helper 1–6 dependency | YES, formulation | UNCERTAIN | Predicate Search | Conditional Grover-style | M/H/H/M | Include helper in WHERE? What establishes an exact no-solution answer? |
| [002](pilot-002.md) | NONE; rejected hotspot 7–9 | NO, scoped | NO, scoped | Other / Unsupported | Remain Classical | H/H/M/H | Is a rejected hotspot a candidate annotation or an explicit NONE? |
| [003](pilot-003.md) | program.py:2–7 | YES, quadratic | UNCERTAIN | Combinatorial Optimization | QUBO/Ising; QAOA conditional | H/H/H/M | Separate representability from exact maximum certification. |
| [004](pilot-004.md) | program.py:4–7; retain checks 2–3 | YES, formulation | UNCERTAIN, leans against | Predicate Search | Remain Classical pending evidence | H/H/L/M | Does ≤8 one-shot lookup justify a policy NO, or require costs to label suitability? |
| [005](pilot-005.md) | program.py:5–12; preserve wrapper/helper | YES, formulation | UNCERTAIN | Predicate Search; optimization alternative | Conditional Grover; QUBO alternative | M/H/H/M | Can both supported families be admissible for the same Boolean intent? |
| [006](pilot-006.md) | program.py:2–8 | YES, already quadratic | UNCERTAIN | Combinatorial Optimization | QUBO/Ising; QAOA conditional | H/H/H/M | Preserve exact minimum, signs, duplicate/self terms and constants. |
| [007](pilot-007.md) | program.py:2–7 | YES, formulation | UNCERTAIN | Predicate Search; optimization alternative | Conditional Grover; squared-residual QUBO | H/H/H/M | Separate intent from family; account for signed arithmetic and zero-energy decisions. |
| [008](pilot-008.md) | NONE; rejected hotspot 3–7 | NO, scoped | NO, scoped | Other / Unsupported | Remain Classical | H/H/M/H | Full ordered output and independent mutable copies cannot become a sampled answer. |
| [009](pilot-009.md) | program.py:5–12; preserve validation/report | YES, quadratic kernel | UNCERTAIN | Combinatorial Optimization | QUBO/Ising; QAOA conditional | M/H/H/M | Public task says name is integer; validator requires str. Also distinguish soft costs from hard constraints. |
| [010](pilot-010.md) | program.py:5–8; preserve full parse at 12 | YES, conditional representation | UNCERTAIN, leans against | Predicate Search | Remain Classical pending evidence | H/M/L/M | Is fresh-data overhead sufficient evidence for NO? Preserve parse-before-lookup exceptions. |

Case numbers abbreviate pilot-001 through pilot-010. Ranges refer to the blinded
source files; links open the detailed proposal. W/S/P/A = WHERE, structural,
practical judgment and approach; H/M/L = HIGH/MEDIUM/LOW. A high-confidence
UNCERTAIN means confidence that supplied evidence is insufficient, not confidence
in a profitable migration. Confidence is uncalibrated and is never correctness.

Structural YES means a supported mathematical formulation, not a verified oracle,
solver, semantic migration or resource feasibility. Scoped NO for 002/008 means
no meaningful target under the two current families, not general quantum
impossibility or a measured timing comparison. The cautious action for 004/010
does not turn their unknown practical suitability into a proven NO.

**Independence disclosure:** this assistant helped prepare the cases in the prior
conversation. That context and startup project summaries cannot be unlearned.
Each proposal was derived from and cites only blinded source/task/menu evidence,
then hashed before workflow/provenance inspection. These are not independent
annotator submissions or a blind-model baseline. Keep this directory away from
independent A/B reviewers until their own records are submitted.

## Review order

These groups indicate the most useful entry point for review, not disjoint claims
about which dimensions are fully resolved.

**A. Apparently straightforward within the stated scope: 002, 008.** Their complete
ordered/effectful outputs give no natural search or optimization objective. Review
the definition of a rejected candidate rather than assuming a generic impossibility.

**B. Requires careful researcher review: 001, 003, 005, 006, 007, 009.** The source
supports predicate/quadratic formulations; exactness, dependency boundaries,
alternative formulations and wrapper semantics still need human contracts. Read
009 early because its public type declaration conflicts with its validator.

**C. Cannot resolve the central suitability question from supplied information:
004, 010.** Both make classical retention plausible, but neither provides a
quantitative profitability criterion. This limitation also affects every case in
B: **all eight structurally proposed cases have unresolved practical suitability**.
The supplied “growing” domains do not specify a deployment size distribution.

## Scientific Decisions Requiring Human Review

These nine decisions are the proposed agenda. None was resolved by changing labels,
programs, prompts, schemas or metrics overnight.

| Decision | Affected cases | Choice/evidence the researcher must establish |
| --- | --- | --- |
| 1. Resolve public input-domain inconsistency | 009 | Does name mean str as the validator enforces, or is the public integer-field statement intended? Decide the valid domain and invalid-input obligations before distributing a corrected snapshot. |
| 2. Define candidate-region meaning and boundaries | all; especially 001, 005, 009 and 002/008 | Statements versus entire function; oracle/helper dependencies versus target; eligible region versus rejected hotspot. Keep exact/overlap diagnostics provisional and do not select a cutoff without annotation evidence. |
| 3. Define evidence needed for structural YES | 001, 003–007, 009, 010 | Is a constructive predicate/quadratic expression enough, or must a bounded reversible oracle/costed encoding already be supplied? A missing implementation is not automatically structural NO. |
| 4. Define the semantic target of a valid HOW plan | search: 001, 004, 005, 007, 010; optimization: 003, 006, 009 | Exact False/absence and exact optimum versus a stochastic procedure. Decide proof/certification/fallback or an explicitly revised contract; do not invent success/quality thresholds. |
| 5. Operationalize practical suitability | all eight proposed structural cases, especially 004/010 | Quantitative runtime/resource comparison, declared cost-model regime or conservative qualitative migration policy? Specify needed scale, integer/data widths, oracle/setup/loading/reuse costs and classical comparison; otherwise retain null. |
| 6. Allow or reject alternative supported formulations explicitly | strongest examples 005, 007; potential threshold alternatives 003, 006, 009 | Boolean intent can have a search or zero-minimum quadratic formulation. A single reference family may penalize a legitimate plan; decide the admissible set rather than grading the primary intent as the only algorithm. |
| 7. State observable software obligations | 002, 004, 005, 008, 009, 010 | Callback order/exceptions, guard errors, preprocessing/nonmutation, independent output lists, validation/report metadata and full-parse errors. Decide whether proposed regions/contracts carry these obligations. |
| 8. Define what the blinded task actually measures | all; strongest direct cues 002, 005, 008 | Public software_contract/title often supplies intent; 005 explicitly points to enumeration, 002/008 explicitly deny search/optimization structure. Are these permitted specifications or cues that weaken WHERE/intent discovery? Field-level blinding does not answer this design question. |
| 9. Distinguish ignorance, abstention and independence | all; notably 004/010 | Boolean labels support null but decision has only QUANTUMIZE/REMAIN_CLASSICAL; candidate_regions requires an array. Decide interpretation of uncertainty-driven abstention and unknown localization, and use fresh independent researchers rather than count these context-exposed AI proposals as independent evidence. |

Repeated missing cost/semantic policies are a **possible benchmark-definition
problem**, not ten isolated annotation errors. The same is true of single-family
scoring when multiple supported formulations could preserve one intent. Whether
to narrow Phase 1 to conditional planning or supply richer execution assumptions
is a human task-definition choice. No profitability claim can be extracted from
this review package.

## Information sufficiency and workflow

See [INFORMATION_SUFFICIENCY.md](INFORMATION_SUFFICIENCY.md) for the full matrix and
[WORKFLOW_AUDIT.md](WORKFLOW_AUDIT.md) for exact checks and commands.

The input → schema → collector → evaluator path works mechanically with temporary
dummy fixtures, including explicit abstention and null labels. A fresh packet export
is byte-identical to the existing packets; no populated case-specific reference
fields were found in prompts and A/B forms remain blank. There are no real model
responses or scores. Public prose cueing, the 009 type mismatch and unresolved
scoring semantics are human-review blockers, not failures that were hidden by
changing tests. [PROVENANCE_AUDIT.md](PROVENANCE_AUDIT.md) retains unknown licensing.

## Practical start tomorrow

1. Read this table, then 009's proposal and the information-sufficiency matrix.
2. Work through decisions 1–9; record unresolved items rather than force labels.
3. Decide whether any public specification needs a separately versioned correction.
4. Distribute only the original/newly approved role packets to fresh independent
   A/B researchers. Do not include annotation_assist or the full repository.
5. After independent records are preserved, use these proposals as discussion aids,
   compare/adjudicate human records and decide when a direct-model pilot is interpretable.

Exact overnight completion, test outcomes and preserved files are summarized in
[OVERNIGHT_STATUS.md](OVERNIGHT_STATUS.md). No scientific decision is assumed approved.
