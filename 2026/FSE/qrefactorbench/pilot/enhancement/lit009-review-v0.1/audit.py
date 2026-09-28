"""Offline N-044 trace audit. Executes only unchanged trusted case code.

No model runner import, network request, generated-code execution or score update.
Write results to a fresh directory; old artifacts are read-only inputs.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import platform
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / "pilot/model_comparison/20260923-four-model-c-v0.1"
CASE = ROOT / "pilot/reference_completion/v0.1.1/cases/lit-009"


def module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def trace_request(program: Any, kernel: Any, request: dict[str, Any]) -> dict[str, Any]:
    before = deepcopy(request)
    pivots: list[dict[str, Any]] = []
    updates: list[dict[str, Any]] = []
    exceptions: list[dict[str, Any]] = []
    pending: dict[str, Any] | None = None

    def trace(frame: Any, event: str, arg: Any) -> Any:
        nonlocal pending
        if frame.f_code is not kernel.solve.__code__:
            return trace
        state = frame.f_locals
        if pending is not None and event == "line":
            value = state["rows"][pending["i"]][pending["j"]]
            if not math.isfinite(value):
                updates.append({**pending, "after": repr(value)})
            pending = None
        if event == "line" and frame.f_lineno == 20:
            i, j, col = state["i"], state["j"], state["col"]
            pending = {"column": col, "i": i, "j": j,
                       "before": repr(state["rows"][i][j]),
                       "factor": repr(state["factor"]),
                       "pivot_value": repr(state["rows"][col][j])}
        if event == "line" and frame.f_lineno == 14:
            col, n = state["col"], state["n"]
            values = {i: abs(state["rows"][i][col]) for i in range(col, n)}
            marked = [i for i in values if all(values[i] >= v for v in values.values())
                      and not any(values[j] == values[i] for j in values if j < i)]
            excluding_self = [i for i in values
                              if all(values[i] >= values[k] for k in values if k != i)
                              and not any(values[j] == values[i] for j in values if j < i)]
            incumbent = col
            for i in range(col + 1, n):
                if values[i] > values[incumbent]:
                    incumbent = i
            pivots.append({"column": col, "values": [repr(v) for v in values.values()],
                           "original": state["pivot"], "literal_marked": marked,
                           "excluding_self_marked": excluding_self,
                           "ordered_scan_control": incumbent})
        if event == "exception":
            exceptions.append({"line": frame.f_lineno, "type": arg[0].__name__,
                               "message": str(arg[1])})
        return trace

    inspection = program.review({**request, "mode": "inspect"})
    previous = sys.gettrace()
    try:
        sys.settrace(trace)
        outcome = {"report": program.review(request)}
    except ValueError as exc:
        outcome = {"exception": type(exc).__name__, "message": str(exc)}
    finally:
        sys.settrace(previous)
    assert request == before
    assert all(p["ordered_scan_control"] == p["original"] for p in pivots)
    return {"input": request, "inspection": inspection, "outcome": outcome,
            "pivots": pivots, "nonfinite_updates": updates,
            "kernel_exceptions": exceptions, "input_unchanged": True}


def run(output: Path) -> None:
    if output.exists():
        raise FileExistsError(output)
    saved = json.loads((OLD / "pivot-witness/result.json").read_text())
    for relative, expected in saved["source_sha256"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected
    provenance = saved["provenance"]
    raw = ROOT / provenance["response_path"]
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == provenance["response_sha256"]
    response = json.loads(raw.read_text())
    assert response["plan"]["formulation"] == provenance["quote"]
    # Isolated CLI process: use original module names required by program.py.
    for name in ("common", "kernel", "program"):
        sys.modules[name] = module(name, CASE / f"{name}.py")
    program, kernel = sys.modules["program"], sys.modules["kernel"]
    normal = trace_request(program, kernel, saved["normal_control"]["input"])
    witness = trace_request(program, kernel, saved["counterexample"]["input"])
    assert normal["outcome"] == saved["normal_control"]["original_result"]
    assert witness["outcome"] == saved["counterexample"]["original_result"]
    for new, old in zip((normal, witness), (saved["normal_control"], saved["counterexample"])):
        assert len(new["pivots"]) == len(old["pivot_trace"])
        for actual, expected in zip(new["pivots"], old["pivot_trace"]):
            assert actual["original"] == expected["original_pivot"]
            assert actual["literal_marked"] == expected["model_predicate_marked"]
            assert actual["values"] == expected["absolute_values_repr"]
    # Reviewer sensitivity probe, same mother case, not a fresh model sample.
    extended = deepcopy(saved["counterexample"]["input"])
    extended["variables"].append("f")
    extended["matrix"] = [row + [0.0] for row in extended["matrix"]] + [[0.0] * 5 + [1.0]]
    extended["rhs"].append(1.0)
    extended["current"].append(0.0)
    sensitivity = trace_request(program, kernel, extended)
    assert witness["pivots"][-1]["excluding_self_marked"] == [4]
    assert any(p["excluding_self_marked"] != [p["original"]] for p in sensitivity["pivots"])
    result = {"review_status": "AI_REVIEW_PENDING", "post_hoc": True,
              "python": platform.python_version(), "platform": platform.platform(),
              "provenance": provenance, "normal_control": normal, "archived_witness": witness,
              "reviewer_sensitivity_probe": sensitivity,
              "task_pass": None, "fallback_execution": None, "new_model_calls": 0}
    output.mkdir(parents=True)
    (output / "trace.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"archived_pivots_replayed": len(normal["pivots"]) + len(witness["pivots"]),
                      "sensitivity_pivots": len(sensitivity["pivots"]),
                      "archived_literal_failures": [p["column"] for p in witness["pivots"]
                                                    if p["literal_marked"] != [p["original"]]],
                      "sensitivity_excluding_self_failures": [p["column"] for p in sensitivity["pivots"]
                                                              if p["excluding_self_marked"] != [p["original"]]],
                      "task_pass": None}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    run(parser.parse_args().output)
