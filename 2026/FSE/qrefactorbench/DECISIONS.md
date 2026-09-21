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
