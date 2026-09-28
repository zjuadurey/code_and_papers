# TODO

Long-term backlog, not the session execution queue. Start at
[NEXT_ACTIONS.md](NEXT_ACTIONS.md); completed items below are historical milestones.
Unchecked research items are not automatic implementation/model-run authorization.

## P0 — Blocking

- [x] Complete initial evaluator, CLI and case scaffolding; run validation.
- [x] N-004: fix packet byte identity using versioned instructions instead of mutable
  README; frozen packets unchanged. Modified/missing-README regressions pass;
  latest full suite 89 passed/3 optional skips, separate optional suite 5 passed.
- [ ] Human review D-004, D-005, D-006 before using metrics in a pilot study.
- [ ] Operationalize candidate inclusion/boundary criteria under D-016: WHERE may
  nominate subsequently rejected regions. Q14's direction is decided; no relabeling.
- [x] Resolve Q17's pilot-009 public-domain/code contradiction in pilot-v0.1; preserve originals.
- [ ] Choose infrastructure license and resolve per-case redistribution rights.

## P1 — Important next steps

- [x] N-063 / D-042: integrate pinned Microsoft QDK through a local callable/CLI resource tool,
  controller-owned cost context and conditional feedback; real SDK smoke,30 focused tests,
  full253 passed/15 optional skips. [Interface](docs/quantum_advantage/RESOURCE_WORKFLOW.md).
- [x] N-062 / D-041: record the accepted shift to inferring resource conditions for beneficial
  quantumization from classical programs; [specification](docs/quantum_advantage/RESOURCE_CONDITIONS.md).
- [ ] Prepare the first resource-conditions / end-to-end-benefit analysis with workload assumptions,
  competitive classical comparison, complete costs and uncertainty; no assumed single qubit threshold.
- [x] N-061 / D-040: make contract and end-to-end benefit core decision criteria;
  complete [lit-005 analysis](pilot/benefit_analysis/lit005-v0.1/REPORT.md), logical oracle,
  finite exactness checks and scoped no-speedup proof for serial prefix-enumeration repair.
- [ ] Prepare first/absence proof obligations, plan/certificate cost comparison and strong
  incremental-SAT adapter protocol; subtask of D-041 [resource-condition analysis](docs/quantum_advantage/PROGRESSION.md).
- [x] N-059: frontier audit with pinned public evidence and static source inspection complete;
  [report](docs/frontier/README.md). No performance reproduction or new model/QPU run.
- [x] N-060 / D-039: preserve the full idea, extend the frontier audit, compare three technical routes,
  and complete static diagnostics on N-054 and N-058 C01/C02. [Current report](docs/frontier/v2/README.md).
  Supersedes N-059 route priority; no external-system failures or new method efficacy demonstrated.
- [ ] Prepare support-aligned C2Q / pattern-matching / QPipe-style adapters and a bounded diagnostic
  protocol for source-to-candidate identification; keep native versus adapted baselines explicit.
  Retained downstream work; N-061 supersedes its isolated first priority.

- [x] N-052: single generic claim-elicitation interface, paired ten-slot protocol;32 focused tests,
  49 regressions and5 offline preflight checks pass. No checker/schema/gold changes.
- [x] N-053: ten-call S/F diagnostic under D-035 complete; one F44-state pass and one guarded
  31-pass/13-excluded result. S contains two contradicted local claims (one secondary).
  F's explicit QUBO is outside the frozen checker; both arms still have3 insufficient rows.
  Ten exact replays and3114 old hashes match; [report](pilot/enhancement/claim-elicitation-v0.1/execution-20260927/REPORT.md).
- [x] N-054: quote-bound rank-QUBO audit;31 known finite states plus1704 post-hoc synthetic states
  pass,13 excluded;72990 assignments checked,18 tests and exact replay pass,3285 old files unchanged.
  Original N-053 result retained; mathematical P>0 argument is not hardware/benefit or gold evidence.
- [x] N-055: neutral analysis entry for empty/function/region/statement nominations, preserving
  declared region, analysis scope and seed.31 tests plus49 regressions pass; five historical packets
  use only public source,3298 old files unchanged. No model effect claim.
- [x] N-056: freeze S/C/R15-position control;112 combined tests and5 offline preflight checks pass.
- [x] N-057: all15 positions complete and valid; nomination changes separated from correctness.
  No clear R-over-C benefit; new contradicted and ambiguous claims retained. Exact replay and3312
  protected hashes match. [Report](pilot/enhancement/candidate-routing-control-v0.1/execution-20260927/REPORT.md).
- [x] D-036: researcher chose A; bounded candidate-dossier preparation authorized.
- [x] N-058: three source-pinned dossiers, old-ten lineage comparison, classical reproduction and
  review checklist complete;3555 old hashes unchanged. [Deliverable](pilot/new_mother_candidates/v0.1/README.md).
- [ ] Review N-058 specific admission/contracts and reference/evaluation roles before formal cases,
  gold or split; no model-based selection. C01/C02 proposed for DRAFT review, C03 boundary candidate.

- [x] N-043 / D-031: implemented and ran the separate lit-002 structured-QUBO paired
  pilot with GPT-5.6 Sol: 15/15 calls, initial/self-review/semantic-feedback each 5/5
  finite passes. All initial answers correct; zero actual counterexamples, no evidence
  of improvement or measured repair ability. 26 new tests; 223 repository tests pass,
  15 optional skips. [Report](pilot/enhancement/lit002-v0.1/REPORT.md).
- [x] N-044: reviewed Sol lit-009 transcription, reachable state and fallback scope;
  replayed seven old pivots and six sensitivity-probe pivots. Prepared a bounded
  [dynamic-state analysis proposal](pilot/enhancement/lit009-review-v0.1/README.md); no new model run.
- [x] D-032: researcher delegated method/workflow progression and requested explanations of
  next action, purpose and actual effect; no longer blocked on beginner architecture choices.
- [x] N-045: offline single-model workflow with lexical state inventory, bound development
  feedback and four revision branches; 12 checks pass, zero model calls.
  [Implementation](pilot/enhancement/state-workflow-v0.1/README.md),
  [learning notes](docs/AGENT_WORKFLOW_LEARNING.md).
- [x] N-046: explicit new-response quote bindings, bounded predicate/scan interpretation,
  ambiguity/guard/unknown/withdrawal handling and separate development/reserved checks.
  37 new + 12 prior tests pass; two correct/equivalent and five erroneous controls discriminate.
  [Report](pilot/enhancement/state-workflow-v0.2/README.md). Reviewer transcription remains necessary.
- [x] N-047: wired the 25-slot protocol to isolated transport, verified recovery/failure retention,
  final-binding barrier and model-visible allowlists. 26 new + 49 regression tests pass;
  CLI 0.156.1 local request capture has zero tools after scoped catalog overrides.
  [Protocol, preflight and handoff](pilot/enhancement/state-workflow-v0.3/README.md).
- [x] N-048 / D-033: ran all25 approved Sol/medium subscription calls. One explicitly wrong initial
  yields local V/AV repairs across44 reserved states; S/A still fail in that replicate. Unknowns,
  ambiguity, guarded scope and newly wrong claims are separate; no whole-task or universal uplift.
  [Results and audit](pilot/enhancement/state-workflow-v0.3/execution-20260926/REPORT.md).
- [x] N-049: mapped25 responses/90 anchors, audited5 candidate entries and prepared16 offline S/C/E/W
  prompts. Missing-rule, nomination, range, QUBO and ambiguity routes remain design-only; old44 states
  are now known regression data. [Design](pilot/enhancement/state-workflow-design-v0.1/README.md).
- [x] N-050: adapted16-slot feedback control with retained transport, failure handling and review gates.
  32 new +49 relevant regression tests pass; complete fake-transport rehearsal and5 offline isolation
  checks pass. [Ready configuration](pilot/enhancement/feedback-control-v0.1/README.md).
- [x] N-051 / D-034: executed all16 feedback-control calls, all valid. E/W both pass44 known states
  for the sole explicit initial error; no additional W benefit observed,12 responses insufficient.
  [Results](pilot/enhancement/feedback-control-v0.1/execution-20260927/REPORT.md).
- [x] D-035: researcher delegated same-direction existing-subscription model-call budget ("限额随便用").
  Future concrete protocols may proceed under this delegation without repeated per-round budget requests.
- [ ] Implement N-049's single-step missing-information elicitation with an equal-call self-review
  control; validate offline before a new protocol. Preserve unknowns, alternate families and old results.
- [x] N-042 / D-030: record the researcher-confirmed direction: diagnose weaknesses and
  enhance the same LLM with program analysis and semantic verification. Harness is the
  execution framework; mechanism choice and improvement evidence remain open.
  [Canonical direction](docs/RESEARCH_CHARTER.md#same-model-enhancement).
- [ ] Extend the N-043 local mapping prototype toward the broader weakness-to-method
  study; distinguish stage improvement, overall outcome and added budget. Production-code
  program analysis and migration remain unimplemented.

- [x] N-041 / D-029: forty C repeat requests completed, 36 valid and four budget failures.
  Seven quote-bound objectives pass 38 finite checks; a post-hoc reachable-NaN witness
  contradicts Sol/Pro lit-009 predicates without refuting their fallback plans. 28 offline tests pass.
  [Report](pilot/model_comparison/20260923-four-model-c-v0.1/REPORT.md).
- [x] N-044: source-level review of N-041 witness and 009/010 validation-scan nominations;
  recorded singleton transcription sensitivity and Sol010 missing-entry prose ambiguity.
  Formal candidate acceptance, whole plans and deployment benefit remain unjudged.

- [x] N-039: audit current task/loader/scoring and baseline tests; add ten private contract
  sidecars and four scoped definition-based verifiers with 23 inputs, 8 passing correct/
  equivalent controls and 10 rejected semantic mutants. 42 regression tests pass.
  [Scope and evidence](pilot/semantic_verification/v0.1/README.md); not whole-case gold or migration success.
- [x] N-040: extend scoped control verification to the remaining six cases. Ten mothers,
  61 inputs, 22 accepted correct/equivalent controls and 30 rejected mutants; 84 new tests pass.
  [Versioned extension](pilot/semantic_verification/v0.2/README.md); preserve the old four scopes.
- [ ] Review transcription fidelity, other alternate mappings/boundaries and full context
  obligations; scoped checks do not establish whole-task or quantum migration success.
- [x] N-036: prepare HOW claim/obligation rubric, five-case four-model trial review
  (19 answers, one preserved budget failure), exact-response provenance and finite
  arithmetic evidence. [Review package](pilot/how_review/v0.1/README.md).
- [x] D-026: researcher chose A, retaining conditional plans and separate correctness/
  completion records, no scalar score. Individual labels remain pending.
- [x] N-037: implement independent HOW v0.2, complete all 39 answer review records,
  preserve the budget failure, prepare the reference-review packet and holdout draft.
  [Package](pilot/how_review/v0.2/README.md). No new model run or gold promotion.
- [x] N-038: archive user-supplied review concurring with both narrow lit-002 formula
  refutations; preserve interpretation/fallback limits and unknown reviewer identity/
  independence. [Feedback](pilot/how_review/adjudications/20260922-lit002/README.md).
  This is not independently verified human annotation or whole-case gold; other judgments stay pending.

- [x] N-035: add DeepSeek Pro/Flash under D-024, twenty first C requests, high/direct
  API. Pro 10/10 valid; Flash 9/10, with one output-budget exhaustion and no retry.
  Preserve raw/derived artifacts and the four-model report; reproduce two distinct
  lit-002 tie-encoding counterexamples against the original classical kernel.
  [Report](pilot/model_comparison/20260922-deepseek-c-v0.1/REPORT.md).
- [x] N-036: coordinator reviewed the two formula counterexamples and proposed explicit
  HOW checks, separating budget/content/boundary evidence. Human adjudication remains open.

- [x] N-034: execute the authorized first current-package comparison: two GPT models,
  ten C inputs each, medium, existing ChatGPT subscription, twenty first attempts.
  All outputs valid; preserve raw data, pending-reference diagnostics and AI content
  review. Coarse scores tie; alternative families, pivot subregions and support
  terminology need review. [Report](pilot/model_comparison/20260922-c-v0.1/REPORT.md).
- [x] N-036: prepare coordinator review of lit-003 / lit-009 boundaries and proposed
  support/practical clarification; formal definitions and labels remain pending.

- [x] N-033: D-022 authorizes pending reference labels for exploratory model comparison.
  Add private v0.1 labels, formulas, core/context obligations and executable diagnostics;
  preserve current inputs and historical labels. Seven structural YES / three unresolved;
  actual model discrimination and human review are not completed by scoring fixtures.

- [x] N-032: two-level “读取当前目录” entry, explicit read-versus-continue behavior,
  concise current status/action queue, original-idea summary, old-document archive,
  documentation sync requirements and static link/artifact preservation checks.

- [x] N-031: fix lit-005 lock-report ordering and lit-009 delta overflow under the
  existing contracts; remove lit-007 explicit QAOA class/path cues in a versioned
  input package. Preserve prior bytes, source attribution and scientific labels.
- [x] N-030 engineering review: inspect ten programs/contracts/tests; identify and
  reproduce concrete issues. Human case inclusion/scoring review below is distinct.

- [x] N-029: fill external-reference adoption gap with six source-derived classical
  programs, explicit source/license differences, executable method fixtures and
  ten-group/30-condition review inputs. No new scientific labels or model runs.
- [ ] N-030: review six new functional contracts plus four reused source groups;
  approve/change/drop proposed cues, scope controls and per-contract evaluation
  methods before a separately authorized experiment. N-027 remains part of this review.

- [x] N-028: polish two source-driven WHERE cases into boundary/dependency/obligation
  dossiers, thirteen classical witnesses, six DRAFT A/B/C inputs and protocol limitations.
- [ ] Before any A/B/C model run, review cue locations/alternative boundaries,
  functional realism, control coverage, rubric and matched execution/sampling protocol.
  User accepted the three-condition design direction (D-020), not these open details.
  D-022 permits pending-reference exploratory preparation; D-023 subsequently authorizes
  the completed twenty-call C comparison before formal review. Review remains open;
  new runs still require explicit scope/configuration authorization.
- [x] N-026: correct expansion direction using pinned external source records and
  meaningful WHERE alternatives/dependencies; add lit-003/lit-004 plus core views,
  source/method audit, independent tests and allowlisted exports.
- [ ] N-027: review the two new source-driven workflows and provisional localization
  boundaries. Distinct preview/full-solver contracts are tested; difficulty is not.
- [x] N-020: polish MaxCut/vertex-cover reference pairs; add complete inspection
  assessment/worklists/transfer context, explicit core contracts, independent tests,
  paired lineage and public allowlist export in pilot/reference_cases/v0.1/.
- [ ] N-021: two-pair researcher review is now included in N-023; not completed by code tests.
- [x] N-022: complete configuration-search and ordered-batch retention exemplars,
  source-preserving core/context views, independent truth-table/trace checks and public export.
- [ ] N-023: original four-pair review is now included in N-025; not completed.
  The user's later expansion instruction superseded waiting for this review first.
- [x] N-024: bounded expansion using the four exemplars to eight groups / sixteen
  core-context views; independent tests, contracts, provenance, examples and public export.
- [ ] N-025 (paused after sourcing correction): review v0.3's eight groups, especially archive tie semantics, optional
  component assumptions, independent capacity requests and mutable output identity.
  Paired views and pilot/source parents remain dependent; no independent-count claim.
- [x] Resume FSE priority after the user ended the coursework diversion; N-006
  checks three saved optimization-plan objective mappings with reproducible bounded
  arithmetic evidence, without label promotion or new model calls.
- [ ] N-007 (paused): bounded predicate/decoding evidence for the five saved search
  plans; user currently prioritizes case representativeness.
- [x] N-008: review functional context, source provenance and test gaps in 005/009;
  keep synthetic examples and scientific labels unchanged.
- [x] N-009 / researcher-approved two-case trial: pinned C2|Q> MaxCut and vertex-cover
  examples, source-preserving kernels, synthetic context, tests and evaluation-method
  comparison in pilot/source_adaptations/v0.1/. No new scientific labels or baseline.
- [ ] N-010: researcher reviews these two source adaptations' functional context,
  original/tie contract and evaluation obligations before expanding case count.
- [x] N-011: approved second-context maintenance assessment/adjustment case with
  current/proposed evaluations, movement/conflict reporting and full API tests.
  See pilot/context_adaptations/v0.1/; same source lineage as lit-001, still DRAFT.
- [ ] N-012: walk the researcher through the concrete context-001 report and review
  functional scope, inherited tie behavior and candidate/dependency boundaries.
- [x] N-013: context-001 structural mapping evidence: exact derivation, bounded
  per-assignment QUBO/Ising checks and classical exact-polynomial full-report agreement.
- [x] N-014: researcher accepted the concrete structural correspondence as a narrow
  initial opinion; practical UNKNOWN and unverified quantum migration remain separate.
  See artifacts/context001_mapping_audit/RESEARCHER_REVIEW.md; case stays DRAFT.
- [x] N-015: actually implement/run a bounded context-001 Qiskit conversion, retain
  first outputs, sample counts, optimizer nonconvergence and full-report comparison.
  See demo/context001_qiskit/README.md; no exact fallback or benchmark modification.
- [x] N-016: verified original run evidence and exposed the 7-device rejection;
  no solver rerun or contract relaxation during that audit.
- [x] N-017: restore original 16-device maximum, preserve v0.1.0 source/results,
  measure four real boundary runs and retain two observed exactness failures.
- [ ] N-018 (paused during new contract discussion): feed saved 16-device mismatches through existing semantic checks;
  execution success must remain distinct from exact-output preservation.
- [x] D-018: record case-specific approximation permission and satisfied-weight quality
  ratio in a separate v0.2-draft document; keep original precise case/results unchanged.
- [ ] N-019: researcher defines approximate-profile acceptance threshold and selection/
  tie policy; 95% is only an example. Do not silently implement approximate scoring.
- [ ] Resolve the demo's remaining artificial 2**40 weight-domain restriction with
  explicit numerical behavior checks; do not claim that device-count repair restores
  the original arbitrary-integer domain or silently erase precision limitations.
- [ ] Clarify whether pilot-005's required sorting is a process constraint or an
  implementation detail; retain existing frozen contract until explicitly resolved.
- [x] User-selected CA6000 SAT coursework: own-program synthetic inputs, exact labels,
  real neural training, error-cleaning/statistics, English report and eight-slide PPT.
- [ ] Student fills identity, reads/reproduces the selected SAT submission and submits
  through the course channel. External status unknown; no longer the active Codex
  queue. This is not a benchmark adjudication task.
- [x] User-prioritized terminal demo: saved analysis replay, real local Qiskit search,
  exact classical fallback, classical-retention checks and one-command startup.
  See demo/README.md; no automatic translator or new baseline is claimed.
- [x] Record D-016's accepted directions from discussion items 2–5 without changing
  old formats/labels.
- [x] Record D-017: item 1 resolved; concrete structural mapping is distinct from
  complete original-contract preservation and practical suitability.
- [ ] Implement a versioned protocol consistent with D-016/D-017:
  reviewed unknowns, nomination-before-exclusion and staged review records;
  preserve old packets, scientific annotations and evaluation meaning.

- [x] Consolidate the stable charter, current handoff and Codex operating protocol;
  add the short NEXT_ACTIONS queue so a new session can start with “继续”.
- [x] Complete N-001's coordinator-only review record without filling human judgments;
  use NEXT_ACTIONS for its current status and completion condition.
- [x] N-002 policy branch: record researcher choice A as D-014, future conditional
  planning independent of adoption; case review remains pending under N-003.
- [x] Record D-015: preserve the original software contract by default; exactness,
  exceptions and effects remain obligations, with no invented approximation policy.
- [ ] N-003: receive actual human plan review; preserve submissions and unresolved
  issues without automatic adjudication or another run.
- [ ] Track the alignment audit's engineering gaps separately: return annotations
  omitted from interface checks; Phase-1 verifier gated by unknown intent; pilot-009
  private oracle name-type description differs from the corrected public contract.
  Preserve frozen artifacts; scientific interpretation changes still need review.

- [x] Prepare ten DRAFT synthetic seeds with explicit provenance and classical tests.
- [x] Prepare separately distributable A/B, adjudication and single-response model packets.
- [x] Add Phase-1 predicted labels, raw-evidence retention and a no-repair JSON collector.
- [x] Prepare ten advisory proposals, tomorrow review table, sufficiency/provenance
  audits and dummy workflow verification without changing scientific annotations.
- [x] Audit ten model-facing descriptions, remove explicit answer cues and regenerate
  versioned packets; validate type consistency and the existing evaluation workflow.
- [ ] Coordinator reviews all ten proposed seeds and public workload assumptions.
- [ ] Collect two independent annotations per seed and record disagreements.
- [ ] Adjudicate labels and at least one full migration contract per positive.
- [x] Run the first Restricted Codex CLI single-turn baseline with exact settings,
  raw outputs and DRAFT-reference diagnostics; this is not a raw API baseline.
- [ ] Human-review practical NO/unknown consistency, support terminology and missing
  conditional T3 plans in pilot/baseline-v0.1/restricted-codex/FAILURE_NOTES.md.
- [x] Complete the explicitly authorized one-off conditional-plan diagnostic with
  unchanged original artifacts, ten first attempts and an exact prompt-addition diff.
- [ ] Human-review the eight SUBSTANTIVE content codings and unresolved exactness,
  oracle/certification and resource obligations; review changed support/applicability
  judgments; D-014 adopts elicitation policy only, with coverage/quality criteria
  still open (Q19).
- [ ] Open-code intent/applicability and failure observations; retain reference uncertainty.
- [ ] Curate real-world source programs separately; current seeds are synthetic, not mined.
- [ ] Implement case-specific trusted oracle/contract checks from human contracts.

## P2 — Useful improvements

- [ ] Add a reviewed release manifest/freeze workflow with hash verification.
- [ ] Exercise an installed wheel in a clean, authorized environment.
- [x] Build a wheel and check extracted-wheel imports, schemas and entrypoint outside the checkout.
- [ ] Add a full environment lock for the future frozen benchmark release.
- [ ] Define a sandboxed execution runner before accepting arbitrary model code.
- [ ] Add a versioned JSON Schema for evaluation outputs after the pilot protocol stabilizes.
- [ ] Define how trusted oracle/quantum/resource evidence is bundled and attached to a full evaluation run.

## Research questions requiring human decision

- Case-specific suitability/mapping evidence and review consistency (remaining Q1/Q2);
  the D-017 conceptual structural boundary is decided, not a question to repeat.
- Reviewed-but-unknown annotation support and positive-category meaning: the current
  schema forces non-DRAFT certainty and positive practical YES. D-016 accepts reviewed
  uncertainty and staged review; representation/category/scoring details remain open
  (Q12), pending a versioned transition. Do not ask the accepted principles again.
- Candidate overlap scoring and hard-negative taxonomy (Q3, Q4).
- Contract coverage, advantage assumptions and quantum-output tests (Q5, Q6, Q9).
- Context realism, composition, leakage and release splits (Q7, Q8, Q10).
- Repository/data licensing (Q11).
- Negative-region semantics, blind recognition rubric and response-failure policy (Q14–Q16).
- Residual intent/localization information inherent in required functional specifications (Q18);
  Q17's input-type contradiction was resolved by researcher instruction on 2026-09-20.
- Distinguish unknown labels/localization from binary abstention (Q15); assess the
  nine human decisions in pilot/annotation_assist/TOMORROW_REVIEW.md.

## Deferred ideas

- 20–30 case pilot after annotation consistency review.
- A finalized failure taxonomy after actual pilot observations; the current form is open-coded.
- Agent architecture only if benchmark failures motivate it.
- Repository-scale cases, other languages/frameworks, real QPU execution.
