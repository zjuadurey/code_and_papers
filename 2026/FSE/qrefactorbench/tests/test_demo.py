"""Actual reversible-oracle and original-interface checks for the local demo."""

import itertools

import pytest

from demo.hybrid_search import (ORIGINAL, build_phase_oracle, has_assignment,
                                load_original, normalize_clauses, run_hybrid)


def test_oracle_phase_and_clean_workspace_exhaustively():
    pytest.importorskip("qiskit")
    import numpy as np
    from qiskit.quantum_info import Statevector

    clauses = [[1], [-1], [2], [-2], [1, 2], [-1, 2], [1, -2], [-1, -2]]
    for formula in itertools.chain(([c] for c in clauses), itertools.combinations(clauses, 2)):
        circuit = build_phase_oracle(2, list(formula))
        for mask in range(4):
            state = Statevector.from_int(mask, 2 ** circuit.num_qubits).evolve(circuit)
            expected = np.zeros(2 ** circuit.num_qubits, dtype=complex)
            expected[mask] = -1 if ORIGINAL.satisfies(mask, formula) else 1
            # Compare relative phase exactly, not only probabilities/global equivalence.
            assert np.allclose(state.data, expected, atol=1e-10)


@pytest.mark.parametrize("n,clauses", [(0, []), (0, [[]]), (1, [[1], [-1]]),
    (3, [[1, 2], [-2, 3], [-1, -3]]), (2, [[1, 1], [-1, 1]]),
    (2, [[-2, -2]]), (2, [[1, -1]]), (7, [[7]]), (2, [[1]] * 14)])
def test_hybrid_preserves_bool_and_inputs(n, clauses):
    pytest.importorskip("qiskit")
    import copy

    before = copy.deepcopy(clauses)
    result = has_assignment(n, clauses)
    assert type(result) is bool
    assert result == ORIGINAL.has_assignment(n, clauses)
    assert clauses == before


def test_quantum_success_and_failed_search_fallback():
    pytest.importorskip("qiskit")
    success = run_hybrid(3, [[1], [2], [3]])
    assert success["quantum_executed"] and success["witness"] == 7
    assert not success["classical_fallback"]
    failure = run_hybrid(3, [[1], [-1]])
    assert failure["quantum_executed"] and failure["classical_fallback"]
    assert failure["output"] is False
    # A missed sample on a satisfiable input must still return true.
    for seed in range(30):
        missed = run_hybrid(3, [[1], [2], [3]], seed=seed, shots=1)
        if missed["classical_fallback"]:
            assert missed["output"] is True
            break
    else:
        pytest.fail("Expected a reproducible missed witness to exercise exact fallback")


def test_retained_classical_callback_exception_stops_processing():
    seen = []

    def audit(index, digest):
        seen.append(index)
        raise RuntimeError("stop")

    with pytest.raises(RuntimeError, match="stop"):
        load_original("pilot-002").ledger_digest([b"first", b"second"], audit)
    assert seen == [0]


def test_normalization_and_original_error_behavior():
    assert normalize_clauses([[1, 1], [-1, 1], []]) == [[1], []]
    with pytest.raises(ValueError):
        has_assignment(-1, [])
    with pytest.raises(TypeError):
        has_assignment("invalid", [])
