"""Review independent transfer windows against the eligible item catalogue."""
import json
import sys
from common import fields, integer, names
from kernel import choose


def describe(items, chosen, capacity):
    selected = [x for x in items if x["id"] in chosen]
    weight = sum(x["weight"] for x in selected)
    return {"ids": [x["id"] for x in selected], "weight": weight,
            "value": sum(x["value"] for x in selected),
            "feasible": weight <= capacity and all(x["active"] for x in selected)}


def review(request):
    fields(request, ("items", "windows"))
    if not isinstance(request["items"], list) or not isinstance(request["windows"], list):
        raise ValueError("lists required")
    for item in request["items"]:
        fields(item, ("id", "weight", "value", "active"))
        integer(item["weight"], 1); integer(item["value"])
        if type(item["active"]) is not bool:
            raise ValueError("boolean active required")
    ids = names([x["id"] for x in request["items"]])
    names([fields(w, ("id", "capacity", "current", "mode"))["id"] for w in request["windows"]])
    for window in request["windows"]:
        integer(window["capacity"])
        if not set(names(window["current"])) <= set(ids) or window["mode"] not in ("inspect", "select"):
            raise ValueError("invalid window")
    eligible = [x for x in request["items"] if x["active"]]
    reports = []
    for window in request["windows"]:
        row = {"id": window["id"], "current": describe(request["items"], window["current"], window["capacity"]),
               "proposal": None, "transfers": []}
        if window["mode"] == "select":
            mask = choose(eligible, window["capacity"])
            chosen = [x["id"] for i, x in enumerate(eligible) if mask & (1 << i)]
            row["proposal"] = describe(request["items"], chosen, window["capacity"])
            offset = 0
            for item in eligible:
                if item["id"] in chosen:
                    row["transfers"].append({"id": item["id"], "offset": offset, "length": item["weight"]})
                    offset += item["weight"]
        reports.append(row)
    return {"eligible": [x["id"] for x in eligible], "windows": reports}


if __name__ == "__main__":
    print(json.dumps(review(json.load(sys.stdin)), indent=2))
