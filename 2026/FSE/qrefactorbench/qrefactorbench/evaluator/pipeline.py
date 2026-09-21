"""Static evaluation pipeline and explicit evidence-based strict aggregation."""

from pathlib import Path
from typing import Any

from ..loader import DataError, safe_path
from ..schema import schema_errors
from ..validator import region_errors
from . import Check, strict_conjunction
from .candidate import evaluate_candidates
from .execution import static_execution
from .planning import evaluate_plan
from .recognition import evaluate_recognition


def end_to_end_quantumization_success(expected_decision: str | None,
                                      components: dict[str, bool | None]) -> bool | None:
    """Strict v0.1 gate; absent keys are unknown, including quantum constraints."""
    if expected_decision != "QUANTUMIZE":
        return None
    required = ("candidate_correct", "decision_correct", "admissible_plan", "syntax_valid",
                "imports_valid", "execution_success", "interface_preserved", "semantic_oracle_pass",
                "quantum_constraints_pass", "resource_limits_pass")
    return strict_conjunction([components.get(name) for name in required])


def prediction_errors(prediction: Any, case: dict[str, Any], root: Path) -> list[str]:
    errors = schema_errors(prediction, "prediction")
    if errors:
        return errors
    if prediction["case_id"] != case["case_id"]:
        errors.append("Prediction case_id does not match case")
    errors += region_errors(prediction["candidate_regions"], case, root)
    files = prediction.get("generated_files", [])
    names = [file["path"] for file in files]
    if len(names) != len(set(names)):
        errors.append("Duplicate generated file path")
    for name in names:
        try:
            safe_path(root, name)
        except (DataError, OSError, ValueError) as exc:
            errors.append(str(exc))
    plan = prediction.get("plan")
    contract_ids = [c["contract_id"] for c in prediction.get("contract_applicability", [])]
    if len(contract_ids) != len(set(contract_ids)):
        errors.append("Duplicate contract applicability ID")
    if plan:
        for name in ("computational_intent_id", "migration_family"):
            if prediction.get(name) is not None and prediction[name] != plan[name]:
                errors.append(f"Prediction {name} contradicts its plan")
    return errors


def evaluate_static(case: dict[str, Any], prediction: dict[str, Any]) -> dict[str, Any]:
    candidates = evaluate_candidates(case["candidate_regions"], prediction["candidate_regions"])
    expected = case["expected_decision"]
    decision_correct = prediction["decision"] == expected if expected else None
    planning = evaluate_plan(case, prediction)
    execution = static_execution({f["path"]: f["content"] for f in prediction.get("generated_files", [])})
    missing = Check(None, "Not evaluated: requires trusted case-specific evidence").to_dict()
    components = {"candidate_correct": candidates["candidate_correct"], "decision_correct": decision_correct,
                  "admissible_plan": planning["admissible_plan"],
                  "syntax_valid": execution["syntax"]["passed"], "imports_valid": None,
                  "execution_success": None, "interface_preserved": None,
                  "semantic_oracle_pass": None, "quantum_constraints_pass": None, "resource_limits_pass": None}
    return {"case_id": case["case_id"], "annotation_status": case["annotation_status"],
            "prediction": prediction, "recognition": evaluate_recognition(case, prediction),
            "candidate": candidates, "decision_correct": decision_correct,
            "abstention_correct": decision_correct if expected == "REMAIN_CLASSICAL" else None,
            "planning": planning, "execution": execution, "semantics": missing.copy(),
            "quantum_constraints": missing.copy(), "resources": missing.copy(),
            "components": components,
            "end_to_end_quantumization_success": end_to_end_quantumization_success(expected, components)}
