# Human annotation guidelines

These guidelines are provisional. Humans define and verify scientific labels;
schema validity is an engineering property, not evidence of scientific correctness.
These are infrastructure demonstration examples, not scientifically validated benchmark ground truth.

The [research charter](RESEARCH_CHARTER.md) explains the evidence process: AI proposal,
source evidence, literature where needed, researcher review, then independent/expert
validation. Conceptual “researcher-reviewed” or “expert-validated” descriptions are
not new schema states. Keep the existing DRAFT/REVIEWED/ADJUDICATED/FROZEN rules below;
informal review or an AI-generated detailed plan does not promote a case. Expert
validation must be documented as evidence, not inferred from FROZEN metadata.

## Separate the three questions

1. **Structural eligibility:** identify a meaningful formulation and its conditions.
   Provide evidence about the input domain, predicate/objective, data dependencies
   and output requirements. Under [D-017](../DECISIONS.md#d-017-structural-mapping-is-distinct-from-contract-preservation),
   YES requires a concrete established correspondence to a supported formulation;
   a loop or family name alone is insufficient. Missing essential mapping evidence
   remains UNCERTAIN. Complete original-contract preservation is a separate obligation:
   objective encoding alone does not certify the complete solver's exact optimum,
   nor does a predicate formulation settle a search API's no-solution behavior.
   Record these remaining obligations without treating the migration as validated.
2. **Practical suitability:** state the problem scale and execution assumptions.
   Consider data encoding/loading, oracle construction, classical–quantum transfer,
   classical preprocessing/postprocessing, repeated execution, resource costs and
   visible effects. A structural mapping need not be worthwhile.
3. **Benchmark support:** establish a reviewed contract and an evaluation protocol
   that this release can apply. A theoretically possible migration can be outside
   current benchmark coverage.

`quantumizable != worth_quantumizing`. Record the labels separately, and use null
for unresolved draft judgments. Practical suitability=true in the two shipped
positive toys means an artificial teaching policy only, not economic, asymptotic
or hardware feasibility evidence. Replace that assumption for real seed cases.

`executable_quantum_code != semantically_correct_migration`. Outputs must satisfy
the software contract, including side effects, failure behavior, tie handling,
exact versus approximate answers, and output type/interface requirements. Running
a Qiskit circuit or selecting a known algorithm establishes none of these alone.

## Abstention and case types

Prospective [D-016](../DECISIONS.md#d-016-reviewed-uncertainty-broad-candidates-and-staged-evidence)
allows a WHERE candidate to be excluded by WHETHER; rejected hotspots may therefore
be recorded as candidates in the next protocol. It also permits reviewed judgments
to remain uncertain. The legacy category/schema conventions below have not been
rewritten or applied retroactively; case-level annotations and scoring need a
versioned transition. D-017 resolves structural eligibility's conceptual boundary;
case-specific evidence and scoring criteria still require review.

`NO_QUANTUMIZATION` is an important correct answer, serialized as REMAIN_CLASSICAL.
It can mean there is no candidate, or that a candidate fails suitability or current
benchmark support. Do not force a positive migration for every case.

- **positive**: intended to permit at least one admissible migration under the
  explicit case assumptions; expected_decision=QUANTUMIZE when settled.
- **negative**: intended to remain classical; there may be no candidate at all.
- **hard_negative**: superficially promising computation that fails an important
  requirement. Ordered side effects, data dependencies and encoding overhead are
  hypotheses to examine, not an established taxonomy.

D-005 provisionally requires all three labels true for reviewed positives and at
least one false for reviewed negative types. A reviewed hard negative retains a
candidate region documenting the tempting computation. These conventions need
empirical review. If reality does not fit them, record a disagreement/open question
instead of altering a label to satisfy the validator.

## Describe regions and contracts

Use original program coordinates: relative file path, inclusive 1-based source
lines and optional qualified function (`Class.method`, `outer.inner`). Boundaries
must lie within the declared function. Multiple regions are allowed; annotations
do not imply that disconnected regions are independently quantumizable.

State computational intent with a stable ID and a human-readable explanation.
Enumerate admissible contracts without inventing a unique correct algorithm.
Specify encoding, assumptions, formulation, allowed algorithm families, decoding,
semantic relation, resources and limitations. A reference plan is optional and
illustrative. For an exact classical optimizer, accepting a merely approximate
quantum result requires an explicitly approved change of contract; it cannot be
silently counted as semantic preservation.

Researcher-approved default [D-015](../DECISIONS.md#d-015-preserve-the-original-software-contract-by-default):
preserve the original behavior contract. Exactness, exceptions, side effects,
ordering and output conventions cannot be weakened to accommodate an algorithm.
Approximation/probabilistic guarantees must be permitted by the original contract;
unknown thresholds remain unknown. A later approved relaxation must be separately
versioned and must not receive credit for preserving the old contract. Conflicting
specification/code/test evidence needs review. D-014 conditional plans may retain
open obligations; their presence does not resolve these obligations or validate labels.

## Independent annotation to freeze

D-016 approves a preliminary coordinator-review stage: inspect AI proposals against
source/evidence and preserve actual reviewer comments separately. This is not
independent annotation, gold or automatic promotion to the legacy REVIEWED status.
Important cases used for formal accuracy claims subsequently need independent
annotation and appropriate domain-expert validation. No actual review is implied
by accepting this workflow. The following is the existing independent-review path.

1. Curate the classical program, provenance/license, relevant inputs, interfaces,
   classical tests and stable case ID. Keep annotation_status=DRAFT.
2. A and B independently write full annotation copies, e.g. annotations/a.json and
   annotations/b.json, before viewing one another's labels. Preserve those records.
3. Compare with `qrefactorbench compare-annotations annotations/a.json annotations/b.json
   --json` (one shell line). Store the output as a disagreements artifact. The tool
   compares structured fields; it neither scores agreement nor adjudicates truth.
4. Record review.independent_annotations with distinct annotator IDs and files,
   and review.disagreements. Complete tests, oracle and resource declarations.
   REVIEWED means these records exist; the validator cannot verify independence.
5. A human expert adjudicates differences and records evidence and uncertainty in
   a resolution file; specify review.adjudicator_id and review.resolution. Add the
   adjudicator to annotators, then mark ADJUDICATED when appropriate. Whether the
   expert must be distinct from A/B remains a workflow choice to validate.
6. After release review, assign benchmark_release, resolve licensing, archive the
   exact files/hashes, and mark FROZEN. The current validator checks metadata and
   file presence; a published immutable release still requires a human process.

Do not fabricate reviewer names or agreement statistics. The initial generated
toys deliberately have annotators=[]; authoring assistance is recorded in source.
Missing expected values/thresholds/hooks can remain in a DRAFT oracle. REVIEWED
oracles require usable configuration for their declared kind, but human review
must establish scientific coverage, sample sizes and validity.

## Pending reference labels for exploratory comparison (D-022)

The researcher authorized concrete provisional labels while retaining pending review.
The current private overlay is [provisional_labels/v0.1](../pilot/provisional_labels/v0.1/README.md).
Label content and scientific maturity are independent: DRAFT can contain a proposed
YES with mapping evidence. PENDING is overlay review metadata, not a new case-schema
enum. Original case manifests and public inputs remain unchanged. These scores are
reference-agreement diagnostics, not gold accuracy; unknown references are unscored.
Alternate supported formulations and boundaries require review rather than automatic
rejection. No recorded individual approval or independent annotation follows from
authorization to prepare these labels. Revisions must preserve the previous version.

## Evidence checklist for human review

Document eligible input domain, oracle access/data-loading model, side effects,
failure behavior, exactness/tolerance, probabilistic semantics, resource basis,
and reasons to accept or abstain. No automatic threshold or unreviewed complexity
claim should substitute for this evidence. Keep unresolved issues in
docs/open_questions.md and observations in docs/research_log.md.

## Phase-1 blind packets

Use pilot/packets-v0.1/annotator_a and annotator_b as separately distributed directories.
The original pilot/packets/ is preserved for history, not current distribution.
Each has ten neutral task/source inputs, the same DRAFT contract menu and blank
annotation forms. Do not provide either annotator the repository, private manifest,
draft references, other annotator's packet or model outputs. Folder separation alone
does not enforce this; the coordinator controls distribution.

The packet template is an independent working form, not a case.schema.json object.
candidate_regions=null means unfilled/unknown; [] means an explicit no-candidate
judgment. completion_status=SUBMITTED records completion without implying REVIEWED.
Use actual annotator IDs only when submitting, preserve both raw forms and compare
them with the existing CLI. Assumptions, uncertainty and applicability are included
in field comparisons; textual differences are not automatic scientific disagreement.

The adjudication packet records evidence and unresolved issues; it does not merge
or promote annotations automatically. See pilot/annotation/adjudication_instructions.md.
Two unsupported hard-negative drafts use empty eligible candidate sets while D-005
requires a region at REVIEWED. Decide the eligible-region versus rejected-hotspot
semantics (Q14) before promotion; do not invent a candidate to pass the validator.
All ten seeds remain DRAFT and all independent forms remain UNFILLED at handoff.
