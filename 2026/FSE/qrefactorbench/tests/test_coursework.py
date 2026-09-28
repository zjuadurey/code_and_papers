"""Coursework-only input boundaries and actual execution, no benchmark changes."""
import pytest

from coursework.app import run_request, source_data


@pytest.mark.parametrize("payload", [{"n": 7, "clauses": []}, {"n": True, "clauses": []},
    {"n": 2, "clauses": [[0]]}, {"n": 2, "clauses": [[3]]},
    {"n": 2, "clauses": [[1]] * 9}, {"n": 2, "clauses": ["code"]}])
def test_reject_unbounded_or_invalid_request(payload):
    with pytest.raises(ValueError):
        run_request(payload)


def test_actual_coursework_run_and_replay_provenance():
    pytest.importorskip("qiskit")
    result = run_request({"n": 3, "clauses": [[1], [-1]]})
    assert result["semantic_check"] and result["classical_fallback"]
    assert result["quantum_executed"] and not result["model_called"]
    assert sum(result["counts"].values()) == 16
    data = source_data()
    assert data["pilot-001"]["prediction_mode"] == "historical_replay_not_ground_truth"
    assert data["pilot-002"]["retained_execution"]["passed"]
