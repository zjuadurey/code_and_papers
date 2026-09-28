"""Resource-analysis tool for a harness; independent of formal benchmark scoring.

Model proposals and controller-owned comparison evidence are separate arguments.
This module consumes evidence; it does not verify semantics or calibrate hardware.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

QDK_VERSION = "1.32.3"
OVERHEADS = ("preparation", "classical_control", "communication", "readout_decode",
             "validation_fallback", "compilation_amortized")


def _fields(value: Any, keys: tuple[str, ...], name: str) -> None:
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError(f"{name} requires exactly {', '.join(keys)}")


def _number(value: Any, name: str, *, positive: bool = False) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if value < 0 or (positive and value == 0):
        raise ValueError(f"{name} must be {'positive' if positive else 'nonnegative'}")
    return float(value)


def _text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")


def _probability(value: Any, name: str) -> None:
    if _number(value, name) > 1:
        raise ValueError(f"{name} must be at most one")


def _interval(value: Any, name: str) -> tuple[float, float] | None:
    if value is None:
        return None
    _fields(value, ("lower", "upper", "source"), name)
    lo, hi = (_number(value[k], name) for k in ("lower", "upper"))
    if hi < lo:
        raise ValueError(f"{name}: upper must be >= lower")
    _text(value["source"], f"{name}.source")
    return lo, hi


def validate_request(request: dict[str, Any]) -> None:
    _fields(request, ("version", "plan_id", "application", "profiles", "max_error"), "request")
    if request["version"] != "resource-workflow-v0.1":
        raise ValueError("Unsupported resource workflow version")
    _text(request["plan_id"], "plan_id")
    app = request["application"]
    _fields(app, ("format", "source", "coverage"), "application")
    if app["format"] != "openqasm3":
        raise ValueError("v0.1 supports self-contained OpenQASM 3 only")
    _text(app["source"], "application.source")
    _text(app["coverage"], "application.coverage")
    if len(app["source"].encode()) > 200_000:
        raise ValueError("Application exceeds 200 KB")
    # Only the built-in standard gates include is accepted. This is not a sandbox.
    stripped = re.sub(r"/\*.*?\*/|//[^\n]*", "", app["source"], flags=re.S)
    if not re.match(r"\s*OPENQASM\s+3(?:\.0)?\s*;", stripped):
        raise ValueError("Expected an OpenQASM 3 header")
    stripped = re.sub(r'\binclude\s+"stdgates.inc"\s*;', "", stripped)
    if re.search(r"\binclude\b", stripped):
        raise ValueError("External include files are not supported")
    profiles = request["profiles"]
    if not isinstance(profiles, list) or not 1 <= len(profiles) <= 8:
        raise ValueError("Provide 1..8 hardware profiles")
    ids = []
    for profile in profiles:
        _fields(profile, ("id", "gate_time_ns", "measurement_time_ns", "error_rate", "source"), "profile")
        for key in ("id", "source"):
            _text(profile[key], f"profile.{key}")
        for key in ("gate_time_ns", "measurement_time_ns"):
            _number(profile[key], key, positive=True)
        if not 0 < _number(profile["error_rate"], "error_rate") < 1:
            raise ValueError("error_rate must be in (0,1)")
        ids.append(profile["id"])
    if len(set(ids)) != len(ids):
        raise ValueError("Profile IDs must be unique")
    if not 0 < _number(request["max_error"], "max_error") < 1:
        raise ValueError("Estimator max_error must be in (0,1); not permission to change the task contract")


def validate_context(context: dict[str, Any], source_hash: str) -> None:
    _fields(context, ("application_sha256", "comparison_id", "evidence_source", "same_task",
                      "classical_seconds", "overheads_seconds", "quantum_executions",
                      "max_failure_probability", "algorithm_failure_bound"), "context")
    if context["application_sha256"] != source_hash:
        raise ValueError("Comparison evidence is bound to a different quantum application")
    for key in ("comparison_id", "evidence_source"):
        _text(context[key], key)
    if context["same_task"] is not None and type(context["same_task"]) is not bool:
        raise ValueError("same_task must be true, false or null")
    _interval(context["classical_seconds"], "classical_seconds")
    _fields(context["overheads_seconds"], OVERHEADS, "overheads_seconds")
    for key in OVERHEADS:
        _interval(context["overheads_seconds"][key], key)
    count = context["quantum_executions"]
    if type(count) is not int or not 1 <= count <= 10**9:
        raise ValueError("quantum_executions must be an integer in [1, 1e9]")
    for key in ("max_failure_probability", "algorithm_failure_bound"):
        if context[key] is not None:
            _probability(context[key], key)


def qdk_backend(request: dict[str, Any], profile: dict[str, Any], *,
                python: str = sys.executable, timeout: float = 60) -> dict[str, Any]:
    """Run pinned QDK in a fresh process. No Azure account or QPU job is used."""
    if not 0 < _number(timeout, "timeout") <= 300:
        raise ValueError("timeout must be in (0,300] seconds per profile")
    payload = {"application": request["application"], "profile": profile,
               "max_error": request["max_error"], "qdk_version": QDK_VERSION}
    env = dict(os.environ, QDK_PYTHON_TELEMETRY="none", QSHARP_PYTHON_TELEMETRY="none",
               PYTHONDONTWRITEBYTECODE="1")
    worker = Path(__file__).with_name("_qdk_resource_worker.py")
    try:
        with tempfile.TemporaryDirectory(prefix="qrefactor-qre-") as directory:
            proc = subprocess.run([python, "-B", str(worker)], input=json.dumps(payload),
                                  text=True, capture_output=True, cwd=directory, env=env,
                                  timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "rows": [], "error": "Estimation exceeded per-profile timeout"}
    except OSError as exc:
        return {"status": "unavailable", "rows": [], "error": str(exc)}
    try:
        result = json.loads(proc.stdout)
        if not isinstance(result, dict) or not isinstance(result.get("rows"), list):
            raise ValueError("Malformed worker result")
    except (ValueError, TypeError):
        return {"status": "error", "rows": [], "error": "Estimator worker returned no valid result",
                "diagnostic": proc.stderr[-4000:]}
    if proc.returncode and result.get("status") == "ok":
        return {"status": "error", "rows": [], "error": "Estimator worker failed after output"}
    if proc.stderr:
        result["diagnostic"] = proc.stderr[-4000:]
    return result


def _compare(row: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    if type(row.get("physical_qubits")) is not int or row["physical_qubits"] < 0:
        raise ValueError("Invalid physical qubit result")
    runtime = _number(row.get("runtime_ns"), "runtime_ns") / 1e9
    _probability(row.get("error_bound"), "error_bound")
    count = context["quantum_executions"]
    quantum = runtime * count
    overheads = {k: _interval(v, k) for k, v in context["overheads_seconds"].items()}
    missing = [k for k, v in overheads.items() if v is None]
    classical = _interval(context["classical_seconds"], "classical_seconds")
    total = None if missing else [quantum + sum(v[i] for v in overheads.values()) for i in (0, 1)]
    relation = "unknown"
    if total is not None and classical is not None:
        relation = "faster" if total[1] < classical[0] else (
            "not_faster" if total[0] >= classical[1] else "overlap")
    hardware_error = min(1.0, count * row["error_bound"])
    algorithm_error = context["algorithm_failure_bound"]
    error = None if algorithm_error is None else min(1.0, hardware_error + algorithm_error)
    allowed = context["max_failure_probability"]
    quality = None if error is None or allowed is None else error <= allowed
    if context["same_task"] is False:
        decision = "contract_mismatch"
    elif quality is False:
        decision = "quality_not_established"
    elif context["same_task"] is not True or quality is None:
        decision = "insufficient_evidence"
    else:
        decision = {"faster": "conditional_benefit", "not_faster": "no_timing_benefit",
                    "overlap": "uncertain", "unknown": "insufficient_evidence"}[relation]
    return {**row, "quantum_seconds_total": quantum, "hybrid_seconds": total,
            "missing_cost_terms": missing + ([] if classical is not None else ["classical_seconds"]),
            "timing_relation": relation, "failure_upper_bound": error,
            "quality_bound_satisfied": quality, "decision": decision}


def analyze_resources(request: dict[str, Any], context: dict[str, Any], *,
                      backend: Callable | None = None, python: str = sys.executable,
                      timeout: float = 60) -> dict[str, Any]:
    """Callable tool entry: proposals from the model, context from the controller.

    All costs use the same per-request serial-schedule basis. Counts include all
    shots/retries; overhead intervals include their complete aggregate costs.
    Backend failures/empty frontiers never imply absence of quantum advantage.
    """
    validate_request(request)
    source_hash = hashlib.sha256(request["application"]["source"].encode()).hexdigest()
    validate_context(context, source_hash)
    points, runs = [], []
    for profile in request["profiles"]:
        raw = (backend(request, profile) if backend is not None else
               qdk_backend(request, profile, python=python, timeout=timeout))
        if raw.get("status") == "ok":
            current = [_compare(row, context) for row in raw["rows"]]
            points.extend({**row, "profile_id": profile["id"]} for row in current)
        runs.append({"profile_id": profile["id"], **raw})
    encode = lambda value: json.dumps(value, sort_keys=True, allow_nan=False).encode()
    return {"version": request["version"], "plan_id": request["plan_id"],
            "request_sha256": hashlib.sha256(encode(request)).hexdigest(),
            "context_sha256": hashlib.sha256(encode(context)).hexdigest(),
            "application_sha256": source_hash, "comparison_id": context["comparison_id"],
            "estimation_runs": runs, "points": points,
            "conditional_benefit_points": [p for p in points if p["decision"] == "conditional_benefit"],
            "assumptions": {"request": request, "controller_context": context},
            "limitations": ["Predictions under supplied models, not hardware observations or benchmark scores.",
                            "Controller evidence is consumed, not independently verified by this tool.",
                            "Serial schedule; all costs aggregated per request; no implicit overlap/amortization.",
                            "Failure bound uses a union bound; exceeding it does not prove actual failure rate.",
                            "Sampled profiles and backend frontier do not establish a globally minimal threshold."]}
