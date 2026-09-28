from fractions import Fraction
from itertools import product
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import check_instance, energy, expanded_energy, rank_costs


@pytest.mark.parametrize("values,expected", [([2.0, -2.0, 1.0], [0, 1, 2]),
    ([-0.0, 0.0], [0, 1]), ([1.0, -2.0, 2.0], [2, 0, 1]), ([0.0], [0]),
    ([5e-324, 1.7976931348623157e308], [1, 0])])
def test_order_and_ties(values, expected):
    assert rank_costs(values) == expected
    for p in (Fraction(1, 10), Fraction(1), Fraction(7)):
        result = check_instance(values, p)
        assert result["unique_correct_one_hot"] and result["expansion_matches"]


@pytest.mark.parametrize("values", [[], [0.0] * 13, [float('nan')],
    [float('inf'), 0.0], [0.0, float('-inf')]])
def test_admission_retains_guard_and_work_bound(values):
    with pytest.raises(ValueError):
        rank_costs(values)


@pytest.mark.parametrize("p", [Fraction(0), Fraction(-1), 1.0, 1])
def test_penalty_admission(p):
    with pytest.raises(ValueError):
        check_instance([1.0], p)


def test_absent_tie_term_admits_wrong_pivot():
    # Mutation c_i counts strictly greater only: both tied rows obtain rank zero.
    costs = [0, 0]
    winners = [b for b in product((0, 1), repeat=2) if energy(costs, b, Fraction(1)) == 0]
    assert winners == [(0, 1), (1, 0)]


def test_zero_penalty_admits_empty_decoder():
    assert energy([0], [0], Fraction(0)) == energy([0], [1], Fraction(0))


def test_negative_penalty_rewards_infeasibility():
    assert energy([0], [0], Fraction(-1)) < energy([0], [1], Fraction(-1))


def test_expansion_factor_mutation_is_detectable():
    bits, costs, p = (1, 1), [0, 1], Fraction(1)
    wrong_pair_coefficient = p + sum((c-p)*z for c,z in zip(costs,bits)) + p
    assert wrong_pair_coefficient != energy(costs, bits, p)
    assert expanded_energy(costs, bits, p) == energy(costs, bits, p)
