# Research notebook

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
