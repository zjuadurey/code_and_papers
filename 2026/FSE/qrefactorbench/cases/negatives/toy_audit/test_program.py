from program import inspect_flags


def test_audit_semantics():
    audit = [99]
    assert inspect_flags([False, True, False], audit) is True
    assert audit == [99, 0, 1, 2]
    assert inspect_flags([], audit) is False
    assert audit == [99, 0, 1, 2]
