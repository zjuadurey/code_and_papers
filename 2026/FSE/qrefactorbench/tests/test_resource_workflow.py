"""Cost and integration regressions; synthetic numbers are not quantum evidence."""
import copy
import hashlib
import importlib.metadata
import json
import subprocess
import sys
from types import SimpleNamespace
from pathlib import Path

import pytest

from qrefactorbench import resource_workflow as rw
from qrefactorbench.cli import main


@pytest.fixture
def inputs():
    source = 'OPENQASM 3.0; include "stdgates.inc"; qubit q; h q; t q;'
    request = {"version": "resource-workflow-v0.1", "plan_id": "test-plan",
               "application": {"format": "openqasm3", "source": source, "coverage": "synthetic fixture"},
               "profiles": [{"id": "fixture", "gate_time_ns": 100, "measurement_time_ns": 500,
                             "error_rate": 0.0001, "source": "test assumption, not a device"}],
               "max_error": 0.01}
    interval = lambda a, b: {"lower": a, "upper": b, "source": "test fixture"}
    context = {"application_sha256": hashlib.sha256(source.encode()).hexdigest(),
               "comparison_id": "synthetic-task", "evidence_source": "test-only controller",
               "same_task": True, "classical_seconds": interval(20, 25),
               "overheads_seconds": {k: interval(0, 0) for k in rw.OVERHEADS},
               "quantum_executions": 2, "max_failure_probability": 0.1,
               "algorithm_failure_bound": 0.01}
    return request, context


def fixture_backend(request, profile):
    return {"status": "ok", "backend": "synthetic-test-double", "rows": [
        {"physical_qubits": 1000, "runtime_ns": 2e9, "error_bound": 0.01},
        {"physical_qubits": 500, "runtime_ns": 12e9, "error_bound": 0.02}]}


def test_complete_costs_change_recommendation_and_no_input_mutation(inputs):
    request, context = inputs
    before = copy.deepcopy(inputs)
    first = rw.analyze_resources(request, context, backend=fixture_backend)
    assert first["points"][0]["hybrid_seconds"] == [4, 4]
    assert first["points"][0]["failure_upper_bound"] == pytest.approx(0.03)
    assert first["points"][0]["decision"] == "conditional_benefit"
    assert first["points"][1]["decision"] == "uncertain"
    assert inputs == before
    context["overheads_seconds"]["validation_fallback"] = {"lower": 22, "upper": 23, "source": "fixture"}
    second = rw.analyze_resources(request, context, backend=fixture_backend)
    assert all(p["decision"] == "no_timing_benefit" for p in second["points"])
    assert second["conditional_benefit_points"] == []


@pytest.mark.parametrize("term", rw.OVERHEADS)
def test_unknown_cost_never_becomes_free(inputs, term):
    request, context = inputs
    context["overheads_seconds"][term] = None
    p = rw.analyze_resources(request, context, backend=fixture_backend)["points"][0]
    assert p["hybrid_seconds"] is None
    assert p["decision"] == "insufficient_evidence"
    assert term in p["missing_cost_terms"]


@pytest.mark.parametrize("field,value,expected", [
    ("same_task", None, "insufficient_evidence"),
    ("same_task", False, "contract_mismatch"),
    ("classical_seconds", None, "insufficient_evidence"),
    ("algorithm_failure_bound", None, "insufficient_evidence"),
    ("max_failure_probability", None, "insufficient_evidence"),
    ("max_failure_probability", 0, "quality_not_established"),
])
def test_faster_circuit_is_insufficient_for_adoption(inputs, field, value, expected):
    request, context = inputs
    context[field] = value
    output = rw.analyze_resources(request, context, backend=fixture_backend)
    assert output["points"][0]["decision"] == expected
    assert not output["conditional_benefit_points"]


def test_repeated_execution_counts_time_and_error_once(inputs):
    request, context = inputs
    context["quantum_executions"] = 10
    p = rw.analyze_resources(request, context, backend=fixture_backend)["points"][0]
    assert p["quantum_seconds_total"] == 20
    assert p["failure_upper_bound"] == pytest.approx(0.11)
    assert p["decision"] == "quality_not_established"


def test_binding_prevents_stale_semantics_or_cost_evidence(inputs):
    request, context = inputs
    request["application"]["source"] += '\nx q;'
    with pytest.raises(ValueError, match="different quantum application"):
        rw.analyze_resources(request, context, backend=fixture_backend)


@pytest.mark.parametrize("status", ["unavailable", "timeout", "error", "no_estimate"])
def test_backend_failure_is_not_a_negative_case_label(inputs, status):
    output = rw.analyze_resources(*inputs, backend=lambda *_: {"status": status, "rows": []})
    assert output["points"] == []
    assert output["estimation_runs"][0]["status"] == status
    assert "expected_decision" not in output


@pytest.mark.parametrize("value", [-1, True, float("nan"), float("inf")])
def test_invalid_costs_rejected_before_backend(inputs, value):
    request, context = inputs
    context["overheads_seconds"]["preparation"]["lower"] = value
    with pytest.raises(ValueError):
        rw.analyze_resources(request, context, backend=lambda *_: pytest.fail("unexpected backend"))


def test_uncertainty_and_break_even(inputs):
    request, context = inputs
    context["classical_seconds"] = {"lower": 4, "upper": 4, "source": "fixture"}
    p = rw.analyze_resources(request, context, backend=fixture_backend)["points"][0]
    assert p["decision"] == "no_timing_benefit"


def test_unknown_request_fields_and_external_include_rejected(inputs):
    request, _ = inputs
    request["application"]["source"] += '\ninclude "private.qasm";'
    with pytest.raises(ValueError, match="External include"):
        rw.validate_request(request)
    request["application"]["source"] = 'OPENQASM 3.0; qubit q;'
    request["semantics_passed"] = True
    with pytest.raises(ValueError, match="requires exactly"):
        rw.validate_request(request)


def test_process_units_pinning_telemetry_and_empty_warning(inputs, monkeypatch):
    def fake_run(command, **kwargs):
        assert command[0] == sys.executable
        assert kwargs["env"]["QDK_PYTHON_TELEMETRY"] == "none"
        payload = json.loads(kwargs["input"])
        assert payload["qdk_version"] == rw.QDK_VERSION
        assert payload["profile"]["gate_time_ns"] == 100
        return SimpleNamespace(returncode=0, stdout='{"status":"no_estimate","rows":[]}', stderr="No compatible trace")
    monkeypatch.setattr(subprocess, "run", fake_run)
    request, _ = inputs
    result = rw.qdk_backend(request, request["profiles"][0])
    assert result["diagnostic"] == "No compatible trace"


def test_timeout_becomes_structured_feedback(inputs, monkeypatch):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("worker", 1)
    monkeypatch.setattr(subprocess, "run", timeout)
    request, _ = inputs
    assert rw.qdk_backend(request, request["profiles"][0], timeout=1)["status"] == "timeout"


def test_cli_full_path_and_missing_dependency(inputs, tmp_path, capsys, monkeypatch):
    request, context = inputs
    req, ctx = tmp_path / "request.json", tmp_path / "context.json"
    req.write_text(json.dumps(request)); ctx.write_text(json.dumps(context))
    monkeypatch.setattr(rw, "qdk_backend", lambda r, p, **_: fixture_backend(r, p))
    assert main(["estimate-resources", str(req), "--context", str(ctx)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["points"][0]["decision"] == "conditional_benefit"
    monkeypatch.setattr(rw, "qdk_backend", lambda *a, **k: {"status": "unavailable", "rows": []})
    assert main(["estimate-resources", str(req), "--context", str(ctx), "--json"]) == 2
    assert json.loads(capsys.readouterr().out)["points"] == []


def test_real_qdk_process_integration(inputs):
    try:
        installed = importlib.metadata.version("qdk")
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("Optional QDK not installed")
    if installed != rw.QDK_VERSION:
        pytest.skip("Optional QDK version differs from pinned backend")
    request, context = inputs
    context["same_task"] = None
    output = rw.analyze_resources(request, context, timeout=60)
    run = output["estimation_runs"][0]
    assert run["status"] == "ok", run
    assert run["backend_version"] == rw.QDK_VERSION
    assert run["stats"]["total_jobs"] > 0
    assert all(p["physical_qubits"] > 0 and p["runtime_ns"] > 0 for p in output["points"])
    assert all(p["decision"] == "insufficient_evidence" for p in output["points"])


def test_real_process_reports_missing_dependency_without_site_packages(inputs):
    request, _ = inputs
    payload = {"application": request["application"], "profile": request["profiles"][0],
               "max_error": request["max_error"], "qdk_version": rw.QDK_VERSION}
    worker = Path(rw.__file__).with_name("_qdk_resource_worker.py")
    proc = subprocess.run([sys.executable, "-B", "-S", str(worker)], input=json.dumps(payload),
                          text=True, capture_output=True, timeout=10, check=False)
    assert proc.returncode == 2
    assert json.loads(proc.stdout)["status"] == "unavailable"
