# N-004 packet regeneration repair validation

Date: 2026-09-20. Engineering repair only; no scientific baseline or model calls.

The exporter previously copied mutable pilot/baseline/README.md, so coordinator
history changed the generated instructions and manifest. It now reads the dedicated
pilot/baseline/packet_instructions.v0.1.md. That new source preserves the exact bytes
of pilot/packets-v0.1/baseline/INSTRUCTIONS.md; the frozen packet was not edited.
The source's historical wording is intentional, not current run authorization.

- [Before-fix regressions](before_fix_pytest.txt): three failures (the existing
  byte-identity test plus modified/missing-README variants), two deselected.
- [Focused tests](focused_pytest.txt): 25 passed.
- [Full tests](pytest_core.txt): 89 passed, 3 skipped for absent Qiskit/PyYAML in palqo.
- [Optional tests](pytest_optional.txt): 5 passed in the existing htp-static environment.
- [Dataset validation](dataset_validation.txt): 14 structurally valid DRAFT cases.
- [Dataset summary](dataset_summary.json): unchanged scientific counts/maturity.
- [Blind workflow audit](workflow_audit.json): all mechanical checks pass using
  temporary dummy responses, zero model calls and no scores reported. All 99 fresh
  packet files match the frozen snapshot; malformed responses are not repaired.
- [Preservation and links](preservation.json): protected file and manifest checks.

[commands.json](commands.json) records exact post-fix argv, environment override,
exit codes and logs. The before-fix command was the same palqo Python with
PYTHONDONTWRITEBYTECODE=1, followed by:

```text
-m pytest -q -p no:cacheprovider tests/test_pilot_v01.py -k 'regeneration or independent'
```

The two new test cases generate packets without frozen packets or experiment
directories in their source checkout, ruling out a runtime shortcut that simply
copies previously generated output. The README is deliberately overwritten with
a private sentinel or deleted in the temporary fixture, never in this repository.

No scientific label, schema, evaluator semantics or frozen experiment is changed.
Case-specific plan correctness and prospective protocol implementation remain open.
