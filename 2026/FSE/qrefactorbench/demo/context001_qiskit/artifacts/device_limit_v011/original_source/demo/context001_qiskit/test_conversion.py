"""Deterministic circuit/decoding checks; no statistical success threshold."""

import cmath
from copy import deepcopy
import json
from pathlib import Path

import pytest
from qiskit.quantum_info import Statevector

from demo.context001_qiskit import hybrid_program as hybrid
from demo.context001_qiskit import maintenance

MATRIX = [[0, 4, 1], [4, 0, 3], [1, 3, 0]]


@pytest.mark.parametrize("mask", range(8))
def test_cost_phase_and_hamiltonian_match_classical_conflict(mask):
    bits = [(mask >> i) & 1 for i in range(3)]
    cost = sum(MATRIX[i][j] for i in range(3) for j in range(i + 1, 3) if bits[i] == bits[j])
    basis = Statevector.from_int(mask, 8)
    assert basis.expectation_value(hybrid.cost_operator(MATRIX)).real == pytest.approx(cost / 8)
    gamma = 0.73
    actual = basis.evolve(hybrid.cost_layer(MATRIX, gamma)).data
    assert actual[mask] == pytest.approx(cmath.exp(-1j * gamma * (cost / 8 - 0.5)), abs=1e-12)
    assert sum(abs(actual[i]) ** 2 for i in range(8) if i != mask) == pytest.approx(0)


def test_counts_endianness_and_only_sampled_tie_resolution():
    assert hybrid.select_sample(MATRIX, {"010": 1, "101": 2}) == (2, [[1], [0, 2]])
    # Do not manufacture the canonical mask 2 if only its complement was sampled.
    assert hybrid.select_sample(MATRIX, {"101": 1}) == (5, [[0, 2], [1]])
    assert hybrid.select_sample(MATRIX, {"001": 1}) == (1, [[0], [1, 2]])


def test_nonoptimal_sample_is_not_secretly_repaired(monkeypatch):
    def forbidden(*_args):
        raise AssertionError("Original exact optimizer must not run in the quantum branch")

    monkeypatch.setattr(maintenance, "maxcut_bruteforce", forbidden)
    mask, windows = hybrid.select_sample(MATRIX, {"000": 1})
    assert mask == 0 and windows == [[], [0, 1, 2]]
    monkeypatch.setattr(hybrid, "solve", lambda _matrix: (windows, {"injected_test_sample": True}))
    request = {"equipment": ["a", "b", "c"], "requirements": [
        {"first": "a", "second": "b", "weight": 4},
        {"first": "b", "second": "c", "weight": 3},
        {"first": "a", "second": "c", "weight": 1}], "current_windows": [["a", "b", "c"], []]}
    before = deepcopy(request)
    report = hybrid.review_schedule(request)
    assert report["proposed"]["conflict_weight"] == 8  # Optimum is 1; failure remains visible.
    assert request == before


@pytest.mark.parametrize("payload", [None, {}, {
    "equipment": ["a"], "requirements": [], "current_windows": [[], []]}])
def test_invalid_input_rejected_before_quantum_execution(payload, monkeypatch):
    monkeypatch.setattr(hybrid, "solve", lambda *_args: pytest.fail("Should validate before solving"))
    with pytest.raises(ValueError):
        hybrid.review_schedule(payload)


def test_empty_input_and_explicit_prototype_limits():
    report, trace = hybrid.review_schedule_with_trace({"equipment": [], "requirements": [], "current_windows": [[], []]})
    assert report["proposed"]["conflict_weight"] == 0
    assert trace["quantum_executed"] is False
    with pytest.raises(NotImplementedError):
        hybrid.solve([[0] * 7 for _ in range(7)])
    with pytest.raises(NotImplementedError):
        hybrid.solve([[0, 2**50], [2**50, 0]])


def test_recorded_first_attempt_counts_and_resource_accounting():
    path = Path(__file__).with_name("artifacts") / "first_run.json"
    record = json.loads(path.read_text())
    assert record["retry_count"] == 0 and len(record["cases"]) == 5
    for case in record["cases"]:
        assert case["execution_success"]
        trace = case["trace"]
        assert not trace["exact_fallback_used"]
        if trace["quantum_executed"]:
            assert sum(trace["counts"].values()) == record["protocol"]["shots"]
            assert trace["resources"]["num_qubits"] == len(case["input"]["equipment"])
            assert trace["resources"]["measurement_count"] == len(case["input"]["equipment"])
            assert trace["optimizer_evaluations"] == len(trace["optimizer_trace"])
