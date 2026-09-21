# QRefactorBench

Research infrastructure for **Automatic / Selective Quantumization of Existing
Classical Software**, targeting **FSE 2027 / top-tier Software Engineering**.
Current phase: Phase-1 pilot task validation, after one Restricted Codex CLI baseline
and one controlled diagnostic. No scientifically validated benchmark release exists.

**Latest: [v0.1.1 review fixes and corrected inputs](pilot/reference_completion/v0.1.1/README.md).**
Fixed lock-report ordering (lit-005), delta overflow (lit-009), and explicit QAOA
source cues (lit-007); prior v0.1 is preserved. No new cases, labels or model run.
Construction background: [ten sourced tasks and evaluation checks](pilot/reference_completion/v0.1/README.md).
Six new classical programs adopt concrete QuanBench/+, SupermarQ, Qiskit HumanEval,
HPL and HPCG tasks/algorithms; four existing C2|Q> groups are reused. Thirty DRAFT
A/B/C inputs are prepared. [Reference-by-reference coverage](pilot/reference_completion/v0.1/COVERAGE.md)
distinguishes case adoption from methods-only use of PQID/MQT. These are traceable
synthetic adaptations, not ten deployed applications or validated labels. No model run.

**Research resumed after the coursework diversion.** Earlier review package:
[two-case WHERE boundary review and six A/B/C draft inputs](pilot/where_review/v0.1/README.md).
Thirteen classical witnesses show path/contract distinctions; no model experiment
or scientific label change. Three conditions per mother case are an approved design
direction; proposed locations and review criteria remain unvalidated. Source package:
[two source-driven WHERE cases / four views](pilot/source_adaptations/v0.2-where/README.md).
After the researcher corrected the sourcing direction, four pinned C2|Q> functions
were adapted into agenda completion and release-group review. Their functional
contexts add distinct preview/complete policies, conditional paths and cross-file
dependencies. Contexts remain synthetic; harder WHERE is an untested hypothesis,
and scientific judgments remain DRAFT/unknown. [Source and method audit](pilot/source_adaptations/v0.2-where/REFERENCE_BENCHMARK_AUDIT.md).
The earlier [eight paired groups](pilot/reference_cases/v0.3/README.md) are preserved
as synthetic construction work, not newly sourced examples or independent views.
Earlier [maintenance context](pilot/context_adaptations/v0.1/README.md) and
[two sourced DRAFT adaptations](pilot/source_adaptations/v0.1/README.md) remain intact.
Maintenance [structural mapping evidence](artifacts/context001_mapping_audit/README.md)
connects source behavior to a concrete QUBO/Ising expression; a
[narrow researcher initial opinion](artifacts/context001_mapping_audit/RESEARCHER_REVIEW.md)
accepts this correspondence, without independent validation or practical-benefit evidence.
Earlier evidence: [bounded objective-mapping audit](artifacts/plan_mapping_audit/README.md).
The separate [CA6000 SAT study](coursework/sat_case_study/README.md) and its slides
are retained; its neural-classification results are not quantumization evidence.

The task is WHERE → WHETHER → HOW → REFACTOR → VALIDATE. Structural eligibility,
practical suitability and benchmark support are independent labels.
`quantumizable != worth_quantumizing` and
`executable_quantum_code != semantically_correct_migration`.
`NO_QUANTUMIZATION` is a valid answer, serialized as `REMAIN_CLASSICAL`.

Four original DRAFT toys are retained, and ten additional DRAFT synthetic pilot
cases live in cases/pilot/. **Neither set is scientifically validated benchmark
ground truth.** [PHASE1_PILOT_STATUS.md](PHASE1_PILOT_STATUS.md) lists the cases,
blind annotation workflow, direct-LLM protocol, validation and next human actions.
Qiskit inspection is local; no QPU service is used.

**Runnable terminal demo:** `bash scripts/run_demo.sh` — replay two saved analyses,
execute a local Qiskit search implementation with exact classical fallback, and
verify a retained classical program. [Demo instructions and evidence](demo/README.md).
This is an illustrative integration, not a new model experiment or automatic translator.

Current baseline input snapshot: [pilot-v0.1](PILOT_V01_CHANGELOG.md), with corrected
public types and explicit answer cues removed. Use pilot/packets-v0.1/; the original
pilot/packets/ and all draft scientific labels are preserved. The first
[Restricted Codex CLI pilot baseline](pilot/baseline-v0.1/restricted-codex/README.md)
has run: ten first-attempt responses, evaluated only against DRAFT references.
It is not a raw API baseline or a validated benchmark result.

The subsequent [conditional-plan diagnostic](pilot/baseline-v0.1/conditional-plan-diagnostic/CONDITIONAL_PLAN_DIAGNOSTIC_RESULTS.md)
elicited plans in all eight structural-YES responses while their practical/final
judgments stayed unchanged. It is a paired diagnostic, **not an independent baseline**;
substantive text is not proof of semantic correctness. Both runs are complete.

Current coordinator review starts at the [blank human review record](pilot/review/CONDITIONAL_PLAN_HUMAN_REVIEW.md)
for completed conditional-plan outputs. It must not go to blind A/B annotators or
prediction processes. The earlier [Tomorrow review](pilot/annotation_assist/TOMORROW_REVIEW.md)
contains ten advisory proposals and preparation evidence; those context-exposed
AI proposals are not independent annotations and remain outside A/B/model packets.

## Start here

To inspect an actually executed source-to-Qiskit prototype, see
[context-001 conversion](demo/context001_qiskit/README.md): one-layer QAOA replaces
the classical solver, while surrounding reporting remains classical. Five small
inputs matched full reports, with four circuit simulations and no exact fallback.
This is a bounded AI-assisted implementation, not a general translator or advantage claim.

For a new Codex session, saying **“继续”** is sufficient. Follow
[AGENTS.md](AGENTS.md) → [research charter](docs/RESEARCH_CHARTER.md) →
[PROJECT_STATUS.md](PROJECT_STATUS.md) → [NEXT_ACTIONS.md](NEXT_ACTIONS.md) →
[DECISIONS.md](DECISIONS.md), then [Codex workflow](docs/CODEX_WORKFLOW.md) and the
status-linked latest results. The queue selects safe work; it does not authorize
repeating completed model runs. [TODO.md](TODO.md) is the longer backlog.
Research-method guidance lives in
[task definition](docs/task_definition.md), [annotation guidelines](docs/annotation_guidelines.md),
[benchmark design](docs/benchmark_design.md), [evaluation protocol](docs/evaluation_protocol.md)
and [open questions](docs/open_questions.md).

## Commands

Python >=3.10 is required. Installation below is an option for an environment where
dependency installation has been authorized; initialization reused existing Conda
environments instead. Optional extras provide YAML and Qiskit:

```bash
python -m pip install -e '.[test,yaml,quantum]'
python -m pytest -q
qrefactorbench validate cases/
qrefactorbench summarize cases/ --json
qrefactorbench summarize cases/pilot --json
```

From a source checkout in an existing environment with jsonschema/referencing,
use `python -m qrefactorbench` in place of `qrefactorbench`; no install is needed.
The scripts/ wrappers provide the same operations. Validation never executes code.
Exit codes: 0 valid/completed, 1 invalid dataset, 2 input/coverage/dependency errors.
Draft warnings do not fail structural validation. For externally collected pilot
responses, use the provider-neutral workflow below; no model call is made by these
commands and the responses must be obtained separately:

```bash
python scripts/prepare_pilot.py collect --responses /path/to/run/responses --output /path/to/run/predictions.json
python -m qrefactorbench evaluate cases/pilot /path/to/run/predictions.json --allow-draft --json
```

Current A/B/adjudication/model packets are under pilot/packets-v0.1/. The coordinator
distributes only the appropriate role directory, never the full repository or
common parent. See [pilot/README.md](pilot/README.md) for blinding and regeneration.

Legacy predictions use schemas/prediction.schema.json (v0.1.0). The Phase-1 profile
is schemas/phase1_prediction.schema.json (v0.2.0), adding separate predicted labels,
free-text intent and applicability evidence. Both are accepted as JSON arrays.
REMAIN_CLASSICAL permits an empty candidate list. QUANTUMIZE requires a candidate
and structured plan. Evaluation is static, deterministic and produces JSON with
component results and input/implementation hashes. It never applies patches or
runs generated code. Trusted execution, semantic and contract interfaces are
documented in the evaluation protocol; their existence is not a completed
end-to-end migration evaluator.

## Repository map

| Path | Purpose |
| --- | --- |
| schemas/ | case, legacy prediction, migration-plan and Phase-1 prediction schemas |
| cases/ | four original DRAFT toys plus ten DRAFT pilot programs and classical tests |
| pilot/ | private sampling plan, shared contract menu, blind packets, baseline and failure-analysis forms |
| templates/ | positive, hard-negative and negative human annotation scaffolds |
| qrefactorbench/ | loader, validator, CLI, fingerprints and modular evaluators |
| tests/ | validation, scoring, execution-hook and optional Qiskit/YAML tests |
| examples/ | deliberately incomplete predictions for CLI demonstrations |
| scripts/ | source-checkout command wrappers |
| docs/ | research protocol, questions, notebook and actual validation record |

Tests under tests/ run classical toy tests in separate processes to avoid module
name collisions. `pytest` in a toy directory can also run that case's classical
test. Quantum-specific optional tests skip cleanly if Qiskit is unavailable.

Review preparation N-001 is complete. [D-014](DECISIONS.md#d-014-conditional-planning-independent-of-adoption)
records researcher choice A: future protocols require conditional plans for structural
YES independently of adoption. NEXT_ACTIONS now waits for actual human plan review;
do not ask the policy question again, regenerate forms or launch another run.
Scientific progression requires human plan review and independent case
annotation/adjudication. Licensing is pending; see
[LICENSE](LICENSE) before redistribution. Real-world provenance remains future work.
