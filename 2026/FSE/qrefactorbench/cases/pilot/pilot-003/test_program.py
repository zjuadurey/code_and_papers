from program import best_partition_score


def test_weighted_partition():
    assert best_partition_score(0, []) == 0
    assert best_partition_score(3, [(0, 1, 3), (1, 2, 2), (2, 0, 1)]) == 5
    assert best_partition_score(2, [(0, 0, 9), (0, 1, 2), (0, 1, 3)]) == 5
    assert best_partition_score(3, [(0, 1, 0)]) == 0
