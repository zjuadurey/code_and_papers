import pytest
from program import placement_report


def test_placement_report():
    jobs = [{"name": "a", "left_cost": 0, "right_cost": 2},
            {"name": "b", "left_cost": 0, "right_cost": 2}]
    assert placement_report(jobs, [(0, 1, 5)]) == {"cost": 2, "names": ["a", "b"], "count": 2}
    assert placement_report([], []) == {"cost": 0, "names": [], "count": 0}
    assert placement_report(jobs, [])["cost"] == 0
    with pytest.raises(ValueError, match="invalid placement link"):
        placement_report(jobs, [(0, 2, 3)])
