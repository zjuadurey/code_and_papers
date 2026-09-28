"""Phase-1 label diagnostics; free-text intent and applicability require humans."""

from typing import Any

from . import ratio

LABELS = ("structural_eligibility", "practical_suitability", "benchmark_supported", "migration_family")


def evaluate_recognition(case: dict[str, Any], prediction: dict[str, Any]) -> dict[str, Any]:
    """Preserve unknowns, and retain observations needed for subsequent human coding."""
    result: dict[str, Any] = {}
    for label in LABELS:
        expected, observed = case.get(label), prediction.get(label)
        comparable = expected is not None and observed is not None
        result[label] = {"reference": expected, "predicted": observed,
                         "correct": expected == observed if comparable else None,
                         "reason": "Structured comparison" if comparable else "Unknown/missing reference or prediction"}
    result["intent"] = {"reference": case.get("computational_intent"),
                        "predicted": prediction.get("computational_intent"),
                        "correct": None, "reason": "Human semantic coding required; no private-ID/text equality"}
    result["contract_applicability"] = {"predicted": prediction.get("contract_applicability"),
                                        "correct": None, "reason": "Requires human contract review"}
    return result


def aggregate_recognition(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Report coverage alongside conditional accuracy; do not turn null into false."""
    aggregates = {}
    for label in LABELS:
        cells = [r["recognition"][label] for r in results]
        correct = sum(c["correct"] is True for c in cells)
        incorrect = sum(c["correct"] is False for c in cells)
        aggregates[label] = {
            "correct": correct, "incorrect": incorrect,
            "unresolved": len(cells) - correct - incorrect, "total": len(cells),
            "reference_known": sum(c["reference"] is not None for c in cells),
            "prediction_known": sum(c["predicted"] is not None for c in cells),
            "accuracy_on_resolved_pairs": ratio(correct, correct + incorrect),
        }
    return aggregates
