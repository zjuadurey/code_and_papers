# Blind input and evaluation workflow audit

2026-09-19 · Mechanical readiness only; no scientific baseline was run.

**The existing pipeline is mechanically usable.** The scientific interpretation
of its inputs and outputs still needs review. All checks used existing environments,
temporary dummy responses and unchanged production code. See the reproducible
[audit script](verify_workflow.py) and [actual output](validation/workflow.json).

## Checks performed

| Check | Actual result / limit |
| --- | --- |
| Packet inventory, IDs and file hashes | PASS for A, B, adjudication and baseline; exactly pilot-001 through pilot-010. |
| Fresh export using existing prepare CLI | PASS; byte-identical to existing packets in a temporary directory; existing packets untouched. |
| Independent forms | PASS; core judgment fields, candidate regions and annotator IDs remain null, completion_status UNFILLED. |
| Private annotation artifacts | No case.json, curator notes, seed manifest or classical test answers in annotator case directories. Rendered prompts contain no populated case-specific expected_decision, case_type, reference_plan, annotation_rationale or admissible_migration_contracts fields. |
| Public inputs | Only case_id, title, software_contract, input_domain and execution_assumptions in public task JSON, plus the source and common contract menu. This is a field-level check, not proof of absence of semantic cueing. |
| Separate scientific labels | true / false / null accepted for structural_eligibility, practical_suitability and benchmark_supported. Literal strings YES / NO / UNCERTAIN are not schema values. |
| Explicit abstention | REMAIN_CLASSICAL and an empty candidate list are accepted. A null structural/practical label can coexist with this decision. |
| Uncertainty limits | decision has no UNCERTAIN value; candidate_regions cannot be null in model predictions. Do not interpret [] as proof that a model confidently found no candidate. Human forms permit null. |
| Collector → schema → evaluator | PASS for ten temporary fixtures, including both decisions and null labels; all IDs and raw field values preserved, repairs=0. |
| DRAFT safeguard | Evaluation without --allow-draft rejected with exit 2; explicit --allow-draft succeeds with demonstration_only=true. |
| Malformed response | Markdown-fenced dummy response rejected with exit 2; no repaired prediction/output created. |
| Annotation comparison CLI | PASS on two blank forms. Empty differences are NOT annotator agreement. |
| Fresh proposals | All ten pre-audit proposal hashes unchanged after workflow inspection. |

The shared schemas describe label fields and conditional validity rules, and the
common contract menu has DRAFT metadata. Those are generic format/protocol facts,
not populated answers to individual cases. No obvious private reference answer
was found in baseline inputs. This audit cannot certify independence from prior
exposure or remove the following public cues.

## Scientific caveats, not mechanically repaired

- Public titles/software contracts describe intent across all ten cases. In
  pilot-005 the assumptions explicitly direct attention to subset enumeration;
  pilot-002/008 explicitly deny a hidden search query or optimization objective.
  Researchers must decide whether this specification assistance is part of the
  intended task. It could weaken WHERE/WHAT discovery even without private-file leakage.
- pilot-009's public integer-name declaration conflicts with the string-name
  validator. The current validators check artifacts/schema, not consistency of
  natural-language specifications; a passing validation command does not resolve it.
- The pipeline preserves separate label judgments and unknown-result coverage.
  Free-text intent/applicability need human coding. A supplied contract ID establishes
  membership only; conformity and semantic correctness need separate evidence.
- Family matching against one case-level family may not capture multiple valid
  strategies (notably pilot-005/007). Exact localization and provisional overlap
  diagnostics do not select a final scientific boundary policy or cutoff.
- Suitability null, uncertainty-driven abstention and unknown localization must not
  be silently converted to scientific NO labels. Scoring policy remains open.
- Results against DRAFT references remain demonstrations, even if the CLI succeeds.
  No dummy score or response is retained as a pilot observation.

## Reproduce the mechanical checks

Run from the repository root, using the existing environment:

```bash
/home/audrey/miniconda3/envs/palqo/bin/python pilot/annotation_assist/verify_workflow.py
```

The script invokes the documented prepare, collect, evaluate and compare-annotations
commands in temporary directories. It tests both successful and expected failure
paths, discards evaluator scores and deletes all dummy responses automatically.
It makes zero model/API calls. Its fixture values are deliberately arbitrary,
not generated from the ten analysis proposals.

## Later, for actual researcher-authorized baseline collection

Use the existing [baseline protocol](../baseline/README.md) and only the approved
baseline packet. Keep this directory, private case files and human annotations
away from the model/operator. Preserve model configuration, raw response and prompt
hashes as the existing protocol requires. Do not add feedback, tools or repair loops.

After responses have been obtained externally, the existing commands are:

```bash
python scripts/prepare_pilot.py collect --responses /path/to/run/responses --output /path/to/run/predictions.json
python -m qrefactorbench evaluate cases/pilot /path/to/run/predictions.json --allow-draft --json
python -m qrefactorbench compare-annotations /path/to/A/annotation.json /path/to/B/annotation.json --json
```

Each response filename is its pilot case ID plus .json; its contents must be a
single schema-compatible JSON object. Collection yields the prediction array.
The collector requires all ten responses. For an intentional subset, follow the
existing protocol: create an array of only the unchanged valid responses and pass
explicit --case-id options to evaluate. Report omitted cases and failures; do not
treat a subset diagnostic as a full ten-case result.

All ten original cases remain DRAFT. These commands are ready for a mechanics
demonstration, not an assertion that scientific scoring has been approved.
Human comparison should use completed, independently submitted forms; adjudication
is never automatic. Use the existing [failure-analysis form](../failure_analysis/observation_template.json)
to open-code real observations after collection, keeping model failures separate
from ambiguous specifications, missing reference evidence and alternative valid plans.
