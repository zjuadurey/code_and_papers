import pytest
from program import has_code


def test_small_lookup():
    assert has_code([], 4) is False
    assert has_code([3, 4, 4], 4) is True
    assert has_code(list(range(8)), 9) is False
    with pytest.raises(ValueError, match="at most eight"):
        has_code(list(range(9)), 0)
