import pytest
from htp.e2e.capacity import scaling_capacity_bytes


@pytest.mark.parametrize('n', [26, 28])
def test_capacity_covers_every_growth_transition(n):
    budget = scaling_capacity_bytes(n)
    file_rounding = 2 * (1 << (n - 12)) * 4096
    metadata = 512 * 2**20
    for new in range(1, n + 1):
        for old in range(new):
            assert (16 << old) + (16 << new) + file_rounding + metadata <= budget
    assert (16 << n) + file_rounding + metadata <= budget


def test_28_budget_is_nine_gib():
    assert scaling_capacity_bytes(28) == 9 * 2**30


@pytest.mark.parametrize('n,block', [(30, 4096), (28, 8192), (28, 0)])
def test_unsupported_geometry_refused(n, block):
    with pytest.raises(ValueError):
        scaling_capacity_bytes(n, block)
