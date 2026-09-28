from program import has_total


def test_subset_total():
    assert has_total([], 0) is True
    assert has_total([], 1) is False
    assert has_total([3, -2, 8], 1) is True
    assert has_total([2, 2], 4) is True
    assert has_total([2, 4], 3) is False
