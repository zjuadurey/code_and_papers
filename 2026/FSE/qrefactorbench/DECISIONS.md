# Decisions

ACCEPTED scope decisions below come from the project brief. PROVISIONAL protocol
choices permit infrastructure testing and are not validated research conclusions.

## Ledger conventions and evidence index

- **ACCEPTED:** explicitly authorized scope/process decision; not necessarily an
  empirically validated scientific claim.
- **PROVISIONAL:** recorded choice awaiting the stated validation; never promote silently.
- **SUPERSEDED:** retain the original entry and link the dated replacement and reason.
- **OPEN:** no decision taken; track unresolved science in [docs/open_questions.md](docs/open_questions.md).

Keep ID, status, date, decision, rationale, consequences, and evidence/relevant files
for every new entry. Existing D-001–D-012 entry bodies and statuses are preserved.
D-007 records initial 0.1.0 versions; D-009 documents the later 0.2.0 profile/package.
D-010's “no model calls supplied” describes its preparation stage, not present run
history. Current facts belong in [PROJECT_STATUS.md](PROJECT_STATUS.md).

| Decision | Evidence / relevant files |
|---|---|
| D-001 | [Scope and research intent](docs/RESEARCH_CHARTER.md), [dependency declarations](pyproject.toml) |
| D-002 | [Task vocabulary](docs/task_definition.md), [prediction schema](schemas/phase1_prediction.schema.json) |
| D-003 | [Contract design](docs/benchmark_design.md), [planning evaluator](qrefactorbench/evaluator/planning.py) |
| D-004 | [Candidate evaluator](qrefactorbench/evaluator/candidate.py), [evaluation protocol](docs/evaluation_protocol.md) |
| D-005 | [Annotation guidelines](docs/annotation_guidelines.md), [case schema](schemas/case.schema.json), [validator](qrefactorbench/validator.py) |
| D-006 | [Evaluation pipeline](qrefactorbench/evaluator/pipeline.py), [protocol](docs/evaluation_protocol.md) |
| D-007 | [Versioning design](docs/benchmark_design.md), D-009 below |
| D-008 | [Historical pilot preparation](PHASE1_PILOT_STATUS.md), [packet exporter](qrefactorbench/pilot.py) |
| D-009 | [Phase-1 schema](schemas/phase1_prediction.schema.json), [package metadata](pyproject.toml) |
| D-010 | [Provider-neutral protocol](pilot/baseline/README.md), [collector](qrefactorbench/pilot.py) |
| D-011 | [Public-input revision](PILOT_V01_CHANGELOG.md) |
| D-012 | [Diagnostic protocol](pilot/baseline-v0.1/conditional-plan-diagnostic/README.md), [paired evidence](pilot/baseline-v0.1/conditional-plan-diagnostic/CONDITIONAL_PLAN_DIAGNOSTIC_RESULTS.md) |

## D-001: Python and Qiskit in v0.1

Date: 2026-09-18
Status: ACCEPTED

### Decision
Use Python 3 source artifacts and Qiskit as the initial quantum framework.
### Rationale
The requested narrow scope permits executable artifact and circuit inspection.
### Alternatives considered
Multiple languages/frameworks immediately; deferred to avoid unsupported breadth.
### Consequences
No claim of generality beyond these interfaces. Qiskit is an optional dependency.
### Requires future validation?
Yes: later generalization and framework coverage.

## D-002: Selective quantumization and abstention

Date: 2026-09-18
Status: ACCEPTED

### Decision
Evaluate WHERE, WHETHER, HOW, REFACTOR, VALIDATE separately. Separate structural
eligibility, practical suitability, and benchmark support. NO_QUANTUMIZATION is
represented by decision=REMAIN_CLASSICAL, with zero or more identified regions.
### Rationale
Quantumizable != worth_quantumizing; execution != semantic preservation.
### Alternatives considered
One quantumizable flag; unconditional code translation; both lose required distinctions.
### Consequences
Explicit human expected_decision; draft labels may be null. Absence of a region
does not mean that the source program is missing.
### Requires future validation?
Operational suitability definitions remain open (Q1, Q2).

## D-003: Multiple contracts and unknown results

Date: 2026-09-18
Status: ACCEPTED

### Decision
Represent admissible migrations as a set of contracts. Plans select a contract,
but selection alone is not evidence of conformity. Semantic and resource checks
remain separate from execution. Missing evidence yields null, not success.
### Rationale
Several formulations may preserve the required semantics under different assumptions.
### Alternatives considered
One correct_algorithm field or free-text exact matching; rejected.
### Consequences
Contract reviewers/oracles must be supplied by researchers. Initial toys are not
a reviewed contract library and contain no reference quantum implementation.
### Requires future validation?
Yes: contract completeness and oracle validity (Q5, Q9).

## D-004: Source regions and diagnostic overlap

Date: 2026-09-18
Status: PROVISIONAL

### Decision
Use file + inclusive 1-based start/end lines, optional qualified function name.
Exact localization compares sets of (file,start,end); function is a consistency
check, not an alternate coordinate. Report union-of-lines overlap separately,
without a correctness threshold. Exact match is the v0.1 strict gate.
### Rationale
Unambiguous, deterministic coordinates without choosing a scientific overlap cutoff.
### Alternatives considered
AST identities, token overlap, weighted region matching; remain possible.
### Consequences
Exact scoring is sensitive to boundary choices. Empty denominators yield null;
empty predicted and reference sets still have candidate_correct=true.
### Requires future validation?
Yes: Q3; these diagnostics are not an accepted final paper metric.

## D-005: Annotation maturity and provisional decision policy

Date: 2026-09-18
Status: PROVISIONAL

Supersession note (2026-09-20): D-016 supersedes the mandatory-certainty rule
prospectively and adds a coordinator-review stage before independent validation.
The body below documents the unchanged legacy schema. Other category/scoring
rules remain provisional; no historical record or serialized status is rewritten.

### Decision
DRAFT permits unknown labels. REVIEWED requires completed labels, oracle and
resource configuration, classical tests, and two distinct annotation records.
ADJUDICATED additionally requires an adjudicator and resolution artifact. FROZEN
additionally requires a release ID and resolved source licensing. Positive cases
are intended QUANTUMIZE examples; negative/hard-negative cases REMAIN_CLASSICAL.
Non-DRAFT positive cases require all three scientific labels true; non-DRAFT
negative types require at least one false. Hard negatives retain a candidate.
### Rationale
Catch contradictions and record human evidence without automatically adjudicating.
### Alternatives considered
Deriving every decision from one label; accepting incomplete reviewed records.
### Consequences
Unsupported-but-theoretically-eligible cases can remain classical within this
release. These conventions need pilot review; they are not universal scientific laws.
The validator checks records, not whether humans really worked independently.
### Requires future validation?
Yes: Q1, Q4 and unsupported-family abstention policy.

## D-006: Evaluation denominators and strict success

Date: 2026-09-18
Status: PROVISIONAL

### Decision
False quantumization rate is false QUANTUMIZE decisions divided by annotated
REMAIN_CLASSICAL cases. Report counts and null for zero denominators. Use explicit
expected_decision, never silently derive scoring labels from case_type.
Strict positive success requires localization, decision, verified plan conformity,
syntax/import/execution/interface success, semantic validation, quantum constraints,
and declared resource checks. False dominates unknown; otherwise missing evidence
yields null. Abstention cases have end_to_end_quantumization_success=null and
separate abstention_correct. The CLI is static and does not run generated code.
### Rationale
Make every failure and missing evidence visible; prevent unexecuted plans passing.
### Alternatives considered
Execution-only success, optimistic missing checks, a single blended score.
### Consequences
Initial static evaluation normally cannot establish end-to-end success.
### Requires future validation?
Yes: human protocol review before pilot reporting.

## D-007: Versioned artifacts and future releases

Date: 2026-09-18
Status: PROVISIONAL

### Decision
Use schema/package version 0.1.0, stable case IDs and separate case versions.
Capture hashes and dependency versions in evaluation outputs. No final release,
train/validation/test split, license grant, or freeze automation in this phase.
### Rationale
Preserve traceability while avoiding premature release and leakage decisions.
### Alternatives considered
Random split now; silently treating examples as a benchmark release.
### Consequences
Humans must choose licensing, composition, leakage policy and freeze procedure.
FROZEN metadata alone does not create an immutable released dataset.
### Requires future validation?
Yes: Q7, Q8, Q10, Q11.

## D-008: Phase-1 pilot material and blind distribution

Date: 2026-09-18
Status: PROVISIONAL

### Decision
Keep four original toys and add a separate ten-case synthetic DRAFT pilot with
neutral IDs. Distribute only allowlisted task/source facts, common candidate
contracts and blank forms to independent annotators; keep draft labels, categories
and references curator-only. Public workload assumptions are inputs, not labels.
### Rationale
Pilot sampling needs reviewable examples without fabricating annotation evidence
or seeding annotators with the expected answer.
### Alternatives considered
Editing/relabeling old toys; copying full manifests into annotation packets; rejected.
### Consequences
There are 14 cases overall and 10 in cases/pilot. Six proposed positive cases retain
unknown suitability/support/decision. Two unsupported hard-negative drafts use
empty eligible candidate sets with rejected hotspots recorded separately. D-005's
REVIEWED nonempty-region rule conflicts with promoting these drafts as-is; D-005
is not changed, and Q14 requires human resolution. Neither category hypotheses nor
synthetic provenance establish scientific validity. Folder separation is not ACLs.
### Requires future validation?
Yes: independent annotation, applicability, suitability and negative-region semantics.

## D-009: Phase-1 prediction profile and recognition evidence

Date: 2026-09-18
Status: PROVISIONAL

### Decision
Add a version 0.2.0 prediction profile reusing the unchanged v0.1 case/plan/legacy
prediction schemas. It records separate labels, free-text intent, family, contract
applicability, assumptions and risks even on abstention. Keep the complete raw
prediction in evaluation results. Do not exact-match a model's intent description
or self-chosen ID to a private reference ID. Report label comparison coverage and
conditional accuracy on resolved pairs; retain unknowns. Result/package version
is 0.2.0; case/plan versions remain 0.1.0; pilot name is QRefactorBench-v0.
### Rationale
The legacy format lacked separate predicted labels and private IDs would confound
intent recognition in a blinded open-description task.
### Alternatives considered
Changing old schema content under its old ID; leaking reference intent IDs;
grading arbitrary text equality; all rejected.
### Consequences
Legacy predictions still work. Human intent/applicability coding remains necessary.
Shared contract IDs permit set-selection diagnostics but are not correctness proof.
Null responses are retained in coverage, not silently counted as correct/incorrect.
Candidate overlap metrics and all existing scientific thresholds remain provisional.
### Requires future validation?
Yes: recognition rubric, coverage/abstention interpretation and final metric policy.

## D-010: Direct-LLM collection without repair

Date: 2026-09-18
Status: PROVISIONAL

### Decision
One response per case in a fresh context, fixed recorded settings and full prompt
snapshot; no tools, retrieval, feedback, repair or provider dependency. Preserve
raw outputs/errors. Collect valid external Phase-1 JSON with exact coverage and
evaluate against an explicitly selected dataset. No automatic missing-response
substitution or partial aggregate; intentional subsets record selected/unselected IDs.
### Rationale
Task validation needs a reproducible direct-model baseline before agent design.
### Alternatives considered
Provider-specific client, automatic JSON repair and default abstention on failures;
deferred because they change the baseline or obscure failures.
### Consequences
No API configuration, credentials, model calls or baseline scores are supplied.
The metadata and error observations are human-completed. Missing/invalid prediction
scoring policy and repeat/sample settings need review before scientific reporting.
### Requires future validation?
Yes: pilot execution and empirical failure analysis before a final protocol.

## D-011: Researcher-approved pilot-v0.1 public-input correction

Date: 2026-09-20
Status: ACCEPTED (explicit researcher instruction; input presentation only)

### Decision
Make pilot-009's public name type match the executable string-name requirement.
Remove case-specific prose that prescribes a candidate, intent/family or expected
category, while preserving functional requirements and genuine execution facts.
Archive original task text and keep original packets; distribute a new pilot-v0.1
snapshot. Do not change labels, algorithms, schemas, scoring or scientific maturity.
### Rationale
The researcher approved these specific fixes for preparing the first direct-LLM
baseline, without authorizing scientific relabeling or running that baseline.
### Alternatives considered
Overwriting distributed packets, changing source to match the typo, or removing
necessary exact-output/workload requirements; excluded by the approved scope.
### Consequences
Use pilot/packets-v0.1 and its hashes. Q17 is resolved; Q18's explicit prose cues
are removed, but the effect of necessary specifications remains unmeasured.
All prior provisional scoring/annotation decisions remain provisional.
### Requires future validation?
Mechanical validation passes; independent scientific annotation and baseline
interpretation remain pending. This decision approves no quantumization label.

## D-012: One-off conditional-plan elicitation diagnostic

Date: 2026-09-20
Status: PROVISIONAL

### Decision
Under explicit researcher authorization, run one paired ten-case diagnostic with
the original CLI/model/reasoning/isolation/schema and only the supplied appended
conditional-plan instruction. Preserve the original baseline and all new first
attempts. Do not count this as an independent baseline or compare against labels.
### Rationale
Original abstentions left plan=null despite some explicit mappings in rationales.
The diagnostic separates eliciting conditional HOW from recommending adoption.
### Alternatives considered
Schema/evaluator changes, prompt redesign, output repair, extra families or agent
implementation; excluded by the authorized controlled experiment.
### Consequences
Results live in pilot/baseline-v0.1/conditional-plan-diagnostic/. Eight structural-YES
responses now emit substantive descriptions while all practical/final decisions
remain unchanged. This observation does not establish scientific plan correctness
or adopt the diagnostic instruction as the benchmark's future default.
### Requires future validation?
Yes: independent review of content coding, semantic obligations and task separation
(Q19). No accepted research decision, label or scientific scoring rule is changed.

## D-013: Repository-driven continuation and documentation ownership

Date: 2026-09-20
Status: ACCEPTED (explicit user instruction; project control only)

### Decision
Use AGENTS as entry, the research charter for stable intent, PROJECT_STATUS for
the current handoff, NEXT_ACTIONS for a finite queue, this ledger for decisions,
and the existing lowercase research_log for append-only history. “继续” means
reconstruct context and do the next authorized safe action without a new long prompt.
### Rationale
Overlapping preparation/status text obscured completed experiments and future
authorization. A compact current route prevents repeated context reconstruction.
### Consequences
Historical artifacts and D-001–D-012 remain intact; conceptual T1–T6 numbering has an
explicit crosswalk rather than changing old T1–T3 protocols. Routine work proceeds;
scientific meaning changes need one concise human decision. Completed one-off runs
do not authorize repeats. No label, schema, metric or experiment changes follow.
### Evidence / relevant files
[AGENTS.md](AGENTS.md), [charter](docs/RESEARCH_CHARTER.md),
[workflow](docs/CODEX_WORKFLOW.md), [queue](NEXT_ACTIONS.md),
[consolidation audit](docs/DOCUMENTATION_AUDIT.md).
### Requires future validation?
Check the startup route and update the queue after real work. Scientific questions
remain OPEN/PROVISIONAL; this administrative decision resolves none of them.

## D-014: Conditional planning independent of adoption

Date: 2026-09-20
Status: ACCEPTED (researcher selected option A; future elicitation policy)

### Decision
In future protocol versions, require a conditional migration plan whenever the
response reports structural eligibility YES, including practical NO/UNCERTAIN and
REMAIN_CLASSICAL. The plan describes HOW under explicit assumptions; it does not
recommend deployment. Unresolved semantic, exactness, encoding, oracle,
certification, feasibility and resource requirements must remain explicit.

Separate plan presence, substantive content, technical correctness, semantic
preservation and practical benefit. Do not evaluate HOW solely on the subset the
model itself calls eligible: future evaluation must account for human-reviewed
eligibility and distinguish recognition omissions, planning coverage and quality.
Exact scoring definitions remain open; this decision changes no implemented metric.

### Rationale
The researcher chose A after discussion of the benchmark's translation objective.
The completed diagnostic elicited plans in 8/8 structural-YES responses without
changing practical/final decisions. This supports separating elicitation from
adoption, but does not validate those plans or establish general model capability.

### Alternatives considered
Require plans only when recommending QUANTUMIZE. That would leave conditional
mapping ability unobserved for recognized structures retained classically.

### Consequences
This resolves the policy-adoption part of Q19, not plan correctness or annotation.
Apply it when preparing a future version under its authorized scope; preserve the
frozen pilot-v0.1 prompt, baseline and diagnostic unchanged. The existing schema
permits REMAIN_CLASSICAL with a plan but does not enforce this elicitation rule.
No new prompt snapshot, experiment, schema/evaluator change or label promotion is
authorized here. D-012 remains the historical one-off diagnostic decision.

### Evidence / relevant files
Researcher's explicit option-A selection in this session;
[diagnostic results](pilot/baseline-v0.1/conditional-plan-diagnostic/CONDITIONAL_PLAN_DIAGNOSTIC_RESULTS.md),
[plan-content review](pilot/baseline-v0.1/conditional-plan-diagnostic/PLAN_CONTENT_REVIEW.md),
[human review record](pilot/review/CONDITIONAL_PLAN_HUMAN_REVIEW.md),
[remaining Q19 questions](docs/open_questions.md).

### Requires future validation?
Yes: independent technical/semantic review of the plans and human-reviewed case
eligibility; coverage/quality rubrics and practical evidence requirements remain
unresolved. Acceptance is a task-design decision, not validated ground truth.

## D-015: Preserve the original software contract by default

Date: 2026-09-20
Status: ACCEPTED (explicit researcher instruction)

### Decision
The default migration requirement is to preserve the original software contract
(原程序的行为约定): the declared input domain, observable output meaning and
representation, interface, exceptions, side effects and required ordering. Internal
algorithms may change; their externally required behavior may not silently change.
This is distinct from a quantum migration contract, which describes applicability,
encoding, formulation, decoding and obligations for achieving that behavior.

Keep exact requirements exact. Approximation or probabilistic output guarantees
are admissible under the default only to the extent permitted by the original
contract. Internal randomness alone is not a violation; the resulting observable
guarantees must meet that contract. Do not invent error rates, quality tolerances,
confidence levels, shot budgets or permissions to relax semantics.

Finding a valid witness does not certify absence; a feasible/high-quality assignment
does not certify an exact optimum. Preserve specified tie/first-result behavior and
validation/exception/effect ordering. If specifications, code or tests conflict,
record the discrepancy for review rather than selecting a convenient interpretation.

D-014 still requires conditional plans for response-reported structural YES in
future protocols. Such a plan may identify unresolved preservation obligations,
but is not thereby a verified migration. Neither an incomplete plan nor this policy
automatically determines a structural/practical label or a numeric score.

### Rationale
The researcher approved “保持原软件合同” as the default after the repository
alignment review. This keeps selective refactoring tied to existing software
behavior rather than replacing it with a different, easier quantum task.

### Alternatives considered
Silently allow approximate answers wherever a quantum algorithm supplies them;
or require identical internal implementations/randomness. Both miss the intended
boundary: preserve the specified observable contract, not implementation details.

### Consequences
Existing exact pilot requirements remain exact. Future tasks whose original APIs
already allow approximation may use their explicit quality contracts. Any later
researcher-approved relaxation of an existing contract requires a separately
identified/versioned task or condition and must not be reported as preserving the
old contract. No such relaxation, new case, new family or experiment is approved here.

This records policy only: no frozen input, model output, annotation, schema or
evaluator is modified. Earlier PROVISIONAL decisions remain PROVISIONAL; Q9's
default-preservation question is resolved, while case-specific validation remains open.

### Evidence / relevant files
Researcher's explicit instruction in this session;
[research charter](docs/RESEARCH_CHARTER.md#original-software-contract),
[task vocabulary](docs/task_definition.md),
[annotation guidance](docs/annotation_guidelines.md),
[existing plan obligations](pilot/baseline-v0.1/conditional-plan-diagnostic/PLAN_CONTENT_REVIEW.md),
[remaining semantic questions](docs/open_questions.md).

### Requires future validation?
Yes: case-specific contract reconciliation, semantic oracles, statistical policies
where already permitted, and independent review of migrations. This accepted
requirement is not proof that any existing plan or implementation satisfies it.

## D-016: Reviewed uncertainty, broad candidates and staged evidence

Date: 2026-09-20
Status: ACCEPTED (researcher responses to discussion items 2–5; item 1 remains OPEN)

### Decision
1. **Reviewed uncertainty (item 2):** allow an annotation to have been reviewed
   while retaining UNCERTAIN judgments. Review maturity and evidence certainty
   are separate. This supersedes D-005's mandatory-certainty requirement for a
   future version; it does not assign case labels or finalize category meanings.
2. **WHERE before exclusion (item 3):** candidates may include tempting/expensive
   regions worth examining that WHETHER subsequently rejects. Candidate presence
   does not establish a supported formulation, suitability or adoption. This does
   not require every hotspot/loop to be a candidate; the annotation boundary and
   scoring rubric remain to be operationalized. Do not relabel or rescore old cases.
3. **Practical evidence (item 4):** assess suitability under explicit workload and
   resource assumptions; report scale, encoding, oracle, communication and classical
   alternative evidence separately. Missing evidence stays unknown. No aggregate
   profitability score or measured end-to-end quantum-advantage claim is adopted.
   Simulator runtime versus Python runtime is not an advantage measurement.
4. **Staged human review (item 5):** begin with coordinator review of AI proposals
   against code/evidence, then obtain independent annotation and needed domain-expert
   validation for important cases supporting formal accuracy claims. Coordinator
   review is not independent validation or gold. Record real reviews when supplied;
   this process decision is not a completed review of any case.

### Rationale
The researcher explicitly allowed item 2, chose inclusion followed by WHETHER
exclusion for item 3, and accepted the recommended approaches for items 4 and 5.
They noted the limitations of simulator-only performance evidence and explicitly
requested further discussion of item 1 (structural eligibility's semantic boundary).

### Alternatives considered
Require certainty at review; permit only structurally accepted WHERE candidates;
require hardware profitability or two independent annotations before initial
coordinator review. These were not the selected directions.

### Consequences
These are prospective protocol decisions. Existing schemas still reject unknown
non-DRAFT labels and require independent records for REVIEWED. Preserve those
versioned formats and frozen packets/results; record coordinator evidence separately
without falsely promoting old manifests. Versioned implementation work remains.
The broad WHERE definition must not be used to reinterpret historical exact/overlap
scores. Which evidence justifies structural YES, case-specific labels, final
localization criteria, statistical thresholds and scoring denominators remain open.
No new family, model run, score, code-generation system or label promotion follows.

### Evidence / relevant files
Researcher's explicit responses in this session;
[annotation guidance](docs/annotation_guidelines.md),
[open questions Q1/Q2/Q12/Q14](docs/open_questions.md),
[legacy case schema](schemas/case.schema.json),
[current queue](NEXT_ACTIONS.md).

### Requires future validation?
Yes: operational candidate inclusion criteria, case-level review evidence, practical
assumption profiles and a versioned implementation consistent with the eventual
structural-eligibility definition. Do not treat policy acceptance as empirical validation.

## D-017: Structural mapping is distinct from contract preservation

Date: 2026-09-20
Status: ACCEPTED (researcher confirmation of discussion item 1)

### Decision
Structural YES means that a concrete correspondence has been established between
the computational core and a formulation in the supported families. It does not
mean that a complete migration preserving the original software contract has
already been established. Distinguish structural mapping, contract preservation,
and practical suitability, with evidence for each.

The mapping must identify the input domain and predicate, or the variables,
objective and constraints; explain their correspondence to the proposed formulation;
and identify the necessary conditions, supporting evidence and remaining unknowns.
An expensive loop, the word optimization, or an algorithm name is insufficient.
If an essential correspondence/condition is not established, retain UNCERTAIN
rather than claiming YES followed by an unsupported list of assumptions. Unknown
deployment costs alone need not invalidate an otherwise established structural map.

For example, an explicit objective/variable correspondence to QUBO can establish
a structural map while exact-optimum certification remains an unresolved obligation
for the complete solver. Such a plan is not a verified migration. The same distinction
applies to a predicate formulation and a complete search API's no-solution behavior.
Do not infer case-specific labels merely from these illustrative examples.

### Rationale
The researcher accepted this distinction after discussing whether structural YES
must already establish a complete migration. It separates failure to recover a
formulation from failure to complete software-contract preservation, enabling
interpretable WHERE/WHETHER/HOW research without weakening migration correctness.

### Alternatives considered
Require complete contract-preserving migratability for structural YES; or permit
superficial family recognition alone. The chosen boundary requires concrete mapping
evidence but reserves full preservation for its separate validation obligation.

### Consequences
Q2's conceptual boundary is resolved; the evidence must still be reviewed per case.
D-014 conditional planning, D-015 original-contract preservation and D-016 broad
WHERE/staged review remain consistent. No inference of suitability or advantage
follows from structural YES. Preserve existing labels, frozen prompts, experiments,
schemas and evaluator behavior; implement accepted directions in a new version.
No new Boolean success field, score, statistical threshold or experiment is defined
by this documentation decision. D-016's open-item wording remains historical.

### Evidence / relevant files
Researcher's explicit “可以，这样更细节” confirmation in this session;
[research charter](docs/RESEARCH_CHARTER.md),
[annotation guidance](docs/annotation_guidelines.md),
[remaining evidence questions](docs/open_questions.md),
[current implementation limitations](PROJECT_STATUS.md).

### Requires future validation?
Yes: case-specific mapping evidence, admissibility conditions, semantic oracles and
review consistency. Acceptance of the definition does not validate existing plans
or annotations, or finalize an accuracy/localization rubric.

## D-018: Context-001 approximate quality profile

Date: 2026-09-21
Status: ACCEPTED (scoped permission and ratio definition; acceptance threshold OPEN)

### Decision
Create a separately versioned DRAFT contract proposal for context-001 that permits
approximate arrangements. Report feasibility, report/interface correctness, exact
objective gap and quality ratio ρ=(W−C)/(W−C*), where W is total requirement weight,
C returned conflict weight and C* exact minimum conflict weight. This measures the
fraction of optimal attainable satisfied weight, not relative conflict error or
probability of success. With zero denominator report ratio as not applicable and
check zero cost/feasibility separately; absent certified reference means unknown.

The researcher explicitly chose reporting gaps with tolerance pending, then accepted
the ratio definition after it was distinguished from a proposed 95% threshold.
95% remains illustrative, not approved. Do not mark approximate semantic acceptance
passed without a specified policy. New tie/selection and probabilistic criteria are
also unresolved. Original interfaces, validation, reporting and input domain remain
obligations. No label, source algorithm, schema or evaluator change is authorized
by this documentation decision.

### Rationale
The researcher requested considering algorithm output characteristics and explicitly
documenting acceptable approximation in this case. Weighted satisfied-demand quality
has a useful interpretation even when the original minimum conflict cost is zero.
It must still be justified as a task requirement, not selected to reward one solver.

### Alternatives considered
Exact-only evaluation for every version; silently relax the observed version;
relative error divided by C* (undefined at C*=0); or automatically adopt 95%.
The approved direction preserves the original exact case and defers thresholds.

### Consequences
D-015 remains the default for unchanged cases; this follows its explicit versioned
exception process and does not supersede it globally. Observed old failures stay
failures under the original contract. The new proposal is not independently validated,
not a new population member or a release, and not a practical-advantage claim. Final
rules must be fixed before a future confirmatory experiment; current data are exploratory.

### Evidence / relevant files
Researcher: “近似精确解我们也接受，但是要在这个case文档里说清楚”; then
“先报告差距，容差待定（推荐）”; finally “可以” in response to the ratio definition,
with 95% explicitly separated as an undecided threshold.
[Case contract proposal](pilot/context_adaptations/v0.2-draft/CONTRACT_CONTEXT_001.md),
[original case](pilot/context_adaptations/v0.1/cases/context-001/public_task.json).

### Requires future validation?
Yes: business-grounded tolerance, new tie policy, repeatability/statistical criteria,
oracle implementation and independent review. The permission is not scientific ground truth.

## D-019: Source-driven expansion and behaviorally meaningful WHERE contexts

Date: 2026-09-21
Status: ACCEPTED (researcher-directed construction priority; case judgments and difficulty OPEN)

### Decision
Select suitable examples from the previously referenced benchmarks and record exact
source lineage before adapting them. Strengthen WHERE through functional alternatives,
data dependencies and necessary program paths, rather than primarily reusing local
pilots with additional wrappers. Preserve original source views and distinguish
new synthetic application requirements from upstream code or deployed software.

### Rationale
The researcher clarified: “我想要的是你从那些参考benchmark里找合适的例子加进去，
同时把对困难的 WHERE 发现也强化一下”. The prior expansion had useful contract
tests but largely reused local synthetic kernels and did not fulfill this intention.

### Alternatives considered
Continue the local synthetic expansion; treat quantum circuit-generation prompts as
existing classical software; add unrelated distractors or conceal function names only.
Those do not supply the requested source provenance and functional discovery problem.

### Consequences
Keep earlier artifacts intact. The bounded implementation adds two sourced mother
problems/four related views, not ten independent external cases. Code tests establish
specific behavioral distinctions, not harder model localization, quantum eligibility
or practical benefit. Source labels are not imported as gold; new judgments stay
DRAFT/unknown. Other benchmarks can inform evaluation without supplying classical
source code. No family, metric, original-contract rule or experiment authorization changes.

### Evidence / relevant files
[Source records](pilot/source_adaptations/v0.2-where/SOURCES.md),
[reference/method audit](pilot/source_adaptations/v0.2-where/REFERENCE_BENCHMARK_AUDIT.md),
[WHERE hypotheses and boundaries](pilot/source_adaptations/v0.2-where/WHERE_REVIEW.md).

### Requires future validation?
Yes: functional relevance, alternate boundaries, independent annotation, source-level
split dependence and controlled difficulty comparison. No acceptance of the particular
adaptations is inferred from the researcher's general construction direction.

## D-020: Three conditions per mother case for WHERE diagnosis

Date: 2026-09-21
Status: ACCEPTED (design direction); specific locations, rubric and execution protocol PROVISIONAL/OPEN

### Decision
Prepare A: original core view; B: complete context with a location cue; C: the same
complete context without that cue. Keep B/C source, contract, task and output format
identical apart from the explicit cue. Analyze pairs by mother problem, not as three
independent benchmark cases. Separate nomination from boundary/dependency evidence,
conditional HOW and practical recommendation. Preparation is authorized; model runs
are not authorized by this decision.

### Rationale
Researcher requested “打磨！” after the proposed design, then explicitly said
“每个母案例设置三个实验条件很有道理”. The comparison can help distinguish discovery
from understanding/planning when the region is supplied. A/B/C are input conditions,
not three new models or a proof of difficulty.

### Alternatives considered
Only compare core versus longer context (mixes length, names, interfaces and discovery);
only exact-span scores; repeatedly add distractors until models fail. These do not
provide the intended interpretable task characterization.

### Consequences
New DRAFT messages and review records live separately; existing cases/packets/results,
schemas and metrics remain unchanged. B's cue is deliberate information and can alter
attention/prior belief; B–C is not a pure causal isolation of WHERE. A preserves two
source operations and is calibration, not a precisely matched intervention. Detailed
boundary proposals, functional validity, control population and scores still need
human review. Existing exact-span evaluator output is not silently reinterpreted.

### Evidence / relevant files
[Review package](pilot/where_review/v0.1/README.md),
[protocol and limitations](pilot/where_review/v0.1/PROTOCOL.md),
[six prepared input manifests](pilot/where_review/v0.1/prepared/manifest.json).

### Requires future validation?
Yes: cue validity, alternate spans/dependencies, reviewer agreement, no-candidate and
multi-candidate coverage, matched run/sampling policy and measured difficulty. Direction
approval is not human case annotation, a release, novelty verification or run permission.

## D-021: Minimal session entry and documentation ownership

Date: 2026-09-21
Status: ACCEPTED (project operation only; no scientific policy change)

### Decision
The user requested that a new conversation given only “读取当前目录” recover research
intent and progress. Provide parent-workspace and project AGENTS entries. Reading
restores context and reports it without executing experiments or modifying files;
“继续” follows the existing safe-action queue. Keep charter stable, status current,
queue short, and history in logs/archives. Check affected documentation before delivery.

### Rationale
The old status/queue grew to 527/212 lines and the entry still called historical
baseline packets current. A short canonical path avoids requiring long user prompts.

### Alternatives considered
Keep duplicating history in every entry file; require the user to restate the idea;
or introduce a new automation framework. None is needed for this documentation task.

### Consequences
Original documents archived byte-for-byte; no case/label/metric or experiment changes.
Synchronization is an explicit operating requirement, not a claim of automated
semantic consistency or a new authority to run models. No Git commit/push authorized.

### Evidence / relevant files
[Entry](AGENTS.md), [workflow](docs/CODEX_WORKFLOW.md),
[archive and checks](artifacts/session_entry_20260921/README.md).

### Requires future validation?
Check real future-session usability and keep the queue current. Static link/path
checks cannot prove comprehension; no model experiment was used as a startup test.

## D-022: Provisional labels before scientific review

Date: 2026-09-21
Status: ACCEPTED (prepare pending labels for exploratory model comparison);
individual labels, boundaries and diagnostic scoring choices remain PROVISIONAL.

### Decision
The researcher stated: “我懂量子，但是保守起见，先设置为待审，但是现在需要有标签了，
至少先能区分开不同模型的能力”. Prepare concrete reference-label proposals now,
while keeping scientific review pending. Maturity and label content are distinct:
a proposed YES can coexist with DRAFT/PENDING. The statement authorizes preparation,
not approval of every proposed judgment or a new model run.

### Rationale
Current inputs can elicit answers, but entirely empty reference judgments prevent
useful structured comparison. Waiting for full independent review is unnecessary
for explicitly provisional diagnostics; unsupported certainty remains inappropriate.

### Implementation and provisional choices
Use a private versioned reference overlay, preserving all current public inputs,
original case metadata, schemas, main evaluator and historical results. Seven mother
cases have concrete positive structural mappings; three controls remain unresolved.
Record source anchors, primary families, formulas and core/context obligations.
Practical suitability remains unknown; conservative adoption is REMAIN_CLASSICAL,
and migration-contract support false. These constant fields alone cannot rank models.
No universal structural NO is inferred from absent mapping evidence.

Reuse exact/overlap and label diagnostics, explicitly exposing reference agreement
and coverage. Different supported families require content review, not automatic
failure. Plan coverage uses reference-positive cases, including model omissions.
HOW content and alternate boundaries require semantic review; no automatic text
grading, composite score or task pass rate is adopted. Missing/invalid response
sets are rejected by the diagnostic collector, preserving the old failure-policy
boundary; final experiment scoring is still open.

### Evidence / relevant files
[Pending reference labels and diagnostics](pilot/provisional_labels/v0.1/README.md),
[validation](pilot/provisional_labels/v0.1/validation.json).

### Consequences and review
This prospectively supersedes waiting for N-030's complete human acceptance before
preparing exploratory labels. It does not complete N-030, settle Q3/Q12/Q14–Q16,
relax contracts, promote annotation status or authorize model/QPU execution.
The researcher can review the prepared evidence using their quantum expertise;
no review identity or agreement is invented. Real model discrimination remains
an experimental question. Changes after review receive a new reference version.

## D-023: First current-package comparison through the ChatGPT subscription

Date: 2026-09-22
Status: ACCEPTED (bounded exploratory execution; scientific labels remain pending)

### Authorization and operational scope
The user requested: “用当前benchmark跑一下llm测试，给我一个小报告”. Following
the successful subscription connectivity check and the preceding two-model proposal,
run gpt-5.6-sol and gpt-6-astra once on each of the ten current C inputs: twenty
first attempts through the existing ChatGPT login. The operator fixes medium effort,
CLI 0.155.1, identical restricted wrapper, two concurrent requests maximum and a
600-second per-call timeout before inference. These are operational settings,
not separately approved scientific scoring policies. No API key, QPU or installation.

### Evaluation boundary
Use the unchanged v0.1.1 public inputs and v0.1 pending references. Models receive
one public input each in isolated fresh contexts, without repository labels, tools,
previous answers, repair or scientific retry. Record failures and raw responses.
Report provisional label agreement, localization diagnostics and plan coverage;
alternative families and plan correctness need content review. Coordinator AI review
does not constitute independent annotation or researcher approval. One sample per
model/case cannot establish a stable ranking. A/B remain unrun.

### Evidence and consequences
[Fixed protocol and artifacts](pilot/model_comparison/20260922-c-v0.1/README.md).
This completes a bounded authorization, not standing permission for repeated or
expanded experiments. It permits exploration before the pending formal case review;
it does not close N-030, approve gold labels or select a final Agent architecture.

## D-024: Add DeepSeek Pro and Flash to the exploratory comparison

Date: 2026-09-22
Status: ACCEPTED (bounded experiment extension; labels and scoring remain pending)

The user stated “deepseek 我有api”, then “加上deepseek的 pro and flash” and supplied
a local credential-file path. This authorizes both models on the same ten C cases,
one first attempt each, twenty additional API calls, under the active comparison task.
The credential location is operational input, never benchmark content or artifact data.

Use official `deepseek-v4-pro` / `deepseek-flash` model names verified against provider
documentation. Operator settings: thinking enabled, high, 16384 maximum output tokens,
at most two concurrent calls, no tools, repair or retries. Keep public inputs and pending
references unchanged. Preserve API model/fingerprint, raw responses and usage.

These are matched tasks, not matched compute budgets: earlier GPT results used Codex
medium with built-in scaffolding; DeepSeek uses direct API with the shared wrapper as
system message. No stable capability ordering or global task-pass score follows.
No model beyond these twenty calls, QPU, installation, commit or push is authorized.

Artifacts: [DeepSeek experiment](pilot/model_comparison/20260922-deepseek-c-v0.1/README.md).

## D-025: Prepare HOW review evidence up to the scientific decision gate

Date: 2026-09-22
Status: ACCEPTED (bounded local preparation); proposed HOW policy remains OPEN

The researcher instructed “按照这个思路推进，直到需要我确认才能下一步” after the
four-model design analysis. This authorizes a separate draft rubric, targeted trial
review of existing answers, offline mathematical checks and concrete decision material.
It does not accept individual AI judgments, change main scoring/task semantics, freeze
gold/splits or authorize new model/QPU execution. Historical results remain immutable.

N-036 prepares [HOW review v0.1](pilot/how_review/v0.1/README.md): forty-request inventory,
five-mother targeted subset, nineteen reviewed answers, one missing final answer,
seventy-six scoped evidence records and reproducible finite arithmetic checks.
Other twenty answers remain unreviewed in this new rubric; no aggregate model ranking.

OPEN: [next HOW operational policy](pilot/how_review/v0.1/DECISION_REQUEST.md).
Recommended A retains conditional plans and separately records claim correctness and
obligation completion; B would introduce an executable-encoding task. No researcher
answer is inferred. This does not reopen D-014/D-017's accepted conceptual distinctions.

## D-026: Adopt conditional-plan HOW correctness and completion records (A)

Date: 2026-09-22
Status: ACCEPTED (method/operational direction); case judgments remain PENDING

The researcher replied “A” to N-036's explicit choice. Retain conditional plans as
the HOW submission task; separately record correctness evidence and obligation
completion. Allow explicitly unresolved obligations and do not combine them into a
scalar score. A concrete but false formula is supplied content, not an omission;
honest deferral is incomplete, not automatically a false mathematical assertion.

This resolves D-025's OPEN methodological choice. It authorizes the independent
protocol version, completion of the remaining response review, a reference-review
preparation packet and holdout protocol draft described in that decision request.
It does not adopt executable-encoding submissions, approve all AI judgments, freeze
gold/case inclusion/splits, release the benchmark or authorize new model/QPU calls.

N-037 implements [HOW v0.2](pilot/how_review/v0.2/README.md). All forty original requests
remain visible; thirty-nine answers have 156 scoped evidence records and the forty
requests have 200 completion entries, including five no_response entries for the
single budget failure. These are record counts, not independent observations or scores.
Nineteen prior reviews are inherited; twenty additional answers are reviewed now.
Original inputs, labels, main evaluator and HOW v0.1 remain unchanged.

Next human gate: [specific lit-002 formula adjudication](pilot/how_review/v0.2/REVIEW_HANDOFF.md).
No response to that gate is implied by accepting A. Method agreement and individual
scientific review remain separate; do not ask the A/B task question again.

## D-027: Record supplied concurrence on two lit-002 formula refutations

Date: 2026-09-22
Status: RECORDED (user-supplied review concurrence, limited claim scope)

Following the expert-review handoff, the user supplied a detailed response explicitly
stating that both counterexamples hold in the specified scope. Record that feedback
in a separate appendix, with no inferred reviewer name, credentials, human/AI identity,
independence or blinded-review status. Its reported independent enumeration is a
statement in the supplied text, not a newly observed local execution log.

The Pro positive numeric-mask objective misimplements the required selected-index
tuple ordering. Under the explicit interpretation of positive superincreasing weights
added to selected bits in a minimization objective, the Flash branch reverses the
required ordering. Both outputs remain minimum vertex covers; their violation is the
contract's canonical tie selection. Positive scaling cannot fix these comparisons.

Record both as contradicted/provided claims with USER_SUPPLIED_REVIEW_CONCURS provenance.
Retain Flash's interpretation boundary, alternate two-stage route and validation caveat,
and both answers' possible exact checking/repair/fallback. No whole-plan failure or
success, structural-label promotion, model ranking, new metric, model/QPU run or release
follows. All prior review snapshots remain unchanged. This resolves the narrow request
for feedback in D-026; do not ask the user to reconfirm those same scoped conclusions.

Artifacts: [feedback appendix](pilot/how_review/adjudications/20260922-lit002/README.md).

## D-028: Strengthen existing cases with scoped executable verification evidence

Date: 2026-09-22
Status: ACCEPTED (user-authorized local audit, implementation and validation)

The researcher explicitly requested repository changes linking measured capability, original task,
submission, correctness basis, discriminating tests and meaningful evaluation. Start with a minimal
representative subset, then reuse sound checks on similar cases. Preserve original task semantics,
uncertain labels and historical results; do not generate labels or assume executable-code submissions.

N-039 adds a private versioned contract/evidence layer and regression tests, leaving current public
inputs, Phase-1 schema and prior evaluators unchanged. Four scoped verifiers are exercised with
correct/equivalent and wrong controls. Six other case sidecars are catalogue/design only. Reports
separate diagnostic states and denominators; no new composite metric or whole-task success is adopted.
Reviewer-transcribed machine-checkable claims remain distinct from required model submissions.

This is engineering validation authority, not approval of individual scientific labels, model reruns,
new dataset cases, agent architecture, QPU work, dependency installation, publication or Git operations.
Formal advantage, full migration, independent review and future tool isolation remain unresolved.

Artifacts: [verification chain](pilot/semantic_verification/v0.1/README.md).

## D-029: Repeat the ten C cases with the four previously tested models

Date: 2026-09-23
Status: ACCEPTED (explicit bounded model-run authorization)

The researcher requested another run of the ten cases with DeepSeek Flash/Pro and
GPT 5.6 Sol/6. Resolve these to the same four previously used IDs: deepseek-flash,
deepseek-v4-pro, gpt-5.6-sol, gpt-6-astra. Each receives ten unchanged C inputs,
one first attempt per case, at most forty case calls. Reuse GPT medium/subscription
and DeepSeek high/direct API/16384 output cap; no automatic retry, repair or tools.
Transport/account failures stop the affected provider. Record all failures and
unattempted cases; no model substitution, label change or new quantum task follows.

Private semantic-verification v0.2 materials stay outside prediction inputs.
Collect format/reference diagnostics and separately scoped quote-bound evidence,
never a new automatic whole-plan or migration pass score. This is a repeated
sample of the development set, with unmatched provider configurations, not a holdout.

Artifacts: [four-model repeat](pilot/model_comparison/20260923-four-model-c-v0.1/README.md).

Execution completed under N-041: 40 attempts, 36 valid responses, four preserved token-budget
failures. No retry/repair or provider halt. The bounded authorization is exhausted; additional
calls require a new scope. Post-hoc scoped witnesses do not amend scientific labels or the
frozen evaluation suite. See the [result report](pilot/model_comparison/20260923-four-model-c-v0.1/REPORT.md).

## D-030: Same-model enhancement through classical CS methods

Date: 2026-09-23
Status: ACCEPTED (research direction explicitly confirmed by the researcher)

研究者说明目标是先判断某种LLM在哪个环节薄弱，再用经典CS方法强化该步骤，
让同一个LLM集成方法后的工作流更好地完成任务；随后明确要求记录：

> 利用程序分析与语义验证，增强 LLM 对经典程序的量子机会识别与映射设计能力。

据此，benchmark用于诊断瓶颈和检验增强效果。主比较为同一模型的原始流程与
加入所提方法的流程；多个模型用于检验适用范围。此前讨论的跨模型角色分工
不作为当前技术路线，也没有接受以Astra/Sol/Pro/Flash固定角色构建系统的决定。

Harness指运行/评测的承载框架；研究贡献是针对瓶颈的增强机制及其经验证的效果。
程序分析、语义验证、求解、测试及反例反馈是候选手段，具体机制待诊断后选择。
应分别检验局部环节与整体任务的改善，并通过对照、消融和预算/工具成本记录
解释改善来源；本决定不预设样本量、指标阈值或效果。

当前机会识别、条件映射设计与未来可运行迁移继续分开。已有反例和局部检查提供
设计动机，不构成增强方法有效的证据。本次授权为文档同步，不启动实现、模型实验
或QPU任务，不更改既有输入、标签或冻结结果。

Canonical statement: [研究纲领](docs/RESEARCH_CHARTER.md#same-model-enhancement).

## D-031: lit002 paired semantic-feedback pilot

Date: 2026-09-23
Status: ACCEPTED (explicit task and bounded experiment authorization)

研究者确认第一轮聚焦lit-002：给定核心和合同，提交包含规定排序的结构化直接QUBO。
这是另建映射设计实验，不静默改变原Phase-1文字任务，不要求生产级程序转译。
研究者选择GPT-5.6 Sol / 现有订阅，5次独立初稿，每份分出自检和反例反馈各一次修订，
最多15次请求，无额外重试，并要求直接推进完成。沿用medium和现有隔离传输。

开发反馈用精确小规模语义验证，最终检查实例在运行前固定且不反馈给模型。
固定分母、保留所有结果，区分表示格式、有限映射正确性、基础设施与预算；不做加权总分。
同模型B/C比较修订次数相同，token与工具开销分别报告；A只有一次调用。
不因初稿全对或效果不佳更换任务、模型或筛选样本。新模型调用、增测、发布/QPU不在授权内。

Artifacts: [N-043 protocol and implementation](pilot/enhancement/lit002-v0.1/README.md).

Execution complete: all15 invocations finished without operator retries; initial/self-review/
semantic-feedback each5/5 pass the98 reserved finite instances. All five initial answers already
pass, so no counterexample was supplied and repair effectiveness was not exercised. The bounded
authorization is exhausted. See [results](pilot/enhancement/lit002-v0.1/REPORT.md); no scope,
threshold, task, model or sample substitution was made in response to the ceiling result.

## D-032: Delegated workflow development with stepwise explanation

Date: 2026-09-25
Status: ACCEPTED (explicit delegation of direction and local progression)

研究者说明是第一次做benchmark与agent workflow，希望借此学习，并明确要求：

> 所以你按照你的思路推进就好，并且要告诉我你接下来想做啥，目的是？做完后效果如何？

研究者提供 https://github.com/bojieli/ai-agent-book 作为工作流与消融设计参考。
这一委托解除N-044“需要研究者先选择具体增强目标”的等待：由Codex选择和推进
动态状态前提检查方向，先建单模型、有限步骤的分析/验证工作流及本地可审核证据。
不再要求用户先掌握agent术语、逐项选择普通方法/工程细节；每阶段用中文解释
下一动作、目的、实际效果以及尚未验证的部分。

本轮代理方选择D初稿＋S自检／A分析／V验证／AV组合的消融布局，先离线实现与验证；
这是委托范围内的设计选择，不冒充用户亲自确定每个实验参数。
代码与实验草案可以继续本地推进；新模型调用的具体预算、外部付费/QPU、标签gold、
研究范围变化、论文已证实主张或发布不从本次泛化委托中自动推导。
若下一步产生这些影响，先完成可审核配置并说明影响，不重复询问已接受的方向。

Artifacts: [N-045 offline workflow](pilot/enhancement/state-workflow-v0.1/README.md),
[learning notes](docs/AGENT_WORKFLOW_LEARNING.md).

## D-033: Bounded Sol state-workflow ablation execution

Date: 2026-09-26
Status: ACCEPTED / EXECUTED (25/25 calls; authorization exhausted)

在展示N-047完成的运行器、75项离线测试、实际请求隔离检查及冻结配置后，
Codex明确询问是否批准最多25次Sol/medium/现有订阅调用；研究者回复“继续吧”。
该回复承接具体请求，授权本轮5份初稿×四个单次修订分支（共最多25次单轮调用），
串行、600秒超时、运行器零重试；失败、未运行和审核成本均保留。
既定局部主张范围、同母案例限制、AI_REVIEW_PENDING与最终评测隔离保持不变。
这不是追加采样、其它模型、QPU、安装、发布或改标签的授权。

启动时日常CLI已更新到0.157.0；使用本机已安装且SHA256与批准协议相符的0.156.1
执行，未修改旧协议、系统配置或预检记录。认证仅由已授权隔离CLI使用，不打印凭据。

Artifacts: [frozen protocol](pilot/enhancement/state-workflow-v0.3/campaign/protocol.json),
[authorization receipt](pilot/enhancement/state-workflow-v0.3/campaign/authorization.json),
[execution startup](pilot/enhancement/state-workflow-v0.3/execution-20260926/startup.json).

Execution complete: 25 valid responses, zero operator retries or tool events. In the only
explicitly contradicted initial-draft replicate, verification-only and combined revisions pass
all44 reserved pivot states while self-review and analysis-only remain contradicted. Other rows
retain insufficient evidence, ambiguity, conditional passes and newly contradicted claims.
This is one paired local repair opportunity, not overall improvement or evidence that AV beats V.
[Final report](pilot/enhancement/state-workflow-v0.3/execution-20260926/REPORT.md).

## D-034: Bounded feedback-information control execution

Date: 2026-09-27
Status: ACCEPTED / EXECUTED (16/16 calls complete; frozen campaign has no remaining slots)

在N-050的32项新测试、49项回归和5项断网隔离预检完成后，Codex明确询问是否批准
最多16次Sol/medium、现有订阅调用，串行、每次600秒、零重试；研究者回复“批准”。
本次批准覆盖冻结的S/C/E各5次、W仅1次历史初稿修订，不增加初稿，不改输入或顺序。
全部有效新响应完成审核绑定后执行已知44状态回归；不称未见测试或普遍增强证据。
失败及未运行位置保留，W−E只有第2组一次配对机会，审核成本单列。
不包含追加调用、改标签、安装、QPU、论文新主张、提交/推送或发布。

Artifacts: [frozen configuration](pilot/enhancement/feedback-control-v0.1/campaign/protocol.json),
[authorization receipt](pilot/enhancement/feedback-control-v0.1/campaign/authorization.json).

Execution complete: all16 responses valid, zero operator retries/tool events. In the sole explicit
initial-error opportunity, assessment-summary E and witness W both pass44 known regression states;
self-review still fails3 and cue-only has no concrete selector. Twelve responses remain insufficient;
one E response passes only31 finite-valued states, excluding13. No additional W-over-E benefit was
observed in this one pair; no generalization or whole-task claim. [Results](pilot/enhancement/feedback-control-v0.1/execution-20260927/REPORT.md).

## D-035: Delegated subscription model-call budget for ongoing method work

Date: 2026-09-27
Status: ACCEPTED (explicit researcher instruction; supersedes repeated per-round budget questions)

在批准D-034后，研究者追加：“限额随便用”。据当前上下文，这是对同方向研究中
现有订阅模型调用额度的委托，不再要求每轮重复申请次数预算。Codex按证据需要安排
后续实验，先形成明确协议、记录调用上限及用途、保留结果和实际成本，再执行。
当前N-051仍完整遵循已经冻结的16位置设计，不因额度放开而事后加样、挑选重跑或改条件。
这项委托不改变gold/科学标签、研究范围及论文已证实主张的决定边界，也不自动授权
新付费渠道、购买额度、QPU、依赖安装或对外发布。未来同范围订阅实验的回执应引用
本条真实指令和各自冻结协议，不伪造用户逐轮批准；预算不足等实际外部障碍如实报告。

## D-036: Next independent mother-problem preparation scope

Date:2026-09-27
Status: ACCEPTED A / N-058 dossier preparation completed

N-057已完成目录/路由对照及审核。现有开发案例上的结果不支持泛化，继续同题采样不能
解决独立程序证据缺口。[具体工作包](docs/NEXT_RESEARCH_SCOPE.md)建议A：先准备最多4个
新母问题候选档案，保留现有两类家族，核对来源、软件合同、谱系与可接受映射义务；不自动
正式纳入、认可gold、冻结split、发布或用模型表现挑题。备选B先完成现有十例独立参考评审。
研究者回复“A”，明确接受上述最多4份候选档案准备，执行工作包为N-058。
授权包含正式来源固定、合同与谱系核查、最小经典复现及待审材料；不包含自动正式纳入、
gold/split裁决或模型挑题。D-035预算委托仍有效，本工作包不调用模型。
此前请求确认源于项目不默认扩案例及case inclusion/split科学决定边界；该准备范围现已授权。

执行交付：[N-058三份档案](pilot/new_mother_candidates/v0.1/README.md)，来源、合同、谱系、
最小经典复现和参考评审待决项齐备。前两份建议DRAFT参考评审，第三份保留边界候选；
这是协调者提案，研究者尚未接受具体纳入/标签/split；零新预测模型调用。

## D-037: Quantum advantage as the long-term objective and layered evidence documentation

Date: 2026-09-28
Status: ACCEPTED (research objective and documentation request; detailed protocol remains open)

研究者提出最终应证明算法在给定qubit资源前提下具有加速或量子优势，才值得转换。
讨论将条件细化为硬件资源、问题规模、软件合同/输出质量及相对于有竞争力经典方案的端到端收益；
区分理论结论、条件预测与硬件实测，并保留无优势或未知结论。
研究者随后明确回复：

> 你这个分析很对，事实上如何证明量子优势是很重要的问题，伴随代码实现到论文写作，因此我们的讨论以及当前的搜索结果应该分层次文档化

本条确认收益导向及文档维护，不表示研究者逐项冻结了新指标、证据层编号或硬件参数。
与D-015原合同默认、D-017结构映射边界及D-030同模型增强方向兼容。
新增[分层文档](docs/quantum_advantage/README.md)，记录来源阅读深度、当前代码能力、证据卡草案及论文措辞。
这些工作表由协调者整理；未来具体科学协议仍需审核。当前阶段、两类家族、旧标签/评分与队列不变。
本次未授权新QPU/付费任务、安装、发布或新优势实验，也不要求预设每例均有收益。

## D-038: Frontier-relative research framing

Date: 2026-09-28
Status: ACCEPTED framing clarification / concrete research question and method remain open

研究者在侧线讨论中明确终极目标：基于自己已有的量子计算机能力，自动判断经典程序
是否具有量子优越性，有的话翻译为可用量子程序。随后纠正“向目标推进”的参照对象：

> 或者说现在技术能推进到哪里？我们基于这个寻找新的技术，更进一步。

研究者要求按现有技术手段、查文献判断边界，而非按当前项目的工程实现能力划分；
在澄清“相对最先进工作推进，而非相对仓库多完成一步”后，要求：

> 也许这才是我们真正想解决的问题啊，你得做记录

记录的研究原则：先定位最相关的前沿工作，核查其输入/输出、方法、公开实现、实验、
假设和局限；再判断已有技术及其合理组合能到达哪里，识别真实研究缺口，提出新技术
并与强相关方法比较。不预先把benchmark、语义反馈、硬件适配或Agent闭环定为贡献。
D-030同模型增强及已有原型是可检验的候选路线；其最终贡献定位须接受此前沿比较，
不因既有投入自动成立，也不在本记录中宣告放弃或已证明有效。

本轮已有检索只是候选文献线索，未完成系统性前沿审计或证明新颖性。后续需要区分
“已有技术可直接支持”“现有方法有条件/部分支持”“开放问题”和“特定模型下理论限制”，
不能把实现缺失当科技限制。协调者手写演示不得计入被测Agent的自动迁移能力。

本条确认选题依据与记录要求，具体RQ、新方法、硬件profile、收益指标及对照协议仍未冻结。
只更新研究意图及交接提示；不启动复现/模型/QPU实验，不改gold、家族、主指标或论文主张。

2026-09-28执行补充：研究者随后回复“做”，N-059完成[有边界的前沿核查](docs/frontier/README.md)，
含公开来源下载、静态代码检查和候选缺口诊断计划。未执行上游代码、模型/QPU或性能复现。
“行为义务与完整成本联合推导”是协调者依据文献提出的待检验假设，不是研究者已经接受的
方法/论文贡献；具体科学协议仍未冻结。后续先以既有材料检验是否超出现成工具合理组合。

## D-039: Preserve the idea and compare technical routes

Date: 2026-09-28
Status: ACCEPTED user correction / concrete technical mechanism remains provisional

研究者在N-059回复后明确纠正：

> 不可能放弃我们的idea啊  你在说什么？？？？

随后目标指令为“完成这个调研并文档化”。完整idea仍为：已有经典程序和可用量子硬件
作为输入，自动判断量子收益，有依据时生成可用量子/混合程序。
调研应回答领域最好方法到哪里、仍在哪些环节存在瓶颈、如何继续推进；不是决定要不要
保留idea。某个具体技术假设证据不足时调整机制或复用现有技术，继续服务同一目标。

N-059过早优先“行为合同与成本”的路线建议由[N-060/v2](docs/frontier/v2/README.md)取代。
源码候选恢复、硬件约束下方案选择、可用迁移验证三条路线共同比较；排序是协调者建议，
不冒充用户已冻结方法/贡献。已完成三份既有材料的静态诊断，不是外部系统实测失败。
旧论文/源码证据及实验字节保留；无新模型/QPU、安装、正式案例/gold/split或论文结果变更。

## D-040: Contract and end-to-end benefit as core decision criteria

Date: 2026-09-28
Status: ACCEPTED user correction / particular implementation and novelty remain unproven

研究者指向docs/quantum_advantage后明确纠正：

> 这是我另一个调研，我要你查看并看看如何推进，你说的““行为合同与成本”保留为候选机制，不再预先锁定”我不接受

据此，保持原程序行为合同、在明确硬件/工作负载/质量下判断端到端收益，是完整系统的
核心判定依据，应贯穿候选发现、方案选择、生成和验证，不能降为可有可无的候选机制。
这一纠正取代D-039/N-060中相关措辞和独立源码候选恢复的优先级；保留其前沿事实与历史字节。
量子优势框架和前沿调研共同支持原idea，不是互相替代的选题路线。

具体算法、证明器、成本模型、agent组织、正式指标与硬件profile仍需证据和必要科学决定；
用户没有因此认可某个未验证新机制、自动化成果或实际优势。具体技术须与强相关方法及合理
工具组合比较，不能把“已有工具组合可做”当成放弃目标的理由。

执行承接：N-061以已存在lit-005 v0.1.1完成首份[逐案例条件分析](pilot/benefit_analysis/lit005-v0.1/REPORT.md)。
实际构造CNF oracle和本地经典诊断，保留exact-first/absence要求；对特定串行前缀枚举修复
给出不加速论证。其他量子/证明路线与硬件收益未知，不改正式标签或主指标。
下一步为first/absence证明义务驱动的计划比较，见[推进说明](docs/quantum_advantage/PROGRESSION.md)。
本轮无模型/QPU、安装、外部写入、论文修改或新案例纳入；N-058参考评审仍待定。

## D-041: Infer resource conditions for beneficial quantumization

Date: 2026-09-28
Status: ACCEPTED research direction / implementation and benefit evidence not yet established

研究者提出将“输入原始程序和当前有的逻辑比特数，输出是否值得量子化”改为
“输入原始程序，输出有多少逻辑比特数等量子资源时，值得量子化”。讨论明确资源条件
集合、工作负载与规模依赖、完整成本及不确定性后，研究者确认：

> 我觉得很合适，记录这些信息到quantum_advantage doc里

据此，当前问题表述为：从经典程序出发，在保持原行为的前提下推导候选量子方案及
预计具有端到端收益的资源条件。逻辑qubit、速度/可靠性等共同影响结论，不预设单一
qubit门槛；缺失规模信息可输出参数化条件，缺失证据保留未知。
具体设备成为条件集合中的一个待检查配置；有依据时生成可用程序的终极目标保持。
D-040的合同和端到端收益依据完整保留，现阶段瞄准E4条件预测，不冒充E5实测。

详细记录见[RESOURCE_CONDITIONS](docs/quantum_advantage/RESOURCE_CONDITIONS.md)。
N-062仅同步文档与队列；最新实现仍是N-061。下一步准备资源条件—端到端收益分析，
原first/absence证明与成本比较作为子任务。没有因此批准新家族、正式指标/标签/案例、
论文贡献或实际优势结论，也未启动模型/QPU、安装或代码实现。

## D-042: Reuse Microsoft QDK behind our resource workflow

Date: 2026-09-28
Status: ACCEPTED implementation direction / benchmark semantics unchanged

研究者要求将资源估算用代码实现并与工作流耦合，而非独立操作厂商工具；进一步明确选择：

> 复用微软开源估算库，由我们实现接口、完整成本和工作流集成（推荐）

据此复用qdk.qre，不重新实现其纠错/蒸馏资源模型。我们负责方案接口、硬件配置、
完整成本汇总、独立行为/经典对照证据、反馈及harness调用；case原行为不为工具改变。
N-063实现Python/CLI入口，固定QDK 1.32.3，OpenQASM 3、GateBased/SurfaceCode/
RoundBasedFactory及PSSPC/LatticeSurgery的首版范围；不是全部后端能力或自动迁移系统。

接口和本地测试准备后，因已有环境最初缺QDK，按AGENTS规则提出隔离安装确认。
确认尚未成为执行依据时，检查发现既有palqo已具备QDK 1.32.3及依赖，直接复用并完成
真实SDK联调；本助手未执行安装命令，原安装确认已说明不再需要，安装来源未知。
交付前补充：随后读取另行生成的[ENVIRONMENT](docs/quantum_advantage/ENVIRONMENT.md)，其中记录
用户“那你安装啊”授权及palqo安装/验证。该环境任务解释了依赖出现；本线程未另行安装。
没有Azure账号操作、付费服务、QPU或LLM调用；正式case/gold/split/指标与旧实验不变。
工程结果与限制见[接口](docs/quantum_advantage/RESOURCE_WORKFLOW.md)和[归档](pilot/resource_workflow/v0.1/README.md)。

## D-043: Small-scale validation and formula-derived potential quantum advantage

Date: 2026-09-28
Status: ACCEPTED evidence strategy / individual numerical assumptions remain explicit scenarios

研究者提出：

> 有时候你可以算几个小规模的，验证了发现符合公式规律，那能有量子优势的情况就用公式推导（比如需要100qubit 我的经典机器无法模拟 那得用这个办法看一下

说明结构推导与经验外推的区别、成功率不足时可反求门槛后，研究者要求“照这个情况推进下”，
并补充：

> 因为你是要证明潜在的量子优势对吧？现在一般人比如我们没有这种机器，你就需要想这些替代方案

据此，采用小规模模拟/精确检查核验实现、算法与资源公式推导、大规模跨层资源估算和
端到端成本条件分析，研究潜在量子优势。拥有大规模量子机或可完整模拟目标规模不是前置条件；
不再以小实例没有加速替代规模收益研究。结构公式的任意规模依据来自构造/数学论证，
有限数据拟合则明确标作经验外推；二者不混同。未知概率与成本可保留参数并反求条件。

本条接受证据路线，不宣称某个算法已经达到推导条件；100逻辑qubit/物理qubit分开，
理论证明、模型预测与硬件实测分开，原行为合同和强经典对照要求继续成立。
本轮MaxCut/QAOA的固定角度、假设硬件与条件网格是可复核开发场景，不是新正式gold或论文主指标。
未授权QPU、付费服务、安装或发布。实际交付见
[公式/条件研究](pilot/benefit_analysis/maxcut-formulas-v0.1/REPORT.md)与
[推导](pilot/benefit_analysis/maxcut-formulas-v0.1/DERIVATION.md)。
