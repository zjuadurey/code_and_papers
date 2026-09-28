from program import exists_marked


def test_exists_marked():
    assert exists_marked([]) is False
    assert exists_marked([False, False]) is False
    assert exists_marked([False, True, True]) is True
