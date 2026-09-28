# Actual post-run validation — 2026-09-20

All commands ran from the repository root after all ten model invocations finished.
Existing environments were reused; no dependencies were installed. All commands
below exited 0. Model outputs were not fed back for repair.

```bash
/home/audrey/miniconda3/envs/palqo/bin/python scripts/prepare_pilot.py collect --responses pilot/baseline-v0.1/restricted-codex/parsed --output pilot/baseline-v0.1/restricted-codex/predictions.json
# collection.json: prediction_count=10, repairs=0; existing schema/path/span checks pass
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench evaluate cases/pilot pilot/baseline-v0.1/restricted-codex/predictions.json --allow-draft --json
# ../evaluation.DRAFT_REFERENCE.json: ten selected cases, demonstration_only=true
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q
# pytest-core.txt: 87 passed, 3 skipped in 3.20s (Qiskit/PyYAML absent here)
/home/audrey/miniconda3/envs/htp-static/bin/python -m pytest -q tests/test_optional.py
# pytest-optional.txt: 5 passed in 0.95s
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench validate cases/
# dataset-validation.txt: VALID: 14; 14 expected DRAFT warnings
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench summarize cases/ --json
# dataset-summary.json: 14 DRAFT; 8 positive, 5 hard_negative, 1 negative
```

These output files preserve stdout; the evaluator was not modified. Collector output
already exists, so a repeated collector command must use a new destination instead
of overwriting it. Evaluation/test commands do not invoke the model.

benchmark-preservation.json compares 308 file hashes with ../benchmark-before.json.
Sources, scientific annotations, schemas, evaluator, existing tests, both packet
versions and original baseline materials are unchanged. Project handoff documentation
and this new experiment-result directory are outside that protected set.

The complete event/raw/hash audit is ../metadata/run-audit.json. It establishes
artifact/mechanical properties, not scientific label correctness, calibrated model
confidence, quantum advantage or end-to-end semantic preservation.
