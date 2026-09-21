"""Review two-group assignments under signed pair preferences."""
import json
import sys
from common import bits, fields, names
from kernel import choose, score


def describe(members, values, pairs):
    return {"groups": [[n for n, v in zip(members, values) if v == side] for side in (False, True)],
            "score": score(values, pairs),
            "violated": [[members[i], members[j]] for i, j, w in pairs if (values[i] != values[j]) != (w == 1)]}


def review(request):
    fields(request, ("members", "preferences", "current", "mode"))
    members = names(request["members"])
    current = bits(request["current"], len(members))
    if not isinstance(request["preferences"], list) or request["mode"] not in ("inspect", "propose"):
        raise ValueError("invalid preferences or mode")
    pairs, seen = [], set()
    for row in request["preferences"]:
        fields(row, ("left", "right", "relation"))
        if row["left"] not in members or row["right"] not in members or row["left"] == row["right"] or row["relation"] not in ("together", "apart"):
            raise ValueError("invalid pair")
        i, j = sorted((members.index(row["left"]), members.index(row["right"])))
        if (i, j) in seen:
            raise ValueError("duplicate pair")
        seen.add((i, j)); pairs.append((i, j, 1 if row["relation"] == "apart" else -1))
    if len(pairs) != len(members) * (len(members) - 1) // 2:
        raise ValueError("one preference for every pair required")
    pairs.sort()
    current_report = describe(members, current, pairs)
    result = {"current": current_report, "proposed": None, "gain": None, "moves": []}
    if request["mode"] == "propose":
        selected = choose(len(members), pairs)
        result["proposed"] = describe(members, selected, pairs)
        result["gain"] = result["proposed"]["score"] - current_report["score"]
        result["moves"] = [name for name, a, b in zip(members, current, selected) if a != b]
    return result


if __name__ == "__main__":
    print(json.dumps(review(json.load(sys.stdin)), indent=2))
