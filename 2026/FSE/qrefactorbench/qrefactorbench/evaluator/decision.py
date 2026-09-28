"""Decision counts with explicit denominators and abstention performance."""

from typing import Any

from . import ratio


def evaluate_decisions(pairs: list[tuple[str | None, str]]) -> dict[str, Any]:
    allowed = {"QUANTUMIZE", "REMAIN_CLASSICAL"}
    if any(g not in allowed | {None} or p not in allowed for g, p in pairs):
        raise ValueError("Unknown decision label")
    scored = [(g, p) for g, p in pairs if g is not None]
    tp = sum(g == p == "QUANTUMIZE" for g, p in scored)
    tn = sum(g == p == "REMAIN_CLASSICAL" for g, p in scored)
    fp = sum(g == "REMAIN_CLASSICAL" and p == "QUANTUMIZE" for g, p in scored)
    fn = sum(g == "QUANTUMIZE" and p == "REMAIN_CLASSICAL" for g, p in scored)
    return {"counts": {"true_quantumize": tp, "true_remain_classical": tn,
                       "false_quantumize": fp, "missed_quantumize": fn,
                       "scored": len(scored), "unscored": len(pairs) - len(scored)},
            "overall_decision_accuracy": ratio(tp + tn, len(scored)),
            "quantumize_precision": ratio(tp, tp + fp),
            "quantumize_recall": ratio(tp, tp + fn),
            "remain_classical_accuracy": ratio(tn, tn + fp),
            "false_quantumization_rate": ratio(fp, tn + fp)}

