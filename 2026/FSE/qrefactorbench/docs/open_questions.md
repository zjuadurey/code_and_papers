# Open scientific questions

Questions below are OPEN unless explicitly marked RESOLVED. Candidate options are
proposals, not accepted facts.
Do not implement a resolution merely for engineering convenience.

2026-09-21 evidence for Q7/Q9: the [005/009 context review](../artifacts/context_case_review/README.md)
distinguishes functional context from real-project provenance. In pilot-005,
filtering changes observable behavior, whereas sorting normal eligible records
does not change the handler's existence/count output. The frozen public contract
explicitly requires sorting. OPEN: is this an intentional process constraint or an
implementation detail, and what helper API / sku domain is actually promised?
Preserve the requirement pending review; no automatic relaxation or label change.

| ID | Question | Options / arguments | Evidence needed |
| --- | --- | --- | --- |
| Q1 | How should practical suitability be operationalized? | PARTIALLY RESOLVED by D-016: evidence under explicit workload/resource assumptions, unknown when insufficient; no composite score or simulator-runtime advantage claim. | Still OPEN: case-specific assumption profiles, cost evidence and reviewed judgments. |
| Q2 | What evidence establishes structural eligibility? | PARTIALLY RESOLVED by D-017: YES establishes a concrete supported formulation of the computational core with domain/predicate or variables/objective/constraints correspondence and conditions. It does not certify complete contract preservation. Missing essential mapping evidence remains UNCERTAIN. D-015 still governs migration correctness. | Still OPEN: case-specific mapping verification and review consistency; no automatic relabeling or final scoring rubric. The conceptual boundary is decided; do not ask item 1 again. |
| Q3 | How should region overlap be scored? | Exact regions, AST boundaries, token/line IoU, matched regions; no cutoff currently accepted. | Human localization variability and error analysis. |
| Q4 | Which categories constitute hard negatives? | Effects, dependencies, data loading, problem scale, unsupported family; taxonomy remains provisional. | Pilot cases and annotation confusion patterns. |
| Q5 | How should admissible migration sets be represented and reviewed? | Case-local versus versioned library contracts; open versus enumerated algorithm families; composite strategies. | Multiple independent valid formulations and working validators. |
| Q6 | How should theoretical advantage assumptions be encoded? | Oracle access, QRAM/data loading, preprocessing, repetitions, precision and classical baseline model must be explicit. | End-to-end cost analyses with comparable classical baselines. |
| Q7 | Should real-world repository cases differ from canonical kernels? | Same labels with richer provenance, dependency/effects metadata, or context-specific annotation rubric. | Matched kernel/context examples and human effort measurements. |
| Q8 | What size and composition support an eventual FSE evaluation? | First 5–10 human seeds, then a possible 20–30 case pilot; these are workflow targets, not power claims. | Annotation cost, coverage, variability and statistical study design. |
| Q9 | Which semantic and probabilistic contracts are acceptable? | PARTIALLY RESOLVED, 2026-09-20: D-015 adopts preservation of the original software contract by default. Keep exact requirements exact; approximation/probabilistic guarantees need permission in that original contract. Any later relaxation is a separately versioned changed contract. | Still OPEN: case-specific oracle coverage, absence/optimality certification, tie/effect behavior, and statistical tests where permitted. Missing error/quality/confidence/shot thresholds are not invented. Do not re-ask the default-preservation question. |
| Q10 | How should releases be split and frozen without leakage? | Group source lineage, near duplicates, templates and algorithm variants before splitting; immutable signed/hash manifests. | Provenance audit, contamination analysis and release policy review. |
| Q11 | What licenses should infrastructure and cases use? | Choose an infrastructure license and independently verify per-source redistribution. LICENSE currently grants nothing. | Rights-holder decision and source records. |
| Q12 | What annotation workflow and scoring population are defensible? | PARTIALLY RESOLVED by D-016: review may retain uncertainty; coordinator review precedes independent annotation/needed expert validation for important formal-evaluation cases. | Still OPEN: versioned state representation, category meaning, scoring population and missing-response policy. Old schemas retain their constraints; D-005 certainty policy is superseded prospectively, not by relabeling old cases. |
| Q13 | How should multiple candidate regions and constraints compose? | Case-level versus per-region suitability, dependency graphs, alternate candidates, no-bound resource policies. | Real multi-region examples and human semantics review. |
| Q14 | Does a hard negative's candidate_regions describe an eligible candidate or a rejected tempting hotspot? | PARTIALLY RESOLVED by D-016: WHERE may include tempting regions, with exclusion performed by WHETHER. Candidate presence is not structural YES. | Still OPEN: meaningful nomination/boundary rubric and future scoring. Do not automatically annotate every hotspot or change old empty-region cases and their scores. |
| Q15 | How should blind intent recognition, applicability and unknown model judgments be evaluated? | Open-text human coding versus a preregistered shared vocabulary; preserve private-ID independence and report unresolved coverage separately. | Pilot descriptions, coder disagreements and valid alternative formulations. |
| Q16 | How should malformed/missing direct-model responses and related synthetic cases affect analysis? | Preserve raw failures, explicit subset diagnostics, prospective failure scoring; group related predicate/objective constructions before any future split. | Actual baseline failure rates and provenance/dependency review; no split or scores chosen now. |
| Q17 — RESOLVED 2026-09-20 | What is the intended valid input domain for pilot-009? | Researcher instructed matching executable behavior: string name, integer cost fields, existing validation errors. Corrected public text in pilot-v0.1; preserved original text and packets (D-011). | Executable type/error checks pass; this resolves the specification typo, not scientific labels. Original finding remains in pilot/annotation_assist/pilot-009.md. |
| Q18 | How much intent/localization information should public specifications reveal? | D-011 removes explicit per-case candidate/family/category cues, including 005's enumeration direction and 002/008's exclusions. Necessary functional specifications still describe exact outputs and may convey intent. | Independent annotation and later baseline evidence about the remaining specification assistance; no empirical comparison or scientific conclusion yet. |
| Q19 | How should conditional HOW coverage be separated from verified migration quality and adoption? | PARTIALLY RESOLVED, 2026-09-20: researcher selected A; D-014 adopts conditional planning for response-reported structural YES in future protocols, independently of practical adoption. The diagnostic's 8/8 emitted plans are not verified correct. | Still OPEN: independent plan/semantic/certification review, resource evidence and support/applicability variation; define coverage and quality against human-reviewed eligibility without hiding recognition omissions. Exact scoring remains unresolved; do not ask the adopted policy question again. |

Engineering supports recording these decisions but cannot replace the required
research evidence. No question has been resolved by the presence of a schema field.

2026-09-19 review notes for existing questions: Q1/Q6 affect practical judgments in
all eight structurally proposed pilot cases, including 004/010; small scale or fresh
data alone does not establish the missing decision criterion. Q5/Q15 also cover
alternative search/quadratic formulations in 005/007 and unknown-versus-abstention:
model labels allow null, but decisions are binary and candidate_regions cannot be
null. See ../pilot/annotation_assist/TOMORROW_REVIEW.md for the nine-item human agenda.

2026-09-21 source-adaptation trial: Q7/Q9/Q18 also affect lit-001/lit-002 in
[source_adaptations/v0.1](../pilot/source_adaptations/v0.1/README.md). Their application
contexts are new synthetic requirements around sourced kernels, not deployed-system
evidence. Review whether inherited deterministic tie behavior is an intended test
obligation, how much original algorithm-name cueing is acceptable, and where the
replaceable region ends versus its input/output dependencies. No answer is implied
by passing classical tests. Q1/Q6 practical evidence and Q11 package release
licensing remain open; source snippets retain the dataset's CC-BY-4.0 attribution.

2026-09-21 second-context follow-up: [context-001](../pilot/context_adaptations/v0.1/README.md)
adds current/proposed evaluation and action reporting, with the approved report-only
movement count. The inherited tie rule can move an already optimal assignment; this
is documented behavior, not silently repaired by adding a new objective. Q7/Q9/Q18
review should address functional expectations and actual localization difficulty.
Context-001 and lit-001 share a computational source; future splitting/comparison
must account for this dependence, without deciding a final split in this task.

2026-09-21 structural review evidence: context-001 now has an explicit source-to-QUBO/
Ising derivation and bounded executable correspondence checks in
[the structural audit](../artifacts/context001_mapping_audit/README.md). This supports
an AI structural-YES recommendation under the already accepted D-017 definition;
human initial review is still pending. Q1/Q6 practical benefit and Q9/Q19 exact
solver/tie/full-migration obligations are not resolved by objective correspondence.

2026-09-21 Q9/Q19 follow-up: [D-018](../DECISIONS.md#d-018-context-001-approximate-quality-profile)
records explicit permission for a separate context-001 approximate profile and accepts
ρ=(W−C)/(W−C*) as its descriptive satisfied-weight quality ratio. Report feasibility
and gaps with acceptance pending; 95% is an example, not a resolved threshold.
Still OPEN: minimum ratio justified by intended use, selection/tie behavior for
approximate arrangements, and any per-run versus repeated-run statistical requirements.
Do not treat current observed 91.11%/97.77% as independent evidence for choosing a
cutoff. The old exact contract remains unchanged; the new document is not a gold case.

2026-09-21 Q7/Q9/Q14/Q18 follow-up — [eight-group reference expansion](../pilot/reference_cases/v0.3/TOMORROW_REVIEW.md):
the researcher authorized bounded construction, not label validation. New functional
review questions: context-005 assesses requests independently rather than simultaneously;
context-006 assumes all components are optional and reports a charge floor, not preserved
application functionality; context-007 has exact hard capacity and an explicit tuple
tie policy that can include zero-priority items; context-008 requires all mutable copies,
not a sampled/aggregate substitute. Keep/change/drop is pending human review.
Constraint-to-QUBO penalty/slack evidence for 007 is absent. None of these cases inherits
context-001's approximation permission. Core/context and pilot ancestry, plus cross-group
algebraic similarity, need consideration in any future independent split. Scientific
labels, practical evidence and demonstrated WHERE difficulty remain unresolved.

2026-09-21 Q7/Q9/Q14/Q18 source-first follow-up —
[lit-003/lit-004](../pilot/source_adaptations/v0.2-where/WHERE_REVIEW.md):
review recursive-region versus tighter recurrence boundaries, and inline-loop versus
loop-plus-cross-file-predicate nominations. Required dependencies should be retained
without silently adopting exact-span or overlap scoring. Static candidate existence
and activation on a particular inspect/retain/solve input are distinct: which is
the unit of evaluation? Greedy preview and full solving have different public
contracts; accepting nomination followed by rejection does not imply either is
automatically an incorrect WHERE prediction. A future core/context comparison must
address naming, length and interface complexity before attributing changes to WHERE.
Source records improve traceability but their synthetic nature does not establish
real-application representativeness; the new application requirements need human
review. Functional tests do not resolve quantum eligibility, practical suitability,
exactness certification or final release licensing. D-019 sets direction only.

2026-09-21 Q7/Q14/Q18 WHERE design follow-up:
[D-020](../DECISIONS.md#d-020-three-conditions-per-mother-case-for-where-diagnosis)
accepts three conditions per mother problem; [concrete protocol](../pilot/where_review/v0.1/PROTOCOL.md)
and two review dossiers now exist. Still unresolved: validate the proposed cue spans;
allow narrow core plus dependencies versus wider spans; distinguish absent explanation
from actual misunderstanding; establish comparable no-candidate/multiple-candidate
controls without assuming an intended span is the only valid answer. B supplies a
candidate-existence/attention cue, so B–C is not pure causal localization difficulty;
A additionally differs in names, length and interface. Choose sampling/order policy
and human evidence rubric before future runs. These are two mother cases/six inputs,
not six independent observations or a model result. No new metric is adopted.

2026-09-21 source-completion follow-up (Q7/Q9/Q11/Q14/Q18):
[Ten source-derived groups](../pilot/reference_completion/v0.1/README.md) now exist,
including six new programs. Review whether their authored functional requirements
are representative and whether XOR/numerical workflows are useful scope controls
without claiming absolute non-quantumizability. B's proposed control-region cue may
induce nomination, so compare it carefully with no-cue C. Source overlap (SAT,
knapsack, cut/Ising and numerical systems) must inform future splitting; ten groups
are not ten independent algorithm families. Known source test/implementation
inconsistencies cannot become benchmark gold. HPL webpage and new-package licensing
remain unresolved where no license is established.

[Executable method witnesses](../pilot/reference_completion/v0.1/METHODS.md) do not
choose a scientific threshold. Which cases require equivalent unitary behavior,
which require only task-level outcomes, and which permit approximate/probabilistic
outputs? Determine support, bit order, sample counts, feasibility and confidence
policies before a future experiment. Never apply the source KL cutoff or process
overlap as a universal semantic-migration rule; no such policy is accepted here.

The new A/B/C allowlist excludes private answers/tests but retains NOTICE provenance
and meaningful source names. Those can cue task identity or memorization. Decide and
version a legally sound source-information presentation policy before a formal run;
do not claim that allowlist checks establish fully anonymous/blind inputs. B/C share
prediction case IDs and must be collected in separate condition result sets.
