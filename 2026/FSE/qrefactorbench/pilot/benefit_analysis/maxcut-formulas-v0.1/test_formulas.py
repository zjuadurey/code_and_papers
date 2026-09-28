import itertools
import math

import numpy as np
import pytest

import formulas as f


def test_single_edge_closed_form():
    # Exact two-qubit formula independently derived from the four amplitudes.
    for gamma, beta in itertools.product((0, .3, math.pi/2), (0, .2, math.pi/8)):
        state = f.hamiltonian_state(2, [(0, 1, 1)], 1, gamma, beta)
        probability = float(abs(state[1])**2+abs(state[2])**2)
        assert probability == pytest.approx((1+math.sin(4*beta)*math.sin(gamma))/2)


def test_all_four_node_graphs_counts_unitary_and_symmetry():
    pairs = list(itertools.combinations(range(4), 2))
    for mask in range(64):
        edges = [(u, v, 1+i % 3) for i, (u, v) in enumerate(pairs) if mask & (1 << i)]
        for depth in (0, 1, 2):
            f.verify_structure(4, edges, depth)
            a, b = f.hamiltonian_state(4, edges, depth), f.gate_state(4, edges, depth)
            assert abs(np.vdot(a, b))**2 == pytest.approx(1, abs=1e-12)
            assert np.abs(a)**2 == pytest.approx(np.abs(a[::-1])**2)


def test_probability_and_cost_against_enumerated_outcomes():
    for s, shots in itertools.product((0, .01, .2, .9, 1), (1, 2, 5)):
        q = total = 0.0
        for outcome in itertools.product((False, True), repeat=shots):
            probability = math.prod(s if x else 1-s for x in outcome)
            q += probability*any(outcome)
            total += probability*(.02+shots*(.003+.001)+(0 if any(outcome) else .7))
        assert f.batch_success(s, shots) == pytest.approx(q)
        assert f.expected_time(s, shots, .003, .02, .001, .7) == pytest.approx(total)


@pytest.mark.parametrize('fallback', [.2, 1., 2.])
def test_inverse_strict_threshold(fallback):
    answer = f.required_success(10, .01, .1, .002, 1, fallback)
    if answer['status'] == 'all_probabilities':
        assert f.expected_time(0, 10, .01, .1, .002, fallback) < 1
    else:
        s = answer['s_strictly_greater_than']
        assert f.expected_time(s, 10, .01, .1, .002, fallback) == pytest.approx(1)
        assert f.expected_time(s+1e-6, 10, .01, .1, .002, fallback) < 1
        assert f.expected_time(s-1e-6, 10, .01, .1, .002, fallback) > 1


def test_impossible_and_zero_threshold_boundaries():
    assert f.required_success(10, .1, 0, 0, 1)['status'] == 'impossible_at_this_budget'
    assert f.required_success(1, 0, 0, 0, 1)['s_strictly_greater_than'] == 0
    assert f.required_success(1, 0, 0, 0, 1, 0)['status'] == 'all_probabilities'
    assert f.conservative_certified_probability(.005, .01) == 0
    with pytest.raises(ValueError):
        f.gate_state(100, [], 1)
    with pytest.raises(ValueError):
        f.batch_success(.1, 0)


def test_symbolic_scaling_without_state_allocation():
    for n, depth in itertools.product((100, 200, 500), (1, 4, 16)):
        edges = f.graph(n, 20260928)
        observed = f.verify_structure(n, edges, depth)
        assert observed['unitary_gate_count'] == n*(1+7*depth)
        assert observed['logical_qubits'] == n
