from copy import deepcopy
import pytest
from run import INSTANCE, circuit, probabilities, score, finish_cycle, program


def test_qaoa_improves_objective_and_phase_sign():
    _, gates, matrix = circuit(INSTANCE)
    probs = probabilities(gates, 4)
    assert sum(p * score(i, matrix) for i, p in enumerate(probs)) == pytest.approx(3)
    assert sum(probs) == pytest.approx(1)


@pytest.mark.parametrize('mask', range(16))
def test_all_measurement_outputs_preserve_task(mask):
    original = deepcopy(INSTANCE)
    result, _ = finish_cycle(INSTANCE, [mask])
    assert result == program.schedule(INSTANCE)
    assert INSTANCE == original


def test_canonical_pair_accepted_without_fallback():
    for mask in (5, 10):
        result, fallback = finish_cycle(INSTANCE, [mask])
        assert not fallback and result['windows'] == [['A', 'C'], ['B', 'D']]


def test_other_instance_uses_original_solver():
    request = {'equipment': ['x', 'y'], 'requirements': []}
    assert finish_cycle(request, [0]) == (program.schedule(request), True)


def test_no_samples_and_malformed_samples_use_fallback():
    for samples in ([], [16], [-1], [True], ['0101']):
        assert finish_cycle(INSTANCE, samples) == (program.schedule(INSTANCE), True)
