"""Check actual gates, full reports, exceptions, fallback and reachable NaNs."""
import copy
import itertools
import json

import numpy as np
import pytest
from qiskit.quantum_info import Operator, Statevector

from demo.lit009_end_to_end import hybrid as h


def request(matrix, rhs=None):
    n = len(matrix)
    return dict(variables=[f"x{i}" for i in range(n)], matrix=matrix,
                rhs=rhs if rhs is not None else [1.] * n, current=[0.] * n,
                mode="solve", residual_limit=1.)


def outcome(function, value):
    original = copy.deepcopy(value)
    before = json.dumps(original, sort_keys=True, allow_nan=True)
    try:
        result = ("return", json.dumps(function(original), sort_keys=True, allow_nan=False))
    except Exception as exc:
        result = (type(exc).__name__, str(exc))
    assert json.dumps(original, sort_keys=True, allow_nan=True) == before
    return result


def test_oracle_truth_table_including_padding():
    checks = 0
    for size in range(2, 5):
        for values in itertools.product((0., 1., 2.), repeat=size):
            for threshold in range(size):
                matrix = Operator(h.threshold_oracle(list(values), threshold)).data
                expected = [(-1 if i < size and (values[i] > values[threshold] or
                            (values[i] == values[threshold] and i < threshold)) else 1)
                            for i in range(len(matrix))]
                assert np.allclose(matrix, np.diag(expected), atol=1e-12)
                checks += 1
    assert checks == 423


def test_grover_amplifies_one_marked_state():
    _, circuit = h.search_circuit([0., 3., 0., 1.])
    assert Statevector.from_instruction(circuit).probabilities()[1] == pytest.approx(1.)


@pytest.mark.parametrize("seed", h.PROTOCOL["semantic_seeds"])
def test_entire_reports_and_exceptions_small_matrices(seed):
    # Includes singular systems, ties, negative coefficients and all 81 matrices.
    for entries in itertools.product((-1., 0., 1.), repeat=4):
        value = request([list(entries[:2]), list(entries[2:])], [1., 2.])
        assert outcome(h.make_review(h.PivotSelector(seed)), value) == outcome(h.ORIGINAL.review, value)


@pytest.mark.parametrize("case", ["normal_control", "archived_witness", "reviewer_sensitivity_probe"])
def test_original_reachable_traces(case):
    path = h.ROOT / "pilot/enhancement/lit009-review-v0.1/evidence/trace.json"
    value = json.loads(path.read_text())[case]["input"]
    selector = h.PivotSelector()
    assert outcome(h.make_review(selector), value) == outcome(h.ORIGINAL.review, value)
    if case != "normal_control":
        assert any(e["route"] == "nonfinite" for e in selector.events)
        assert outcome(h.ORIGINAL.review, value) == ("ValueError", "numerical overflow")


@pytest.mark.parametrize("samples", [[0], [999], [-1], [], [None], [True]])
def test_wrong_or_invalid_samples_cannot_change_result(samples):
    selector = h.PivotSelector(sampler=lambda *_: samples)
    assert selector([[1.], [4.], [2.]], 0, 3) == 1
    assert selector.events[-1]["route"] == "fallback"


def test_tie_and_signed_zero_keep_first():
    selector = h.PivotSelector(sampler=lambda *_: [1])
    assert selector([[-0.], [0.]], 0, 2) == 0
    assert selector([[3.], [-3.]], 0, 2) == 0


def test_backend_and_compiler_failure_fallback(monkeypatch):
    def fail(*_args, **_kwargs):
        raise RuntimeError("injected offline failure")
    selector = h.PivotSelector(sampler=fail)
    assert selector([[1.], [4.]], 0, 2) == 1
    assert selector.events[-1]["route"] == "backend_error"
    monkeypatch.setattr(h, "transpile", fail)
    selector = h.PivotSelector()
    assert selector([[1.], [4.]], 0, 2) == 1
    assert selector.events[-1]["route"] == "construction_error"


@pytest.mark.parametrize("mode", ["solve", "inspect"])
def test_empty_and_inspect_do_not_call_quantum(mode):
    value = request([]) if mode == "solve" else request([[0., 0.], [0., 0.]])
    value["mode"] = mode
    selector = h.PivotSelector()
    assert outcome(h.make_review(selector), value) == outcome(h.ORIGINAL.review, value)
    assert selector.events == []


@pytest.mark.parametrize("field,value", [
    ("rhs", [True, 2]), ("matrix", [[1], [2]]), ("current", [float("nan"), 0]),
    ("variables", ["a", "a"]), ("residual_limit", -1), ("mode", "other"),
    ("rhs", [10**400, 1])])
def test_validation_precedes_quantum(field, value):
    data = request([[1., 0.], [0., 1.]])
    data[field] = value
    selector = h.PivotSelector()
    assert outcome(h.make_review(selector), data) == outcome(h.ORIGINAL.review, data)
    assert selector.events == []


@pytest.mark.parametrize("sign", [-1, 1])
def test_delta_overflow(sign):
    data = request([[1e-308]], [float(sign)])
    data["current"] = [-sign * 1e308]
    assert outcome(h.make_review(h.PivotSelector()), data) == outcome(h.ORIGINAL.review, data)


def test_size_guard():
    selector = h.PivotSelector()
    assert selector([[float(i)] for i in range(9)], 0, 9) == 8
    assert selector.events[-1]["route"] == "size_limit"


def test_cli_matches_original_success_and_failure():
    import subprocess
    import sys
    for data in (request([[0., 2.], [1., 3.]], [4., 7.]), request([[0.]])):
        payload = json.dumps(data)
        old = subprocess.run([sys.executable, "-B", str(h.SOURCE / "program.py")],
                             input=payload, text=True, capture_output=True)
        new = subprocess.run([sys.executable, "-B", "-m", "demo.lit009_end_to_end.hybrid"],
                             cwd=h.ROOT, input=payload, text=True, capture_output=True)
        assert old.returncode == new.returncode
        assert old.stdout == new.stdout
        if old.returncode:
            assert old.stderr.splitlines()[-1] == new.stderr.splitlines()[-1]
