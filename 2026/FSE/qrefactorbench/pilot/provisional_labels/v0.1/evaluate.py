"""Private provisional-reference diagnostics; no model calls or code execution."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from qrefactorbench.evaluator.candidate import evaluate_candidates
from qrefactorbench.evaluator.recognition import aggregate_recognition, evaluate_recognition
from qrefactorbench.loader import DataError, load_document
from qrefactorbench.schema import schema_errors


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packet_sources(path: Path) -> tuple[dict[str, Any], dict[str, str]]:
    """Read exactly the versioned public view; never import its Python modules."""
    public = path.read_text().split("\nPUBLIC TASK\n", 1)[1].split("\nSHARED DRAFT CONTRACTS\n", 1)[0]
    task = json.JSONDecoder().raw_decode(public)[0]
    sources = {}
    for name, body in re.findall(r"\nFILE ([^\n]+)\n(.*?)(?=\nFILE |\Z)", public, re.S):
        if name.endswith(".py"):
            lines = body.rstrip("\n").splitlines()
            if any(not line.startswith(f"{i}: ") for i, line in enumerate(lines, 1)):
                raise DataError(f"Invalid source numbering: {path.name}/{name}")
            sources[name] = "\n".join(line.split(": ", 1)[1] for line in lines) + "\n"
    return task, sources


def region_errors(regions: list[dict[str, Any]], sources: dict[str, str]) -> list[str]:
    errors = []
    for region in regions:
        name, start, end = region["file"], region["start_line"], region["end_line"]
        if name not in sources or not 1 <= start <= end <= len(sources[name].splitlines()):
            errors.append(f"Region outside supplied source: {region}")
            continue
        if region.get("function"):
            functions: dict[str, ast.AST] = {}

            def visit(node: ast.AST, prefix: str = "") -> None:
                for child in ast.iter_child_nodes(node):
                    scope = prefix
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        scope = f"{prefix}.{child.name}" if prefix else child.name
                        if not isinstance(child, ast.ClassDef):
                            functions[scope] = child
                    visit(child, scope)

            visit(ast.parse(sources[name]))
            function = functions.get(region["function"])
            if function is None or not function.lineno <= start <= end <= function.end_lineno:
                errors.append(f"Region does not belong to declared function: {region}")
    return errors


def references(condition: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if condition not in ("A", "B", "C"):
        raise DataError("Condition must be A, B or C")
    labels = load_document(HERE / "labels.json")
    provenance = load_document(HERE / "provenance.json")
    for relative, digest in provenance["evaluation_files_sha256"].items():
        if sha256(ROOT / relative) != digest:
            raise DataError(f"Versioned evaluation artifact changed: {relative}")
    manifest_path = ROOT / labels["input_manifest"]
    manifest = load_document(manifest_path)
    proposals = {case["mother_case_id"]: case for case in labels["cases"]}
    if len(proposals) != 10 or len(manifest["conditions"]) != 30:
        raise DataError("Expected ten mothers and thirty conditions")
    result = []
    seen = set()
    for entry in manifest["conditions"]:
        key = (entry["case_id"], entry["condition"])
        if key in seen:
            raise DataError(f"Duplicate manifest entry: {key}")
        seen.add(key)
        path = manifest_path.parent / entry["file"]
        if sha256(path) != entry["sha256"]:
            raise DataError(f"Public input changed: {path}")
        if entry["condition"] != condition:
            continue
        case = proposals[entry["case_id"]]
        task, sources = packet_sources(path)
        if task["case_id"] != entry["prediction_case_id"]:
            raise DataError("Manifest/public prediction ID mismatch")
        regions = case["core_regions" if condition == "A" else "context_regions"]
        errors = region_errors(regions, sources)
        if errors:
            raise DataError("; ".join(errors))
        result.append({
            **labels["shared_labels"],
            "case_id": task["case_id"], "mother_case_id": entry["case_id"],
            "structural_eligibility": case["structural_eligibility"],
            "migration_family": case["primary_family"],
            "candidate_regions": regions, "sources": sources,
            "input_sha256": entry["sha256"],
            "checks": case["core_checks"] + (case["context_checks"] if condition != "A" else []),
        })
    if seen != {(mother, c) for mother in proposals for c in "ABC"}:
        raise DataError("Manifest does not cover the exact mother/condition product")
    return labels, result


def evaluate(predictions: Any, condition: str, model_id: str) -> dict[str, Any]:
    labels, refs = references(condition)
    if not isinstance(predictions, list):
        raise DataError("Predictions must be an array, exactly ten for one condition")
    by_id = {}
    for prediction in predictions:
        errors = schema_errors(prediction, "prediction")
        if errors or prediction.get("schema_version") != "0.2.0":
            raise DataError(f"Invalid Phase-1 prediction: {errors}")
        case_id = prediction["case_id"]
        if case_id in by_id:
            raise DataError(f"Duplicate prediction ID: {case_id}")
        by_id[case_id] = prediction
    if set(by_id) != {ref["case_id"] for ref in refs}:
        raise DataError("Predictions must cover exactly the ten IDs of the selected condition; no silent dropping")
    results = []
    for ref in refs:
        prediction = by_id[ref["case_id"]]
        errors = region_errors(prediction["candidate_regions"], ref["sources"])
        plan = prediction["plan"]
        if plan and prediction["migration_family"] is not None and plan["migration_family"] != prediction["migration_family"]:
            errors.append("Plan family contradicts top-level family")
        if errors:
            raise DataError(f"{ref['case_id']}: {'; '.join(errors)}")
        recognition = evaluate_recognition(ref, prediction)
        # A reference family is illustrative, not the sole admissible formulation.
        family = recognition["migration_family"]
        if family["correct"] is False:
            family.update(correct=None, reason="Alternative supported family requires mapping review; not automatically incorrect")
        for name in ("intent", "contract_applicability"):
            recognition.pop(name)  # Reviewed using the explicit checklist below.
        required = ref["structural_eligibility"] is True
        results.append({
            "case_id": ref["case_id"], "mother_case_id": ref["mother_case_id"],
            "input_sha256": ref["input_sha256"], "prediction": prediction,
            "recognition": recognition,
            "where_diagnostic": evaluate_candidates(ref["candidate_regions"], prediction["candidate_regions"]),
            "decision_reference_agreement": prediction["decision"] == ref["expected_decision"],
            "plan_required_by_reference": required,
            "plan_present": plan is not None,
            "self_reported_yes_without_plan": prediction["structural_eligibility"] is True and plan is None,
            "manual_review": [{**item, "judgment": None, "response_evidence": None,
                               "reviewer": None} for item in ref["checks"]],
            "plan_correct": None, "task_pass": None,
        })
    aggregate = aggregate_recognition(results)
    # Existing names contain 'correct'; expose only reference-agreement terminology here.
    for field, counts in aggregate.items():
        counts["matched"] = counts.pop("correct")
        counts["mismatched"] = counts.pop("incorrect")
        counts["agreement_on_resolved_pairs"] = counts.pop("accuracy_on_resolved_pairs")
        known = counts["reference_known"]
        counts["matched_over_known_references"] = counts["matched"] / known if known else None
    for result in results:
        for cell in result["recognition"].values():
            cell["reference_agreement"] = cell.pop("correct")
    required_rows = [row for row in results if row["plan_required_by_reference"]]
    return {
        "protocol": "provisional-labels-v0.1", "review_status": "PENDING",
        "demonstration_only": True, "model_id": model_id, "condition": condition,
        "mother_cases": 10, "labels_sha256": sha256(HERE / "labels.json"),
        "provenance_sha256": sha256(HERE / "provenance.json"),
        "aggregate": aggregate,
        "plan_coverage": {"reference_required": len(required_rows),
                          "present": sum(row["plan_present"] for row in required_rows)},
        "decision_agreement": {"matched": sum(row["decision_reference_agreement"] for row in results), "total": 10},
        "warnings": [
            "AI-proposed pending labels; reference agreement is not validated correctness.",
            "All known structural references are YES; negative-class discrimination is not measured.",
            "Three structural references and all practical references are unresolved, not gold null labels.",
            "Decision/support references are constant and cannot alone distinguish capability.",
            "Report matched/mismatched/unresolved and coverage together; do not rank by resolved-pair agreement alone.",
            "Primary-family agreement and plan presence do not establish a correct mapping.",
            "WHERE exact/overlap are diagnostics; alternative boundaries require review.",
            "A/B/C share ten mothers; never pool as thirty independent problems. No overall task pass score.",
        ],
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--condition", choices=list("ABC"), required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = evaluate(load_document(args.predictions), args.condition, args.model_id)
        result["predictions_sha256"] = sha256(args.predictions)
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    except (DataError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
