# Actual diagnostic validation — 2026-09-20

All model responses were fixed before these commands ran. No model was invoked by validation and no validation output was returned to a prediction process. Existing environments were reused without installation. No reference-accuracy evaluation was run.

Working directory: `/home/audrey/code_and_papers/2026/FSE/qrefactorbench`.

```bash
/home/audrey/miniconda3/envs/palqo/bin/python scripts/prepare_pilot.py collect --responses /home/audrey/code_and_papers/2026/FSE/qrefactorbench/pilot/baseline-v0.1/conditional-plan-diagnostic/parsed --output /home/audrey/code_and_papers/2026/FSE/qrefactorbench/pilot/baseline-v0.1/conditional-plan-diagnostic/predictions.json
# exit 0: 10 predictions, 0 repairs; existing schema/path/span checks
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q
# exit 0: 87 passed, 3 skipped in 3.61s
/home/audrey/miniconda3/envs/htp-static/bin/python -m pytest -q tests/test_optional.py
# exit 0: 5 passed in 0.96s
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench validate cases/
# exit 0: 14 structurally valid cases; 14 expected DRAFT warnings
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench summarize cases/ --json
# exit 0: 14 cases, all DRAFT
```

The three core skips are missing Qiskit/PyYAML in the core environment; the separate optional-suite environment covers those features. Passing these tests validates existing infrastructure, not scientific plans. The collector loads cases for mechanical validation; it does not compute agreement with reference labels. The standard test suite uses its existing fixtures; none is used for scientific interpretation here.

[commands.json](commands.json) preserves exact argument lists and exit codes. Named `.stdout`/`.stderr` files preserve complete outputs. The collector output exists and must not be overwritten on repetition.

[protected-before.json](protected-before.json) fingerprints 557 pre-existing files before experiment creation. [preservation.json](preservation.json) confirms all 557 were unchanged immediately after the run/tests, including 122 original-baseline files and 99 frozen packet files. [final-preservation.json](final-preservation.json) records the later six explicitly allowlisted project-memory updates while requiring every other protected file to remain unchanged. No case/program/schema/evaluator/label/original prediction changed.

[../metadata/run-audit.json](../metadata/run-audit.json) checks ten distinct threads, one turn/final response each, matching raw/event content, byte-identical raw/parsed copies, no tool items, and command identity with the original except temporary directory paths. Each stream contains only the original two startup warnings and one final message, plus thread/turn events. No operator or visible transport retry occurred; underlying provider internals remain unobservable.

Every diagnostic prompt equals its original frozen bytes plus two LF bytes plus the exact approved instruction. Per-case hashes and exact textual diffs are preserved; the original schemas are byte-identical. The [rubric lock](review-rubric-lock.json) records the initial descriptive rubric before output-content inspection. [final-checks.json](final-checks.json) records final schema, link, prompt-diff and evidence checks. No new scientific acceptance threshold or evaluator rule was introduced.

One initial final-audit assertion failed: it incorrectly required byte identity
between the exported packet schemas and source-package schema files. All four
already use different JSON serialization while their parsed JSON objects are
identical. The audit was corrected to require byte identity with the original
frozen packet and JSON-object identity with the unchanged package schemas. No
schema, prediction, evaluator, or scientific call was changed/repeated. The
existing collector and repository tests had already passed; this was an overly
strict diagnostic audit assertion, not a model/schema-validation failure.
