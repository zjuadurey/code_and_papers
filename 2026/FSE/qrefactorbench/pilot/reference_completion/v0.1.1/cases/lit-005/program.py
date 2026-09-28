"""Inspect feature choices or complete them under named requirements."""
import json
import sys
from common import bits, fields, names
from kernel import complete, conforms


def review(request):
    fields(request, ("features", "rules", "locked", "current", "mode"))
    features = names(request["features"])
    current = bits(request["current"], len(features))
    if request["mode"] not in ("inspect", "complete") or not isinstance(request["rules"], list):
        raise ValueError("invalid mode or rules")
    rule_ids, clauses = [], []
    for rule in request["rules"]:
        fields(rule, ("id", "any"))
        rule_ids.append(rule["id"])
        if not isinstance(rule["any"], list) or len(rule["any"]) != 3:
            raise ValueError("three alternatives per rule required")
        clause = []
        for literal in rule["any"]:
            fields(literal, ("feature", "enabled"))
            if literal["feature"] not in features or type(literal["enabled"]) is not bool:
                raise ValueError("invalid requirement")
            clause.append((features.index(literal["feature"]), literal["enabled"]))
        clauses.append(clause)
    names(rule_ids)
    if not isinstance(request["locked"], dict) or any(k not in features or type(v) is not bool for k, v in request["locked"].items()):
        raise ValueError("invalid locked choices")
    locked = {features.index(k): v for k, v in request["locked"].items()}
    failed = [key for key, clause in zip(rule_ids, clauses) if not any(current[i] == v for i, v in clause)]
    locked_failures = [name for i, name in enumerate(features) if i in locked and current[i] != locked[i]]
    result = {"failed_rules": failed, "locked_failures": locked_failures,
              "status": "inspected", "proposal": None, "changes": []}
    if request["mode"] == "inspect":
        return result
    if conforms(current, clauses, locked):
        chosen, status = current, "retained"
    else:
        chosen = complete(len(features), clauses, locked)
        status = "completed" if chosen is not None else "unavailable"
    result["status"] = status
    if chosen is not None:
        result["proposal"] = dict(zip(features, chosen))
        result["changes"] = [name for name, a, b in zip(features, current, chosen) if a != b]
    return result


if __name__ == "__main__":
    print(json.dumps(review(json.load(sys.stdin)), indent=2))
