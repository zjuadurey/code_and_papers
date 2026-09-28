# Changelog

## 2026-09-28 — Mac handoff and LogicalQubit platform reconnaissance

- Saved [Mac handoff](docs/MAC_HANDOFF.md): current results, raw-artifact pointers, complete working-tree
  transfer, Python3.11 environment proposal, local checks, and Linux-only bwrap runner limitation.
- Recorded official AGate-100 physical-qubit/SDK information; live account/backend/calibration/budget
  remain unchecked. Confirmed macOS wheels for pinnedQDK/pyqir and lqcloud0.5.0 Python constraints.
- Synced status/queue/README/environment entries and corrected the stale QDK optional-dependency note.
- Documentation only; no new tests/experiments, dependency install, credentials, QPU, commit/push or transfer.

## 2026-09-28 — D-043 formula-derived potential advantage beyond simulation

- Recorded the user's explicit small-validation/formula/resource-estimation evidence strategy;
  owning a large QPU or simulating its entire state is not a prerequisite for conditional benefit research.
- Derived QAOA gate counts/scheduled depth and exact-fallback expected-cost thresholds, checked
  45 small states and 8 focused tests, and made 11 QDK resource calls for100/200/500logical qubits.
- Added2376 parameter conditions, reproducible raw artifacts, derivations and a standalone plot.
  100qubit example: under declared classical/certificate/cost assumptions, certified per-shot
  success above0.197415% predicts benefit; these probabilities/costs are conditions, not observed outcomes.
-175 protected files unchanged; no large state simulation, new LLM/QPU/install or formal case changes.
- [Report](pilot/benefit_analysis/maxcut-formulas-v0.1/REPORT.md).

## 2026-09-28 — MaxCut scaling and resource-budget diagnostic

- Responded to the user's correction that a four-node negative result does not assess scaling benefit.
  Added an isolated 8–64-node kernel diagnostic without changing the capped original API/cases.
- Ran 18 classical instances (14 complete, four budget-limited) and 18 actual QDK estimates;
  retained raw outputs, frozen configuration/hashes, and a standalone resource-budget plot.
- Compared MILP/optimized enumeration with the original kernel on all 64 four-node graphs.
  Identified the existing all-edges certificate's obstruction on positive triangles.
- Positive remaining time budgets are necessary conditions only: exact certification, required shots,
  and complete hybrid benefit remain unestablished. No new LLM/QPU/install or formal label changes.
- [Report](pilot/benefit_analysis/maxcut-scaling-v0.1/REPORT.md).

## 2026-09-28 — lit-001 actual LLM/tool/feedback workflow

- Added a bounded single-model JSON action controller reusing the existing isolated subscription
  inference transport and QDK backend. The model reads source, submits its own QASM, invokes behavior
  and complete scenario-cost tools, then consumes feedback and concludes.
- Actual run: four Sol/medium calls, one candidate, no revisions/retries; exact observed output without
  fallback. 44 focused/regression tests passed. Offline replay matched simulation and QDK estimates.
- Added cross-machine replay/live commands, six populated cost terms with explicit assumptions,
  stronger classical comparison and resource/time conditions. [Evidence](pilot/llm_workflow/lit001-v0.1/README.md).
- Preserved historical hand-authored smoke and raw runs; no formal case/gold/metric or backend changes.

## 2026-09-28 — N-063 / D-042 callable QDK resource and cost workflow

- Added a pinned local QDK subprocess adapter and Python/CLI resource-analysis entry; OpenQASM3
  proposals and controller-owned comparison evidence are separate, with application hash binding.
- Added complete declared serial overhead intervals, repeated execution/error accounting and
  explicit unknown/quality/contract/backend-failure feedback. Formal case/scoring semantics unchanged.
- Real QDK1.32.3 smoke passed;30 focused tests and full253 passed/15 optional skips.
  No model/QPU or installation command executed. [Evidence](pilot/resource_workflow/v0.1/README.md).

## 2026-09-28 — N-062 / D-041 infer beneficial resource conditions from classical programs

- Recorded the accepted shift from evaluating a supplied device to inferring resource conditions
  for beneficial quantumization, with plans, workload/scale, complete costs and uncertainty.
- Added [RESOURCE_CONDITIONS](docs/quantum_advantage/RESOURCE_CONDITIONS.md); synchronized the
  advantage-doc entry, progression, charter, decision, status and queue. N-061 remains the latest
  implementation; its proof/cost tasks feed the new analysis rather than defining its whole scope.
- Documentation only; no code, experimental results, formal cases/metrics or paper changes.
  Local-link and protected-file checks are recorded in the advantage-doc validation addendum.

## 2026-09-28 — N-061 / D-040 contract and benefit guide concrete plan analysis

- Recorded the user's rejection of treating contract/cost as optional candidate mechanisms;
  made them core decision criteria and integrated the two surveys in a concrete progression plan.
- Analyzed existing lit-005 exact-first/absence behavior; constructed a source-derived reversible
  CNF oracle, lex-DPLL comparator and serial prefix-repair diagnostic in a new artifact version.
- Proved a scoped no-speedup result for that repair architecture; other plans and physical benefit
  remain unknown. Saved five primary PDFs, complete cost terms, hardware unknowns and next comparisons.
- Eight focused tests and eleven existing wrapper tests passed; 1809 formula/lock instances,
  4633 basis checks and 6442 repairs passed with exact replay. Corrected and recorded one initial
  hand-count test expectation; oracle unchanged. Protected 3675 old files unchanged.
- No model/QPU calls, installations, case/gold/split/metric or paper edits.
  [Report and verification](pilot/benefit_analysis/lit005-v0.1/README.md).

## 2026-09-28 — N-060 / D-039 complete the survey while preserving the full idea

- Recorded the user's correction: preserve the complete classical-program / available-hardware /
  benefit-decision / usable-migration objective; adjust mechanisms without abandoning the idea.
- Added source-offloading and real-software migration evidence (Yamato and Road), plus scoped
  hybrid-verification context. Compared eight direct works and three possible technical routes.
- Completed static diagnostics on three existing materials and documented technology boundaries,
  strong-baseline requirements, FSE evidence gaps and requirement-by-requirement survey completion.
- Added a v2 report and new immutable evidence package; N-059 bytes remain intact. Updated current
  charter, decision, status, queue and backlog. No upstream execution, model/QPU calls, installations,
  case/score changes or paper edits. See [delivery verification](pilot/frontier_audit/20260928-goal-review/README.md).

## 2026-09-28 — N-059 frontier-relative evidence audit

- Audited classical-to-quantum generation, agent verification, algorithm selection and feasibility;
  added C2Q, QPipe, QuaST, Predict and Conquer, Q-READY and early equivalence-based offloading.
- Archived versioned papers and pinned public source; inspected C2Q/Predict code and selected
  QPipe tool-package files. Recorded unavailable sources instead of inferring absent capabilities.
- Rejected overly broad novelty framing and proposed a falsifiable contract/total-cost diagnostic
  against reasonable tool composition. Concrete method/contribution remains provisional.
- Updated current handoff and finite next task. No upstream execution, models/QPU, installs,
  performance reproduction, case/score changes or paper edits. Integrity checks are in
  [the evidence package](pilot/frontier_audit/20260928/README.md).

## 2026-09-28 — D-038 research progress relative to the state of the art

- Recorded the researcher's clarification: locate the current frontier toward hardware-aware
  classical-to-quantum benefit assessment and migration, identify its limits, then develop and
  evaluate a new technique beyond that frontier. Repository feature completion is not the reference.
- Added the clarification to the charter, decision ledger, status and next-action handoff;
  existing benchmark/feedback prototypes remain evidence and candidate approaches, not fixed contributions.
- Concrete research questions and methods remain open. Documentation only; no new experiments,
  scientific label changes or paper edits. Prior uncommitted documentation additions preserved.

## 2026-09-28 — D-037 quantum-advantage discussion and evidence documentation

- Recorded the researcher's confirmed long-term benefit objective and request to preserve the discussion/search.
- Added layered evidence, code/evaluation guidance, primary-source reading notes and paper claim guidance.
  Distinguishes structural mapping, semantics, resources, conditional prediction and measured benefit;
  theoretical proof retains its own model/assumption scope. Detailed protocols remain open.
- Inspected existing resource/pipeline code: circuit counts and strict success do not compare classical/quantum costs.
- Synchronized charter, decision ledger, status, queue and paper notes/entry points. Corrected the stale D-036
  blocker to reflect completed preparation; admission/contract review remains pending.
- Documentation-only checks and protected-file comparison are recorded in
  [validation](docs/quantum_advantage/VALIDATION.md). No model/QPU runs, tests, installs or LaTeX compilation.

## 2026-09-27 — N-058 candidate dossiers under accepted D-036 A

- Researcher answered A. Prepared three dossiers within the four-dossier cap: CPython text matching,
  python-tsp closed TSP and NetworkX lazy simple-path enumeration, with10 commit-pinned source/license
  files, old-ten lineage comparison, exclusions and pending reference-review decisions.
- Classical checks:961 full-string pairs and961 bounded matches;779 TSP matrices/2337 calls;
  four QUBOs/1552 assignments;64 directed graphs/2880 path-multiset comparisons plus targeted controls.
  Exact replay passes;3555 preexisting files unchanged. No model/QPU calls, installs or paper edits.
- Only unchanged standalone TSP module reproduced on existing NumPy; tag/package-version and
  declared NumPy2-versus-installed1.26.4 discrepancies retained. No full-package compatibility claim.
- C01/C02 proposed for DRAFT source/contract review; C03 remains a boundary candidate. No formal
  case admission, gold, split or contamination-free claim. [Dossiers](pilot/new_mother_candidates/v0.1/README.md).

## 2026-09-27 — N-057 catalog/routing control completed; D-036 scope decision prepared

- All15 responses valid, zero retries/tools/errors. In the single empty-nomination replicate, C/R
  both nominate line13 while S remains empty; in the whole-function replicate even S localizes.
  No clear incremental correctness benefit of routed information over catalog alone is established.
- R1's stated predicate has two readings, each fails16 known states (11 finite). C2 retains two
  interpretations, one fails3 and one passes44. R5's secondary finite Grover claim has two readings
  passing31/excluding13; its primary QUBO remains unconstructed. No unambiguous finite-pass row.
- Separately checked C4's classical certificate: it accepts a nonmaximal index in a known state;
  this auxiliary record does not replace the primary-plan insufficient result.
-15 exact replays and3312 protected hashes match. Input286333/output36550 tokens; model746.619s.
  Review intervals overlap: sum593.539s, union199.326s, span200.344s. AI review only.
- Prepared concrete D-036 proposal for at most4 new mother-problem dossiers, versus first obtaining
  existing independent reference review. No new-case/gold/split authorization inferred; budget is
  already delegated. [Results](pilot/enhancement/candidate-routing-control-v0.1/execution-20260927/REPORT.md),
  [scope decision](docs/NEXT_RESEARCH_SCOPE.md).

## 2026-09-27 — N-056 accepted mechanics; N-057 catalog/routing control started

- Froze S/C/R each5: common original draft and revision wrapper, identical C/R public catalog,
  additional routes and legacy inventories only in R. No formalization/correctness feedback.
-31 routing tests,32 runner tests and49 regressions pass;5 offline preflight checks pass. A first
  rehearsal's14-versus15 assertion typo was fixed before freezing; all32 tests rerun successfully.
- Bound D-035 to protocol c0f572881fe9ab3eb8d2b3c53fa7ca150b5365273acaf81ba21b613650abeb6d,
  verified3312 old file hashes and started serial15-call N-057. No outcome claimed before review.
  [Protocol rationale](pilot/enhancement/candidate-routing-control-v0.1/README.md).

## 2026-09-27 — N-055 neutral candidate-analysis entry

- Added versioned syntax-only routing over an explicit public source map. Empty nomination,
  whole function, partial region, exact statement, ambiguous and unsupported cases remain distinct.
  Declared spans are preserved; function context and seed are separate, with source-order outlines.
- Reuse old lexical inventory only for unambiguous complete statements; no silent12–16 to12–20
  expansion, private-path reads, nested-scope mixing, candidate ranking or eligibility verdict.
-31 focused tests and49 regressions pass; five original drafts produce audited packets. Three source
  files match the public task line-for-line;3298 old hashes unchanged. Zero new model/QPU calls.
- Next: freeze a separate S self-review/C directory/R directory-plus-routing control; no mixing with
  formalization or correctness feedback. [Interface](pilot/enhancement/candidate-routing-v0.1/README.md).

## 2026-09-27 — N-054 separate rank-QUBO audit

- Manually bound N-053 F5's actual rank construction and objective; froze a separate offline audit
  without changing original experimental results, checker, benchmark labels or paper.
- Exact enumeration passes31 known finite states and1704 post-hoc synthetic states;13 nonfinite
  states excluded.72990 assignments checked across P=1/10,1,7; fractional P probes the abstract
  positive-penalty claim, not the response's integer-coefficient admission wording.
- Added a reviewable general mathematical argument for exact P>0;18 tests include four failure
  controls. Exact replay passes and3285 old hashes match; zero new model/QPU calls.
- Quadratic classical rank construction reveals the winner; no practical gain or structural-gold
  adjudication follows. Next is the already designed neutral candidate-analysis entry interface.
  [Report](pilot/enhancement/rank-qubo-audit-v0.1/REPORT.md).

## 2026-09-27 — N-053 claim elicitation completed

- All10 revisions valid, zero operator retries/tool events/transport errors. F replicate1's explicit
  reference scan passes44 known states; replicate2 passes31 under its finite guard, excluding13.
  S replicate2 fails8 states; replicate5's secondary Grover relation has two readings, each fails3.
- Both arms retain null plans in replicates3/4. F replicate5 supplies rank-QUBO coefficients, a
  positive-penalty argument and decoding, but lies outside the frozen checker. Both arms still have
  three insufficient rows: distinguish a missing construction from a checker coverage gap.
- Ten exact replays and3114 old hashes match. Input162484/output21096 tokens, model434.623s.
  Per-response review intervals sum321.440s but overlap; union161.909s, span163.350s, AI review only.
- Added read-only --check-only replay and actual-results learning notes. Next: separately verify
  the explicit QUBO, keeping this protocol, outcomes, guard, costs and scientific labels unchanged.
  [Report](pilot/enhancement/claim-elicitation-v0.1/execution-20260927/REPORT.md).

## 2026-09-27 — N-052 claim-elicitation preparation; N-053 started

- Froze ten paired revisions of all five original N-048 drafts: self-review versus generic
  specification request, with shared new wrapper, alternating order and no evaluator feedback.
  Null plans and supported alternative families remain permitted; known44-state regression only.
- Versioned N-050 runner mechanics;32 focused tests and49 regressions passed, including a complete
  ten-position fake-transport rehearsal. Five offline isolation/wire checks passed without inference.
- D-035 delegated-budget receipt bound to protocol dfec27c33f110f47aaa63d969d45622e1bd37861d27f2aded85a1a34ab2bedc2.
  N-053 live queue started, serial Sol/medium,600-second timeout,zero operator retries;3114 old files
  hash-checked unchanged before launch. No outcome claimed until final review and collection.
  [Protocol and rationale](pilot/enhancement/claim-elicitation-v0.1/README.md).

## 2026-09-27 — N-051 feedback-information control completed

- Recorded D-034 approval and ran all16 frozen Sol/medium subscription revisions, all valid with zero
  operator retries, tool events or transport errors. No new initials or post-hoc added positions.
- In the sole explicit initial-error pair, E summary and W witness both produce ordered strict-greater
  selection and pass44 known regression states. S still fails3; C lacks a concrete selector. No W-over-E
  incremental finite-correctness benefit observed. E also has one guarded31-pass/13-excluded claim.
- Twelve responses remain insufficient; nomination/plan growth and QUBO sketches are not credited as
  semantic repair. Recorded finite-test-count versus finite-value wording confusion for future versions.
- All16 reviews followed the model queue and preceded evaluation; exact replay and2921 protected-file
  hashes match. Input260561/output36815 tokens, model746.119s, coordinator review315.204s wall time.
- Recorded D-035 delegated subscription budget and synchronized workflow: no repeated same-scope
  per-round quota questions, while each future experiment still has its own fixed protocol and limits.
  [Report](pilot/enhancement/feedback-control-v0.1/execution-20260927/REPORT.md).

## 2026-09-27 — N-050 feedback-control execution preparation

- Adapted N-049's exact16 prompts to retained isolated transport and reviewer-bound checking,
  with S/C/E denominators5 each and W1. Protocol and88 source dependencies frozen; no live approval.
- Preserved at-most-once attempts, recovery without reissue, invalid-response retention, infrastructure
  stops and final-binding barriers. Results explicitly distinguish known regression from unseen testing.
- 32 focused tests and49 semantic/analysis regressions pass. Retained full16-slot fake-transport
  rehearsal; its responses and costs are fixtures, not new model observations.
- Five offline preflight checks pass using pinned CLI0.156.1, dummy auth and a local rejecting sink in
  an unshared network namespace. Actual witness-prompt request has no tools; private roots are hidden.
- Live queue remains await_authorization with zero attempts;2764 prior files unchanged. No dependencies,
  QPU, paper edits or real credential access. [Configuration](pilot/enhancement/feedback-control-v0.1/README.md).

## 2026-09-26 — N-049 offline feedback-control design

- Mapped all25 N-048 responses to six coordinator-authored design routes with90 exact source anchors;
  retained original verdicts, QUBO limitations and main/secondary claim distinction.
- Audited five analysis entries: empty nominations and function-start rejection remain distinct;
  compound seed selection uses only start_line and can exceed the declared end. Generated syntax-only
  public function/body outlines, without candidate ranking, source execution or a new analysis adapter.
- Prepared16 exact offline prompts: five each self-review/scope-cue/assessment-summary, one witnessed
  development-failure branch. No simultaneous clarification or analysis intervention; no new model calls.
- Marked the previously inspected44 reserved states as known regression data for prospective work.
  Next: adapt and offline-preflight the concrete configuration before asking for new call authorization.
  [Design and validation](pilot/enhancement/state-workflow-design-v0.1/README.md).

## 2026-09-26 — N-048 bounded Sol ablation completed

- Recorded D-033 approval and ran all25 frozen Sol/medium subscription calls: 25 valid responses,
  no operator retries, transport errors or tool events. Used installed/pinned CLI0.156.1 after the
  default CLI updated to0.157.0; original protocol, source and preflight remain unchanged.
- The only explicitly contradicted initial replicate is repaired locally by V and AV on all44
  reserved pivot states; S and A remain contradicted. Both repairs share one initial draft.
- Reported all five slots per arm, unknowns, ambiguity, guarded passes, newly contradicted claims,
  task-cue confounding and unverified fallback/QUBO scope; no overall or universal uplift claim.
- All25 final evaluations replay exactly; bindings and chronology verified, 2429 prior files unchanged.
  Usage395819 input/53025 output tokens; model1164.678s, reviewer wall605.356s, distinct cost scopes.
  No QPU, installs, paper edits or extra sampling. Authorization exhausted.
  [Report](pilot/enhancement/state-workflow-v0.3/execution-20260926/REPORT.md).

## 2026-09-25 — N-047 recoverable ablation runner and wire-level offline preflight

- Added immutable attempt/review/result records, single-process lock, at-most-once dispatch,
  same-draft revisions and final-binding/evaluation barriers; all 25 slots remain in reporting.
- 26 new and 49 prior tests pass, including complete fake-transport rehearsal and crash injection.
- Offline capture found bundled Sol tool metadata overrides feature flags in CLI 0.156.1.
  A local pinned catalog clears three tool fields; explicit plan/question disabling completes
  tool removal. Actual serialized requests now have no tools; historical artifacts stay untouched.
- Five preflight checks pass with dummy auth and an unshared network namespace. Local HTTP sink
  rejects requests, never infers. No real credentials read, model/QPU calls, installations or paper edits.
- 2391 prior files unchanged. Prepared exact 25-call protocol, still without authorization receipt.
  [Report, limitations and commands](pilot/enhancement/state-workflow-v0.3/README.md).

## 2026-09-25 — N-046 reviewed claims and separate feedback/evaluation suites

- Added new-response quote/hash bindings, reviewer provenance, bounded data-only expressions
  and predicate/ordered-scan checks; preserved ambiguity, guards, withdrawal and unsupported claims.
- Prepared 3 development requests/13 pivot states and 12 reserved requests/44 states from
  unchanged trusted source. Same mother case, no independent holdout or whole-task verdict.
- Correct/equivalent controls pass; five incorrect controls fail reserved checks. The always-first
  mutant passes development and fails reserved checks, exposing the development coverage limit.
- 37 new plus 12 previous tests pass, including 780 abstract-state comparisons and byte-identical
  evidence regeneration; 2364 protected files unchanged. Zero model/QPU calls or paper edits.
- Prepared a 25-slot proposal and offline reviewer CLI. Live adapter/preflight and new call scope
  remain next; current CLI is 0.156.1, so historical preflight is not assumed current.
  [Report and validation](pilot/enhancement/state-workflow-v0.2/README.md).

## 2026-09-25 — N-045 offline workflow and guided learning

- Recorded D-032 delegation: choose and advance the current workflow locally, explaining
  next action, purpose and actual effect; do not keep asking the beginner to select architecture.
- Read pinned ai-agent-book chapters and experiment records; adapted component ablations,
  recorded observations and explicit outcome boundaries. Added a Chinese project-based guide.
- Implemented AST lexical dependency inventory, exact historical-claim feedback binding and
  S/A/V/AV revision-packet preparation. No live model transport or automatic arbitrary-prose judge.
- Twelve focused tests pass; four offline branch inputs generated, 2347 previous files unchanged.
  No model-quality effect measured, no new model/QPU calls, installs, manuscript edits or publication.
  [Implementation and validation](pilot/enhancement/state-workflow-v0.1/README.md).

## 2026-09-25 — N-044 reachable-state and transcription audit

- Reviewed the existing Sol009 claim, actual elimination state and classical fallback limits.
  Replayed seven historical pivot states and traced six states in a new same-mother sensitivity
  input; the two-NaN state refutes both inclusive and self-excluding predicate interpretations.
- Audited 009/010 scan source boundaries and recorded Sol010 missing-entry wording ambiguity
  without relabeling. Proposed dynamic-state premise analysis plus counterexample feedback;
  no method or future run authorization inferred from this proposal.
- Added an offline trusted-source trace script and evidence; synchronized status/queue/backlog.
  Verified local links and 2342 protected old files; no model/QPU, shared evaluator changes,
  manuscript edits, dependency installation or Git publication. Main tests not rerun.
  [Review and validation](pilot/enhancement/lit009-review-v0.1/README.md).

## 2026-09-25 — Current paper directory and new-session handoff

- Clarified the user's interaction requirement: agents restore context automatically;
  the user can simply say “继续” and need not name or paste any handoff path.
- Recorded the user-designated `FSE/paper/` as the sole manuscript editing location
  after its requested rename; preserved the original draft and ZIP as historical snapshots.
- Updated workspace entry, project status/queue links, and paper-local AGENTS/README/HANDOFF
  so a new conversation can recover both research and manuscript context.
- Compared manuscript bytes with the original delivery and checked local prototype entry points;
  documented that the integrated method and extended experiments remain proposals.
- Documentation-only handoff: no paper TeX, research code, labels, results, model calls,
  dependencies, Git commits or external state changed. Local-link and protected-file checks
  are recorded in `../paper/notes/handoff-validation-20260925.json`.

## 2026-09-25 — FSE 2027 manuscript source draft

- Prepared an English LaTeX draft under the CFP's acmsmall anonymous-review
  configuration, with six research questions, eight proposed experiments, empty
  empirical result tables, and three conceptual figure placeholders.
- Kept implemented benchmark/local-feedback evidence distinct from the proposed
  integrated method; no new experiment, scientific label, split, or metric adopted.
- Added source/evidence notes and experiment templates. Local preview compiles
  using explicitly substituted fonts because the installed TeX environment lacks
  ACM font packages; final standard-font pagination remains to be checked.
- [Editing package](paper/fse2027-draft-20260925/README.md) and
  [actual validation](paper/fse2027-draft-20260925/validation.json).

## 2026-09-23 — N-043 bounded same-model semantic-feedback pilot

- Under explicit D-031 task/configuration choices, implemented a separate lit-002
  general QUBO-template protocol, safe arithmetic compiler, exact development feedback,
  paired self-review control and evaluator-reserved final tests. Existing benchmark unchanged.
- Completed15 GPT-5.6 Sol subscription calls: all three arms5/5 finite passes. No initial
  error, no actual counterexample feedback and no observed gain; repair ability unmeasured.
- Two correct/equivalent controls accepted, five semantic mutants rejected;26 new tests
  pass, repository223 pass/15 optional skips. Preserved raw inputs/responses and exhausted
  run authorization. Replayed15 responses,104 definition expectations and863 old-file hashes.
- [Report](pilot/enhancement/lit002-v0.1/REPORT.md),
  [final validation](pilot/enhancement/lit002-v0.1/validation.json).

## 2026-09-23 — N-042 record the confirmed same-model enhancement direction

- Added the researcher's exact statement to the charter and accepted decision D-030:
  use program analysis and semantic verification to strengthen LLM-based quantum
  opportunity identification and mapping design.
- Clarified the bottleneck-to-method research path, same-model baseline comparison,
  harness terminology and distinction between direction, implementation and evidence.
  Synchronized status, queue, backlog and research log. Documentation only; existing
  cases, labels, code and experiment artifacts unchanged; no new model or QPU calls.
- Documentation/link and protected-file audit:
  [validation](artifacts/research_direction_20260923/validation.json).

## 2026-09-23 — N-041 authorized four-model C repeat

- Ran ten unchanged C inputs per model under D-029: Sol/Astra 10 valid each,
  DeepSeek Pro 9, Flash 7; all forty attempts retained. Four completion-budget failures,
  no operator retries, repairs, tool calls, model substitution or private-test exposure.
- Kept pending-reference diagnostics separate from correctness and fixed denominators
  even for incomplete models. Seven quote-bound objectives pass 38 finite checks.
- Executed the original numerical program to expose reachable NaN contradicting the
  unique-marker pivot predicate in Sol/Pro lit-009. Normal/corrected controls pass;
  the models' classical fallback and whole plans remain unjudged. Post-hoc evidence,
  not a retroactive addition to the frozen test suite or a model ranking.
- Recorded new validation-scan nomination differences in 009/010. No labels changed.
- 28 offline tests passed; replay/provenance/link audit and 1654 protected files unchanged.
  [Report](pilot/model_comparison/20260923-four-model-c-v0.1/REPORT.md).

## 2026-09-22 — N-040 complete scoped verification for the remaining six cases

- Extended private v0.2 contracts/oracles/controls to weighted cut, coloring, knapsack,
  signed pairs, small-system/pivot behavior and bounded iteration behavior. The original
  four contracts remain identical; all ten mothers now have scoped executable controls.
- Accepted both binary-search and one-hot coloring constructions, explicit equivalent
  encodings/energy shifts and knapsack auxiliary decoding; numerical labels remain unknown.
- Detected and preserved a real new-verifier failure: negated coloring penalties had the
  right zero set but wrong minimum. Added extremum-bound checks and retained before-fix log.
- Final: 61 inputs; 22 correct/equivalent controls accepted and 30 mutants rejected;
  84 new tests pass, main suite 223 passed/15 optional skips. 1646 previous files unchanged.
  No model/QPU calls or scientific relabeling. [Report](pilot/semantic_verification/v0.2/README.md).

## 2026-09-22 — N-039 connect case contracts, oracles and evaluator controls

- Added ten private case sidecars retaining the original Phase-1 identification/conditional-plan task.
  Four scoped verifiers cover cover/clique ground-state decoding, locked-SAT predicate/selection,
  and deterministic receipt-report obligations; six remaining cases are metadata-only in this version.
- Ran 23 named inputs with 8 correct/equivalent controls passing and 10 semantic mutants rejected.
  Bound and reproduced the two archived lit-002 formula counterexamples without whole-plan verdicts.
- Added 42 regression tests: equivalent representations, all ground states, exact definition anchors,
  diagnostic categories, fixed denominators, source integrity, unknowns and overwrite refusal.
- Baseline main suite: 97 passed/15 skipped; after: 139 passed/15 skipped. Seven legacy focused groups
  pass unchanged; 1636 protected files unchanged. No model/QPU calls, installs or historical rescoring.
  [Report](pilot/semantic_verification/v0.1/README.md).

## 2026-09-22 — N-038 archive supplied lit-002 review feedback

- Recorded the supplied concurrence on two formula refutations in a separate appendix,
  preserving the Flash textual-branch interpretation and whole-plan/fallback limits.
- Bound the two records to unchanged model responses and HOW v0.2; no other review,
  label or score changed. Reviewer identity and independence remain unknown.
- Updated the supervisor brief and current queue to acknowledge received feedback.
  No new mathematical execution, model call or independent-review claim.
  [Record](pilot/how_review/adjudications/20260922-lit002/README.md).

## 2026-09-22 — Supervisor progress summary

- Added a short Chinese progress brief for supervisor synchronization, covering the
  research objective, ten-case/four-model pilot, pending semantic evidence and next
  methodological questions. No new experiment, scientific decision or label change.
  [Brief](docs/SUPERVISOR_UPDATE_2026-09-22.md).

## 2026-09-22 — N-037 implement accepted HOW option A

- D-026 records the researcher's explicit A choice: conditional plans with separate
  correctness evidence and obligation completion, no scalar score or executable-code requirement.
- Added independent HOW v0.2. Inherited nineteen reviewed answers and reviewed the
  remaining twenty; forty requests retain 156 claim records and 200 completion entries,
  including the untouched Flash budget failure. All case judgments remain AI/PENDING.
- Prepared thirteen allowlisted reference-review payload files plus manifest, blank
  human forms and holdout protocol draft. No claim of completed blind/independent review.
- Additional finite checks cover 761 weighted MaxCut graphs, 1100 signed graphs and
  6472 Boolean predicate instances. Four corruption-rejection tests pass; provenance,
  replay, packet identity and 1605 protected old files verified unchanged.
- No new model, QPU, install, Git commit/push or label promotion. Next gate is narrow
  researcher adjudication of the two [lit-002 formula witnesses](pilot/how_review/v0.2/REVIEW_HANDOFF.md).

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
