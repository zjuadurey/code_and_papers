# Changelog

## 2026-09-22 — N-036 HOW rubric proposal and targeted trial review

- Under the user's proceed-until-decision instruction, prepared a separate private
  claim/obligation review package; no old labels, prompts or main evaluator changed.
- Inventoried all forty requests; reviewed nineteen answers across five selected
  mothers, preserving Flash's missing final answer separately and twenty unreviewed
  answers explicitly. Seventy-six scoped evidence records, no overall score or gold.
- Reproduced two tie counterexamples; checked vertex-cover/clique formulas on 1100
  graphs each, knapsack on 4100 instances, coloring-order on 499 vectors and incumbent
  pivot selection on 3905 finite columns. These are classical finite checks only.
- Bound reviews to exact raw-response excerpts/hashes; replay and 1593-file integrity
  checks recorded in [validation](pilot/how_review/v0.1/validation.json).
- Next gate is the formal HOW operational policy; no new model, QPU, install or Agent.

## 2026-09-22 — N-035 DeepSeek Pro/Flash comparison extension

- D-024 records the user's explicit two-model addition and credential-file provision.
  Added a dependency-free API runner with immutable public-input snapshots, bounded
  twenty first requests, no tools/retries/repair, and strict full-population collection.
- Actual run: twenty HTTP 200 responses; Pro 10/10 valid, Flash 9/10. Flash lit-009
  spent its 16384 completion tokens in reasoning and produced no final answer; preserve
  that failure and withhold full-population diagnostics instead of silently dropping it.
- Reproduced two distinct lit-002 tie-encoding mistakes; confirmed both witness inputs
  with the unchanged original classical validator/kernel. No automatic task-pass or
  gold-label changes. Distinguish budget/configuration effects and AI content review.
- Nine offline tests passed; protected 458 prior artifacts unchanged. No dependency
  installation, QPU, Git staging/commit/push or credential content in experiment artifacts.
  [Four-model report and validation](pilot/model_comparison/20260922-deepseek-c-v0.1/REPORT.md).

## 2026-09-22 — N-034 current-package C comparison

- Under the user's benchmark-test request (D-023), ran gpt-5.6-sol and gpt-6-astra
  once on each current C input, medium, CLI 0.155.1, existing ChatGPT subscription.
  Twenty completed/valid first responses; no tools, output repair or scientific retry.
- Both match seven pending positive structural references, cover all seven plans,
  and exactly match six localization anchors. Coarse diagnostics do not separate them.
  Preserve the lit-003 alternative family, both models' lit-009 pivot-search nomination,
  practical NO/unknown differences and ambiguous support interpretation for review.
- [Report and evidence](pilot/model_comparison/20260922-c-v0.1/REPORT.md),
  including offline collector checks, isolation/output/integrity validation and
  AI-only content review. No labels promoted, old inputs changed, QPU, installation,
  commit or push. The bounded model authorization is complete.

## 2026-09-22 — ChatGPT subscription connectivity smoke

- Under the user's “试一下？” instruction, requested one short response each from
  gpt-5.6-sol and gpt-6-astra via saved ChatGPT login, CLI 0.155.1, medium effort.
  Both returned SUBSCRIPTION_SMOKE_OK with exit code 0; no API keys or benchmark inputs.
- Preserved a pre-inference CLI flag error and startup warning events. The initial
  checker misclassified warnings as tool use; post-hoc event inspection is recorded
  separately without rewriting raw flags or repeating inference.
- [Artifacts and actual checks](artifacts/subscription_smoke_20260922/README.md):
  thirty input hashes and current reference fingerprints unchanged. No full benchmark,
  dependency installation, source/label change, Git commit or push.

## 2026-09-21 — N-033 pending labels for model comparison

- Recorded D-022: researcher requests usable labels now while retaining pending review.
- Added a private versioned reference overlay for ten mothers / thirty unchanged inputs:
  seven concrete structural YES proposals, three unresolved controls, source anchors,
  formulas and per-view obligations. Original case metadata and main scores are unchanged.
- Added an offline diagnostic entrypoint reusing existing candidate/recognition code;
  condition-specific IDs, schema/region/coverage checks, pinned inputs and reference hashes,
  no silent output repair, no automatic alternative-family rejection or task-pass claim.
- Validation: 24 focused checks passed, including seven finite mathematical/source
  correspondence checks and synthetic-response discrimination. Integration results and
  old-artifact/document checks are recorded in
  [validation.json](pilot/provisional_labels/v0.1/validation.json).
- No model/QPU calls, dependency installation, annotation promotion, Git commit or push.

## 2026-09-18 — initial benchmark infrastructure

### Added

- Standalone qrefactorbench/ project in a previously empty workspace; no prior work replaced.
- AGENTS.md startup/handoff procedure, current status, decisions, backlog and research docs.
- JSON Schema 2020-12 case, prediction and plan formats; multiple admissible contracts,
  independent eligibility/suitability/support labels and explicit abstention.
- JSON/optional YAML loading, duplicate-key rejection, portable artifact containment,
  region/function checks, duplicate case detection and maturity-specific validation.
- Read-only validation/summary/static evaluation CLI, annotation comparison and wrappers.
- Candidate exact/line diagnostics, decision confusion metrics, plan membership/verifier
  interfaces, syntax/import/execution/interface helpers, semantic oracle hooks, resource
  inspection and explicit end_to_end_quantumization_success aggregation.
- Four DRAFT toy cases with classical tests; three templates; incomplete demo predictions.
- Evaluation hashes/version manifests, packaged schema data and stored validation outputs.

### Changed

- Initial Python minimum aligned to Python 3.10 after inspecting and testing the
  existing environments; Python 3.11 optional and 3.12 integration checks also passed.
- Licensing deliberately left ungranted pending human choice, recorded as Q11.

### Fixed during implementation

- Syntax checks compile without executing, rejecting context-invalid Python such as
  top-level return; null-byte paths produce diagnostics rather than escaping validation.
- Reviewed equality/objective/property oracles require explicit expected values,
  thresholds or hook IDs. Missing task annotations cannot establish plan conformity.

### Validation

- palqo Python 3.10.21: `python -m pytest -q` → 64 passed, 3 skipped (Qiskit/YAML absent).
- htp-static Python 3.11.16: `python -m pytest -q tests/test_optional.py` → 5 passed,
  including all optional checks skipped in the core environment.
- Python 3.12.12 integration: dataset, schema resources, YAML round trip, real Qiskit
  resources and static evaluation passed.
- Dataset validation passed with four expected DRAFT warnings; summaries and deliberate
  demonstration evaluation generated machine-readable artifacts.
- Wheel built with existing setuptools, then extracted and checked outside the source
  checkout; all three schemas, console entrypoint and integration smoke check passed.
- No dependencies installed, no generated prediction code/QPU executed, no external
  state changed. No quantum migration or model-performance result is claimed.

See docs/validation.md for environments, commands and limitations.

## 2026-09-18 — Phase-1 pilot preparation

### Added

- Ten explicitly synthetic/Codex-assisted DRAFT cases under cases/pilot/, each
  with classical tests, neutral public task facts, curator notes and draft criteria.
  Sampling categories match the requested 2+2+2+2+2 composition, pending human review.
- Pilot sampling manifest, common DRAFT contract menu, independent A/B templates,
  adjudication records and separately distributable packets with content hashes.
- Reusable direct-LLM prompt, ten rendered prompts, provider-neutral run metadata,
  no-repair external JSON collector and open-coded observation form.
- Phase-1 prediction profile 0.2.0 and recognition diagnostics retaining raw
  predictions, independent labels, free-text intent, coverage and unknown results.
- PHASE1_PILOT_STATUS.md with exact next human actions; D-008–D-010 PROVISIONAL
  decisions and Q14–Q16 unresolved questions.

### Changed

- Package/result version is 0.2.0. All three v0.1 schema documents remain unchanged;
  prediction validation dispatches to the additional Phase-1 profile by version.
- Phase-1 intent is not graded by private-ID equality. Conditional plans can be
  retained on abstention; contract membership remains distinct from conformity.
- Existing CLI comparison includes assumptions, applicability and uncertainty;
  evaluation supports explicit case selection with selected/unselected IDs.
- Existing four-toy evaluation tests now select those IDs explicitly within the
  expanded dataset. Current docs describe fourteen total cases and ten pilot cases.

### Scientific boundaries

- Every new annotation remains DRAFT. Six proposed positives retain unknown
  suitability/support/decision; no human annotator identities or model outputs exist.
- The no-candidate versus rejected-hotspot conflict for REVIEWED hard negatives
  is documented, not automatically resolved or hidden by fabricated spans.
- No new families, agent framework, provider configuration, dependencies, QPU
  jobs, empirical model scores, licenses, splits or accepted scientific claims.

### Validation

- Focused tests: 73 passed. Full core suite: 84 passed, 3 optional dependency skips.
- Optional Qiskit/YAML suite in the existing environment: 5 passed.
- Full dataset validation: 14 valid DRAFT cases; pilot subset: 10 valid DRAFT cases.
- Summary, packet export, real-Qiskit/YAML Python 3.12 integration and extracted
  0.2.0 wheel/schema/entrypoint checks passed. Raw logs are in artifacts/phase1_validation/.
- Ten classical program tests run in isolated subprocesses; collector/evaluator
  checks use temporary synthetic test responses only. No baseline was executed.

## 2026-09-19 — Researcher review preparation

### Added

- pilot/annotation_assist/: ten source-grounded advisory proposals, tomorrow review
  table with nine human decisions, information-sufficiency and repository-only
  provenance audits, workflow audit and concise overnight handoff.
- Explicit prior-context/independence disclosure, blinded input hashes and proposal
  hashes frozen before workflow/provenance inspection. No scientific labels changed.
- Local verification script exercising fresh packet export and temporary dummy
  collection/schema/evaluation/comparison; no model calls, stored responses or scores.
- Persistent raw validation logs and verification that 225 protected existing files
  are unchanged. No new dependencies or production-code changes.

### Changed

- Current project/backlog/readme/pilot-status handoff points to the review package.
- Research notebook records source observations; Q17/Q18 retain the pilot-009 public
  domain conflict and public intent/localization cues for human review. Existing
  accepted/provisional decisions and evaluator semantics remain unchanged.

### Validation

- Full pytest: 84 passed, 3 optional skips in 3.22s; separate optional suite:
  5 passed in 1.26s. Python 3.12 integration: 14 cases, four schemas, Qiskit/YAML passed.
- Dataset validate/summarize: 14 valid DRAFT cases, 14 expected warnings.
- Fresh four-role packet export byte-identical; all ten IDs and raw dummy labels
  preserved; expected DRAFT/malformed-input rejections passed. Blank-form comparison
  is plumbing evidence, not agreement. Evidence: pilot/annotation_assist/validation/.
- No source programs, scientific annotations, existing packets, schemas, contracts,
  licenses, splits, baseline results or scientific ground truth were altered.

## 2026-09-20 — pilot-v0.1 public-input revision

### Changed

- Researcher-approved correction of pilot-009's public name type to str, consistent
  with unchanged executable behavior; documented existing validation errors.
- Audited all ten descriptions and removed explicit candidate/intent/family/category
  cues while preserving functional requirements and workload facts. Exact changes
  are in PILOT_V01_CHANGELOG.md and the archived public-task diff.
- Current distribution pointers now use pilot/packets-v0.1; the workflow audit accepts
  --packets and checks this snapshot by default. Earlier audit results remain historical.

### Added

- Original public-task archive, revision hashes and newly generated four-role packets;
  original pilot/packets remains unchanged. D-011 records the approved scope; Q17
  is resolved and Q18 retains the unresolved effect of necessary specifications.
- Three regression tests for preserved/revised inputs, deterministic new packets
  and executable pilot-009 type/error consistency. No production/schema/algorithm changes.

### Validation

- Focused: 23 passed. Full: 87 passed, 3 optional skips. Separate optional suite: 5 passed.
- Ten pilot cases and fourteen total DRAFT cases validate; JSON summary unchanged.
- New packet/dummy prediction/evaluation audit passed; private-sentinel export tests
  passed. Raw evidence: artifacts/pilot_v01_validation/.
- No scientific labels, maturity, suitability scoring, contract families or formal
  baseline results changed; no dependencies installed and no model call made.

## 2026-09-20 — First Restricted Codex CLI pilot baseline

### Added

- Ten real first-attempt responses from ChatGPT-authenticated Codex CLI 0.154.0,
  gpt-5.6-sol/high, each in a fresh Bubblewrap namespace outside the repository.
- pilot/baseline-v0.1/restricted-codex/: raw outputs/events, exact argv/config/hashes,
  original runner snapshot, schema-valid predictions, unchanged evaluator output,
  result table and open-coded human review notes. No API key or agent framework.
- Explicit harness limitations: built-in descriptive context persists, native
  bounded transport defaults remain, and no server snapshot ID is exposed.

### Observed

- Ten successful calls/predictions, zero malformed outputs, retries or tool calls;
  ten abstentions, eight structural YES, eight practical NO/two unknown, no plans.
- DRAFT-reference diagnostics remain PILOT/NON-FINAL; no labels were promoted,
  no statistical/advantage claims and no prediction repair or formal taxonomy.

### Validation

- Existing collector: 10 predictions, 0 repairs; evaluator: demonstration_only=true.
- Post-run pytest: 87 passed, 3 optional skips; separate optional suite: 5 passed.
- Dataset: 14 valid DRAFT cases; JSON summary unchanged. 308 protected files
  retain their pre-run hashes, including all input/source/annotation/schema/evaluator
  and frozen packet files. No dependencies installed or quantum solving performed.

## 2026-09-20 — Controlled conditional-plan diagnostic

### Added

- Separately versioned diagnostic under pilot/baseline-v0.1/conditional-plan-diagnostic/,
  with exact approved prompt addition/diffs, hashes, original runner copy, ten raw
  first attempts, metadata/events, paired tables and descriptive plan-content review.
- New external isolation directory /home/audrey/qrefactor_conditional_plan_diagnostic/;
  same Codex 0.154.0, gpt-5.6-sol/high, ChatGPT login and per-case Bubblewrap protocol.
- D-012 and Q19 record the one-off protocol and unresolved conditional-HOW validation.

### Observed

- Ten successful/schema-valid responses; zero repairs/retries/observed tools.
- Eight structural-YES cases now have plans despite continued classical retention;
  both structural-NO controls retain null. Main structural/practical/decision/family
  fields are identical to the original; other changes are explicitly reported.
- Eight plans descriptively coded SUBSTANTIVE, with exactness and resource gaps;
  no reference accuracy evaluation or scientific label promotion.

### Validation

- Existing collector: 10 predictions, zero repairs; pytest: 87 passed/3 skipped
  in 3.61s; optional suite: 5 passed in 0.96s; dataset: 14 valid DRAFT cases.
- Before handoff edits, 557 pre-existing files unchanged, including all 122 original
  baseline artifacts and 99 frozen packet files. Final check separately allowlists
  six project-memory documents; cases/schemas/evaluator/original results unchanged.
- Exact command arrays match except temporary paths; frozen input bytes are exact
  diagnostic-prompt prefixes. No further model run or research system implemented.

## 2026-09-20 — Self-describing project control

### Added

- Stable docs/RESEARCH_CHARTER.md, practical docs/CODEX_WORKFLOW.md, and short
  NEXT_ACTIONS.md queue; docs/DOCUMENTATION_AUDIT.md maps canonical ownership.
- D-013 records the explicitly requested repository-driven continuation policy;
  the existing research log records the documentation/methodology clarification.

### Changed

- AGENTS startup now supports a minimal “继续”; PROJECT_STATUS is a concise current
  handoff and README links the completed paired diagnostic and next safe action.
- Historical preparation documents have time-scope banners; TODO is explicitly a
  backlog. Task-number and maturity-state crosswalks preserve current scientific
  semantics. Existing decision bodies/statuses and frozen experiment files remain.

### Validation

- Documentation links/anchors, startup route, before/after protected-file hashes,
  historical ledger/log preservation and existing experiment manifests checked.
  Evidence: artifacts/documentation_control/validation.json.
- No code/tooling hook changed, so no runtime test suite, experiment, dependency
  installation, benchmark regeneration or reference scoring was performed.

## 2026-09-20 — N-001 human review preparation

### Added

- One coordinator-only Markdown review record linking all ten frozen inputs and
  original/diagnostic responses, with the existing unresolved questions retained.
- Forty per-case reviewer/date/judgment/evidence cells and nine cross-case human
  entry cells left blank; no researcher review, new score or protocol adoption.

### Changed

- Marked N-001 complete and moved the queue/status to N-002: await actual human
  evidence/the Q19 decision. README points to the ready record. No new scientific
  decision, prompt, label, schema, source algorithm or evaluator change.

### Validation

- Checked ten unique case IDs, eight non-null-plan/two null-plan source responses,
  local links, blank human fields and before/after file fingerprints. Evidence:
  artifacts/n001_review_preparation/validation.json.
- Documentation-only work: no model calls, generated-code execution, dependency
  installation or runtime test suite; original experiment manifests verified.

## 2026-09-20 — D-014 conditional-planning policy

### Changed

- Recorded researcher choice A as ACCEPTED for future protocol elicitation;
  preserved all earlier decision entries and frozen experiment artifacts.
- Aligned charter, status, queue, README and TODO: policy selection is complete;
  actual human plan review is N-003. Marked Q19 partially resolved, retaining
  technical/semantic validation and coverage/quality scoring as open questions.

### Validation

- Documentation-only path/link and before/after hash checks, plus original and
  diagnostic experiment manifest verification; exact results in
  artifacts/d014_protocol_decision/validation.json.
- No runtime tests or model calls; no source, schema, evaluator, prompt, label or
  human-review-field modifications.

## 2026-09-20 — D-015 original software contract default

### Changed

- Recorded the researcher's original-contract preservation requirement as ACCEPTED;
  clarified the distinction from quantum migration contracts in the existing charter,
  task vocabulary and annotation guidance. Q9 is partially resolved, not closed.
- Updated current status/queue/backlog and appended the research record. Recorded
  the preceding alignment audit's 86-pass/3-skip/1-failure result rather than presenting
  the historical 87-pass result as current. No outstanding implementation issue fixed.

### Validation

- Documentation link/anchor and protected-file checks plus both experiment manifests;
  exact evidence: artifacts/d015_contract_decision/validation.json.
- No runtime tests or model calls in this documentation task. Cases, scientific
  labels, frozen inputs/results, schemas, evaluator and blank review fields unchanged.

## 2026-09-20 — D-016 prospective protocol directions

### Changed

- Recorded researcher decisions for discussion items 2–5; marked D-005's certainty
  rule superseded prospectively while retaining its historical body and old schema.
- Linked prospective WHERE/review policies in charter, task/annotation guidance,
  questions, status and queue. Kept Q2/item 1 explicitly open for discussion.

### Validation

- Documentation links/anchors and before/after protected-file checks, plus original
  baseline and diagnostic manifest verification; evidence in
  artifacts/d016_policy_directions/validation.json.
- No runtime tests/model calls or implementation changes. The previously reported
  packet-regeneration failure remains outstanding; no labels or reviews promoted.

## 2026-09-20 — D-017 structural definition

### Changed

- Recorded researcher acceptance of discussion item 1, distinguishing concrete
  structural mapping, complete contract preservation and practical suitability.
- Updated charter, task/annotation guidance, Q2 and current handoff. All five
  directions are settled; per-case evidence and final scoring remain open.
- Queued the existing packet regression fix and prospective versioned implementation;
  no implementation, case-label or experiment changes in this documentation task.

### Validation

- Local links/anchors, append-only ledgers and protected-file hashes checked;
  both experiment manifests verified. Evidence:
  artifacts/d017_structural_definition/validation.json.
- No runtime tests/model calls. The prior 86-pass/3-skip/1-failure suite result and
  packet-regeneration issue remain unchanged; this task does not claim a fix.

## 2026-09-20 — N-004 packet regeneration fix

### Fixed

- Export baseline instructions from packet_instructions.v0.1.md rather than the
  mutable project README. Dedicated source is byte-identical to frozen instructions;
  no packet, manifest expectation, scientific prompt, case or evaluator was edited.
- Add modified/missing-README regressions in a checkout containing only export
  sources, verifying unchanged packet bytes and exclusion of private README notes.

### Validation

- Before fix: existing regeneration test plus both new regression variants fail.
- After fix: focused suite 25 passed; full suite 89 passed/3 optional skips;
  separate optional suite 5 passed. All 14 DRAFT cases validate; JSON summary and
  dummy blind prepare/collect/evaluate/compare workflow pass.
- All 99 regenerated packet files match; existing packets and experimental results
  preserved. Exact logs/hash checks: artifacts/n004_packet_regeneration/README.md.
- No model run, dependency installation, scientific score or label change.

## 2026-09-20 — One-command terminal demonstration

### Added

- `bash scripts/run_demo.sh`: source/region and saved conditional-plan replay for
  pilot-001/002, actual bounded Qiskit CNF search, original-predicate verification,
  exact exhaustive fallback, and retained classical digest/callback checks.
- AI-assisted demo implementation, no live code generation/model calls. JSON report
  retains input/implementation hashes, actual outputs, samples and resource counts.
- Thirteen focused tests including oracle phase/workspace checks, missed-witness
  fallback, original edge behavior and callback exception propagation.

### Validation

- Demo PASS; core 91 passed/14 optional skips, quantum demo + optional 18 passed.
- Initial full-suite attempt in quantum env failed with four collection errors
  (missing jsonschema); reused existing core/quantum split, installed nothing.
- All 14 cases validate and JSON summary passes; 442 protected files unchanged.
- Exact artifacts and limits: [demo/README.md](demo/README.md). No new scientific
  labels, case/schema/evaluator changes, model experiment or advantage claims.

## 2026-09-20 — Selected CA6000 SAT prediction coursework

### Added

- Separate course study derived from pilot-001, explicitly selected by the user:
  3,000 generated CNF instances, canonical renaming/order deduplication, exact labels,
  documented training-only corruption, Pandas cleaning/statistics and PyTorch training.
- MLP, linear and majority comparisons; actual test metrics 91.68%, 90.85%, 55.91%.
  Feature collisions and a 597-row sensitivity subset are disclosed, not hidden.
- English interactive prediction/exact-solver comparison, including a real error.
- Eight-slide English PPTX/PDF, seven-page English report, speaker notes, model/data
  artifacts and an allowlisted submission package. Earlier medical fallback retained
  but excluded from submission. No installed dependencies or external submission.

### Validation

- Six focused tests pass, including independent checks of all 3,000 exact labels;
  original repository suite 97 passed/15 optional skips; separate optional suite
  25 passed. All 14 benchmark cases validate and remain DRAFT.
- Browser prediction/error/invalid-input checks pass. PPTX XML/relationships and
  English text checked, eight-slide preview and seven-page report PDF inspected.
- Native PowerPoint automation was blocked by Windows script policy; no policy was
  bypassed. Package/reproduction and preservation evidence is recorded in the
  selected study's results/validation.json.

## 2026-09-20 — White NTU coursework presentation

- Restyled the selected eight-slide English SAT deck with a white background,
  dark text and pale cards; added unaltered NTU Singapore artwork from the official
  student-organisation website on the cover and footers, with asset provenance.
- Preserved the previous navy deck locally; regenerated PPTX, PDF and PNG previews
  and rebuilt the selected submission ZIP. No retraining or research-artifact edits.
- Validated eight slides, OOXML and relationships, white backgrounds, logo placement,
  unchanged body text and protected-file hashes; inspected the slide overview.
  Native PowerPoint rendering remains unverified (earlier Windows policy blocker).
  Evidence: coursework/sat_case_study/deliverables/style_validation.json.

## 2026-09-20 — Resume FSE; bounded optimization-plan audit

- Moved active status/queue back from coursework to FSE at the user's instruction;
  retained all coursework artifacts and did not infer external submission status.
- Added an isolated standard-library audit of all three saved optimization plans:
  explicit objective transcription, exact rational Ising expansion, original-function
  comparison, deliberate incorrect variants and sample-only exactness witnesses.
- Actual checks: 1,805 inputs / 7,083 assignments agree; repeat output identical;
  29 focused tests pass in 2.74s; 14 valid DRAFT cases and summary succeeds.
  All 717 protected files unchanged; source matches frozen model-facing programs.
- No model calls, quantum execution, training, schema/evaluator/label edits or human
  review claims. Evidence: artifacts/plan_mapping_audit/README.md and validation.json.
- Next safe item is bounded evidence for five search plans; case adjudication and
  final scoring remain human decisions. No new architecture or protocol adopted.

## 2026-09-21 — Review software context in pilot-005/009

- Recorded source-backed functional-context, provenance and test-gap analysis;
  minimal original-code probes show filtering, metadata and exception behavior.
- Both examples remain DRAFT synthetic material. Flagged 005's sorting requirement
  for Q7/Q9 review; did not change that requirement or invent application origins.
- Original test files each pass separately: 1 passed in 0.01s per case. Checked
  local document links, repeatable observations and 717 protected-file hashes.
- Updated current status/queue to follow the user's benchmark-representativeness
  discussion: N-007 paused; N-008 complete; N-009 is read-only C2|Q> case comparison.
- No schema, source algorithm, evaluator, case label, frozen artifact or coursework
  change; no installation or model/QPU task. Evidence: artifacts/context_case_review/.

## 2026-09-21 — Two source-grounded case construction drafts

### Added

- Researcher narrowed expansion to one MaxCut and one constrained graph task.
  Added lit-001/lit-002 under pilot/source_adaptations/v0.1/, separate from cases/.
- Pinned C2|Q> HF revision and rows 164/427, original record/code/hash/license
  evidence, unchanged extracted functions, explicit synthetic application adapters,
  public requirements, classical tests and private adaptation notes.
- Evaluation-method mapping to C2|Q>, Qiskit HumanEval and SupermarQ; feasibility,
  objective quality and full software behavior remain distinct.
- Six-file public source/spec export, deterministic manifest and refusal to overwrite.
  This is a review input bundle, not a new baseline prompt or model experiment.

### Validation

- lit-001: 24 passed in 0.03s; lit-002: 22 passed in 0.03s.
- Core suite: 97 passed, 15 skipped in 3.52s; skips are optional Qiskit/PyYAML
  absent in the core environment. Optional suites not rerun: no quantum code changed.
- Both new manifests validate; original 14 cases validate; both JSON summaries pass.
- Two terminal JSON examples, byte-identical source kernels, allowlisted/reproducible
  public export and overwrite refusal checked; 691 protected files unchanged.
- All new scientific judgment fields remain null, manifests DRAFT; provisional
  sampling categories/candidate nominations are not gold. No source algorithm,
  legacy case, schema, evaluator, frozen input or baseline artifact modified.
- Evidence: pilot/source_adaptations/v0.1/validation/results.json.

## 2026-09-21 — Second-context maintenance assessment and adjustment

### Added

- Researcher-approved context-001 in pilot/context_adaptations/v0.1/: full current
  assignment validation, conflict evaluation, proposed arrangement and change report.
- Original sourced MaxCut function retained byte-for-byte inside maintenance.py;
  provenance records shared lit-001 lineage. Existing source adaptations unchanged.
- Versioned public contract, sample request/actual report, DRAFT manifest, independent
  complete-report tests, allowlisted public export and source/preservation checks.
- Movement count is report-only, exact optimum and original tie rule retained;
  no capacity/duration/availability constraints invented. New context remains synthetic.

### Validation

- Context suite: 43 passed in 0.19s. Covers 1,099 small graph/current-assignment
  requests, 27 weighted inputs, interface/exception cases and a report mutation check.
- Core regression: 97 passed, 15 skipped in 3.45s; optional Qiskit/PyYAML unavailable.
  Quantum suites not rerun; no quantum code changed or quantum execution performed.
- New DRAFT validates/summarizes; original 14 cases validate/summarize; old two source
  drafts validate. Reproducible public export/refusal to overwrite and example CLI pass.
- 593 protected files unchanged; all scientific judgment fields remain null.
  No model call, new evaluator/schema semantics, installation, release or label promotion.
- Evidence: pilot/context_adaptations/v0.1/validation/results.json.

## 2026-09-21 — Context-001 structural correspondence audit

- Added artifacts/context001_mapping_audit/: source/variable/objective/decoding
  evidence, exact QUBO and Ising derivation, reproducible classical audit and results.
- Reused existing rational polynomial utilities. Checked 98 inputs / 1,271 assignments
  against raw request costs and original source scoring; exact optima/ties and all
  98 full reports agree using a classical polynomial enumeration substitute.
- Retained counterexamples for omitted constant, wrong linear sign, wrong pair
  coefficient and reversed equipment-bit order. No source or evaluation code changed.
- Context tests: 43 passed in 0.19s; core: 97 passed, 15 optional skips in 3.52s.
  New and original manifests validate; repeat audit output is identical; 625 protected
  files unchanged. No quantum/optional suite execution, new model run or dependency.
- Structural YES is now an evidence-backed AI recommendation awaiting actual human
  initial review, not a serialized label change or REVIEWED/FROZEN promotion.
  Practical suitability and complete quantum migration remain separately unresolved.
- Current queue asks for one case-specific review rather than automatically adding
  more input checks or designing an agent. Evidence: audit validation.json.

## 2026-09-21 — Record narrow researcher initial opinion

- Recorded the researcher's explicit acceptance of context-001 structural correspondence,
  with complete quantum migration unverified and practical suitability unknown.
- Preserved source/case labels, DRAFT status, audit and experiment results. This is
  an initial review record, not independent annotation or expert/gold promotion.
- Updated current status/queue to stop re-asking the resolved question. Explained
  classical exact-enumeration substitution versus actual quantum solution finding.
- Documentation-only change; local links and protected artifacts checked, no tests
  or experiments rerun. Record: artifacts/context001_mapping_audit/RESEARCHER_REVIEW.md.

## 2026-09-21 — Execute context-001 Qiskit conversion

- User requested running the converted program; added an isolated AI-assisted
  one-layer QAOA/Statevector hybrid prototype in demo/context001_qiskit/.
- Preserved source helpers byte-for-byte, replaced only solver usage, retained
  first responses/counts/optimizer traces/resources and full-report comparisons.
- Five first attempts completed; four quantum circuit simulations, empty classical
  return; all five reports match. No exact fallback, reference feedback or retries.
  Three nonzero objectives hit the fixed 80-evaluation budget without convergence.
- Quantum/optional tests: 20 passed in 1.46s; source context: 43 passed in 0.19s;
  core: 97 passed, 15 optional skips in 3.48s. Original 14 cases/context manifest
  validate; JSON summary succeeds; 529 protected files and first-run hashes unchanged.
- Domain bound, finite-sampling exactness/tie gaps and ideal simulator expectation
  optimization are explicit. No benchmark/evaluator/schema/label change, dependency
  installation, model call, QPU job, release or practical-benefit claim.
- Evidence: demo/context001_qiskit/artifacts/validation.json and README.md.

## 2026-09-21 — Fix arbitrary six-device restriction

- Researcher challenged the unsupported simulator-size cap. Updated the separate
  demo protocol to v0.1.1/max 16 and original ValueError boundary; numerical solver
  parameters unchanged. Preserved v0.1.0 sources/tests/README and old run artifacts.
- Added 7–16 device circuit/decoding regressions and pre-solver rejection at 17.
  Four real fresh-process runs measured 7/12/16 devices (including dense 16): all
  execute, 2 reports match, 2 have objective gaps 4 and 5. No retry/feedback/fallback.
  Durations 0.155–8.888s; whole-process peak RSS 127.91–385.34 MiB, single-thread env.
- Tests: 31 quantum/optional passed in 2.13s; context 43 passed in 0.19s; core 97
  passed/15 skipped in 3.40s. Original/context manifests validate. 547 protected
  files and both snapshot/new-run hashes checked; no dependencies or benchmark edits.
- Remaining weight cap and exactness/tie incompatibilities are explicit. No practical
  quantum benefit is inferred. Evidence: demo/context001_qiskit/artifacts/device_limit_v011/README.md.

## 2026-09-21 — Record scoped approximate-contract direction

- Added pilot/context_adaptations/v0.2-draft/CONTRACT_CONTEXT_001.md following researcher
  permission: explains soft conflict weights, preserved hard/interface requirements,
  absolute gap and accepted satisfied-weight quality ratio. Threshold remains pending.
- Appended D-018; updated current status/queue and Q9/Q19. Paused N-018 until new
  contract criteria are clear; no new oracle, schema, evaluator, labels or experiment.
- Original exact-case files and all observed results remain unchanged. Documentation
  links, protected hashes and ratio arithmetic checked; no test/solver rerun needed.
  Validation record: pilot/context_adaptations/v0.2-draft/validation.json.

## 2026-09-21 — Polish two core/context reference pairs

- Added pilot/reference_cases/v0.1/: two explicit core contracts over unchanged
  sourced functions, reused maintenance context, and new context-002 inspection
  review with coverage gaps, deterministic station worklists and transfer reports.
- New synthetic context has a DRAFT manifest with null scientific judgments;
  inherited hard coverage/exact cardinality/ties, full input validation and no mutation.
  Maintenance approximation permission is not silently extended to inspection.
- Added independent full-report oracle over 1,099 graph/current-selection inputs,
  boundary/CLI checks and fault cases for suboptimality, wrong ties, coverage and
  corrupt worklists. Fixed public allowlist, byte-identity/refusal checks, provenance,
  paired lineage index and researcher-facing exemplar/expansion review guide.
- Validation: new context 37 passed (0.16s); view/export checks 7 passed (0.12s);
  source suites 24/22 passed (0.03s each); existing context 43 passed (0.19s);
  core 97 passed/15 optional skips (3.40s). New/original manifests validate; summary
  passes; 823 old files preserved. No model, quantum experiment or dependency change.
- Exact evidence: pilot/reference_cases/v0.1/validation.json.

## 2026-09-21 — Complete search and classical-retention reference pairs

- Added pilot/reference_cases/v0.2/: partial feature-profile compatibility review and
  change-record sealing with canonical encoding, checkpoints, component receipts and
  audit-error propagation. Pilot-001/002 core functions retained verbatim; new contexts
  are explicitly Codex-assisted synthetic work, license NOASSERTION, no external source.
- Added exact core/public context contracts, two DRAFT manifests with unknown science,
  provenance/lineage, real CLI reports and independent named-rule/audit-trace tests.
- Exporter reuses old packet mapping and adds four views; previous four inputs stay
  byte-identical. Source identities, allowlist, standalone use and overwrite refusal checked.
  Eight-view review package/TOMORROW_REVIEW ready; no bulk generation or model/quantum run.
- Validation: new tests 37/26/5 passed (0.09/0.10/0.12s); parent tests 1/2 passed
  (0.01s each); core 97 passed/15 optional skips (3.68s). New/original validation and
  summaries pass; 867 old files preserved; no installs, schema/evaluator or label edits.
- Evidence: pilot/reference_cases/v0.2/validation.json.

## 2026-09-21 — Authorized bounded expansion to eight paired groups

- User requested expansion using the four prepared exemplars. Added v0.3 with four
  new contexts: eligible indivisible lots, optional component charges, capacity-limited
  archive selection and complete normalized exports. Eight groups now have sixteen
  core/context public views; views do not count as independent problem observations.
- Reused pilot-007/006/008 functions verbatim; authored one new synthetic archive core.
  Added explicit domains, exact contracts, meaningful dependent reports, DRAFT manifests
  with null science, source provenance, examples, private review notes and tomorrow table.
- Added independent small-domain oracles and bad-substitute checks for eligibility,
  exact existence, additive charges, capacity/optimality/ties, transfer offsets, row order
  and mutable aliasing. Allowlist/export/source identity and wider core domains verified.
- Focused tests: context-005/006/007 each 25 passed (0.08/0.14/0.18s), context-008
  24 passed (0.04s), paired/domain/export tests 10 passed (0.24s). Core suite 97 passed,
  15 optional Qiskit/PyYAML skips (3.45s). Four new and fourteen original manifests
  validate; both summaries pass. Exact logs: pilot/reference_cases/v0.3/validation.json.
- Earlier eight public views and 926 protected files unchanged. No benchmark/schema/
  evaluator edits, installs, model/quantum calls, label promotion or invented source.
  N-024 complete; N-025 is concrete human quality review, with prior reviews still pending.

## 2026-09-21 — Source-first correction and WHERE-sensitive adaptations

- Responded to the researcher's correction with pilot/source_adaptations/v0.2-where/:
  audited ten pinned C2|Q> records, selected four functions for two problems, and
  preserved original functions alongside agenda/release-group functional contexts.
  Added source snapshots/hashes, exact adaptation diffs, attribution and a separate
  benchmark/method audit. Ten reviewed records are not ten independent new cases.
- Added lit-003/lit-004 DRAFT manifests with null scientific judgments, complete
  contracts, executable examples, independent small-domain oracles, behavioral
  counterexamples and four public views exported through a fixed allowlist.
- WHERE design now includes separately required greedy previews and complete solving,
  conditional paths, nested state, inline selection and history/filter dependencies.
  Difficulty and quantum applicability remain unverified hypotheses; no new model,
  QPU, quantum simulation, schema/evaluator changes, labels or dependency installs.
- Validation: agenda 17 passed; release groups 15 passed; source/export checks
  6 passed. Initial export check had 5 passed/1 failed from generated bytecode;
  subprocesses now use -B, with original failure log retained and assertions intact.
  Core suite 97 passed/15 optional skips (3.45s); two new and fourteen original
  cases validate and summarize. Logs: pilot/source_adaptations/v0.2-where/validation.json.
- Recorded D-019's researcher-directed construction priority; N-026 complete,
  N-027 reviews the two new workflows. Prior eight-group review N-025 is paused.

## 2026-09-21 — Polish WHERE review and prepare three conditions

- Added pilot/where_review/v0.1/ with two private concrete core/dependency/outer-contract
  dossiers, alternate-span proposals, prospective A/B/C protocol and a shared draft task.
  Researcher explicitly endorsed three conditions; D-020 records direction, not gold.
- Offline builder reuses public source snapshots, generic schemas and contract menu;
  six self-contained messages, B/C differing only by one file/range cue, no family/
  reference-answer hint. Output refuses overwrite. Kept all prior sources/artifacts.
- Recorded 13 real classical path/substitution witnesses, complete reports and changed
  fields. Same final proposal can coexist with wrong preview/status. These are controlled
  semantic counterexamples, not observed model failures or quantum validation.
- Validation: preparation 6 passed (0.24s); source suites 17/15/6 passed (0.05/0.05/0.14s);
  core 97 passed/15 optional skips (3.20s); two source and fourteen original cases validate,
  original summary succeeds. No dependency install, evaluator/schema edits or new models.
- N-028 complete; N-027 now reviews the prepared pages. Human functionality/boundary
  decisions remain unfilled. Evidence: pilot/where_review/v0.1/validation.json.

## 2026-09-21 — N-029: fill reference-case and executable-method adoption gaps

- Added six concrete classical programs lit-005–010 from QuanBench/+, SupermarQ,
  Qiskit HumanEval, HPL and HPCG tasks/formulas/algorithms. Each has public contracts,
  runnable examples, full-report tests, source adaptation notes and available notices.
  New contexts remain authored synthetic software; scientific labels remain null/DRAFT.
- Combined with four existing C2|Q> mother groups into thirty A/B/C review inputs.
  Prior local synthetic groups are preserved and excluded from the external-source count.
- Added pinned source snapshots (22 files), corrected the previously mistyped
  QuanBench+ repository URL in an addendum, and retained source inconsistencies.
- Implemented isolated descriptive Pass@k, distribution, process, count-signature,
  resource-representation, objective and numerical checks. Executed reviewed source
  functions and local deterministic fixtures; no model, optimizer or QPU experiment.
- Fixed new method code rejecting NumPy scalar values; initial 2 failed/3 passed log
  retained. Final new suites: 56+14+5+6 = 81 passed. Core: 97 passed/15 optional skips
  in 4.08s; existing optional suite 5 passed in 1.07s. Six new/fourteen original cases
  validate and summarize successfully. No installs, main evaluator/schema/label edits.
- Updated current queue to N-030 concrete source/functionality/method review. No human
  judgment is fabricated; new case acceptance and A/B/C cue/scoring policy remain open.
  Artifacts: pilot/reference_completion/v0.1/README.md and validation.json.
- Final integrity check: 1,170 old files unchanged; 22 source/30 input hashes match;
  222 local Markdown paths exist. Explicitly documented source NOTICE task-cue risk
  and separate-condition collection for shared B/C prediction IDs. No fully blind
  evaluation or scientific difficulty claim is made.

## 2026-09-21 — N-031: three approved review fixes in reference v0.1.1

- Preserved v0.1; new case-version snapshot fixes lit-005's conflict order and
  lit-009's missing finite-delta guard using existing helpers and unchanged contracts.
- Removed lit-007 QAOA class/path hints from public comments/NOTICE. Apache text and
  source copyright/project attribution retained; exact provenance remains private.
- Added five behavior regression cases; four fail on the copied pre-fix implementation,
  then pass after fixes. Existing algorithms, labels and nomination coordinates unchanged.
- Generated thirty inputs with the existing exporter; seven changed and twenty-three
  identical. Prompt/schema/menu bytes unchanged. New exporter refuses overwrite.
- Validation: 61 case + 12 version/export tests pass; core 97 passed/15 optional skips
  (4.05s), optional 5 passed (0.89s). Six new-version/fourteen original cases validate
  and summarize. All 1,189 protected files unchanged; failures and exact commands saved
  in pilot/reference_completion/v0.1.1/validation.json. No new dependencies/model/QPU run.

## 2026-09-21 — N-032: short session entry and current-state consolidation

- Added parent FSE/AGENTS.md redirect and rewrote project entry around “读取当前目录”
  as read-only orientation, distinct from “继续”. No user context reconstruction needed.
- Archived original six control documents byte-for-byte, including 527-line status
  and 212-line queue; replaced current status/queue with short Chinese handoffs.
- Added original-intent summary to the charter without altering existing scientific
  sections. Separated current source-case inputs from completed baseline inputs;
  clarified that README collector examples target the historical pilot.
- Added workflow sync matrix; D-021 records administrative behavior, not new science.
- Validation: local entry/link/anchor and artifact-preservation audit in
  artifacts/session_entry_20260921/validation.json. No runtime tests, model or QPU
  rerun, dependency installation, Git staging/commit/push or scientific artifact edit.
