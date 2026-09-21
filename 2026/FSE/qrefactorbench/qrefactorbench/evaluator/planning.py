"""Structured plan checks; contract membership is not semantic conformity."""

from collections.abc import Callable
from typing import Any

from . import Check
from .. import PHASE1_PREDICTION_VERSION

PlanVerifier = Callable[[dict[str, Any], dict[str, Any]], Check]


def evaluate_plan(case: dict[str, Any], prediction: dict[str, Any],
                  verifier: PlanVerifier | None = None) -> dict[str, Any]:
    plan = prediction.get("plan")
    phase1 = prediction.get("schema_version") == PHASE1_PREDICTION_VERSION
    if (prediction["decision"] != "QUANTUMIZE" and not phase1) or plan is None:
        return {"computational_intent_correct": None, "migration_family_correct": None,
                "contract_membership": None, "admissible_plan": None,
                "reason": "No quantumization plan to evaluate"}
    intent = case.get("computational_intent")
    intent_correct = plan["computational_intent_id"] == intent["id"] if intent and not phase1 else None
    family_correct = plan["migration_family"] == case["migration_family"] if case["migration_family"] else None
    contracts = case.get("admissible_migration_contracts", [])
    contract = next((c for c in contracts if c["contract_id"] == plan["contract_id"]), None)
    membership = (contract is not None and plan["quantum_algorithm_family"] in contract["algorithm_families"]) if contracts else None
    if membership is False or intent_correct is False or family_correct is False:
        conformity = Check(False, "Structured plan contradicts the declared admissible set or task")
    elif membership is not True:
        conformity = Check(None, "No annotated admissible contract set")
    elif intent_correct is None or family_correct is None:
        conformity = Check(None, "Intent requires human semantic review, or task annotation is missing")
    elif verifier is None:
        conformity = Check(None, "Contract selected; conformity requires a trusted contract verifier")
    else:
        try:
            conformity = verifier(contract, plan)
            if not isinstance(conformity, Check) or (conformity.passed is not None and type(conformity.passed) is not bool):
                raise TypeError("Verifier must return Check(bool | None, reason)")
        except Exception as exc:
            conformity = Check(None, f"Contract verifier error: {type(exc).__name__}: {exc}")
    return {"computational_intent_correct": intent_correct, "migration_family_correct": family_correct,
            "contract_membership": membership, "admissible_plan": conformity.passed,
            "reason": conformity.reason}
