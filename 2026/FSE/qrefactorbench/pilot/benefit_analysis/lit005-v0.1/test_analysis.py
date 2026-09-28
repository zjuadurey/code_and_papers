"""Analytic edge cases complement finite source-derived diagnostics."""
import pytest
from analysis import build_oracle, enumerate_first, lex_dpll, prefix_repair


@pytest.mark.parametrize("n", [3, 4, 6])
def test_conjunction_chains_have_clean_scratch(n):
    # More than two controls exercises both forward and reverse scratch chains.
    oracle = build_oracle(n, [[(i, True)] for i in range(n)], {})
    for mask in range(1 << n):
        values = [bool(mask & (1 << i)) for i in range(n)]
        bits, phase = oracle.apply_basis(values)
        assert bits == values + [False] * (oracle.width - n)
        assert phase == (-1 if all(values) else 1)


def test_rank_order_after_nonprefix_locks():
    clauses = [[(0, True), (2, True)]]
    assert lex_dpll(3, clauses, {1: True}) == [False, True, True]
    assert prefix_repair(3, clauses, {1: True}, (True, True, True)) == (
        [False, True, True], 3)


def test_absence_requires_fallback_and_locked_witness_is_rejected():
    clauses = [[(0, True)], [(0, False)]]
    assert prefix_repair(1, clauses, {}, None) == (None, 2)
    assert prefix_repair(1, [], {0: False}, (True,)) == ([False], 2)


def test_known_example_resource_count_not_truth_table_encoding():
    from run import source_clauses
    result = build_oracle(3, source_clauses(), {}).resources()
    # Six flags twice + nine positive literals, each wrapped twice in compute
    # and twice in uncompute: X = 12 + 4*9 = 48. CCX = 2*6*3 + 2*9.
    assert result == {"logical_qubits": 14,
                      "gate_counts": {"X": 48, "CCX": 54, "Z": 1},
                      "serialized_gate_count": 103,
                      "constant_preprocessing_result": None}


def test_unit_propagation_and_lexicographic_branching():
    clauses = [[(0, True), (1, True)], [(1, False), (2, True)]]
    assert lex_dpll(3, clauses, {}) == [False, True, True]
    assert lex_dpll(3, [[(0, True)], [(0, False)]], {}) is None


def test_constant_oracle_is_classically_dispatchable():
    assert build_oracle(1, [[(0, True), (0, False)]], {}).constant is True
    assert build_oracle(1, [[(0, True)]], {0: False}).constant is False
    assert enumerate_first(0, [], {}) == ([], 1)
