from program import has_assignment


def test_clause_semantics():
    assert has_assignment(0, []) is True
    assert has_assignment(0, [[]]) is False
    assert has_assignment(1, [[1], [-1]]) is False
    assert has_assignment(3, [[1, 2], [-2, 3], [-1, -3]]) is True
