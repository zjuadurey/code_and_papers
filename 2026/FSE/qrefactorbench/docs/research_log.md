# Research notebook

## 2026-09-28 — lit-001 actual single-model workflow integration

User explicitly requested a real LLM/tool/feedback run after correcting a hand-authored smoke
misreported as workflow completion. [New run](../pilot/llm_workflow/lit001-v0.1/README.md): four
Sol/medium calls read source, generated QAOA QASM, invoked verification and QDK/cost tools, and
concluded REMAIN_CLASSICAL. Actual quantum samples produced the exact output without fallback.
The controller supplied the certificate/recovery helper and requested the QAOA family; this is a
single supplied workload integration result, not autonomous algorithm discovery or an effect comparison.
All six scenario cost terms were populated; dispatch/transfer/offline compilation are explicit
assumptions. Strong classical coloring beat this tiny candidate under those assumptions.
44 focused/regression tests passed, and replay reproduced simulation and QDK estimates exactly.
No source-case/gold/metric, historical run, resource-backend implementation, or paper was modified.

## 2026-09-28 — Benefit objective and layers of evidence (D-037)

**RESEARCHER DIRECTION:** Quantum benefit is central to whether migration is worthwhile; preserve the
discussion and current search in layered documentation spanning implementation and paper writing.
**CODE OBSERVATION:** `extract_resources` reports supplied-circuit counts; the strict
`end_to_end_quantumization_success` conjunction contains no classical/quantum cost comparison.
**SOURCE REVIEW:** Checked official abstracts/metadata for Dalzell et al. (2310.03011v2),
Beverland et al. (2211.07629v1) and Babbush et al. (PRX Quantum 2, 010103). No full-paper audit.
**WORKING PROPOSAL:** Separate mapping, semantics, resource feasibility, conditional benefit predictions
and measured task benefit; record theoretical claims with their computational model and assumptions.
Hardware profiles, main benefit metric, thresholds and a concrete protocol remain open.
No new empirical result, label, experiment or paper contribution is asserted.
[Layered record](quantum_advantage/README.md).

## 2026-09-18 — infrastructure initialization

**OBSERVATION (artifact inspection):** The starting workspace was empty. The four
initial cases are generated infrastructure demonstrations, all DRAFT, with no
human annotators. No pilot benchmark or agreement evidence exists.

**OBSERVATION (contract inspection):** The toy maximum-cut function returns an
exact optimal score. Its proposed QAOA contract leaves the method of obtaining an
exact answer unresolved. The schema can record this gap; passing schema validation
cannot establish that the proposed migration preserves the function's semantics.

**HYPOTHESIS:** Annotation disagreement may be concentrated in practical suitability
because oracle access, loading costs and execution assumptions change the answer.
This has not been measured; independent human seed annotation is needed.

**HYPOTHESIS:** Explicit ordered side effects may create useful hard negatives.
The audit-loop case illustrates the recording format only; no empirical taxonomy
or impossibility claim is established.

**OPEN QUESTION:** A selected contract ID is cheap to produce. What structured
proof obligations or trusted tests will establish actual plan conformity across
multiple formulations? See Q5 and Q9.

**OPEN QUESTION:** Should strict success require numeric resource bounds for every
positive, or admit human-certified non-applicability for some components? Current
D-006 preserves unknown results until this is decided (Q13).

No model-quality, quantum-advantage, annotator-agreement or semantic-migration
RESULT is claimed. Test results belong to CHANGELOG.md and validation.md.

## 2026-09-18 — Phase-1 pilot preparation

**OBSERVATION (schema/code inspection):** The v0.1 prediction format did not retain
separate structural/suitability judgments. Its private intent-ID comparison would
be unsuitable as a blind open-description recognition test. The new profile
retains free text for human semantic coding; no recognition score is inferred.

**OBSERVATION (protocol inspection):** D-005's reviewed hard-negative region rule
and a T1 answer of no supported candidate can conflict. Two unsupported DRAFT
pilot cases explicitly use empty eligible spans and retain hotspot notes privately.
This remains Q14, not an automatically resolved scientific convention.

**OBSERVATION (artifact provenance):** Ten synthetic programs and draft annotation
proposals were written with Codex assistance. All independent annotator identities
and judgments are blank. Six positive-category proposals retain unknown practical
suitability, support and final decision. No model API was invoked.

**HYPOTHESIS:** Exposing workload assumptions may reveal confusion between a
structural predicate formulation and the cost of loading fresh classical data.
The tiny-lookup and fresh-data cases are probes, not empirical evidence.

**OPEN QUESTION:** Exact optimization outputs, no-solution search semantics,
baseline response failures and alternate valid plans require human review before
scientific scoring. Neither passing classical tests nor sharing a contract ID
establishes quantum semantic preservation.

## 2026-09-19 — Source-grounded advisory review

**OBSERVATION (blinded source/public specification):** pilot-009 public_task.json
describes name,left_cost,right_cost as integer fields, while support.py:2 rejects
non-string names. Schema/file validation does not resolve this specification
conflict. Q17 records the human decision; neither artifact was modified.

**OBSERVATION (source algebra, not an executed quantum migration):** 007's subset
equality can be expressed by a zero squared residual; 005's unit equality plus
budget bound admits a proposed squared-residual/slack construction under explicit
encoding conditions. These illustrate possible alternate supported formulations,
not reviewed admissible contracts. Intent need not determine a unique family.

**OBSERVATION (supplied assumptions):** The review could not derive a practical
cost comparison for eight structurally proposed cases from supplied workload and
resource facts. The bounded lookup and fresh-data cases motivate conservative
retention but still require an explicit suitability rubric (Q1/Q6). This is an
information audit, not annotator agreement or a measured profitability result.

**OBSERVATION (public prose):** Public tasks describe computational intent; 005
points to enumeration and 002/008 explicitly exclude search/optimization readings.
No populated private case-label fields were found in model prompts, but field-level
blinding alone does not settle whether these cues fit the intended task (Q18).

**HYPOTHESIS:** Shared uncertainty about exactness, suitability and alternate
formulations may reflect incomplete benchmark definitions rather than individual
annotation errors. Independent human evidence is needed to test this.

**OPEN QUESTION:** How should unknown localization and uncertainty-driven abstention
be interpreted when label fields allow null but final decisions are binary and
model candidate_regions requires an array? No schema/scoring policy was changed.

Ten AI-assisted proposals cite blinded source/task/menu evidence and were hashed
before reference-dependent workflow/provenance inspection. Earlier preparation
context was available, so they are not independent annotations. No scientific
model, agreement, advantage or semantic-migration RESULT is claimed.

## 2026-09-20 — Approved public-input revision

**OBSERVATION (source/specification check):** The researcher chose the executable
string-name behavior for pilot-009. pilot-v0.1 corrects only its public description;
valid names and invalid-name/link errors were checked against unchanged code.

**OBSERVATION (ten-case prose audit):** Explicit enumeration directions, assertions
excluding search/optimization, formulation-oriented titles and a QAOA hint were
removed. Exact output requirements, side effects and cost-relevant workload facts
remain. Original public inputs and packets are preserved with a field-level diff.

**OPEN QUESTION:** How much recognition assistance remains inherent in the necessary
functional specifications and original source identifiers? No scientific model
response or before/after comparison was collected. No label or suitability claim
follows from this presentation revision (D-011/Q18).

## 2026-09-20 — First restricted CLI pilot observations

**RESULT (descriptive outputs from one ten-case run):** Restricted Codex CLI
0.154.0, gpt-5.6-sol/high, ChatGPT-authenticated, produced ten schema-valid first
responses. All decisions are REMAIN_CLASSICAL; eight structural YES and two NO;
practical NO=8 and unknown=2; every structured plan is null. No practical YES
appears. This is not a general capability result or a raw API experiment.

**OBSERVATION (rationales):** Several practical NO judgments cite unknown costs
or missing exactness guarantees, while two cases retain practical null. The
distinction between violated conditions, insufficient evidence and conservative
action requires a human rubric; no scientific labels were changed.

**OBSERVATION (existing DRAFT evaluator):** Five case-level candidate sets match
exactly; all five mismatches still overlap draft regions. Only four decisions
have known references, all REMAIN_CLASSICAL; conditional agreement of 4/4 cannot
be interpreted as ten-case migration success. Free-text intent remains unscored.

**OPEN QUESTION:** Does requiring a structured plan only on QUANTUMIZE leave T3
unobserved when suitable caution produces universal abstention? Should benchmark
support be more clearly separated from measured-benefit evidence? Neither question
was resolved by changing this experiment, its frozen inputs or scoring.

Evidence and limitations: ../pilot/baseline-v0.1/restricted-codex/BASELINE_RESULTS.md
and FAILURE_NOTES.md. No finalized taxonomy, statistical significance, quantum
advantage, independently validated labels or agent-design conclusion is claimed.

## 2026-09-20 — Conditional-plan controlled diagnostic

**RESULT (descriptive paired outputs):** With the same CLI 0.154.0, gpt-5.6-sol/high,
ChatGPT login, ten frozen inputs and isolation, appending only the researcher-approved
conditional-planning instruction produced 8/8 non-null plans among structural YES,
versus 0/8 originally. All eight still report practical NO/UNCERTAIN and recommend
REMAIN_CLASSICAL. Both structural-NO controls retain null. All ten first attempts
are schema-valid; no repairs, retries or observed tools.

**OBSERVATION (AI-assisted content coding):** Eight plans contain case-specific
predicate/objective, encoding and verification paths and are coded SUBSTANTIVE.
All eight resource objects remain generic unresolved markers, and exact absence
or global-optimality certification remains unresolved. Content is not correctness.

**OBSERVATION (paired variation):** Structural, practical, decision and main family
fields are unchanged; candidate regions change in three cases, benchmark support
in five, and contract applicability labels in four. Intent wording changes while
the described main computations remain recognizable. Changes are not scored as
improvements or regressions.

**HYPOTHESIS:** The pattern provides stronger support for H1 (adoption/planning
elicitation coupling) at the formulation level. It does not identify the original
internal reasoning cause, prove complete HOW competence or establish significance.

**OPEN QUESTION (Q19):** How should conditional plan coverage and scientifically
verified HOW quality be assessed separately when semantic/resource obligations
remain unresolved? Human review and a future protocol decision are still needed.

Evidence: ../pilot/baseline-v0.1/conditional-plan-diagnostic/CONDITIONAL_PLAN_DIAGNOSTIC_RESULTS.md
and PLAN_CONTENT_REVIEW.md. This paired diagnostic is not an independent baseline;
no reference-label comparison or further system development was performed.

## 2026-09-20 — Repository-driven research continuation

**ACTION (project control):** Consolidated stable research intent, dynamic status,
decision history and a finite safe-action queue. The current handoff points to the
completed paired diagnostic without counting it as an independent baseline.

**OBSERVATION (documentation audit):** Historical T1/T2/T3 task numbering and
conceptual T1–T6 describe different granularity; an explicit crosswalk avoids a
silent metric/protocol change. Conceptual expert validation also differs from
schema maturity metadata. Historical decision/experiment content is retained.

**INTERPRETATION:** These are clarification and navigation changes, not new evidence
of quantumizability, suitability, plan correctness or advantage. No experiment ran.

**UNRESOLVED:** Q19 and other scientific decisions still require human review.
Next safe work is a blank coordinator-only review record using existing analyses.
Evidence: [documentation audit](DOCUMENTATION_AUDIT.md),
[charter](RESEARCH_CHARTER.md), [workflow](CODEX_WORKFLOW.md),
[next actions](../NEXT_ACTIONS.md). No scientific label was changed.

## 2026-09-20 — Human review handoff (N-001)

**ACTION:** Prepared one [coordinator-only review record](../pilot/review/CONDITIONAL_PLAN_HUMAN_REVIEW.md)
linking eight emitted plans and two controls, reusing existing unanswered questions.
All human identity/date/judgment/evidence fields remain blank. No new analysis,
review submission, scientific finding, independent annotation or experiment occurred.

**UNRESOLVED:** Plan correctness and Q19 policy adoption require actual human
evidence/direction. N-002 now records that boundary; no additional engineering or
experimental task is inferred from the absence of a submitted review.

## 2026-09-20 — Researcher adopts conditional-planning direction A

**ACTION / DECISION:** The researcher explicitly selected A. [D-014](../DECISIONS.md#d-014-conditional-planning-independent-of-adoption)
records the future protocol requirement: response-reported structural YES elicits
a conditional plan independently of practical suitability and final recommendation.
N-002's policy question is resolved; pending technical review moves to N-003.

**INTERPRETATION:** This is an accepted task-design choice, not a new experiment or
validation of the eight plans. Plan presence/content, correctness, semantics and
practical benefit remain distinct. Human-reviewed eligibility must inform future
coverage/quality assessment; model-self-selected YES cases alone are insufficient.

**UNRESOLVED:** Technical/semantic review, eligibility annotation and precise
coverage/quality metrics remain open under Q19. The blank [human review record](../pilot/review/CONDITIONAL_PLAN_HUMAN_REVIEW.md)
is unchanged. Frozen prompts, results, labels, schemas and evaluator are preserved.

## 2026-09-20 — Alignment audit and original-contract decision

**OBSERVATION (preceding read-only audit):** The repository provides benchmark and
static evaluation infrastructure, not an automatic migration system. Source review
and in-memory probes found: reviewed cases cannot retain unknown practical labels;
Phase-1 evaluate_plan does not reach an explicitly supplied verifier while intent
correctness is unknown; check_interface omits return annotations; pilot-009's private
oracle input description still calls name an integer although public input/code
require a string. These observations do not adjudicate quantumization labels.

**ENGINEERING EVIDENCE:** The preceding audit ran, from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 /home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q -p no:cacheprovider
# 86 passed, 3 skipped, 1 failed in 4.22s
PYTHONDONTWRITEBYTECODE=1 /home/audrey/miniconda3/envs/htp-static/bin/python -m pytest -q -p no:cacheprovider tests/test_optional.py
# 5 passed in 1.52s
PYTHONDONTWRITEBYTECODE=1 /home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench validate cases/
# 14 structurally valid cases; expected DRAFT warnings
PYTHONDONTWRITEBYTECODE=1 /home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench summarize cases/ --json
# valid=true; 14 DRAFT cases
```

The failure was test_v01_regeneration_is_byte_identical: prepare_packets copies
the later historical banner from pilot/baseline/README.md into baseline/INSTRUCTIONS.md,
changing it and packet_manifest.json; 97 other files match. The audit changed no
repository files and verified 120 original/129 diagnostic manifest entries. These
are prior-turn observed results, transcribed here; no runtime suite ran again in
the policy-recording task. The historical 87-pass result remains historical.

**DECISION:** The researcher explicitly approved preserving the original software
contract by default, recorded as [D-015](../DECISIONS.md#d-015-preserve-the-original-software-contract-by-default).
This includes exactness, exceptions, effects and required ordering. Approximation
or probabilistic guarantees require permission in the original contract; internal
randomness alone is not prohibited. Changed contracts require separate versioning.

**INTERPRETATION:** D-014 conditional planning and D-015 preservation coexist:
a plan may explain unresolved obligations without establishing a correct migration.
No plan, label, scoring rule, case or experiment is changed or validated by this choice.

**OPEN QUESTION:** Case-specific oracles/certification, statistical policies where
permitted, reviewed-but-unknown labels, hard-negative region meaning and coverage/
quality scoring remain unresolved. Q9's default is decided; do not ask it again.

## 2026-09-20 — Researcher decisions on discussion items 2–5

**DECISION:** [D-016](../DECISIONS.md#d-016-reviewed-uncertainty-broad-candidates-and-staged-evidence)
records explicit approval of reviewed uncertainty, WHERE candidates that WHETHER
can reject, practical judgments under explicit evidence/assumptions, and preliminary
coordinator review followed by independent/expert validation for important formal
evaluation cases. No real review was submitted by approving this workflow.

**INTERPRETATION:** Candidate nomination no longer prospectively implies structural
acceptance. Review maturity does not imply certainty. Simulator results are not
measured end-to-end quantum advantage. Existing frozen cases, scores and old schema
semantics remain unchanged; a versioned implementation is still needed.

**OPEN QUESTION:** The researcher explicitly requested further discussion of item 1
(Q2): whether structural eligibility certifies a concrete formulation or a complete
contract-preserving migration argument. No answer or new scientific label was inferred.
D-015 preservation and D-014 conditional planning remain in force.

## 2026-09-20 — Structural definition accepted (discussion item 1)

**DECISION:** The researcher accepted the proposed boundary, recorded as
[D-017](../DECISIONS.md#d-017-structural-mapping-is-distinct-from-contract-preservation).
Structural YES requires concrete computational-core/formulation correspondence
with domain/predicate or variables/objective/constraints, conditions and evidence.
Missing essential mapping evidence remains UNCERTAIN. Complete original-contract
preservation and practical suitability are separate judgments.

**INTERPRETATION:** All five discussion directions are now recorded. This allows
future evaluation to distinguish failure to recover a formulation from failure to
complete a correct migration, without accepting superficial algorithm naming.
No existing plan or case was reviewed or relabeled by this policy choice.

**UNRESOLVED:** Case-specific evidence, semantic oracles, annotation consistency and
final scientific metrics still require review. Engineering can proceed with the
existing packet-export regression and a versioned implementation of accepted rules;
no new model experiment or default statistical threshold is authorized.

## 2026-09-20 — Packet reproducibility boundary restored (N-004)

**OBSERVATION:** A mutable coordinator README had become an export dependency;
adding historical experiment links changed regenerated distribution instructions.
This exposed a route for project history to enter future packets, not evidence of
contamination of the already completed isolated runs. Frozen inputs were unchanged.

**ACTION / RESULT:** Separated versioned packet instructions from the coordinator
README. Fresh exports again match all 99 frozen packet files; tests also verify
identity when README contains a private sentinel or is absent, using export sources
without prior packets/results. No scientific prompt, annotation or metric changed.

**INTERPRETATION:** This restores artifact reproducibility only, not scientific
validity. Numerical/runtime checks and preservation evidence are in
[N-004 validation](../artifacts/n004_packet_regeneration/README.md).

## 2026-09-20 — Bounded executable demonstration, before more infrastructure

**ACTION:** At the researcher's request to finish a terminal demo tonight, connected
saved pilot-001/002 analysis replay to a separately AI-assisted CNF/Grover implementation
and an unchanged classical-retention example. No new scientific model call occurred.

**RESULT:** The real local Qiskit simulation returned a classically verified witness
on the selected satisfiable input. The unsatisfiable input used exhaustive classical
fallback; empty and duplicate/tautological-clause examples retained Boolean behavior.
The retained digest program preserved callback contents/order. Focused tests include
a satisfiable case whose quantum sample misses, requiring a true-result fallback.

**INTERPRETATION:** Demonstrates the engineering distinction between a conditional
quantum kernel and a complete exact software interface. Exactness here depends on
verification/fallback, whose cost may remove benefit. Finite tests are not a general
proof, benchmark accuracy, independent plan validation or quantum advantage.

**UNRESOLVED:** General automatic analysis/refactoring, useful search scheduling,
hardware feasibility, practical costs and independent scientific review remain open.
The demo does not resolve them or authorize a new model experiment. Evidence and
one-command walkthrough: [demo](../demo/README.md).

## 2026-09-20 — Separate CA6000 SAT coursework, not benchmark expansion

**ACTION:** After receiving the course's neural-network training requirements, the
researcher chose an own-project SAT prediction dataset rather than a public medical
dataset. Generated 3,000 bounded formula inputs for pilot-001 and computed exact
SAT labels; no quantumization annotations were used or created. English PPT requested.

**RESULT:** A fixed CPU MLP run achieves 551/601 correct predictions (91.68%);
linear 90.85%, majority 55.91%. All formula labels pass a second Boolean evaluator.
Canonical group isolation covers variable renaming/order. Aggregate features still
have four training/test overlaps; excluding those test rows gives 91.62% on 597
without retraining. The interface exposes a real model error and exact verification.

**INTERPRETATION:** An educational workflow demonstrating acquisition, cleaning,
statistics, training, evaluation and AI-assisted development. It is not evidence of
quantumization recognition, validated migration, solver superiority or quantum
advantage. Small synthetic inputs and lossy features constrain interpretation.

**ARTIFACTS:** [Selected coursework](../coursework/sat_case_study/README.md).
Existing benchmark cases, schemas, labels and completed model experiments preserved.

## 2026-09-20 — Return to FSE: objective correspondence versus complete migration

**ACTION:** The researcher ended the coursework diversion. As post-hoc review
support, manually transcribed the three saved optimization plans and compared
their objectives and exact-rational Ising expansions with original computations.
This is a bounded arithmetic audit, not an additional model condition or baseline.

**RESULT:** Across 1,805 permitted inputs / 7,083 assignments, no mismatch; each
recovered optimum also matches an actual original-function call. Fixtures include
empty domains, signed coefficients where permitted, repeated/reversed/self terms,
and a large integer. Deliberately incorrect variants are distinguished. Each case
has a feasible sample whose correctly rescored value differs from the exact API
result, demonstrating the incompleteness of sample-only decoding.

**INTERPRETATION:** Adds finite executable evidence for particular formula
correspondences beyond plan-presence/SUBSTANTIVE coding. The responses already
acknowledge missing certification, so witnesses are not observed model mistakes.
They support keeping objective mapping, optimizer guarantees and full contract
preservation separate; they do not establish a general capability or failure rate.

**UNRESOLVED:** Human inspection of transcription/evidence; concrete circuits,
certification, precision/resource assumptions, interface integration, and eventual
evaluation criteria. No annotation promoted. Five search plans still need bounded
predicate/decoding evidence; no additional model run is authorized.

**ARTIFACTS:** [Audit and reproducible evidence](../artifacts/plan_mapping_audit/README.md).

## 2026-09-21 — Functional context is not verified application provenance

**ACTION:** Following the user's return to benchmark design, inspected source,
public requirements, existing tests and curator provenance for pilot-005/009.
Used a few original-code probes, not another model run or dataset expansion.

**OBSERVATION:** Both examples contain meaningful behavior outside their kernels:
005's available-offer filter changes the answer; 009's validation and name order
affect its public API. Both remain synthetic. Multiple files and realistic names
alone do not establish application provenance or difficult candidate discovery.

**OPEN QUESTION:** 005 explicitly requires sorting, while normal-input permutation
does not change its Boolean/count response. Clarify the external contract versus
process requirements; do not silently remove the existing requirement. Missing
workload and practical evidence remain missing for both cases.

**RESULT / LIMIT:** Original test files each pass (one test each); concrete context
observations recorded. No hybrid migration was executed or validated, no human
annotation completed. N-007's larger predicate audit is paused in favor of concrete
case-source/task-boundary comparison. [Review](../artifacts/context_case_review/README.md).

## 2026-09-21 — Source-grounded two-case construction trial

**ACTION:** Researcher narrowed the proposed ~10-case expansion to MaxCut and one
constrained graph problem. Selected pinned C2|Q> mirror rows 164/427; retained their
complete functions and added explicitly synthetic named maintenance/inspection APIs.
Documented adaptations and evaluation-method borrowing separately from provenance.

**OBSERVATION:** Source classification labels alone do not specify exact versus
heuristic behavior. Selected functions expose deterministic tie behavior, which an
objective-only check would miss. For vertex cover, feasibility also does not imply
minimum cardinality. These observations motivate separated evaluation obligations;
they are not new observed model failures.

**RESULT:** Two executable DRAFT case packages, 24/22 passing classical tests,
schema validation and an allowlisted public export. The source functions are unchanged;
new context/tests are ours, not claimed author artifacts or deployed applications.
Original 14-case population and frozen experiments remain unchanged.

**LIMIT / OPEN QUESTION:** Original function names expose intent. Useful functional
context does not establish difficult localization or real-world representativeness.
Researchers should review the synthetic requirements, inherited exactness/ties,
candidate boundaries and conditional mappings before expanding. Practical evidence
and package release licensing remain unresolved; scientific judgment fields are null.
No new model, quantum run, independent annotation or validated migration was made.

**ARTIFACTS:** [Construction trial](../pilot/source_adaptations/v0.1/README.md),
[evaluation design](../pilot/source_adaptations/v0.1/EVALUATION_DESIGN.md).

## 2026-09-21 — Second-context functionality and complete-report obligations

**ACTION:** Researcher approved a separate maintenance assessment/adjustment case.
Kept the C2|Q> function and lit-001 unchanged; embedded the same function within a
business module alongside validation, current/proposed scoring and change reporting.
Added synthetic requirements and an executable JSON interface, not a model experiment.

**OBSERVATION:** A correct proposed objective value does not ensure correct movement
instructions. An intentionally omitted move list is detected by the independent
full-report oracle while the proposed score remains correct. Inherited deterministic
tie behavior can also move equipment even when the current assignment is optimal.
Minimum movement was explicitly excluded from the new objective, as approved.

**RESULT / LIMIT:** 43 classical checks pass, including bounded exhaustive current
assignments and report/exception behavior. No quantum semantic preservation was
tested. Functional dependence is stronger than in the source wrapper, but difficult
WHERE discovery and real-world representativeness remain unestablished; the original
algorithm name is visible. This is one context view of the same source problem,
not an independent algorithm/data-source observation.

**OPEN QUESTION:** Review the synthetic functional contract, inherited tie policy
and candidate/dependency boundary before further expansion or a versioned experiment.
All scientific judgments remain null/DRAFT; no independent human label submitted.

**ARTIFACTS:** [Context case and commands](../pilot/context_adaptations/v0.1/README.md),
[actual sample report](../pilot/context_adaptations/v0.1/cases/context-001/example_report.json).

## 2026-09-21 — Context-001 has concrete structural mapping evidence

**ACTION:** Following the user's “继续” after discussing which judgments can be made
now, derived the source's same-window cost into an exact binary quadratic expression
and Ising Hamiltonian. Reused existing exact-rational utilities for executable checks.

**RESULT:** The edge identity proves objective correspondence over the declared
binary domain. Separately, 98 bounded inputs / 1,271 assignment checks agree among
raw requests, source scoring, QUBO and Ising values. Exact polynomial minimizers with
source tie handling reproduce 98 full reports. This latter calculation is classical
enumeration, not a quantum solver or an efficiency result.

**INTERPRETATION:** Supports recommending structural YES under D-017 with an explicit
variable/objective/decoding correspondence. This is AI-assisted evidence, not a human
review or label assignment. The sample has optimum masks 2 and 5; energy alone does
not preserve the original mask-2 output and its movement report. Exact global solution,
general tie resolution and actual quantum resource/benefit evidence remain separate.

**UNRESOLVED:** Researcher initial review of this narrow correspondence; independent
annotation before scientific benchmark claims; eventual full quantum implementation,
certification and resource assumptions. No case, prompt, schema or evaluator changed.

**ARTIFACTS:** [Audit](../artifacts/context001_mapping_audit/README.md),
[machine-readable results](../artifacts/context001_mapping_audit/results.json).

## 2026-09-21 — Researcher initial acceptance of context-001 correspondence

**ACTION / RESULT:** Asked whether the researcher accepted the narrow opinion
“structural correspondence established; complete quantum migration unverified;
practical suitability unknown.” The researcher replied “可以。” and asked why the
audit does not establish reliable quantum solution finding or benefit.

**INTERPRETATION:** This records actual initial acceptance of that scope, not proof
that the researcher independently reran or reviewed every artifact. Independent
annotation, expert validation, serialized label changes and gold promotion did not occur.

**UNRESOLVED:** A cost expression alone does not solve its optimization problem.
The audit used classical exact enumeration; concrete quantum solving, exactness/ties,
complete report preservation and end-to-end cost evidence remain separate work.
No new experiment or contract relaxation was approved by this exchange.

**ARTIFACT:** [Initial review record](../artifacts/context001_mapping_audit/RESEARCHER_REVIEW.md).

## 2026-09-21 — Actual local quantum solver conversion check

**ACTION:** Researcher asked to run the Qiskit program produced from the source.
Implemented a separate AI-assisted one-layer QAOA hybrid prototype with original
pre/postprocessing, fixed COBYLA budget, ideal Statevector expectation and final
256-shot sampling. Protocol written before execution; no optimal-reference feedback
or classical fallback. This is not an autonomous translation/model experiment.

**RESULT:** Five first attempts completed, including four actual circuit simulations
and one empty-input return. All five full reports match the original. Three nonzero
objectives exhausted 80 evaluations without optimizer convergence. In the original
three-device example, optimal masks 2 and 5 occurred 68 and 70 times among 256 shots;
selection among observed samples returned mask 2. Its post-hoc ideal optimal-subspace
probability is approximately 0.530218, not a prespecified statistical acceptance test.

**INTERPRETATION:** Extends structural-expression checks with concrete circuit,
sampling, decoding and report evidence on these inputs. It does not prove exact
optima/tie preservation for arbitrary inputs. A six-device/weight-limited prototype
does not cover the original 16-device/unbounded-integer domain. Exact statevector
expectation is a simulator convenience, not evidence of hardware execution cost.

**UNRESOLVED:** General exactness/certification, canonical tie handling under finite
sampling, broader-domain implementation, success criterion and practical costs.
No labels were changed; no claim of quantum advantage or independent validation.

**ARTIFACTS:** [Implementation and actual outputs](../demo/context001_qiskit/README.md),
[first-run evidence](../demo/context001_qiskit/artifacts/first_run.json).

## 2026-09-21 — Device-limit correction exposes larger-input exactness failures

**ACTION:** Researcher questioned why the prototype rejected 7 devices when the
original supports 16. The six-device cap was engineering convenience without
measurement evidence. Restored the original quantity boundary, preserved old sources,
and kept the original QAOA parameters/budget/seed unchanged. Ran four fixed boundary
fixtures locally, with fresh processes and explicitly fixed numeric-library threads.

**RESULT:** 7/12/16-device calls, including a dense 16-device graph, all complete.
Hybrid-call times range 0.155–8.888s; peak process RSS 127.91–385.34 MiB including
libraries and diagnostic data. 7/12-device reports match. For the 16-device path,
sampled conflict cost is 4 versus exact 0; for the dense graph, 141 versus exact 136.
All four optimizers report budget exhaustion. Outputs were retained without retries
or classical correction; reference solving occurred only after saving hybrid outputs.

**INTERPRETATION:** The asserted need to stop at six devices was not supported by
these measurements. Restoring the device domain exposes concrete execution-success /
semantic-failure examples under the unchanged exact contract. Neither a convergence
flag nor a successful return establishes exact optimum. No speedup, representative
success rate or independent quantum benefit is measured by these engineering checks.

**UNRESOLVED:** Arbitrary-integer weight domain, finite-sampling optimum and canonical
tie obligations, and eventual credible cost comparison. The case remains unchanged
and DRAFT; solving these issues must not be replaced by narrowing its contract.

**ARTIFACT:** [Versioned fix and actual measurements](../demo/context001_qiskit/artifacts/device_limit_v011/README.md).

## 2026-09-21 — Researcher permits a scoped approximate-arrangement profile

**ACTION / DECISION:** After inspecting actual exactness failures, researcher requested
case documentation that accounts for algorithm output characteristics and permits
approximate solutions here. Explicitly selected reporting gaps with tolerance pending,
then accepted quality ratio (W−C)/(W−C*) after business meaning was explained.
The illustrative 95% was distinguished from the accepted definition and remains open.

**INTERPRETATION:** This is a documented change of a prospective task contract, not
proof of preserving the original exact program. Existing soft pairwise preferences
make weighted satisfied-demand quality interpretable; their synthetic weights are
not calibrated business losses. Saved path/dense outputs have ratios 41/45 and
219/224; no new solver experiment or pass/fail scoring occurred. The policy discussion
is post-observation, so existing examples cannot independently validate its cutoff.

**UNRESOLVED:** Acceptance threshold, approximate selection/tie policy, repeated-run
criteria and implementation. Keep hard feasibility, exact report arithmetic, API
and original input domain separate from approximate arrangement quality.

**ARTIFACT:** [Case draft](../pilot/context_adaptations/v0.2-draft/CONTRACT_CONTEXT_001.md),
[D-018](../DECISIONS.md#d-018-context-001-approximate-quality-profile).

## 2026-09-21 — Paired exemplar preparation before broader case generation

**ACTION:** Researcher requested polishing a few high-quality exemplars before later
expansion. Reused the two sourced optimization kernels, made core-view contracts
explicit, retained the maintenance context and developed an inspection review/worklist
context. Synthetic assumptions and source lineage are explicit; no independent-source
or deployed-software claims. There are two problem lineages and four public views.

**OBSERVATION / ENGINEERING RESULT:** Inspection responsibility assignment introduces
observable dependencies beyond returning the minimum station set. A correct count
with empty worklists is detected by the independent full-report oracle. Incomplete
current coverage can require more stations in the proposed plan, so “always reduce
station count from current” is incorrect. Tests check 1,099 bounded graph/current-set
inputs plus invalid/CLI/fault examples; they do not demonstrate quantum suitability.

**INTERPRETATION:** Hard connection coverage must remain distinct from maintenance's
soft weighted separation preferences. The researcher-approved maintenance quality
ratio does not authorize missed inspections or approximate station counts here.
Matching source functions allow paired context comparisons, but source names still
cue intent; increased WHERE difficulty is unproven and views are statistically dependent.

**UNRESOLVED:** Researcher assessment of functional realism, inspection unit-cost/
capacity assumptions, localization difficulty, quantum mapping/benefit evidence,
maintenance approximation tolerance/ties, and source redistribution. Search and
classical-retention exemplars are still absent from this reference package.

**ARTIFACTS:** [Reference pairs](../pilot/reference_cases/v0.1/README.md),
[review guide](../pilot/reference_cases/v0.1/REVIEW.md).

## 2026-09-21 — Search and retention exemplars complete the initial four-group set

**ACTION:** Researcher chose to fill remaining coverage before further polishing
optimization examples. Reused synthetic pilot-001/002 source functions unchanged,
with new named configuration rules/partial profiles and change-batch/audit contexts.
This adds functional views of existing lineages, not independently sourced workloads.

**ENGINEERING RESULT:** Configuration truth-table oracle checks 139 bounded catalogues
and 1,163 partial-profile decisions without using production clause compilation.
Batch tests cover 121 event sequences, independent concrete encoding bytes, full
checkpoint traces and exception-prefix semantics. A fault that suppresses audit calls
returns the right receipt but still fails behavioral comparison. All 68 new tests pass.

**INTERPRETATION:** Context can create obligations beyond a kernel's final value:
fixed-profile information must reach the predicate; audit effects must not disappear
even when the final digest matches. These are concrete integration-error examples,
not demonstrated model failures. A finite configuration predicate motivates a
conditional search proposal; ordered processing motivates a retention hypothesis,
neither is promoted to reviewed quantumization ground truth.

**UNRESOLVED:** Functional realism, independent scientific annotation, reversible
predicate/no-solution guarantees, practical assumptions, actual WHERE difficulty,
licensing and group-aware splitting. No arbitrary feature/event-count cap was added;
bounded tests do not prove unrestricted behavior. No new model/quantum execution.

**ARTIFACTS:** [Eight-view package](../pilot/reference_cases/v0.2/README.md),
[human review](../pilot/reference_cases/v0.2/TOMORROW_REVIEW.md).

## 2026-09-21 — Bounded reference expansion following researcher authorization

**ACTION:** Researcher said “好的现在用这四个案例来扩展”. Created four further
synthetic functional groups with core/context views, giving eight groups / sixteen
public inputs. Prior wait-before-expansion guidance is superseded for this completed
engineering task; permission to expand is not evidence of human annotation or approval
of any scientific label. Three existing pilot functions were reused; one new archive
selection kernel was authored. No extra literature/deployment provenance is claimed.

**ENGINEERING RESULT:** The four new contexts and paired export/domain checks pass
109 tests. Their independently enumerated input checks cover 259 inventories, 231
component catalogues / 1,781 current selections, 85 archive item lists with all tested
capacities/current sets, and 321 table/copy configurations. These counts describe
bounded functional tests, not benchmark population sizes. Original core regression
and manifest validation pass; prior inputs/experiments remain unchanged.

**OBSERVATION:** A materialized export can match all initial output values while
violating independent-copy behavior; a controlled aliasing substitute demonstrates
this. Current/archive report correctness also depends on hard capacity, tie ordering
and transfer offsets beyond scalar objective quality. These are constructed semantic
counterexamples, not observed LLM failures.

**HYPOTHESIS / LIMIT:** Functional context may expose integration obligations useful
for migration evaluation. More functions/views do not establish harder localization
or more independent computational diversity. The component model shares quadratic
structure with earlier optimization cases, and several groups reuse pilot parents.
Their full lineage and algebraic similarity matter for later splits.

**UNRESOLVED:** Human functional acceptance (especially all-optional components and
archive tie choices), mapping/encoding/constraint penalties, exactness certification,
WHERE nomination for retention controls, practical evidence and redistribution rights.
No new science was decided and no model or quantum experiment ran.

**ARTIFACTS:** [Sixteen-view package](../pilot/reference_cases/v0.3/README.md),
[tomorrow review](../pilot/reference_cases/v0.3/TOMORROW_REVIEW.md),
[actual validation](../pilot/reference_cases/v0.3/validation.json).

## 2026-09-21 — Correcting case sourcing and making WHERE behavior-sensitive

**ACTION:** Researcher clarified that expansion should draw suitable cases from the
referenced benchmarks and strengthen discovery, not mainly migrate local pilots.
Reviewed ten concrete C2|Q> records, retained four source functions for agenda and
release-group workflows, and audited the other references' case/evaluation roles.
Both new contexts are explicitly synthetic applications of sourced synthetic code.

**OBSERVATION:** The inspected source variants differ materially: ordered greedy
assignment can fail on a feasible input, while backtracking finds the first feasible
vector; clique variants differ on singleton and tie behavior. Two inspected cover
snippets also fail empty-cover expectations. These are specific executable
counterexamples, not findings about every record in C2|Q> or accepted quantum labels.

**ENGINEERING RESULT:** Thirty-eight new tests pass. In a concrete agenda input,
replacing preview with full completion preserves the final assignment but changes
the required status. In a release input, using the greatest group as the preview
preserves the requested proposal but changes another observable output. Dropping
latest-check precedence or active filtering also changes required behavior. These
are constructed wrong substitutions, not observed failures of a model.

**HYPOTHESIS / LIMIT:** Multiple necessary policies, paths and cross-file predicates
may make WHERE more informative than locating a single named solver. No empirical
difficulty claim follows from added functions or passing tests. Paired input length,
naming and source ancestry remain confounds for a later experiment. No new model or
quantum experiment occurred; no scientific labels or old source behavior were changed.

**UNRESOLVED:** Are these functional requirements useful representations of existing
software? Which smaller/larger candidate boundaries with explicit dependencies are
acceptable? How should static opportunities differ from per-input active paths in
evaluation? Practical evidence, exact solver obligations and final licensing remain open.

**ARTIFACTS:** [New package](../pilot/source_adaptations/v0.2-where/README.md),
[source selection](../pilot/source_adaptations/v0.2-where/SOURCES.md),
[WHERE review](../pilot/source_adaptations/v0.2-where/WHERE_REVIEW.md),
[reference/method audit](../pilot/source_adaptations/v0.2-where/REFERENCE_BENCHMARK_AUDIT.md).

## 2026-09-21 — WHERE decomposition and three-condition preparation

**ACTION:** Following the researcher's polishing request and explicit endorsement,
prepared A core / B context with location / C identical context without location
for two mother problems. New task text is a common draft; old prompts are preserved.
The user accepted the direction, not particular cue spans or a model-run protocol.

**ENGINEERING RESULT:** Six generated messages pass cue-only B/C identity, public-file
allowlist and schema/source preservation checks. Thirteen classical traces/substitution
records distinguish paths and report fields; two private dossiers connect actual source
spans to dependencies/outer obligations and alternative boundary formulations.

**OBSERVATION:** On the fixed witnesses, wrong preview replacements leave the final
proposal unchanged but alter visible fields. History reversal in the release example
also changes current/preview reports despite an unchanged maximum proposal. These are
actual controlled classical counterexamples, not evidence that models fail to locate
the core. Wrapped binding call counts are not runtime or quantum-resource measures.

**HYPOTHESIS / LIMIT:** Given-location versus no-location conditions may reveal discovery
limitations, but location hints also change attention and the prior that a candidate
exists. A differs in interface/naming/length. Two nominated-positive mother problems
cannot establish no-candidate specificity, statistical significance or general difficulty.
Candidate nomination, dependency understanding and conditional HOW require separate
recording; detailed explanations still do not prove semantic preservation.

**UNRESOLVED:** Functional realism, cue/alternate boundary review, no/multi-candidate
controls, final human rubric and sampling/run design. No labels, exact-span scoring,
quantum families or old inputs changed; zero model calls.

**ARTIFACTS:** [Review package](../pilot/where_review/v0.1/README.md),
[prospective protocol](../pilot/where_review/v0.1/PROTOCOL.md),
[actual classical evidence](../pilot/where_review/v0.1/prepared/evidence/).

## 2026-09-21 — Sourced tasks and executable evaluation-method adoption

**ACTION:** Responded to the researcher's criticism that the earlier expansion/audit
did not implement the requested breadth of reference adoption. Six new classical
functional programs now adapt concrete QuanBench/+, SupermarQ, Qiskit HumanEval,
HPL and HPCG specifications/algorithms. Ten source-traceable groups have A/B/C inputs;
new application requirements remain synthetic, not claims about deployed software.

**OBSERVATION:** QuanBench 05 specifies five items but its expected bitstring has
four characters, and its canonical top-level function lacks a return. The source
bytes remain intact; exact classical enumeration supports value 8 for items 0/4
under the stated data. This does not validate the source quantum implementation.
Earlier QuanBench+ unavailability was an incorrect repository spelling (missing h),
now corrected with a pinned source, rather than an actual missing benchmark.

**ENGINEERING RESULT:** A constructed pair passes the pinned PQID count-signature
predicate yet has process overlap approximately 0.0625. Identity versus Z agrees on
the all-zero measurement distribution but has process overlap zero. A fixed MQT
four-qubit circuit retains unitary equivalence after decomposition while reported
two-qubit operations change from 2 to 4. Equal objective expectations can coexist
with disjoint distributions. These are deterministic witnesses of check limitations,
not model failures, universal scoring prescriptions or general empirical estimates.

**INTERPRETATION:** Method adoption needs a declared semantic target. Circuit identity,
one-input distribution, task quality and full software behavior are different checks;
process fidelity is not automatically an appropriate migration-equivalence criterion.
Source provenance alone also does not ensure reference answers are usable as gold.

**OPEN:** Review functional realism, proposed localization and control population;
decide per-case exact/approximate/probabilistic obligations before scoring. Negative
control nominations are DRAFT, not proof of absence of all quantum formulations.
No new model/quantum-optimizer/QPU run or main metric change occurred.

**ARTIFACTS:** [Ten-group package](../pilot/reference_completion/v0.1/README.md),
[reference coverage](../pilot/reference_completion/v0.1/COVERAGE.md),
[actual method values](../pilot/reference_completion/v0.1/METHOD_RESULTS.json).

## 2026-09-21 — Review counterexamples and controlled engineering fixes

**OBSERVATION:** Existing tests passed while lit-005 exposed dictionary insertion
order contrary to the feature-order contract. Lit-009 returned Infinity in deltas
from finite inputs despite a finite solution/residual. Both were reproduced, then
fixed under the original public contract in a new version with regression evidence.
Lit-007 public source attribution directly named QAOAVanillaProxy; the new public
view uses project-level attribution with original license retained. Private provenance
still records the specific source. Remaining project recognition is not eliminated.

**RESULT:** Seven of thirty messages change, all others and historical artifacts
remain identical. No model response, scientific label, contract relaxation or score
change follows from this engineering correction. The researcher clarified that WHERE
difficulty is a question for the later experiment, not a prerequisite for case quality.

**ARTIFACT:** [v0.1.1 corrections and exact validation](../pilot/reference_completion/v0.1.1/README.md).

## 2026-09-21 — Pending references before model comparison (N-033 / D-022)

**RESEARCHER DIRECTION:** The researcher understands quantum computing and requests
concrete labels now while conservatively retaining pending review, to enable initial
comparison of different models. This authorizes proposals, not individual label approval.

**ARTIFACT:** [Provisional labels v0.1](../pilot/provisional_labels/v0.1/README.md)
binds the existing thirty inputs to ten mother-level evidence records and per-view
source anchors/obligations. Seven supported structural mappings have positive draft
labels; three controls remain unresolved. No structural NO is manufactured for balance.
Suitability is unknown, adoption provisionally classical, migration support false.

**EVIDENCE LIMIT:** Finite formula checks and constructed response differences validate
parts of the reference/diagnostic machinery, not actual LLM capability. Family names,
plan presence, and localization overlap cannot replace semantic review. No negative-class
structural accuracy or whole-task pass rate is currently established. Constant adoption
judgments alone cannot distinguish models. Human checks and model runs remain pending.

**NEXT:** Review evidence as needed, specify a separately authorized same-condition model
comparison, retain denominators and unresolved items, and version later label changes.

## 2026-09-22 — Current-package first C comparison (N-034 / D-023)

**EXECUTION:** The user requested a current-benchmark LLM test and short report.
Two GPT models, ten unchanged C inputs each, medium, restricted Codex CLI through
existing ChatGPT login. Twenty first responses completed and passed strict validation;
no tools, scientific retry or repair. Private labels remained unavailable to models.

**OBSERVED:** Both match all seven known positive structural proposals, provide all
seven required conditional plans, and exactly match six of seven localization anchors.
Both omit the decoding line from lit-004's nominated span but discuss its dependency.
Sol uses a QUBO alternative for lit-003; Astra uses prefix predicate search. Both
nominate lit-009's single-line pivot argmax, a smaller candidate than the unresolved
reference's solve anchor. Both reject positive nomination for lit-008/010, whose
references remain unresolved. Adoption remains classical in all twenty responses.

**INTERPRETATION:** Coarse diagnostics do not separate these models in this sample.
Content differs in explicit penalty bounds, alternative-contract applicability and
practical NO versus unknown judgments. The support field also suffers from public
definition ambiguity: provenance, performance evidence and reviewed migration support
are being conflated. Do not treat raw support disagreement as model capability error.
These are coordinator AI observations, not independent review or correctness proof.

**NEXT:** Researcher review of lit-003 alternatives, lit-009 candidate granularity,
and public field definitions before versioned refinement of HOW criteria. No automatic
Agent architecture decision or new run follows. One sample per case, no known negative
structural labels and no executed migration prevent stable ranking or task-pass claims.

**ARTIFACTS:** [Small report](../pilot/model_comparison/20260922-c-v0.1/REPORT.md),
[raw/derived data](../pilot/model_comparison/20260922-c-v0.1/README.md),
[AI content review](../pilot/model_comparison/20260922-c-v0.1/CONTENT_REVIEW.md).

## 2026-09-22 — DeepSeek extension and concrete HOW witnesses (N-035 / D-024)

**EXECUTION:** User added DeepSeek Pro and Flash and supplied a local API credential
location. Twenty unchanged C requests through official direct API, thinking/high,
16384 completion-token cap, one sample each, no retries/repair. Pro yielded ten valid
responses; Flash nine. Flash lit-009 used its entire cap in reasoning without a final
answer. This is a budget failure, not evidence of semantic inability; no answer was
reconstructed from reasoning. GPT medium/Codex and DeepSeek high/API are different
system configurations, not a controlled equal-compute comparison.

**OBSERVED:** Pro still matches seven positive structural proposals and provides all
seven plans; its five exact localization matches reflect partly legitimate boundary
choices. Yet two concrete lit-002 formula errors were reproduced: Flash minimizes
positive superincreasing selected-bit weights in the wrong direction; Pro substitutes
numeric-mask order for selected-index tuple lexicographic order. Both counterexamples
are valid inputs and the unchanged original classical kernel returns the contractual
answer. Classical fallback can still preserve a completed implementation, so the
witnesses refute specific formulation claims, not all possible plans.

**INTERPRETATION:** These samples show content differences that plan presence and
family agreement miss. More providers alone do not fix an insensitive rubric.
Conversely, Flash's truncation shows inference-budget effects must not be conflated
with model competence. Pro also rejects the pivot subregion on the overstrong premise
that extreme-value search needs a precomputed optimum; candidate granularity and
conditional exactness remain review questions, not automatically adjudicated labels.

**NEXT:** Review explicit HOW obligations and counterexamples before versioned scoring
changes. Further sampling or a larger-budget Flash run needs a separate authorization.
No stable ranking, gold annotation, complete migration verification or Agent architecture
decision follows from this coordinator AI review.

**ARTIFACTS:** [Four-model report](../pilot/model_comparison/20260922-deepseek-c-v0.1/REPORT.md),
[witnesses and AI review](../pilot/model_comparison/20260922-deepseek-c-v0.1/CONTENT_REVIEW.md).

## 2026-09-22 — HOW review operationalization proposal (N-036 / D-025)

**AUTHORIZATION:** Researcher requested progress along the proposed path until a
scientific decision is needed. Prepared local review artifacts without new inference.

**ARTIFACT:** [HOW v0.1](../pilot/how_review/v0.1/README.md) separates core mapping,
encoding conditions, original-contract obligations and boundary dependencies. Manual
AI codings bind exact response fields/hashes; they are not automatic text grading.
All forty requests are inventoried. Five purposefully selected mothers yield nineteen
reviewed answers / seventy-six records plus one preserved budget failure. Twenty other
answers remain explicitly unreviewed; no population error rate is estimated from this subset.

**EVIDENCE:** Reproduced Flash/Pro vertex-cover tie errors against validated original
inputs. Also checked Sol's tuple encoding and Astra's cardinality-only encoding over
1100 graphs; three clique formulations over 1100 graphs; Astra's knapsack formula over
4100 instances against original DP; two coloring lex objectives over 499 vectors;
incumbent pivot predicate over 3905 finite columns from all starts. Mathematical
reasoning and finite checks have separate scopes; no complete quantum migration was run.

**INTERPRETATION:** The rubric can record a specific false formula differently from
an explicitly deferred obligation, preserve alternative families and candidate boundaries,
and distinguish delivery failure. This does not prove inter-rater reliability, stable
model ranking, holdout performance or general contract correctness. Pro's pivot rationale
is overstrong without adjudicating the unresolved whole-case label. Practical/support
ambiguity still requires prospective clarification rather than retrospective grading.

**GATE:** Researcher should choose the next formal HOW operational policy: retain
conditional plans with separate correctness/completion evidence, or introduce executable
encoding submissions in a new task version. The package recommends the former; neither
choice is automatically gold approval, case/split freezing or new model authorization.
## 2026-09-22 — Accepted A, full pending HOW review (N-037 / D-026)

**RESEARCHER DECISION:** Explicit “A” accepts conditional-plan correctness and
completion as separate records, with honest deferral and no scalar score. It does
not approve all individual judgments or authorize new inference.

**ARTIFACT:** [HOW v0.2](../pilot/how_review/v0.2/README.md) inherits nineteen previous
answer reviews and completes twenty more. All forty requests remain visible: thirty-nine
answers, 156 scoped claim records, 200 completion entries including five no_response
entries for the existing Flash truncation. Completion is manually coded independently:
the wrong DeepSeek002 formulas are provided content, while Astra002 defers its tie
construction. None represents complete migration verification.

**ADDITIONAL EVIDENCE:** Weighted MaxCut over 761 graphs confirms scalar tie and variable
flip correspondence; 1100 complete signed graphs / 33867 assignments check score/Ising
identities and GPT scalar tie; 6472 restricted SAT instances check predicates and
classically certified prefix logic. DeepSeek core mappings can be sound while global
selection/certification remain incomplete. Universal structural rejection of controls
remains unresolved, not newly adjudicated NO. The initial MaxCut check had a wrong
source path and failed before checking; it was corrected, with no model retry.

**REVIEW PREPARATION:** Thirteen allowlisted payload files plus manifest contain unchanged
public C inputs, contract obligations and empty human forms, excluding model outputs,
private labels and coordinator verdicts. Checklists are still AI-authored guidance;
no actual blind study, independent reviewer or human answer is invented. Holdout scope,
source grouping, sample count, execution and statistical policy remain draft.

**NEXT:** Researcher adjudication of the two narrow lit-002 formula witnesses, followed
by remaining disputed boundaries and prospective data/experiment decisions. All prior
scientific artifacts and HOW v0.1 are preserved; no new model/QPU run or release.
## 2026-09-22 — Supplied review concurrence on lit-002 (N-038 / D-027)

**RECEIVED:** User provided detailed review text confirming both counterexamples within
the stated branch scope. Its analysis generalizes Flash's reverse ordering for positive
superincreasing selected-bit costs and confirms that every positive Pro C preserves the
numeric-mask preference in the witness. It reports independent enumeration but does not
re-run the project's validator; no new executable evidence from that reviewer was supplied.

**PROVENANCE:** Recorded as user-supplied review text, with author identity, human/AI
status, credentials, independence and blinding unknown. Do not call this a completed
independent expert annotation. A summary and exact claim bindings live in the separate
[appendix](../pilot/how_review/adjudications/20260922-lit002/README.md); old snapshots are preserved.

**SCOPE:** Both formulas produce a minimum cover with the wrong canonical tie, not an
infeasible or larger cover. Flash's other branch and exact classical checking/repair/
fallback remain potentially correct; none was implemented or verified by this feedback.
Correctness contradicted and selection construction provided remain distinct records.
Other case labels, scientific task acceptance and model ranking remain unresolved.

**NEXT:** Move to remaining alternative-family/candidate-scope review questions without
requesting the same lit-002 concurrence again. Supervisor summary now acknowledges the
received feedback while retaining its provenance limits; no model or QPU was run.

## 2026-09-22 — Scoped case verification and evaluator controls (N-039 / D-028)

**REQUEST:** Implement the capability→task→artifact→oracle→test→score chain in the existing
benchmark. Preserve conditional plans and pending labels; no new tasks, models or agent design.

**AUDIT:** Current ten-mother inputs are loaded by the reference-completion manifest, not the
fourteen old cases/ manifests. Existing scores already distinguish reference agreement/coverage
from unknown plan correctness. Original-program tests and reviewer arithmetic checks do not execute
model migrations. Missing pieces were systematic scoped contracts, evaluator controls and diagnostics.

**IMPLEMENTED:** Ten private sidecars; definition oracles and declarative claim checks for 002/004/005,
plus report obligations for unresolved-control 008. Four cases/23 inputs, 8 correct/equivalent controls
pass and 10 semantic mutants fail. The two archived 002 formulas fail the canonical-selection check
with pinned response text and disclosed reviewer coefficients; fallback/whole plans remain unjudged.
Six cases retain catalogue-only status. All task_pass fields remain null; no main metric replacement.

**VALIDATION:** Baseline main tests 97 passed/15 optional skips; new regression tests 42 passed;
full main suite 139 passed/15 skips. Seven existing focused suites unchanged and passing. 1636 old
files retain SHA256. No installation, model/QPU calls or historical response/score changes.
[Report and commands](../pilot/semantic_verification/v0.1/README.md).

**LIMITS:** Finite controls are development regression evidence, not independent held-out model tests,
universal proof, scientific gold or quantum migration execution. Source hashes don't establish reviewer
independence or an OS security boundary; future tool-enabled agents still need genuine isolation.

## 2026-09-22 — Complete the remaining six scoped case verifiers (N-040)

The researcher asked why the other six cases were not yet modified. Continued D-028's
authorized implementation in a new version, retaining v0.1 and all historical inputs/results.
001/003/006/007 now have explicit finite mapping controls; 009/010 have numerical behavior
controls without asserting structural NO/YES. 003 admits binary predicate and one-hot QUBO
routes; 006 checks slack decoding. Exact dyadic numerical fixtures avoid inventing tolerance.

An additional adversarial test exposed an error in the newly developed coloring verifier:
negating the penalties preserved the zero set while making minimization prefer violations.
The failing test was run and saved before the fix. The final checker also requires the
feasible energy level to be an extremum bound and admits declared energy shifts.

Final evidence: all ten scoped case verifiers run on 61 named inputs; 22 correct/equivalent
controls pass and 30 semantic mutants are rejected. New tests 84 passed; full main suite
223 passed/15 optional skips; six original-program suites and provisional-label checks pass.
1646 old files unchanged. No model/QPU calls, new cases, task replacement or gold promotion.
[Report and exact commands](../pilot/semantic_verification/v0.2/README.md).

These are evaluator controls, not fresh model answers or full migration certificates.
Transcription fidelity, whole-context behavior, arbitrary floating equivalence, scientific
labels, resource claims and genuine isolation for future tool-enabled agents remain open.

## 2026-09-23 — Four-model repeat and reachable numerical-state witness (N-041 / D-029)

The researcher explicitly requested ten cases again with Flash, Pro, Sol and GPT 6.
Resolved to the same four IDs and unchanged C inputs. Forty first attempts completed:
Sol/Astra 10/10 valid each, Pro 9/10, Flash 7/10. Pro002 and Flash004/005/009 exhausted
the existing 16384 completion-token cap; no retry or output repair. GPT medium/subscription
and DeepSeek high/API remain unmatched settings. Total wall time approximately 43.4 minutes.

Seven explicit objective claims across 001/002 were quote/hash-bound and checked on 38
fixed inputs: four direct canonical scopes and three primary-only scopes, all passing.
Missing tie constructions were not silently filled in. These are finite classical claim
checks, not plan execution or whole-task passes.

Post-hoc inspection found that Sol/Pro 009 both identify the first maximum using a
universal >= predicate plus no-earlier-equality. Valid finite inputs can overflow during
the original elimination and produce NaN. Tracing the unchanged original program on a
5x5 input reaches a NaN pivot column where Python max chooses row 4 but the proposed
predicate marks nothing. Normal input passes, and an explicitly separate Python-order
incumbent control agrees throughout. The original program raises numerical overflow;
the proposed classical fallback may preserve that result. Only predicate equivalence
is refuted, with reviewer interpretation/fallback limits retained. No frozen score changed.

Astra009 nominates nonfinite-value checking, while both GPT models nominate validation
scans in 010. DeepSeek010 focuses on the numerical core and declines nomination. This
is evidence of an unresolved candidate-boundary criterion, not an automatic false-positive
label. Pending references and single-repeat evidence do not support stable model rankings.

28 offline transport/collector/transcription tests pass; final audit replays scoped checks
and the new witness, verifies all ten inputs and 1654 old file hashes, and checks document
links. No dependency installation, historical artifact edit, QPU, migration execution or Git
publication. [Report and commands](../pilot/model_comparison/20260923-four-model-c-v0.1/REPORT.md).

## 2026-09-23 — Researcher confirms same-model enhancement as the technique objective (N-042)

The researcher clarified that the objective is to identify a particular LLM's weak
workflow stages and strengthen them using classical CS methods, so the same model
performs the overall task better. They explicitly endorsed and requested documenting:

> 利用程序分析与语义验证，增强 LLM 对经典程序的量子机会识别与映射设计能力。

[D-030](../DECISIONS.md#d-030-same-model-enhancement-through-classical-cs-methods) and the
[charter](RESEARCH_CHARTER.md#same-model-enhancement) now record this direction. The main
contrast is the same LLM with and without the proposed enhancement. Cross-model observations
may inform generality; assigning different models to different roles is not the chosen
research objective. Harness denotes the execution/evaluation framework, while the technical
contribution must lie in the enhancement mechanism and evidence of its effect.

Existing tie and floating-state witnesses motivate possible methods but do not establish
their effectiveness. Specific mechanism selection, stage and overall evaluation, ablations,
budget accounting and future run scope remain to be designed. This turn only synchronized
documentation; no algorithm implementation, prediction, relabeling or new experiment.

## 2026-09-23 — First same-model semantic-feedback pilot reaches a ceiling (N-043)

The researcher explicitly selected a separate lit-002 direct structured-QUBO task and
GPT-5.6 Sol with at most15 subscription invocations. D-031 records the scope: five fresh
initial sessions, each forked as candidate text into one self-review and one development-
feedback revision. Exact definition checks, restricted arithmetic data and instance-level
separation implement the first local method prototype; old Phase-1 tasks remain unchanged.

All15 calls completed. Initial, self-review and feedback each pass all98 reserved final
instances in5/5 responses. All initial answers also pass the6 development instances;
therefore the feedback arm receives only a finite-pass notice, no actual counterexample.
The observed gain is zero and counterexample-driven repair remains unmeasured. This is
a development-exposed one-mother-case ceiling result, not proof that feedback is ineffective
or that quantum mapping is solved. No post-hoc model/case substitution or extra sampling.

Two trusted/equivalent synthetic controls pass, five plausible semantic mutants fail;
these validate the evaluator but are not counted as real model repairs. New26 tests pass;
repository223 pass/15 optional-dependency skips. Offline replay checks all15 responses,
104 definition expectations and863 protected old files. Actual model calls took about
9min05s; the existing subscription transport, tools disabled and restricted mounts were used.
Program analysis for extracting production-code contracts and full migration remain future work.

[Result and exact commands](../pilot/enhancement/lit002-v0.1/REPORT.md).
Next: review the same Sol's existing reachable-NaN predicate failure before designing a
new bounded enhancement experiment. No further model execution authorized by this completed run.

## 2026-09-25 — Reachable-state premise audit and method proposal (N-044)

Continued the authorized offline queue. Sol009 correctly identifies the pivot site and evolving
rows, but its universal maximum predicate assumes order properties that reachable binary64 NaN
states do not satisfy. Traced unchanged original code: finite input passes validation and the
initial residual, col=2 updates overflow, col=3 produces a NaN factor, and col=4 exposes the false
unique-marker claim. The original exception occurs at kernel.py:25; fallback and whole plans
remain unexecuted and unjudged. This does not automatically reverse a structural label.

Transcription sensitivity matters: the old singleton-NaN witness fails the inclusive >= reading,
but a self-excluding reading accepts its only candidate. A new reviewer-built 6x6 extension of
the same input reaches two NaNs at col=4 and refutes both readings. Seven historical pivots were
replayed and six sensitivity pivots traced; ordered-scan controls match all thirteen. These are
post-hoc development states, not new mothers, model samples or frozen-suite scores.

Source review of Astra009 and Sol/Astra010 confirms concrete validation-scan boundaries but
does not resolve formal candidate inclusion. Sol010's "absent or unequal" wording conflicts
with its explicit default-zero formula/assumption; preserve ambiguity rather than silently
choosing a transcription and assigning whole-plan failure.

Proposed next target: dynamic-state premise analysis plus reachable counterexample feedback,
with the same model and a self-review control. The suggested five fresh drafts/two revision
branches (15 calls) and measurement protocol are proposals only, not approved experiments.
The automatic analysis mechanism remains unimplemented. Researcher selection is the next gate.
Actual evidence, commands and limitations: [N-044](../pilot/enhancement/lit009-review-v0.1/README.md).

## 2026-09-25 — Delegated single-model workflow development and teaching (N-045 / D-032)

The researcher stated that this is their first benchmark/agent-workflow project and delegated
progression while requesting clear explanations of the next action, purpose and observed effect.
They supplied bojieli/ai-agent-book as a reference. Read chapters 1/7/9 and relevant experiment
records at commit 04c88c53df962eb4375a0fad9ec041066529b358; no external code was executed.

Chose an offline fixed workflow with a same-draft 2x2 analysis/verification ablation, including
self-review as the no-tool-observation control. This distinguishes extra revision opportunity
from tool-package evidence. It does not establish equal token budgets or isolate all cognitive
content of analysis from validation. Five future drafts would imply 25 calls; this is a budget
proposal, not a new authorized model campaign.

Implemented a lexical AST inventory including mutable-state writes and loop context, selection
of an exactly quote/hash-bound historical development witness, and four revision packets with
event/outcome records. Inventory is neither a sound program slice nor range/reachability proof;
the validator returns insufficient evidence for unbound new prose. No model revision or final
evaluation was run. This is an offline workflow scaffold, not an autonomous agent effectiveness result.

Twelve focused tests passed; four branches prepared from the same historical response with zero
model calls and null quality effects. Prior 2347 protected artifacts unchanged. Next: explicit
new-response claim bindings and independent evaluation interfaces before a bounded live protocol.
[Implementation](../pilot/enhancement/state-workflow-v0.1/README.md),
[Chinese learning guide](AGENT_WORKFLOW_LEARNING.md).

## 2026-09-25 — Explicit new-response claims and feedback boundaries (N-046)

Continued the delegated offline queue. v0.2 accepts a new response through exact prose anchors,
its own hash and explicit reviewer interpretations instead of an allowlist of historical answers.
Data-only Boolean/quantifier expressions and ordered scans are interpreted with budgets; no
model code is executed. Guards, unexercised scope, multiple interpretations, unsupported mappings
and withdrawal remain separate outcomes. Hash/quote consistency does not prove prose fidelity;
coordinator review is still AI_REVIEW_PENDING, not autonomous or independently validated scoring.

Traced unchanged original software on three development requests (13 pivots) and twelve reserved
requests (44 pivots, plus empty-context output). Requests do not overlap by canonical JSON, but
are all same-mother development variants. Two correct/equivalent controls pass; five erroneous
controls fail the reserved checks. Always-first passes development because those requests all
choose the first active row, then fails a reserved row-swap request. This documents a real finite
coverage limitation; it is not a new model error or proof of counterexample-feedback efficacy.

37 new and 12 prior tests pass, including 780 abstract comparator states, feedback-role integrity,
new-response bindings, ambiguity/guard categories, exact evidence regeneration and proposal slots.
2364 old files unchanged. Prepared 25 fixed D/S/A/V/AV slots with no run authorization and an
offline review CLI. The live adapter and isolation preflight remain outstanding; read-only CLI
inspection reports 0.156.1 instead of historical 0.155.1. No inference or credential access.
[Report](../pilot/enhancement/state-workflow-v0.2/README.md).

## 2026-09-25 — Recoverable ablations and request-level preflight (N-047)

Implemented the prepared D/S/A/V/AV campaign using the existing transport with scoped additions.
Durable attempt markers precede dispatch, a lock prevents simultaneous operators, and completed
transport can be classified after interruption without another call. Unknown interrupted attempts
stop. Invalid initials retain four skipped dependents; invalid revisions retain independent siblings;
infrastructure failure stops remaining slots. All five slots per arm stay in the denominator.
Initial bindings freeze before revisions; revision bindings freeze before final suite evaluation.
Model usage/latency, development tool time, final tool time and reviewer time remain separate.

26 new tests plus 49 prior tests pass. Fake responses complete all 25 slots; fault injection covers
interruption, authorization denial, prompt tampering, early evaluation, invalid JSON/schema and
tool/transport failure. This validates execution logic, not model quality or independent review.

Actual CLI 0.156.1 inspection revealed that bundled Sol metadata forces code-mode/collaboration
tools despite feature flags. A dummy-auth, network-isolated local HTTP sink captured those tools
in input.additional_tools (not just top-level tools). Exported bundled Sol metadata and cleared only
tool_mode, multi_agent_version and apply_patch_tool_type; disabled plan/question tools explicitly.
Final capture has no tool schemas, still Sol/medium, original public input and restricted wrapper.
Public catalog is separately read-only mounted; private repo/paper/canary are absent. Five offline
preflight checks pass. Provider routing/compression differ in capture; no subscription availability
or service behavior claim. Historical results remain unchanged; no retrospective tool claim made.

2391 prior files unchanged. No real authentication reads, model/QPU calls, installs or paper edits.
Next: obtain bounded authorization for the frozen 25-call protocol; retain AI_REVIEW_PENDING and
same-mother scope. [Report and operation handoff](../pilot/enhancement/state-workflow-v0.3/README.md).

## 2026-09-26 — Actual 25-call Sol ablation (N-048 / D-033)

The user replied "继续吧" to the concrete 25-call approval request. Recorded protocol-bound
authorization and executed the fixed queue. The default CLI had advanced to0.157.0; selected the
already-installed0.156.1 whose hash matches the approved protocol, without changing frozen code,
configuration, preflight or user setup. All25 calls produced valid Phase-1 responses with zero
operator retries, transport errors or tool events. Original responses and failures policy retained.

Initial reviews found one explicit false predicate (replicate2); the remaining four were an
unspecified oracle, no nomination, broad solver nomination without a plan, and underspecified QUBO.
Replicate2 V/AV explicitly replaced universal comparisons with first-element initialization and
strict-greater ordered updates, including NaN. Both pass44 reserved states; S's two interpretations
and A's retained initial predicate remain contradicted. This is one repair opportunity, not two
independent samples. No evidence establishes AV superiority over V or general enhancement.

Across fixed five-row arms, unguarded finite passes D/S/A/V/AV are0/0/0/1/1. AV additionally has two
guarded claims (31 states checked,13 excluded), not full repairs. S and V each introduce one new
contradicted claim from an unknown initial. A's replicate5 secondary Grover claim remains ambiguous:
one reading fails3 states and another passes44. The primary QUBO is not checked. Plan coverage rises
in V, but insufficient-evidence feedback explicitly names pivot selection, creating a static-cue
confound. Empty/unsupported candidate inventories also limit the analysis mechanism.

All20 revision bindings were frozen after the model queue and before final evaluation, with exact
quotes, hashes, rationales and AI_REVIEW_PENDING provenance. All25 evaluations replay identically;
2429 prior files unchanged, including paper. Usage395819 input/53025 output tokens; model time
1164.678s and recorded reviewer wall605.356s kept separate, with cache/overlap caveats. No new code
dependencies, QPU execution or manuscript claims. All25 authorized calls are consumed.

Next safe work: offline design for missing formal information, candidate-boundary coverage and
pivot-cue-only controls. Do not modify this completed protocol or start new calls without a new
concrete scope. [Results and audit](../pilot/enhancement/state-workflow-v0.3/execution-20260926/REPORT.md).

## N-049 — Offline design for feedback information and checkable claims

Date: 2026-09-26. Continued D-032 delegated local development; no new model authorization.
Mapped all25 N-048 responses and90 existing exact anchors into six design routes: missing rule5,
no nomination3, broad region without plan4, unconstructed QUBO3, ambiguous operator2, explicit
local rule8. These are coordinator-authored design categories, not revised correctness labels.
Main QUBO and secondary Grover claims stay separate. Clarification text is prepared but not sent.

Source audit confirms the old lexical adapter uses only start_line: replicate1's declared12–16
range selects a compound statement ending20; replicate4's function-start9 is unsupported;
replicate3's empty nomination prevents any inventory. A syntax-only public function/body outline
was generated without executing source or ranking candidates. New routing remains proposed.

Prepared16 exact offline revision prompts over all five retained initial drafts: self-review,
scope-cue and assessment-summary each5; actual-witness1 on the sole development-counterexample
opportunity. W differs from same-draft E only in first_counterexample data. Summary-vs-cue is a
packet comparison, not a pure status-word effect. No clarification or new analysis is mixed in.
All inputs remain DRAFT/design_not_run, without authorization or an online dispatcher.

Because prior final results informed this design, the44 previously reserved states are now known
regression data for future work, not new unseen evaluation evidence. Generalization still needs
separate prospectively fixed cases and review. Next safe action is configuration adaptation and
offline isolation/recovery preflight; only then request a concrete new16-call budget. No scientific
labels, frozen artifacts, paper or dependencies changed. [Design](../pilot/enhancement/state-workflow-design-v0.1/README.md).

## N-050 — Sixteen-slot feedback-control runner and offline rehearsal

Date: 2026-09-27. Implemented the next local preparation step under D-032, without new model approval.
The adapter consumes N-049's exact historical-draft prompts and reuses frozen transport, response
validation, immutable records and the N-046 claim interpreter. S/C/E have five planned positions each,
W only one; paired comparisons retain these distinct populations. Old44-state data are explicitly
known regression data in both outer results and inner evaluation split, with source role retained.

32 new tests and49 relevant semantic/analysis regressions passed. Checks cover fixed inputs, protocol
and approval receipts, no fake-to-live fallthrough, missing/invalid responses, timeout/tool/transport
stops, attempts recorded before dispatch, recovery without duplicate calls, concurrent locking,
post-queue binding and all-bindings-before-evaluation. Retained a complete16-position simulation;
its cloned historical responses and synthetic cost metadata are testing fixtures, not observations.

Five actual offline checks passed with pinned installed CLI0.156.1. A dummy-auth local rejecting
HTTP sink in an unshared network namespace captured the exact witness-prompt request: Sol/medium,
no tools, private workspace/host config inaccessible. The expected local400 makes the CLI return1;
capture verification itself succeeds. No real credential access or external inference was performed.
The preflight samples the most informative witness input; all16 payloads are separately checked by
tests. Account availability and server behavior remain untested. Frozen protocol has88 hashed sources.

Current live queue is await_authorization, zero attempts, no receipt. All2764 prior protected files
remain unchanged; no installation, QPU, paper edit or historical artifact mutation. Preparation is
complete; request a new maximum16-call Sol/medium subscription scope before execution, rather than
repeating offline preparation. [Implementation and evidence](../pilot/enhancement/feedback-control-v0.1/README.md).

## N-051 — Feedback-information control executed; summary and witness tie locally

Date: 2026-09-27. User explicitly approved the prepared16-call scope (D-034), then delegated same-
direction existing-subscription quota with “限额随便用” (D-035). Executed exactly the frozen16 positions,
without modifying inputs, conditions, ordering, old artifacts or sampling count. All16 responses valid;
zero operator retries, transport errors or tools. The later quota delegation did not expand this run.

All new responses were reviewed after the queue and all16 bindings frozen before known regression
collection. In replicate2, both E assessment-summary and W concrete-witness responses explicitly
specify first-incumbent, ordered strict-greater updates, passing44 known states. S replaces the initial
formula with earlier-strict/later-nonstrict comparisons but still fails3; C acknowledges nonfinite risks
without constructing the selector. No extra W-over-E finite-correctness benefit is observed in this
single opportunity. E is an information packet, not an isolated error-status word. Results do not
establish that concrete witnesses are generally useless or unnecessary across tasks.

Replicate1 E gives a finite-valued guard:31 passes,13 exclusions, outside behavior unresolved. Twelve
of16 responses remain insufficient. Replicate3 S/C/E all introduce pivot candidates without complete
selectors, so nomination growth is not cue-specific. Replicate4 C wraps entire binary64 solver outputs
as a formal search domain, while E narrows to a threshold-search sketch; neither is verified local repair.
Replicate5 retains underspecified QUBO proposals. Some prose confuses finite test count with finite-
valued states; record for prospective wording correction, never revise the observed prompts/results.

All16 evaluations replay exactly;65 source anchors, chronological gates and2921 protected files
verified. Input260561/output36815 tokens; model746.119s, coordinator review315.204s wall, evaluator
0.01137s. Cache and reasoning tokens not double-counted; historical initial cost excluded. Current
state all_slots_terminal. Paper, dependencies and QPU untouched; no new universal or whole-task claim.

Next: implement the already designed missing-information elicitation interface with equal-call
self-review, retaining abstention/unknown and alternative families. Offline-check before a new
protocol; D-035 covers same-scope subscription budget without repeated quota requests. New channels,
gold/scientific-scope changes and publication still retain their separate boundaries.
[Results and audit](../pilot/enhancement/feedback-control-v0.1/execution-20260927/REPORT.md).

## N-052 / N-053 — Single generic specification request, paired with self-review

Date: 2026-09-27. Frozen all five original N-048 drafts, two new revisions each; no selection on
N-051 outcomes. Same new wrapper, only null versus generic specification request differs; odd
replicates S then F, even F then S. No evaluator verdict, witness, correct operator or new source
outline. Existing families, null plans and unknowns permitted. D-035 covers the ten-call subscription
protocol;32 focused tests plus49 regressions and5 offline isolation/wire checks passed before dispatch.

All10 valid, zero retries/tool events/transport errors. Post-queue quote binding preceded known44-state
collection. F1 explicitly constructs a strict-greater reference traversal and passes44. F2 explicitly
admits finite values only, passes31 and excludes13; classical fallback is declared, not executed.
S2's global comparison predicate fails8; S5's secondary no-smaller/tie predicate retains two readings,
both fail3. Its main QUBO remains unconstructed. Both arms preserve no-plan responses in3/4.

F5 provides an explicit one-hot rank QUBO with coefficient expansion, exact P>0 argument, finite-value
guard, decoding and certification. This is now specified but outside the frozen checker. Do not score
its classical verifier as the primary objective or force a Grover family. Both arms still have three
insufficient statuses; this hides a changing reason, not an overall unknown-rate improvement. Primary
and supplementary claims remain separate. No gold, main metric, software contract or paper changed.

All10 evaluations replay exactly,3114 old files unchanged. Tokens input162484/output21096;
model434.623s, call window437.351s. Per-row review intervals overlap because pairs were inspected
together: sum321.440s, union161.909s, span163.350s. These include tool/coordination delays, not human
annotation labor. This is a single-mother-case prompt-elicitation diagnostic, not new-test generalization.
Next safe work: separate quote-bound local verification of F5's QUBO construction, retaining N-053's
immutable result and its admission/cost limitations. [Report](../pilot/enhancement/claim-elicitation-v0.1/execution-20260927/REPORT.md).

## N-054 — Explicit alternative-family construction receives its own audit

Date:2026-09-27. Manually quote-bound N-053 F5's rank QUBO; no new model call and no revision of
N-053 outcomes. Exact binary enumeration confirms original/expanded energy equality and unique
correct one-hot minimizers in31 known finite states plus1704 post-hoc synthetic diagnostics;13 known
nonfinite states remain excluded.72990 assignment checks for exact rational P=1/10,1,7. Fractional
P tests the general algebraic positive-penalty statement, not integer-coefficient admission.

18 tests include missing tie/zero penalty/negative penalty/wrong expansion controls. Exact replay
matches and3285 protected hashes are unchanged. A separate coordinator mathematical argument uses
the unique zero rank and nonnegative costs to show any exact P>0 suffices. This is not mechanized
proof, independent human review, backend validation or entire-program equivalence. Quadratic rank
construction reveals the optimum before quantum execution, so no benefit evidence follows.

Next safe step: implement the already diagnosed neutral analysis-entry distinctions for empty and
whole-function nominations, preserving original declared regions and not hard-coding a preferred
pivot site. Offline scope/boundary tests before any new model integration.
[Audit](../pilot/enhancement/rank-qubo-audit-v0.1/REPORT.md).

## N-055 — Neutral candidate-analysis entry implemented offline

Date:2026-09-27. Versioned source-map-only routing retains declared_region, enclosing analysis_scope
and optional complete-statement seed separately. Empty nomination returns a source-order public
catalog, not a negative verdict; whole-function and partial spans receive explicit outlines without
silently selecting a preferred subregion. Exact unique statements reuse the old lexical inventory.
Same-line ambiguity, malformed coordinates, unsupported nested/method scopes and unknown paths
are preserved; source strings never execute and nomination paths never read disk.

31 focused tests and49 regressions pass. Five original-draft packets give region_outline, statement
inventory, no_nomination, function_outline and statement_inventory respectively. All three source
files are checked against their numbered public-task text.3298 historical file hashes remain intact;
zero new model/QPU calls, no quality improvement claim. Next prospective comparison: all five
initials × S self-review/C catalog/R catalog plus routing, equal new calls, no verification feedback
or formalization request mixed in. Freeze exact protocol and isolation before D-035 execution.
[Implementation and audit](../pilot/enhancement/candidate-routing-v0.1/README.md).

## N-056 / N-057 — Directory versus routed-analysis control completed

Date:2026-09-27. All five original N-048 drafts retained; S/C/R each5, common revision wrapper,
identical C/R catalog, route/inventory information only in R. No specification request or correctness
feedback.31 entry tests plus32 runner tests plus49 regressions and5 offline preflight checks pass.
A14-versus15 test assertion typo was fixed before freezing, then all32 runner tests rerun successfully.
D-035 receipt binds the15-call protocol; all15 responses valid, zero retries/tools/transport errors.

Replicate3's initially empty nomination becomes line13 plus a plan in C/R while S stays empty.
Replicate4 also localizes in S, so its nomination change is not tool-specific. R1 supplies local
conditions omitting earlier larger values; both retained readings fail16 known states, including11
finite states. C2's not-less wording has >= and not-< readings: the former fails3 and the latter
passes44. R2 reverts to an unspecified selector rather than a verified repair. S2 and S5 fail3 each.
R5 retains the unconstructed primary QUBO and an explicit finite-guard secondary Grover condition;
both interpretations pass31/exclude13, but ambiguity and primary/secondary roles remain explicit.
No unambiguous finite-pass response. Primary-plan status counts S:3 insufficient/2 contradicted;
C:4 insufficient/1 ambiguous;R:3 insufficient/1 all-contradicted/1 ambiguous.

C4 additionally supplies a flawed classical certificate. A separate post-collection check accepts
indices0 and1 on known state[2,0,0] where the original selects0. This does not instantiate the
missing primary search or change its frozen insufficient result. Verification language alone is not
evidence that the verifier is correct. All transcription remains AI_REVIEW_PENDING.

15 exact replays,3312 prior hashes match; input286333/output36550 tokens, model746.619s, window
750.988s. Review intervals overlap: sum593.539s, union199.326s, span200.344s, including tool latency.
No clear extra correctness benefit of routing over catalog is established; one-mother diagnostic,
not generalization. Safe local queue is complete. D-036 now proposes at most4 new mother-problem
dossiers without gold/split/model-based selection, or existing independent reference review first.
Await researcher scope choice; D-035 quota is not the blocker. [Results](../pilot/enhancement/candidate-routing-control-v0.1/execution-20260927/REPORT.md),
[decision material](NEXT_RESEARCH_SCOPE.md).

## N-058 — New mother-problem candidate dossiers after D-036 A

Date:2026-09-27. Researcher answered “A”, accepting at most four dossiers, without formal
admission/gold/split or model-based selection. Prepared three: CPython longest matching block,
python-tsp closed-tour subset DP and NetworkX lazy simple-path enumeration. Three repositories,
ten commit-pinned original source/document/license files; complete old-ten lineage table and
pending reference-review checklist. Alternative TSP brute force and difflib callers share selected
mother computations and were not counted as a fourth independent problem.

Actual local checks:961 full binary-string pairs plus961 bounded matches;779 integer TSP matrices
under three cache sizes (2337 calls);four nonnegative-integer QUBO instances and1552 assignments;
64 directed graphs and2880 path-multiset comparisons. Targeted controls expose junk/autojunk/tie,
missing return edge, zero penalty, sorted/one-witness/deduplicated path outputs; exception and
state observations remain scoped. These are coordinator-authored checks, not model mistakes.

Unchanged upstream modules used; installed NetworkX source matches pinned bytes. CPython source
module was run on current3.10.21 rather than reproducing full3.10.14. TSP tag v0.5.0 points to a
commit whose package metadata says0.4.2 and NumPy^2.0.0; local single-module checks use1.26.4.
No installation/full-package reproduction claim. Source discrepancies retained, not silently fixed.

3555 prior file hashes match and numerical results replay exactly. Package audit covers54 local
link occurrences and22 artifact file hashes. Initial audit bootstrap rejected the not-yet-generated
manifest link; fixed generation-only handling of its two known output paths, then reran audit.
C01/C02 proposed for DRAFT source/contract review, C03 kept as a boundary candidate; final admission,
contract profiles, gold/split and independent review all remain pending. Zero new predictive model
or QPU calls. Public-source contamination unknown; all local probes are development-exposed.
[Deliverable](../pilot/new_mother_candidates/v0.1/README.md).

## N-059 — Frontier-relative audit and a falsifiable next question

Date:2026-09-28. Researcher said “做” after clarifying D-038. Completed targeted literature,
public-artifact retrieval and static source inspection; not a systematic review or performance replication.
C2Q already joins supported classical inputs to generated quantum code/device recommendations;
QPipe already implements agent generation, repair, requirement review and classical reference checking;
QuaST and Predict already address selection/cost/quality; CORK and QSynth preclude broad novelty for
semantic checking/synthesis. Q-READY also articulates the requirements-to-feasibility vision.

Static evidence: C2Q parser has a random-graph fallback on an unsupported extraction path;
its inspected recommender compares quantum devices. QPipe's numerical oracle receives the generated
combined instance, while a separate agent reviews the original requirement. Predict includes classical
approximation benchmarks. These observations delimit claims, not measured failure rates.
QuaST code retrieval failed; current availability of its automation module remains unknown.

Hypothesis: source-behavior obligations may need to change both replacement plans and their full cost.
Neither novelty nor benefit is established. Next diagnose three existing materials against reasonable
tool composition, including generic contract checking and cost estimation; abandon this mechanism
claim if straightforward composition suffices. N-054 and N-058 probes remain development-exposed,
not new formal cases or held-out evidence. No upstream execution, model/QPU calls, installations,
paper edits, label/score changes or practical-advantage claims.
[Report](frontier/README.md), [evidence](frontier/EVIDENCE.md), [next diagnostic](frontier/NEXT_STUDY.md).

## N-060 — Preserve the full idea; finish the frontier and route survey

Date:2026-09-28. D-039 records the explicit user correction and goal “完成这个调研并文档化”.
The ultimate software objective is unchanged. N-059 evidence is retained, but its premature
contract/cost priority is superseded by [v2](frontier/v2/README.md).

Additional primary evidence: Yamato's source-pattern offloading implementation/evaluation and
Road's six-month expert migration study; scoped HPS verification context. The eight-work matrix
distinguishes generated-code completion, source replacement, expert migration, selection and cost
prediction. Actual Azure service timing in a paper is not a demonstrated strong-classical advantage
or our independent QPU reproduction. QuaST code remains inaccessible after another timed request.

Compared three candidate routes: source-to-computation recovery; hardware-aware joint plan selection;
and usable hybrid migration with cross-boundary validation. Source recovery is the recommended
first diagnostic, not an accepted novel mechanism. Static inspection of N-054 and N-058 C01/C02
finds that ordinary cost analysis can already expose the rank-QUBO redundancy; text/TSP materials
motivate source/model fidelity tests but do not establish failures of external systems.

Documented present techniques, conditional predictions, hardware/algorithm limits and narrowly
scoped theoretical restrictions. Mapped FSE evidence needs and survey completion requirements.
No upstream code execution, model/QPU calls, installs, case/gold/split changes or paper edits.
Old experiment and N-059 bytes are covered by the new integrity audit.

## N-061 — Contract and end-to-end benefit drive the first concrete plan analysis

Date:2026-09-28. D-040 records the user's rejection of relegating contract/cost to optional
candidate mechanisms. They are core system decision criteria; specific implementation choices
and novelty still require comparison. Both surveys remain useful under the unchanged full idea.

Selected existing, development-exposed lit-005 v0.1.1, not a new benchmark case. Its exact-first
requirement matters: in the source example, ideal one-iteration Grover succeeds on any witness
with probability1 but on the required first witness with probability1/2. These are analytic values,
not hardware observations. Built a clause-derived phase oracle:14 logical qubits,48 X/54 CCX/1 Z;
preparation, diffusion and physical lowering remain separate costs, not claimed complete resources.

For the specific serial arbitrary-witness proposal plus classical prefix-enumeration repair,
all baseline enumeration work remains necessary. With identical predicate/domain and nonnegative
quantum overhead, this architecture cannot speed up the baseline. This is not a lower bound against
structured certificates, other quantum algorithms or all implementations of the original task.
Minimum-finding and structured prefix-UNSAT proofs remain alternatives with unmeasured costs.

Implemented local lex-DPLL as a correctness comparator, not a state-of-the-art SAT benchmark.
Eight focused and eleven source-wrapper tests pass;1809 instance checks,4633 oracle basis checks,
6442 repair checks and exact replay pass. First focused run failed one hand-count expectation
(44 vs48 X gates); corrected by manual count and retained history, with oracle unchanged.
3675 protected old file hashes match. Five primary source PDFs and hashes saved.

Hardware profile, competitive classical timing and certificate costs remain unknown. No numerical
positive-benefit region, autonomous agent capability, held-out generalization or universal impossibility
claimed. No model/QPU calls, installs, formal labels/metrics/cases or paper edits.
Next: first/absence obligations, reliable proof-checking boundary, complete plan costs and strong
tool-composition/ablation protocol. [Report](../pilot/benefit_analysis/lit005-v0.1/REPORT.md),
[progression](quantum_advantage/PROGRESSION.md).

## N-062 — Accepted resource-condition formulation

Date:2026-09-28. D-041 records the user's proposal and explicit approval to document it.
Input a classical program; infer under what quantum resource and workload conditions a
behavior-preserving migration is predicted to offer end-to-end benefit. The old supplied-device
decision becomes a membership check against those conditions. Logical qubits alone are insufficient;
include speed, reliability, complete costs, a competitive classical comparator and unknowns.

Added [RESOURCE_CONDITIONS](quantum_advantage/RESOURCE_CONDITIONS.md), including the distinction
between conditional prediction and actual hardware benefit, reuse of existing resource estimators,
and the unproven research step of automatically deriving plans and benefit conditions from source.
Updated handoff priorities; N-061 first/absence proof and cost work remains a subtask.
Documentation only: no new implementation, model/QPU run, installation, formal metric/case or paper edit.

## N-063 — Resource estimation integrated as a callable workflow tool

Date:2026-09-28. D-042 records the explicit choice to reuse Microsoft's open-source QDK,
with our own interface, full-cost aggregation and workflow integration. Added a Python function
and CLI command; the model supplies an OpenQASM3 proposal while the controller supplies separately
bound behavior/comparison evidence and cost intervals. Backend error is not a negative case label.

Inspected the official API and pinned1.32.3 wheel source; explicit SurfaceCode/factory/trace stack,
union-bound errors and use_graph=False. The latter avoids a documented incompleteness risk in the
SDK's graph-pruning path but does not establish a globally optimal resource threshold.
All data are model predictions; host preparation/communication/validation/fallback remain declared costs.

Real SDK smoke on a tiny engineering circuit returned177 physical qubits and9000 ns under hypothetical
hardware, with insufficient_evidence feedback because task/classical evidence is absent. No benefit
claim follows.30 focused tests passed;full253 passed/15 optional dependency skips. QDK was initially
absent and later present in existing palqo; no installation command was executed by this assistant.
No model/QPU run or formal case/gold/split/metric/paper modification. Existing artifacts preserved.
[Interface](quantum_advantage/RESOURCE_WORKFLOW.md), [execution](../pilot/resource_workflow/v0.1/README.md).

Handoff clarification: the subsequently read [environment record](quantum_advantage/ENVIRONMENT.md)
attributes QDK installation to a separately authorized environment task. This thread reused that
installation; the earlier execution archive records what was known when the smoke run was saved.

## 2026-09-28 — Scale/resource-condition diagnostic after user correction

The user requested evidence for research effect and rejected four-node no-benefit results as an
answer to the scale-dependent question. The initially proposed model decision comparison was not run.
Instead an exploratory MaxCut kernel study fixed six sizes (8–64), three graph seeds, and three
QAOA resource-template depths. This does not change the original wrapper's 16-node input cap.
18 classical MILP value/minimum-mask solves yielded 14 completions and four budget limits;
18 actual QDK estimates succeeded. The first 32-node graph completed classically in 0.579076s;
a hypothetical p=1 resource point needs6009 physical qubits/0.505ms per shot. The64-shot slice
leaves546.756ms for every remaining overhead, conditional on64shots actually sufficing.
This is a necessary cost budget, not a verified benefit region or a measured QPU result.

The existing all-edges-cut certificate cannot accept any partition of a positive triangle.
All generated general graphs include such a triangle; simply scaling the previous helper cannot
establish exact hybrid benefit. General optimum/tie certification and useful sampling probability
remain unresolved. Fixed angles here are resource templates, not optimized valid migrations.
Eight finite enumeration checks passed; post-run stronger-comparator audit matched MILP and Gray
enumeration to the source kernel on all64 four-node graphs, and timed Gray enumeration on8/16nodes.
No model calls, QPU, dependency installation, formal case/gold/metric changes, or paper edits.
Raw protocol/results, explicit post-hoc audit, necessary-condition plot and limits:
[report](../pilot/benefit_analysis/maxcut-scaling-v0.1/REPORT.md).

## 2026-09-28 — D-043: potential advantage through validated formulas

The researcher explicitly requested small-scale validation followed by formula-based analysis at
100qubits and beyond, emphasizing that ordinary researchers do not own such quantum machines.
Recorded this evidence strategy inD-043; no large-QPU prerequisite or small-instance rejection.
Derived logical countsG=n+p(3m+n) and a constructive matching schedule; checked45 small weighted-graph
instances using Hamiltonian and gate-level state calculations. Eight focused tests cover all64
four-node graphs at three depths, a two-node closed-form probability, enumerated success/failure
cost paths, strict inverse thresholds and large structural counts.

Eleven actual QDK calls estimated100/200/500logical-qubit templates, without their statevectors.
For100logical qubits,p=1, the specified100ns profile returned13310physical qubits and1.6ms/shot.
DerivedA+S(t+v)+(1-s)^S F<T under iid reliable certified-success events, retaining a separate
batch-q formula without iid. With explicitT=F=1s,A=10ms,v=.1ms,S=64 coordinates, s>0.197415%
predicts expected advantage; s=1% predicts0.644396s. These are design conditions, not measured
large-instance success rates or validated general-instance certificate costs.

Saved2376 conditions, raw SDK results, small evidence, constructive derivation and standalone plot.
No extrapolation of timed-out classical runs or small QAOA probabilities was used; ideal optimum
probability and canonical minimum-mask pair probability are separated. Exactness still requires a
sound certificate and exact fallback.175 previously bound files unchanged; no new model/QPU/install
or formal case/metric/paper change. [Report](../pilot/benefit_analysis/maxcut-formulas-v0.1/REPORT.md).

## 2026-09-28 — LogicalQubit access information and Mac continuation

The user reported access to a100bit cloud platform and suppliedcloud.logicalqubit.com, then requested
that current progress be saved for continuation onMac. Public official materials identifyAGate-100
as physical superconducting qubits; lqcloud0.5.0 supports circuit submission/results and requires
Python3.11/3.12. Account permissions, actual backend/calibration/fees were not inspected. No cloud
jobs or installations were authorized by this documentation request or executed.

Saved[Mac handoff](MAC_HANDOFF.md) with formula/scaling/LLM artifacts, original-contract and evidence
boundaries, hypothetical future fault-tolerant versus current physical-hardware distinction,
Python3.11 setup proposal, local-only verification commands and raw data transfer requirements.
OfficialPyPI metadata confirmsmacOSarm64/x86_64 wheels forQDK1.32.3 andpyqir0.12.5; this is not
Mac execution verification. The existingbwrap inference runner remainsLinux/WSL-only.
Project working tree contains untracked artifacts, soGit history alone is not a complete transfer.
This turn only updated documentation; no repeat tests/experiments, credentials, QPU, push or file transfer.
