"""Inspect an agenda or complete it while retaining an already valid arrangement."""

import json
import sys
from typing import Any

from agenda import complete, preview
from catalog import describe, prepare, relations


def review_agenda(request: Any) -> dict:
    slots, sessions, assigned, mode = prepare(request)
    current = describe(slots, sessions, assigned)
    result = {"session_count": len(sessions), "current": current, "preview": None,
              "proposed": None, "status": "inspected", "moves": []}
    if mode == "inspect":
        return result
    if current["feasible"]:
        result.update(status="retained", proposed=describe(slots, sessions, assigned))
        return result
    matrix, neighbors = relations(sessions)
    try:
        indices = preview(matrix, len(slots))
        result["preview"] = {"status": "ready", "assignment": [slots[i] for i in indices]}
        result["status"] = "preview"
    except ValueError:
        result["preview"] = {"status": "blocked", "assignment": None}
        try:
            indices = complete(neighbors, len(slots))
        except ValueError:
            result["status"] = "unavailable"
            return result
        result["status"] = "completed"
    proposal = [slots[i] for i in indices]
    result["proposed"] = describe(slots, sessions, proposal)
    result["moves"] = [{"session_id": s["session_id"], "from": old, "to": new}
                       for s, old, new in zip(sessions, assigned, proposal) if old != new]
    return result


if __name__ == "__main__":
    print(json.dumps(review_agenda(json.load(sys.stdin)), indent=2))
