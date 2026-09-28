"""Build offline review inputs and classical witnesses; never invoke a model.

Only the explicit public packet allowlist goes into prospective A/B/C messages.
Private evidence uses existing classical programs in separate subprocesses.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "pilot/source_adaptations/v0.2-where"
PUBLIC = SOURCE / "review_inputs"
SCHEMAS = ("case", "prediction", "migration_plan", "phase1_prediction")
VIEWS = {
    "lit-003": ("source-core-003", ("program.py", "agenda.py", "catalog.py", "public_task.json", "NOTICE.txt")),
    "lit-004": ("source-core-004", ("program.py", "reports.py", "catalog.py", "public_task.json", "NOTICE.txt")),
}
# Proposed locations only, not scientific gold; B intentionally receives this cue.
HINTS = {
    "lit-003": {"file": "agenda.py", "start_line": 28, "end_line": 57},
    "lit-004": {"file": "program.py", "start_line": 25, "end_line": 29},
}
HINT_MARKER = "\nLOCATION CUE\n"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def render(view: str, names: tuple[str, ...]) -> str:
    """Read only allowlisted public bytes, checking their existing snapshot hashes."""
    manifest = json.loads((PUBLIC / "manifest.json").read_text())["files_sha256"]
    chunks = [(HERE / "TASK.md").read_text(), "\nPUBLIC FILES (line labels are not source code)\n"]
    for name in names:
        data = (PUBLIC / view / name).read_bytes()
        if digest(data) != manifest[f"{view}/{name}"]:
            raise ValueError(f"public snapshot changed: {view}/{name}")
        value = data.decode("utf-8")
        if name.endswith(".py"):
            value = "\n".join(f"{i}: {line}" for i, line in enumerate(value.splitlines(), 1)) + "\n"
        chunks.append(f"\nFILE {name}\n{value}")
    chunks.append("\nSHARED DRAFT CONTRACT MENU\n" + (ROOT / "pilot/public_contracts.json").read_text())
    for name in SCHEMAS:
        chunks.append(f"\nSCHEMA {name}.schema.json\n" + (ROOT / f"schemas/{name}.schema.json").read_text())
    return "".join(chunks)


def changes(left: object, right: object, path: str = "$") -> list[str]:
    """Describe differing report fields, without interpreting scientific correctness."""
    if isinstance(left, dict) and isinstance(right, dict):
        return [p for k in sorted(set(left) | set(right))
                for p in (changes(left[k], right[k], f"{path}.{k}") if k in left and k in right else [f"{path}.{k}"])]
    if isinstance(left, list) and isinstance(right, list) and len(left) == len(right):
        return [p for i, (a, b) in enumerate(zip(left, right)) for p in changes(a, b, f"{path}[{i}]")]
    return [] if left == right else [path]


def witnesses(case_id: str) -> list[dict]:
    """Trace reviewed classical code; each case runs in its own Python process."""
    folder = SOURCE / "cases" / case_id
    sys.path.insert(0, str(folder))
    import program  # Only the local, inspected classical source; not generated code.

    sample = json.loads((folder / "example_request.json").read_text())
    rows = []

    def run(name: str, request: dict, substitutions: dict | None = None) -> dict:
        from contextlib import ExitStack
        tracked = ("preview", "complete") if case_id == "lit-003" else ("preview", "compatible")
        counts = dict.fromkeys(tracked, 0)
        originals = {key: getattr(program, key) for key in tracked}
        with ExitStack() as stack:
            for key, value in (substitutions or {}).items():
                stack.enter_context(patch.object(program, key, value))
            for key in tracked:
                target = getattr(program, key)
                def wrapper(*args, _key=key, _target=target, **kwargs):
                    counts[_key] += 1
                    return _target(*args, **kwargs)
                stack.enter_context(patch.object(program, key, wrapper))
            original_request = deepcopy(request)
            entry = program.review_agenda if case_id == "lit-003" else program.review_releases
            report = entry(request)
            assert request == original_request
        assert all(getattr(program, k) is v for k, v in originals.items())
        record = {"id": name, "input": request, "calls": counts, "report": report,
                  "kind": "constructed_substitution" if substitutions else "original_execution"}
        rows.append(record)
        return record

    if case_id == "lit-003":
        baseline = run("completion_after_blocked_preview", deepcopy(sample))
        run("inspection", dict(deepcopy(sample), mode="inspect"))
        run("retain_valid_current", dict(deepcopy(sample), current=["afternoon", "morning", "morning", "afternoon"]))
        run("ready_preview", {"slots": ["a", "b"], "sessions": [
            {"session_id": "one", "participants": ["shared"]}, {"session_id": "two", "participants": ["shared"]}],
            "current": [None, None], "mode": "complete"})
        run("no_arrangement", dict(deepcopy(sample), slots=["only"]))
        complete = program.complete
        def full_preview(matrix, k):
            return complete({i: [j for j, v in enumerate(row) if v] for i, row in enumerate(matrix)}, k)
        bad = run("replace_preview_with_completion", deepcopy(sample), {"preview": full_preview})
        assert bad["report"]["proposed"] == baseline["report"]["proposed"]
        bad["same_final_proposal"] = True
        bad["changed_fields"] = changes(baseline["report"], bad["report"])
        bad = run("drop_participant_relation", deepcopy(sample), {"relations": lambda sessions: (
            [[0] * len(sessions) for _ in sessions], {i: [] for i in range(len(sessions))})})
        bad["changed_fields"] = changes(baseline["report"], bad["report"])
    else:
        baseline = run("mixed_request_modes", deepcopy(sample))
        run("inspection_only", dict(deepcopy(sample), requests=[deepcopy(sample["requests"][0])]))
        run("selection_only", dict(deepcopy(sample), requests=[deepcopy(sample["requests"][1])]))
        bad = run("replace_preview_with_largest_group", deepcopy(sample), {"preview": lambda _: [1, 2, 3]})
        assert bad["report"]["requests"][1]["proposed"] == baseline["report"]["requests"][1]["proposed"]
        bad["same_final_proposal"] = True
        bad["changed_fields"] = changes(baseline["report"], bad["report"])
        original_latest = program.latest_results
        bad = run("reverse_history_precedence", deepcopy(sample), {"latest_results": lambda rows: original_latest(rows[::-1])})
        bad["changed_fields"] = changes(baseline["report"], bad["report"])
        run("numeric_mask_tie", {"versions": [{"version_id": n, "active": True} for n in "abcd"],
            "checks": [{"left": "a", "right": "d", "passed": True}, {"left": "b", "right": "c", "passed": True}],
            "requests": [{"request_id": "tie", "members": list("dcba"), "current": [], "mode": "select"}]})
    return rows


def build(output: Path) -> None:
    """Write six prospective inputs and private evidence to a fresh directory."""
    output.mkdir(parents=True, exist_ok=False)
    (output / "inputs").mkdir()
    (output / "evidence").mkdir()
    manifest: dict = {"status": "DRAFT_NOT_RUN", "independent_mother_problems": 2,
                      "human_approved_locations": False, "model_calls": 0, "conditions": []}
    for case_id, (core, names) in VIEWS.items():
        context = render(case_id, names)
        messages = {"A": render(core, ("program.py", "public_task.json", "NOTICE.txt")),
                    "B": context + HINT_MARKER + json.dumps(HINTS[case_id], sort_keys=True) + "\n",
                    "C": context}
        for condition, message in messages.items():
            path = output / "inputs" / f"{case_id}-{condition}.txt"
            path.write_text(message)
            manifest["conditions"].append({"mother_case": case_id, "condition": condition,
                "prediction_case_id": core if condition == "A" else case_id,
                "path": str(path.relative_to(output)), "sha256": digest(path.read_bytes()),
                "location_cue": HINTS[case_id] if condition == "B" else None})
        result = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "--witness", case_id],
                                capture_output=True, text=True, check=True)
        (output / "evidence" / f"{case_id}.json").write_text(result.stdout)
        if result.stderr:
            (output / "evidence" / f"{case_id}.stderr.txt").write_text(result.stderr)
    manifest["source_files_sha256"] = {
        str(p.relative_to(ROOT)): digest(p.read_bytes())
        for p in [HERE / "TASK.md", Path(__file__).resolve(), PUBLIC / "manifest.json", ROOT / "pilot/public_contracts.json"]
        + [ROOT / f"schemas/{name}.schema.json" for name in SCHEMAS]}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("Prepared six DRAFT inputs and thirteen classical witnesses; no model call.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--witness", choices=tuple(VIEWS))
    args = parser.parse_args()
    if args.witness:
        print(json.dumps(witnesses(args.witness), indent=2))
    else:
        build(args.output)
