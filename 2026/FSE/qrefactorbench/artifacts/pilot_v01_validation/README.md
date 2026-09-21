# pilot-v0.1 validation — 2026-09-20

Run from the repository root, reusing installed environments. No dependencies
were installed. All commands below exited 0; raw stdout is retained here.

```bash
/home/audrey/miniconda3/envs/palqo/bin/python scripts/prepare_pilot.py prepare --output pilot/packets-v0.1
# packet-export.json; 10 cases, four roles, zero model calls. Output now exists;
# repeat generation into a NEW directory, not this preserved snapshot.
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q tests/test_pilot_v01.py tests/test_pilot.py
# pytest-focused.txt: 23 passed in 1.96s
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q
# pytest-core.txt: 87 passed, 3 skipped in 3.23s (Qiskit/PyYAML unavailable here)
/home/audrey/miniconda3/envs/htp-static/bin/python -m pytest -q tests/test_optional.py
# pytest-optional.txt: 5 passed in 0.89s
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench validate cases/pilot --json
# pilot-validation.json: valid=true, case_count=10; expected DRAFT warnings
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench validate cases/
# dataset-validation.txt: VALID: 14; 14 DRAFT warnings
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench summarize cases/ --json
# dataset-summary.json: 14 DRAFT, 8 positive, 5 hard_negative, 1 negative
/home/audrey/miniconda3/envs/palqo/bin/python pilot/annotation_assist/verify_workflow.py --packets pilot/packets-v0.1
# workflow.json: export/collect/schema/evaluate/comparison checks PASS
```

The workflow script expects exit 2 from evaluation without --allow-draft and from
malformed-response collection; both rejection checks pass. All fixtures are temporary
and independent of scientific proposals. No real baseline response or score exists.
The private-sentinel export regression tests run against the revised public inputs.

protected-before.json records pre-edit hashes of original packets and protected
program/data/configuration files; preservation.json records post-edit verification.
The original/revised task manifests and exact diff are in
../../pilot/revisions/pilot-v0.1/. Licensing and scientific validity are not inferred.
