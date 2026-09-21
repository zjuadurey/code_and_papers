from program import minimum_energy


def test_quadratic_minimum():
    assert minimum_energy([], []) == 0
    assert minimum_energy([-2, -2], [(0, 1, 5)]) == -2
    assert minimum_energy([-2, -2], [(0, 1, -1)]) == -5
    assert minimum_energy([2], [(0, 0, -3)]) == -1
    assert minimum_energy([1, 1], [(0, 1, -2), (0, 1, -3)]) == -3
