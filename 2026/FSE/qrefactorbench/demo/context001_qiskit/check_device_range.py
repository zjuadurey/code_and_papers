"""Measure the restored device range; retain first attempts and semantic failures.

This is a local engineering check, not a quantum-speedup or success-rate study.
Each fixture runs in a fresh process; peak RSS includes Python/Qiskit imports.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
FIXTURES = {"path_7": (7, False), "path_12": (12, False),
            "path_16": (16, False), "dense_16": (16, True)}
THREAD_ENV = {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}


def fixture(name: str) -> dict:
    n, dense = FIXTURES[name]
    names = [f"device-{i}" for i in range(n)]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)] if dense else [
        (i, i + 1) for i in range(n - 1)]
    return {"equipment": names, "requirements": [
        {"first": names[i], "second": names[j], "weight": 1 + (i + 2 * j) % 5}
        for i, j in pairs], "current_windows": [names, []]}


def run_fixture(name: str, target: Path) -> None:
    import numpy
    import qiskit
    import scipy
    from demo.context001_qiskit import hybrid_program as hybrid
    from demo.context001_qiskit.run_comparison import load_original

    record = {"fixture": name, "input": fixture(name), "attempt": 1, "retries": 0,
              "utc": datetime.now(timezone.utc).isoformat(), "protocol": hybrid.PROTOCOL,
              "versions": {"python": platform.python_version(), "qiskit": qiskit.__version__,
                           "numpy": numpy.__version__, "scipy": scipy.__version__},
              "thread_env": {key: os.environ.get(key) for key in THREAD_ENV},
              "model_calls": 0, "qpu_calls": 0}
    with target.open("x") as stream:
        json.dump(record, stream, indent=2)
    before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    start = time.perf_counter()
    try:
        report, trace = hybrid.review_schedule_with_trace(record["input"])
        record.update(hybrid_seconds=time.perf_counter() - start, execution_success=True,
                      report=report, trace=trace,
                      process_peak_rss_kib_after_hybrid=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      process_peak_rss_kib_before_hybrid=before)
        # Save the quantum result BEFORE loading/running the reference optimizer.
        target.write_text(json.dumps(record, indent=2) + "\n")
        reference = load_original().review_schedule(record["input"])
        record.update(reference_report=reference, complete_report_equal=report == reference,
                      objective_equal=report["proposed"]["conflict_weight"] == reference["proposed"]["conflict_weight"],
                      objective_gap=report["proposed"]["conflict_weight"] - reference["proposed"]["conflict_weight"])
    except Exception as exc:
        record.update(error=f"{type(exc).__name__}: {exc}")
        record.setdefault("execution_success", False)
        raise
    finally:
        target.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({key: record[key] for key in (
        "fixture", "execution_success", "hybrid_seconds", "process_peak_rss_kib_after_hybrid",
        "complete_report_equal", "objective_equal", "objective_gap")}))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--fixture", choices=FIXTURES)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.fixture:
        if args.output is None:
            parser.error("--fixture requires --output")
        run_fixture(args.fixture, args.output)
        return
    if args.output_dir is None:
        parser.error("--output-dir required")
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    paths = [HERE / name for name in ("hybrid_program.py", "protocol.json", "maintenance.py",
                                     "run_comparison.py", "check_device_range.py")]
    manifest = {"purpose": "device-limit fix validation; not quantum advantage",
                "utc": datetime.now(timezone.utc).isoformat(), "fixtures": FIXTURES,
                "inputs": {name: fixture(name) for name in FIXTURES},
                "thread_env": THREAD_ENV, "timeout_seconds_per_fixture": 300,
                "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in paths}, "runs": []}
    manifest_path = out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    env = dict(os.environ, **THREAD_ENV)
    for name in FIXTURES:
        command = [sys.executable, "-m", "demo.context001_qiskit.check_device_range",
                   "--fixture", name, "--output", str(out / f"{name}.json")]
        meta = {"fixture": name, "command": command, "retry_count": 0}
        with (out / f"{name}.stdout.txt").open("x") as stdout, (out / f"{name}.stderr.txt").open("x") as stderr:
            try:
                completed = subprocess.run(command, cwd=ROOT, env=env, stdout=stdout,
                                           stderr=stderr, timeout=300, check=False)
                meta["exit_code"] = completed.returncode
            except subprocess.TimeoutExpired:
                meta.update(exit_code=None, timeout=True)
        manifest["runs"].append(meta)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        print(name, meta, flush=True)
    if any(run.get("exit_code") != 0 for run in manifest["runs"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
