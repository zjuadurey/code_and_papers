# QRefactorBench-v0 — Phase-1 pilot preparation

**Historical preparation handoff, not the live project status.** Statements below
about absent model calls describe their original preparation stage. The first CLI
baseline and controlled diagnostic have since completed. Start at
[PROJECT_STATUS.md](PROJECT_STATUS.md) and [NEXT_ACTIONS.md](NEXT_ACTIONS.md) for
current work; preserve this preparation record rather than replaying its commands.

**2026-09-20 baseline update:** the first Restricted Codex CLI single-turn pilot
has completed on unchanged pilot-v0.1 inputs. See
[results](pilot/baseline-v0.1/restricted-codex/BASELINE_RESULTS.md).
Ten first attempts are schema-valid; all labels remain DRAFT. The preparation
record below describes the earlier, pre-experiment state and its validation.

Last updated: 2026-09-20 (public-input revision; original preparation record below).

Current distribution: pilot/packets-v0.1/. See [PILOT_V01_CHANGELOG.md](PILOT_V01_CHANGELOG.md)
for the researcher-approved 009 type correction, ten-case prose audit, preserved
originals and passing validation. All labels remain DRAFT; no baseline ran.

Coordinator entry point: [Tomorrow review](pilot/annotation_assist/TOMORROW_REVIEW.md)
and [overnight results](pilot/annotation_assist/OVERNIGHT_STATUS.md). Ten new advisory
proposals and mechanical checks were added without changing any case/packet/label.
Prior preparation context prevents treating the proposals as independent annotations.
That review describes the original packets; the approved type/cue fixes are now
recorded in pilot-v0.1. Its other scientific uncertainties remain open.

**Status: prepared for human review; not scientifically validated, adjudicated or
frozen.** Ten new synthetic DRAFT cases are separate from the four original toys.
There are no human submissions, model calls, pilot model scores or quantum
migration results. No dependencies were installed.

## What was added

- Ten original programs written with Codex assistance, classical regression tests,
  public task/workload facts, private draft annotations and proposed semantic criteria.
- A/B blind packets, blank adjudication records, shared DRAFT contract menu and
  deterministic packet export with file hashes and overwrite refusal.
- Ten direct-LLM prompts, a reusable prompt template, run metadata and a local
  collector for externally obtained JSON. No provider/API configuration is assumed.
- Phase-1 prediction schema 0.2.0 reusing unchanged v0.1 formats; separate predicted
  eligibility/suitability/support, free-text intent, family, applicability, assumptions
  and risks. Evaluations preserve original predictions and unknown-result coverage.
- A lightweight open-coded observation form; no fixed empirical failure taxonomy.

Software/result/profile version 0.2.0 is distinct from the QRefactorBench-v0 pilot
name. Cases and nested plans still use schema 0.1.0. Legacy predictions remain valid.

## The ten cases (curator-only sampling hypotheses)

| Case | Classical computation | Proposed category |
| --- | --- | --- |
| [pilot-001](cases/pilot/pilot-001/program.py) | Boolean clause satisfaction | search positive |
| [pilot-007](cases/pilot/pilot-007/program.py) | subset-sum existence | search positive |
| [pilot-003](cases/pilot/pilot-003/program.py) | exact weighted maximum-cut score | optimization positive |
| [pilot-006](cases/pilot/pilot-006/program.py) | exact binary quadratic minimum | optimization positive |
| [pilot-005](cases/pilot/pilot-005/program.py) | bundle feasibility with filtering and response metadata | contextual search positive |
| [pilot-009](cases/pilot/pilot-009/program.py) | binary placement cost with validation and reporting | contextual optimization positive |
| [pilot-002](cases/pilot/pilot-002/program.py) | sequential digest with observable ordered audit callbacks | unsupported-hotspot hard negative |
| [pilot-008](cases/pilot/pilot-008/program.py) | complete normalization/materialization with aliasing requirements | unsupported-hotspot hard negative |
| [pilot-004](cases/pilot/pilot-004/program.py) | at-most-eight resident codes, one invocation | structurally plausible, suitability negative |
| [pilot-010](cases/pilot/pilot-010/program.py) | fresh JSON data loading followed by membership | structurally plausible, suitability negative |

These categories are sampling proposals, not established findings. All ten have
annotation_status=DRAFT, annotators=[], source_url=null and license=NOASSERTION.
The synthetic/Codex-assisted origin is explicit; no external provenance or license
is guessed. Six intended positives retain practical_suitability=null,
benchmark_supported=null and expected_decision=null. The two unsuitable labels
are provisional hypotheses under supplied assumptions, not profitability measurements.
Eight cases have proposed DRAFT contracts/plans; the two unsupported cases abstain
with no proposed plan. All scientific oracle hooks remain unimplemented draft specifications.

The case schema uses positive/hard_negative/negative, so the two suitability
negatives also use hard_negative; the private seed_manifest retains the finer
sampling categories. Pilot counts are 6 positive and 4 hard_negative. Overall
counts including old toys are 14 DRAFT, 8 positive, 5 hard_negative and 1 negative.

## Independent annotation and adjudication

1. The coordinator reviews public facts, source/test correctness and proposed
   sampling coverage. If facts/source change, create a new packet before collection.
2. Distribute **only** pilot/packets/annotator_a to A and annotator_b to B, outside
   the full repository. Do not distribute this report, case.json, curator notes,
   private manifest, draft plans, model outputs or the common packets parent.
   Directory separation is not an access-control mechanism.
3. A/B independently fill each annotation.json. Null means unresolved/unfilled;
   candidate_regions=[] means an explicit no-candidate judgment. Record real
   identities only upon submission, and preserve unchanged original submissions.
4. After both submit, compare each pair with the existing CLI:

```bash
python -m qrefactorbench compare-annotations /path/to/A/pilot-001/annotation.json /path/to/B/pilot-001/annotation.json --json
```

5. A human expert records disagreements, resolutions, evidence and remaining
   uncertainty in the adjudication packet. Create separately versioned reviewed
   case manifests with real review artifacts; do not overwrite the original seeds.
   There is no automatic promotion or fabricated agreement statistic.

The two unsupported hard-negative drafts use empty eligible candidate sets and
record rejected hotspots privately. D-005 currently requires nonempty regions for
REVIEWED hard negatives. Resolve Q14 before promoting these cases; don't insert
a fake eligible region to satisfy that rule. Other unknown labels may also keep
cases DRAFT until sufficient scientific evidence exists.

Regeneration into a **new** output directory uses:

```bash
python scripts/prepare_pilot.py prepare --output /path/to/new-pilot-packets
```

## Direct-LLM baseline and evaluation

Give the operator only pilot/packets/baseline. Submit each prompt verbatim once in
a fresh context to a chosen strong generic code LLM. Record model/provider/revision,
system message, actual decoding settings, packet hash, raw outputs and failures
using run_metadata.template.json. No tools, retrieval, execution feedback, repair
or agent loop is permitted by this baseline protocol. See pilot/baseline/README.md.

Retain one raw JSON object per successful response as responses/pilot-NNN.json.
Preserve malformed output unchanged and record it as a failure; the collector
does not strip fences, repair output or manufacture abstentions.

```bash
python scripts/prepare_pilot.py collect --responses /path/to/run/responses --output /path/to/run/predictions.json
python -m qrefactorbench evaluate cases/pilot /path/to/run/predictions.json --allow-draft --json > /path/to/run/evaluation.json
```

These commands are ready for **external responses that do not yet exist**. Until
human references are reviewed, outputs are demonstration diagnostics only. For
later scientific evaluation, point the evaluator to the separate reviewed dataset.
Intent descriptions and contract applicability require human semantic coding;
contract-ID membership alone does not prove correctness. T1 retains exact and
line-overlap diagnostics without a final overlap threshold. Structural/suitability
comparisons retain unknowns and expose coverage with conditional accuracy.

All ten responses are required for normal collection. If inspecting an intentional
subset after failures, use unchanged valid responses and explicit repeated
`--case-id` options, report selected/unselected cases and failures, and do not
present subset diagnostics as a full-pilot score. Final failure scoring is unresolved.

## Failure analysis

After independent reference annotation is preserved, copy
pilot/failure_analysis/observation_template.json for each observation. Record run
and case IDs, raw evidence, source coordinates, reference version/status, free-text
open codes, alternatives and uncertainty. Capture correct behavior and annotation
ambiguity too. Human intent/applicability judgments are nullable and evidence-linked.
Discover recurring categories from actual observations; no taxonomy or model error
rate has been established.

## Scientific questions deliberately unresolved

Suitability/cost assumptions (Q1/Q6), eligibility evidence (Q2), localization metrics
(Q3), hard negatives and region semantics (Q4/Q14), contract completeness and exact
versus stochastic semantics (Q5/Q9), release composition/splits/leakage (Q7/Q8/Q10),
licensing (Q11), annotation workflow (Q12/Q13), intent rubric and response failures
(Q15/Q16). D-008–D-010 are PROVISIONAL; no earlier decision was promoted to ACCEPTED.

## Actual validation

Working directory: /home/audrey/code_and_papers/2026/FSE/qrefactorbench.

| Command / environment | Result |
| --- | --- |
| palqo Python 3.10.21: `python -m pytest -q` | **84 passed, 3 skipped** (Qiskit/YAML absent) |
| htp-static Python 3.11.16: `python -m pytest -q tests/test_optional.py` | **5 passed**, covering the optional skips |
| palqo: `python -m qrefactorbench validate cases/` | valid, 14 expected DRAFT warnings |
| palqo: `python -m qrefactorbench summarize cases/ --json` | 14 DRAFT cases; separate pilot summary: 10 |
| palqo: `python scripts/prepare_pilot.py prepare --output pilot/packets` | 10 cases, 4 role directories, 0 model calls |
| Python 3.12.12: `PYTHONPATH=. python tests/test_packaging_integration.py` | dataset/YAML/real-Qiskit/schema integration passed |
| existing setuptools: build 0.2.0 wheel; Python 3.12 outside-checkout extraction smoke | four schema resources and console entrypoint passed |

Full interpreter paths, exact commands and saved outputs are in docs/validation.md
and artifacts/phase1_validation/. Collector/evaluator tests use temporary synthetic
fixtures, not model runs. All ten classical programs' tests ran in separate processes.
Optional skips are reported separately, not silently counted as core passes.

## Exact next human actions

1. Review the ten programs, neutral workload facts and proposed sampling coverage;
   decide whether any case needs replacement before a fixed packet is distributed.
2. Confirm distribution/licensing conditions; send A/B only their separate packets.
3. Obtain independent annotations, archive them, compare and adjudicate; address
   Q14 and retain any unresolved scientific labels as null/DRAFT.
4. Choose and record one generic code-model configuration; execute the fixed
   single-response baseline, preserving all raw responses and transport/format errors.
5. Collect/evaluate valid responses against the appropriate reference snapshot;
   manually code intent/applicability and open-code observed behavior with evidence.
6. Review disagreements and failure patterns before deciding whether to revise the
   benchmark or pursue any later technique. No agent design is justified by this
   preparation work alone.
