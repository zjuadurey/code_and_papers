"""Small read-only CLI; commands never execute case or generated Python files."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from . import RESULT_SCHEMA_VERSION
from .evaluator import ratio
from .evaluator.decision import evaluate_decisions
from .evaluator.pipeline import evaluate_static, prediction_errors
from .evaluator.recognition import aggregate_recognition
from .loader import DataError, load_document
from .reproducibility import manifest
from .validator import ValidationReport, validate_dataset


def summarize(report: ValidationReport) -> dict[str, Any]:
    fields = ("migration_family", "case_type", "context_level", "difficulty", "annotation_status",
              "structural_eligibility", "practical_suitability", "benchmark_supported")
    result = report.to_dict()
    result["counts"] = {
        field: dict(sorted(Counter(
            "unknown" if case[field] is None else str(case[field]).lower() if isinstance(case[field], bool) else case[field]
            for _, case in report.cases).items()))
        for field in fields
    }
    return result


def evaluate(report: ValidationReport, predictions_path: Path, allow_draft: bool,
             case_ids: set[str] | None = None) -> dict[str, Any]:
    if not report.valid:
        raise DataError("Cannot evaluate an invalid dataset")
    population = [(p, c) for p, c in report.cases if case_ids is None or c["case_id"] in case_ids]
    if case_ids is not None and case_ids - {c["case_id"] for _, c in population}:
        raise DataError("Requested case IDs are absent from dataset")
    selected = [(p, c) for p, c in population if allow_draft or c["annotation_status"] != "DRAFT"]
    excluded = [c["case_id"] for _, c in population if not allow_draft and c["annotation_status"] == "DRAFT"]
    if not selected:
        raise DataError("No eligible cases; DRAFT scoring requires explicit --allow-draft for demonstration")
    raw = load_document(predictions_path)
    if not isinstance(raw, list):
        raise DataError("Predictions document must be a JSON/YAML array")
    indexed: dict[str, Any] = {}
    for prediction in raw:
        if not isinstance(prediction, dict) or not isinstance(prediction.get("case_id"), str):
            raise DataError("Each prediction requires a string case_id")
        case_id = prediction["case_id"]
        if case_id in indexed:
            raise DataError(f"Duplicate prediction case_id: {case_id}")
        indexed[case_id] = prediction
    expected_ids = {c["case_id"] for _, c in selected}
    missing, extra = expected_ids - indexed.keys(), indexed.keys() - expected_ids
    if missing or extra:
        raise DataError(f"Prediction coverage mismatch; missing={sorted(missing)}, extra={sorted(extra)}")
    results = []
    for path, case in selected:
        prediction = indexed[case["case_id"]]
        errors = prediction_errors(prediction, case, path.parent)
        if errors:
            raise DataError(f"{case['case_id']}: {'; '.join(errors)}")
        results.append(evaluate_static(case, prediction))
    tp = sum(r["candidate"]["exact"]["true_positives"] for r in results)
    pred_n = sum(r["candidate"]["exact"]["predicted"] for r in results)
    gold_n = sum(r["candidate"]["exact"]["reference"] for r in results)
    positive = [r for r, (_, c) in zip(results, selected) if c["expected_decision"] == "QUANTUMIZE"]
    end_counts = {"passed": sum(r["end_to_end_quantumization_success"] is True for r in positive),
                  "failed": sum(r["end_to_end_quantumization_success"] is False for r in positive),
                  "unknown": sum(r["end_to_end_quantumization_success"] is None for r in positive),
                  "applicable": len(positive)}
    return {"result_schema_version": RESULT_SCHEMA_VERSION, "protocol": "static-phase1-v0-provisional",
            "demonstration_only": any(c["annotation_status"] == "DRAFT" for _, c in selected),
            "excluded_draft_case_ids": excluded, "execution_mode": "static_no_code_execution",
            "selected_case_ids": [c["case_id"] for _, c in selected],
            "not_selected_case_ids": [c["case_id"] for _, c in report.cases
                                      if case_ids is not None and c["case_id"] not in case_ids],
            "results": results,
            "aggregate": {"candidate_exact_micro": {"true_positives": tp, "predicted": pred_n,
                                                     "reference": gold_n, "precision": ratio(tp, pred_n),
                                                     "recall": ratio(tp, gold_n), "f1": ratio(2 * tp, pred_n + gold_n)},
                          "decision": evaluate_decisions([(c["expected_decision"], indexed[c["case_id"]]["decision"]) for _, c in selected]),
                          "recognition": aggregate_recognition(results),
                          "end_to_end_quantumization_success": end_counts},
            "reproducibility": manifest(selected, predictions_path)}


def compare_annotations(left: Any, right: Any) -> dict[str, Any]:
    """Record field differences; never infer which annotator is correct."""
    if not isinstance(left, dict) or not isinstance(right, dict) or left.get("case_id") != right.get("case_id") or not left.get("case_id"):
        raise DataError("Annotation comparison requires matching case IDs")
    fields = ("candidate_regions", "structural_eligibility", "practical_suitability", "benchmark_supported",
              "expected_decision", "case_type", "migration_family", "computational_intent",
              "admissible_migration_contracts", "semantic_oracle", "resource_expectations", "negative_reason",
              "contract_applicability", "assumptions", "uncertainty", "annotation_rationale")
    return {"case_id": left["case_id"], "comparison": "field-wise diagnostics; no agreement statistic or adjudication",
            "differences": {field: {"left_present": field in left, "right_present": field in right,
                                    "left": left.get(field), "right": right.get(field)}
                            for field in fields if left.get(field) != right.get(field) or (field in left) != (field in right)}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="qrefactorbench")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "summarize", "evaluate"):
        command = sub.add_parser(name)
        command.add_argument("dataset", type=Path)
        command.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
        if name == "evaluate":
            command.add_argument("predictions", type=Path)
            command.add_argument("--allow-draft", action="store_true")
            command.add_argument("--case-id", action="append", help="Explicit case selection; repeat for multiple IDs")
    compare = sub.add_parser("compare-annotations")
    compare.add_argument("left", type=Path)
    compare.add_argument("right", type=Path)
    compare.add_argument("--json", action="store_true")
    resources = sub.add_parser("estimate-resources", help="Analyze a proposed quantum application and controller-owned costs")
    resources.add_argument("request", type=Path)
    resources.add_argument("--context", type=Path, required=True)
    resources.add_argument("--qdk-python", default=sys.executable)
    resources.add_argument("--timeout", type=float, default=60)
    resources.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "estimate-resources":
            from .resource_workflow import analyze_resources
            output = analyze_resources(load_document(args.request), load_document(args.context),
                                       python=args.qdk_python, timeout=args.timeout)
            code = 0 if all(r["status"] == "ok" for r in output["estimation_runs"]) else 2
        elif args.command == "compare-annotations":
            output = compare_annotations(load_document(args.left), load_document(args.right))
            code = 0
        else:
            report = validate_dataset(args.dataset)
            code = 0 if report.valid else 1
            if args.command == "evaluate" and report.valid:
                output = evaluate(report, args.predictions, args.allow_draft,
                                  set(args.case_id) if args.case_id else None)
            elif args.command == "summarize":
                output = summarize(report)
            else:
                output = report.to_dict()
        if args.json or args.command in {"evaluate", "compare-annotations", "estimate-resources"}:
            print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))
        else:
            print(f"{'VALID' if output['valid'] else 'INVALID'}: {output['case_count']} structurally valid cases")
            for issue in output["issues"]:
                print(f"{issue['severity']}: {issue['path']}: {issue['message']}")
            for field, counts in output.get("counts", {}).items():
                print(f"{field}: {json.dumps(counts, sort_keys=True)}")
        return code
    except (DataError, OSError, ValueError) as exc:
        if args.json:
            print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
