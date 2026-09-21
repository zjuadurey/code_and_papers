"""First-attempt local conversion check; no reference feedback to QAOA."""

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import time

import numpy
import qiskit
import scipy

from demo.context001_qiskit import hybrid_program
from demo.context001_qiskit import maintenance

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CASE = ROOT / "pilot/context_adaptations/v0.1/cases/context-001"


def fixtures() -> list[tuple[str, dict]]:
    return [
        ("original_three_equipment_example", json.loads((CASE / "example_request.json").read_text())),
        ("optimal_current_swapped_tie", {"equipment": ["a", "b"], "requirements": [
            {"first": "a", "second": "b", "weight": 3}], "current_windows": [["b"], ["a"]]}),
        ("duplicate_reversed_weights", {"equipment": ["z", "a", "m"], "requirements": [
            {"first": "z", "second": "a", "weight": 2},
            {"first": "a", "second": "z", "weight": 3},
            {"first": "a", "second": "m", "weight": 1}], "current_windows": [["m", "z"], ["a"]]}),
        ("zero_weights", {"equipment": ["a", "b", "c"], "requirements": [],
                          "current_windows": [["a", "c"], ["b"]]}),
        ("empty", {"equipment": [], "requirements": [], "current_windows": [[], []]}),
    ]


def load_original():
    import sys
    spec = importlib.util.spec_from_file_location("context001_original", CASE / "program.py")
    assert spec and spec.loader
    previous = sys.modules.get("maintenance")
    sys.modules["maintenance"] = maintenance
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        if previous is None:
            sys.modules.pop("maintenance", None)
        else:
            sys.modules["maintenance"] = previous
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("Refusing to overwrite an existing run; choose a new path")
    assert (HERE / "maintenance.py").read_bytes() == (CASE / "maintenance.py").read_bytes()
    original = load_original()
    paths = [HERE / name for name in ("hybrid_program.py", "maintenance.py", "protocol.json", "run_comparison.py")]
    paths += [CASE / name for name in ("program.py", "maintenance.py", "public_task.json", "example_request.json")]
    paths.append(ROOT / "qrefactorbench/evaluator/resources.py")
    result = {"kind": "AI-assisted Qiskit conversion smoke check; not model baseline",
              "utc": datetime.now(timezone.utc).isoformat(), "protocol": hybrid_program.PROTOCOL,
              "versions": {"python": platform.python_version(), "qiskit": qiskit.__version__,
                           "numpy": numpy.__version__, "scipy": scipy.__version__},
              "inputs_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
              "model_calls": 0, "qpu_calls": 0, "retry_count": 0, "cases": []}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation reserves a first-attempt artifact before circuit execution.
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
    for name, request in fixtures():
        record = {"fixture": name, "input": request}
        started = time.perf_counter()
        try:
            report, trace = hybrid_program.review_schedule_with_trace(request)
            record.update(report=report, trace=trace, execution_success=True,
                          simulation_seconds=time.perf_counter() - started)
            # Reference computation starts only after the quantum branch finishes.
            expected = original.review_schedule(request)
            record.update(reference_report=expected, complete_report_equal=report == expected,
                          objective_equal=report["proposed"]["conflict_weight"] == expected["proposed"]["conflict_weight"])
            if trace["quantum_executed"]:
                _, matrix, _ = maintenance.prepare_request(request)
                optimal = expected["proposed"]["conflict_weight"]
                probabilities = trace["probabilities_by_integer_mask"]
                record["optimal_probability_posthoc"] = sum(p for mask, p in enumerate(probabilities)
                    if sum(matrix[i][j] for i in range(len(matrix)) for j in range(i + 1, len(matrix))
                           if ((mask >> i) & 1) == ((mask >> j) & 1)) == optimal)
        except Exception as exc:
            record.update(execution_success=False, error=f"{type(exc).__name__}: {exc}")
        result["cases"].append(record)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        print(name, "execution=", record["execution_success"],
              "full_report_equal=", record.get("complete_report_equal"), flush=True)
    result["summary"] = {"fixtures": len(result["cases"]),
        "execution_successes": sum(r["execution_success"] for r in result["cases"]),
        "quantum_executions": sum(r.get("trace", {}).get("quantum_executed", False) for r in result["cases"]),
        "complete_report_matches": sum(r.get("complete_report_equal", False) for r in result["cases"])}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["summary"]))


if __name__ == "__main__":
    main()
