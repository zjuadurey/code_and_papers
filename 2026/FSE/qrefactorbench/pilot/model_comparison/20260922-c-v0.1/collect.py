"""Offline validation and frozen-reference diagnostics; never repairs model output."""
from __future__ import annotations

from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from qrefactorbench.loader import DataError, load_document
from qrefactorbench.schema import schema_errors

SPEC = importlib.util.spec_from_file_location("pending_evaluation", ROOT / "pilot/provisional_labels/v0.1/evaluate.py")
evaluation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluation)


def save(path: Path, data: Any) -> None:
    with path.open("x", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def main() -> None:
    protocol = load_document(HERE / "protocol.json")
    _, references = evaluation.references("C")
    refs = {ref["mother_case_id"]: ref for ref in references}
    summary: dict[str, Any] = {
        "protocol": "restricted-codex-C-20260922", "condition": "C", "review_status": "PENDING",
        "mother_cases": 10, "planned_case_calls": 20, "models": {},
        "reference_labels_sha256": protocol["reference_labels_sha256"],
        "notes": ["No output repair or scientific retry.", "One sample/model/case; no stable ranking claim.",
                  "Pending AI references; control labels unresolved; plan presence is not correctness."],
    }
    for model in protocol["models"]:
        rows, predictions, validation = [], [], []
        usage_total: Counter = Counter()
        for entry in protocol["entries"]:
            folder = HERE / "runs" / model / entry["case_id"]
            ref = refs[entry["case_id"]]
            metadata = load_document(folder / "metadata.json") if (folder / "metadata.json").exists() else {}
            errors = []
            if metadata.get("exit_code") != 0 or not metadata.get("turn_completed"):
                errors.append("CLI turn did not complete successfully")
            if metadata.get("tool_items"):
                errors.append("Unexpected tool event")
            if metadata.get("errors"):
                errors.append("CLI error/failure event")
            response = None
            try:
                response = load_document(folder / "response.txt")
                shape_errors = schema_errors(response, "prediction")
                errors.extend(shape_errors)
                if not shape_errors:
                    if response.get("schema_version") != "0.2.0":
                        errors.append("Not the Phase-1 schema version")
                    if response["case_id"] != ref["case_id"]:
                        errors.append("Wrong prediction case_id")
                    errors.extend(evaluation.region_errors(response["candidate_regions"], ref["sources"]))
                    if response["plan"] and response["migration_family"] is not None and response["plan"]["migration_family"] != response["migration_family"]:
                        errors.append("Top-level and plan families differ")
            except DataError as exc:
                errors.append(str(exc))
            valid = not errors
            if valid:
                predictions.append(response)
            validation.append({"mother_case_id": entry["case_id"], "valid": valid, "errors": errors})
            for usage in metadata.get("usage", []):
                usage_total.update({key: value for key, value in usage.items() if type(value) is int})
            rows.append({
                "mother_case_id": entry["case_id"], "valid": valid,
                "exit_code": metadata.get("exit_code"), "elapsed_seconds": metadata.get("elapsed_seconds"),
                "tool_events": len(metadata.get("tool_items", [])),
                "startup_warning_items": len(metadata.get("startup_warnings", [])),
                "structural": response.get("structural_eligibility") if valid else None,
                "practical": response.get("practical_suitability") if valid else None,
                "supported": response.get("benchmark_supported") if valid else None,
                "family": response.get("migration_family") if valid else None,
                "decision": response.get("decision") if valid else None,
                "plan_present": response.get("plan") is not None if valid else None,
                "regions": response.get("candidate_regions") if valid else None,
            })
        save(HERE / f"validation.{model}.json", validation)
        model_summary = {
            "valid_responses": len(predictions), "population": 10,
            "elapsed_seconds_sum": round(sum(row["elapsed_seconds"] or 0 for row in rows), 3),
            "usage": dict(usage_total), "rows": rows,
            "full_population_evaluation_available": len(predictions) == 10,
        }
        if len(predictions) == 10:
            save(HERE / f"predictions.{model}.json", predictions)
            report = evaluation.evaluate(predictions, "C", model + "/medium/codex-0.155.1")
            save(HERE / f"evaluation.{model}.json", report)
            positive_rows = [row for row in report["results"] if row["plan_required_by_reference"]]
            model_summary.update(
                aggregate=report["aggregate"], plan_coverage=report["plan_coverage"],
                decision_agreement=report["decision_agreement"],
                where_reference_positive={
                    "population": 7,
                    "exact_region_set_matches": sum(row["where_diagnostic"]["candidate_correct"] for row in positive_rows),
                    "mean_line_iou": sum(row["where_diagnostic"]["line_overlap"]["iou"] or 0 for row in positive_rows)/7,
                    "note": "Descriptive overlap against draft anchors, not semantic localization correctness.",
                },
            )
        summary["models"][model] = model_summary
    before = load_document(HERE / "protected_before.json")
    changed = [name for name, digest in before.items() if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest]
    summary["integrity"] = {"protected_files": len(before), "changed": changed}
    if changed:
        raise DataError(f"Protected artifacts changed: {changed}")
    save(HERE / "SUMMARY.json", summary)
    print(json.dumps({model: {k: v for k, v in data.items() if k not in ("rows", "aggregate")}
                      for model, data in summary["models"].items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
