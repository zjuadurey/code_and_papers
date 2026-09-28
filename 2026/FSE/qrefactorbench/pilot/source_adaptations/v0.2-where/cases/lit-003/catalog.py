"""Agenda request validation and participant-derived conflicts."""

from typing import Any


def prepare(request: Any) -> tuple[list[str], list[dict], list[str | None], str]:
    if not isinstance(request, dict) or set(request) != {"slots", "sessions", "current", "mode"}:
        raise ValueError("invalid fields")
    slots, sessions, current, mode = (request[k] for k in ("slots", "sessions", "current", "mode"))
    if (not isinstance(slots, list) or any(not isinstance(s, str) or not s for s in slots)
            or len(set(slots)) != len(slots)):
        raise ValueError("slots must be distinct names")
    if not isinstance(sessions, list) or mode not in ("inspect", "complete"):
        raise ValueError("invalid sessions or mode")
    ids = set()
    for session in sessions:
        if not isinstance(session, dict) or set(session) != {"session_id", "participants"}:
            raise ValueError("invalid session")
        name, participants = session["session_id"], session["participants"]
        if not isinstance(name, str) or not name or name in ids:
            raise ValueError("session IDs must be unique")
        ids.add(name)
        if (not isinstance(participants, list) or any(not isinstance(p, str) or not p for p in participants)
                or len(set(participants)) != len(participants)):
            raise ValueError("participants must be distinct names")
    if (not isinstance(current, list) or len(current) != len(sessions)
            or any(s is not None and (not isinstance(s, str) or s not in slots) for s in current)):
        raise ValueError("one known slot or null per session required")
    return list(slots), sessions, list(current), mode


def relations(sessions: list[dict]) -> tuple[list[list[int]], dict[int, list[int]]]:
    matrix = [[0] * len(sessions) for _ in sessions]
    for i, left in enumerate(sessions):
        for j in range(i + 1, len(sessions)):
            if set(left["participants"]) & set(sessions[j]["participants"]):
                matrix[i][j] = matrix[j][i] = 1
    return matrix, {i: [j for j, connected in enumerate(row) if connected] for i, row in enumerate(matrix)}


def describe(slots: list[str], sessions: list[dict], assigned: list[str | None]) -> dict:
    conflicts = []
    for i, left in enumerate(sessions):
        for j in range(i + 1, len(sessions)):
            shared = sorted(set(left["participants"]) & set(sessions[j]["participants"]))
            if shared and assigned[i] is not None and assigned[i] == assigned[j]:
                conflicts.append({"first": left["session_id"], "second": sessions[j]["session_id"], "participants": shared})
    missing = [s["session_id"] for s, slot in zip(sessions, assigned) if slot is None]
    return {"assignment": list(assigned), "unassigned": missing, "conflicts": conflicts,
            "feasible": not missing and not conflicts,
            "slots": [{"slot": slot, "sessions": [s["session_id"] for s, value in zip(sessions, assigned) if value == slot]}
                      for slot in slots]}
