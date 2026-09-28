# Engineering validation record

Date: 2026-09-18. Working directory:
`/home/audrey/code_and_papers/2026/FSE/qrefactorbench`.
No package installation was performed. Existing Conda environments were reused.

The first section records the historical Phase-0 four-case snapshot. The Phase-1
section below records the current fourteen-case workspace; original artifacts
are intentionally preserved rather than overwritten.

| Environment | Python | Relevant observed versions | Actual result |
| --- | --- | --- | --- |
| palqo | 3.10.21 | pytest 9.1.1, jsonschema 4.26.0, referencing 0.37.0, setuptools 84.0.0, wheel 0.48.0 | 64 passed, 3 optional skips |
| htp-static | 3.11.16 | pytest 9.1.1, PyYAML 6.0.3, Qiskit 2.5.2 | optional suite 5 passed |
| qrefactor-v1-py312 | 3.12.12 | jsonschema 4.26.0, referencing 0.37.0, PyYAML 6.0.3, Qiskit 2.5.2 | runtime integration passed from source and extracted wheel |

Core tests cover schemas, unknown versus false labels, positive/negative
contradictions, missing artifacts, path traversal/symlink escape/null bytes, invalid
ranges/functions, duplicate IDs, annotation maturity, independent review metadata,
missing oracle configuration, multi-contract references, prediction coverage,
metric denominators, unknown end-to-end components, non-executing syntax checks,
trusted fixture process failure/timeout, semantic hooks and resource-bound checks.
Four classical toy tests are executed in isolated processes within this suite.

Optional tests use real Qiskit circuits (including a barrier and dynamic control
flow) and YAML duplicate/recursive/non-JSON-value rejection. These were run in a
second environment, not counted as passes in the first environment.

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q
/home/audrey/miniconda3/envs/htp-static/bin/python -m pytest -q tests/test_optional.py
PYTHONPATH=. /home/audrey/miniconda3/envs/qrefactor-v1-py312/bin/python tests/test_packaging_integration.py
```

The following commands generated the stored JSON evidence:

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench validate cases --json > artifacts/validation/dataset_validation.json
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench summarize cases --json > artifacts/validation/dataset_summary.json
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench evaluate cases examples/draft_predictions.json --allow-draft --json > artifacts/validation/static_evaluation.json
```

Validation reports valid=true, four cases, four DRAFT warnings. Summary: two
positive, one hard_negative, one negative; all DRAFT; kernel=2,
function_with_distractors=1, small_program=1. The static demo reports two applicable
positive cases: one failed decision, one unknown strict success, zero passed.
Those values test pipeline behavior and are not research findings.

Wheel build used the existing backend without dependency installation:

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -c 'import setuptools.build_meta as b; print(b.build_wheel("/tmp/qrefactorbench-wheel-check"))'
```

The produced wheel was extracted into a fresh temporary directory. With that
directory as PYTHONPATH and working directory, Python 3.12 ran the absolute path
to tests/test_packaging_integration.py. All schema files and the console entrypoint
were checked inside the archive. The result is saved in
../artifacts/validation/wheel_integration.json. This verifies wheel contents and
runtime imports; it is not a clean `pip install` test or a full dependency lock.

Not validated: scientific correctness of labels/contracts, quantum migrations,
probabilistic acceptance policies, model performance, speedup, real hardware,
human agreement, repository-scale cases or immutable release integrity. The
trusted subprocess helper is not a sandbox for arbitrary submissions.

## 2026-09-18 — Phase-1 preparation validation

The same existing environments/versions listed above were reused. Actual commands
and outcomes, all from the repository root:

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q tests/test_pilot.py tests/test_evaluation.py tests/test_validation.py
# 73 passed (focused workflow/schema/evaluation validation)
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q
# 84 passed, 3 skipped: Qiskit/PyYAML absent in this environment
/home/audrey/miniconda3/envs/htp-static/bin/python -m pytest -q tests/test_optional.py
# 5 passed, including all optional features skipped above
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench validate cases/
# VALID: 14; 14 expected DRAFT warnings
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench summarize cases/ --json
# 14 DRAFT, 8 positive, 5 hard_negative, 1 negative
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench validate cases/pilot --json
# valid=true, case_count=10; expected DRAFT warnings
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench summarize cases/pilot --json
# 10 DRAFT, 6 positive, 4 hard_negative (including two suitability-negative hypotheses)
/home/audrey/miniconda3/envs/palqo/bin/python scripts/prepare_pilot.py prepare --output pilot/packets
# ten cases, A/B/adjudication/baseline directories, zero model calls
PYTHONPATH=. /home/audrey/miniconda3/envs/qrefactor-v1-py312/bin/python tests/test_packaging_integration.py
# fourteen cases, four schemas, YAML and real Qiskit integration passed
/home/audrey/miniconda3/envs/palqo/bin/python -c 'import setuptools.build_meta as b; print(b.build_wheel("/tmp/qrefactorbench-phase1-wheel"))'
# built qrefactorbench-0.2.0-py3-none-any.whl using existing dependencies
```

The wheel was extracted into a fresh temporary directory and the integration
script run with that directory as cwd/PYTHONPATH under Python 3.12. The new
phase1_prediction.schema.json and console entrypoint were checked in the archive;
four-schema integration passed without installing the wheel or dependencies.
The prepare output now exists: future generation must specify a new directory.

New tests execute all ten classical programs in isolated pytest subprocesses and
check composition/provenance, separate predicted labels, abstention with retained
analysis, missing-reference coverage, no private-ID intent matching, public-field
allowlisting with secret sentinels, unmodified source/line coordinates, packet
hashes, overwrite refusal, malformed response preservation, complete coverage,
explicit subset reporting and annotation differences including assumptions.
Temporary collector/evaluator predictions are test fixtures, not model results.

Saved raw engineering outputs live in artifacts/phase1_validation/:
pytest-core.txt, pytest-optional.txt, dataset_validation.json,
dataset_summary.json, pilot_summary.json, runtime_integration.json,
wheel-build.txt and wheel_integration.json. The earlier artifacts/validation/
directory remains a historical Phase-0 record whose source hashes refer to that
older implementation; it must not be mistaken for a current evaluation.

No independently annotated pilot case, agreement statistic, direct-LLM response,
baseline score, statistical quantum oracle, profitability result or end-to-end
quantum implementation was produced or validated in this session.

## 2026-09-19 — Researcher review preparation validation

Existing environments were reused without installations. From the repository root:

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q
# 84 passed, 3 skipped in 3.22s (Qiskit/PyYAML absent here)
/home/audrey/miniconda3/envs/htp-static/bin/python -m pytest -q tests/test_optional.py
# 5 passed in 1.26s, including the optional features
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench validate cases/
# VALID: 14; 14 expected DRAFT warnings
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench summarize cases/ --json
# valid=true; 14 DRAFT, 8 positive, 5 hard_negative, 1 negative
/home/audrey/miniconda3/envs/palqo/bin/python pilot/annotation_assist/verify_workflow.py
# All mechanical checks PASS; no model calls or scientific scores
PYTHONPATH=. /home/audrey/miniconda3/envs/qrefactor-v1-py312/bin/python tests/test_packaging_integration.py
# integration=passed, 14 cases, 4 schemas, actual Qiskit circuit and YAML roundtrip
```

The audit script runs documented prepare/collect/evaluate/compare commands with
temporary dummy data. Fresh packets match existing bytes; ten IDs and null labels
survive the collector/evaluator, both decisions are exercised, and DRAFT-default
and malformed-response rejection each return the expected exit 2. No dummy scores
or predictions are saved. Blank A/B comparison does not measure human agreement.

Raw outputs, the before-file hash manifest and a 225-file unchanged check are under
pilot/annotation_assist/validation/. Proposal hashes were recorded before workflow
inspection and remain unchanged. See WORKFLOW_AUDIT.md and OVERNIGHT_STATUS.md in
that package for limitations: public prose cueing, pilot-009 domain inconsistency,
uncertainty expressivity and unapproved scientific scoring remain open. No production
code, case labels or distributed packets changed. No new wheel build was needed.

## 2026-09-20 — pilot-v0.1 public-input revision

Exact commands and raw outputs are recorded in
[artifacts/pilot_v01_validation/README.md](../artifacts/pilot_v01_validation/README.md).
The existing environments were reused without installation. Focused tests:
23 passed; full pytest: 87 passed/3 optional skips; separate optional suite: 5 passed.
All ten pilot cases validate; full dataset remains fourteen valid DRAFT cases.

New tests check original task preservation, revised packet contents/source identity,
byte-identical fresh export and pilot-009's public string-name/invalid-input behavior
against the executable program. Existing private-sentinel leakage and prediction/
evaluation tests pass. The workflow audit now accepts --packets; use
`python pilot/annotation_assist/verify_workflow.py --packets pilot/packets-v0.1`.
It verifies temporary dummy responses only, including expected exit-2 rejections;
no baseline was run or scored. The previous 2026-09-19 results describe old packets.

Original packets and scientific annotations are unchanged. The public-input archive,
exact diff and new packet hashes are under pilot/revisions/pilot-v0.1/. Passing these
checks establishes neither scientific annotation validity nor practical advantage.

## 2026-09-20 — Post-baseline validation

After all ten Restricted Codex CLI calls ended, the existing collector accepted
10 predictions with 0 repairs and the existing evaluator completed with --allow-draft,
demonstration_only=true. These are actual outputs, not the earlier dummy fixtures.

Full pytest: 87 passed/3 optional skips in 3.20s; separate optional suite: 5 passed
in 0.95s. validate cases/ reports 14 valid DRAFT cases; JSON summary unchanged.
The raw/event audit verifies ten distinct single-turn threads, one final response
each, zero observed tools/retries, and byte-identical raw/parsed copies. 308 protected
benchmark/code/schema/test/packet files retain their before-run hashes.

Exact commands and saved outputs:
[baseline validation](../pilot/baseline-v0.1/restricted-codex/validation/README.md).
No dependencies installed; no quantum execution or tests were used to solve cases;
all model outputs were fixed before these checks. Scientific correctness and
independence of DRAFT reference annotations remain unvalidated.

## 2026-09-20 — N-004 packet regeneration repair

The alignment audit found a real regeneration regression: current baseline README
history was copied into the frozen packet instructions. Reproduced that failure and
two new modified/missing-README failures before changing the exporter. It now uses
pilot/baseline/packet_instructions.v0.1.md, copied byte-for-byte from the existing
frozen instructions. No frozen output was edited and no expected hash was weakened.

Focused tests: **25 passed**. Full suite: **89 passed, 3 skipped** (Qiskit/PyYAML
absent in palqo). Separate existing htp-static optional suite: **5 passed**.
Dataset validation/summary: **14 valid DRAFT cases**. Existing workflow audit with
`--packets pilot/packets-v0.1`: all mechanical checks pass, including regenerated
packet equality, private-field exclusion, dummy collection/evaluation/comparison
and malformed-response rejection without repair. No scientific predictions or
scores produced; no model calls, installation or quantum benchmark execution.

Exact command arrays, raw outputs and before/after artifact checks:
[N-004 validation record](../artifacts/n004_packet_regeneration/README.md).
