# Conditional-plan HOW evidence protocol v0.2

Method direction: ACCEPTED under D-026 (researcher chose A).
Case judgments: AI_AUTHORED / PENDING. No human annotations are implied.

## Task and scope

Continue the current Phase-1 task: analyze candidates and propose conditional plans
under supported Search/Optimization families. D-014 requires a plan for structural
YES even when adoption remains classical; D-017 separates core structure from full
contract preservation. Neither generated code nor executed migration is required.
This independent review layer does not replace frozen prompts, labels, schemas or
historical evaluator outputs. It adds prospective/reported post-hoc HOW evidence.

Four dimensions remain M (core mapping), E (encoding conditions), C (contract
obligations) and W (scope/dependencies). Every claim must identify its scope, raw
response pointer, evidence kind and unresolved obligations. A dimension may contain
multiple claims; a counterexample refutes only the identified claim/branch.

## Two separate records

**Correctness evidence** uses supported / contradicted / unresolved / not_addressed /
not_reviewed / not_applicable as defined in the prior rubric. Supported is always
scoped: a correct energy does not certify a sampler or whole program. Contradicted
requires a valid witness or specific logical/source inconsistency. Unknown controls
do not become known negatives merely because multiple models reject them.

**Obligation completion** uses these descriptive states, never numerical weights:

| State | Meaning |
|---|---|
| provided | A concrete scoped expression, procedure or source-grounded analysis is supplied and can be examined. It can be wrong. |
| partial | Some construction/analysis is supplied; essential details are still missing. |
| deferred | The answer explicitly leaves the substantive construction/justification for future work. |
| not_addressed | An applicable obligation is not discussed. |
| not_applicable | The obligation is not triggered for this response/task, with a reason. |
| no_response | There is no final answer; this is delivery failure, not a semantic judgment. |

The ledger covers (1) core correspondence, (2) encoding conditions, (3) ordered/tied
selection, (4) exact certification/no-result policy and (5) context preservation.
For a rejection, (1)/(5) include reasoning about the assessed scope; (2)–(4) may be
not_applicable without claiming structural NO is correct. Reference-positive cases
cannot evade applicable obligations merely by predicting NO. Their applicability
follows the pending reference requirement plus D-014, with disagreements exposed.

Completion is **not derived from correctness**: DeepSeek002 has a supplied tie formula
(`provided`) that is `contradicted`; Astra002 explicitly defers tie construction.
The model can supply a concrete source analysis without a complete quantum oracle.
Each state is manually assigned with pointers and a scope note. No complete migration
has been verified in the current review.

## Evidence and reporting

1. Freeze input/response hashes before review; record scope, conditions and code lineage.
2. Compare alternative families and boundaries semantically, not by exact wording or
   one preferred span. Mathematical core, canonical decoding, complete-program behavior
   and resource suitability require separate evidence.
3. Evaluate a stated conditional claim under its stated conditions. Reviewer-selected
   coefficients, slack representation or finite domains must be disclosed. Finite
   checks and manual derivations are different evidence, neither is QPU execution.
4. Preserve honest uncertainty. Classical fallback is an obligation unless specified
   and verified; mentioning it does not erase a wrong formula or establish quantum value.
5. Record raw failed requests and delivery reasons. No final answer means no content
   reconstructed from reasoning. Do not drop failed cases and present the remainder as
   full-population performance. Row-level review is allowed; no new Flash full score.
6. Report evidence matrices and completion ledgers, with pending maturity visible.
   No scalar composite, pass threshold, overall task success or stable model ranking.
   More assertions create more opportunities for checks; raw assertion counts are not
   an accuracy measure. No aggregation of conditional claims as independent samples.
7. Practical UNKNOWN/NO and release support need prospective public definitions;
   existing ambiguous fields are retained but not used as capability scores here.

## Reviewer workflow and independence

First establish contract obligations using public source/contract materials only.
The reviewer_packet is for this reference-building stage and excludes model responses,
private labels and coordinator codings. A reviewer may leave genuinely unresolved
items open; no majority-model vote establishes ground truth.

After a reference review, response review may use those obligations with anonymized
responses. This package does not claim an anonymized response study occurred or that
an expert already exposed to coordinator results is blind. Independent reviewers
record their own identity, evidence and disagreements; adjudication stays explicit.
No reviewer is contacted or human judgment filled automatically.

## Version boundaries

This operational record adopts A. It does not approve individual labels, arbitrary
new workload assumptions, frozen splits, new families, new model runs or a release.
Changes to task contracts, main scoring or case inclusion remain scientific decisions.
Future executable-encoding submissions would be a separate task version.
