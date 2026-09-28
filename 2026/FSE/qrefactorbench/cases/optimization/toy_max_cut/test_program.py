from program import format_label, max_cut_score


def test_max_cut_score():
    assert max_cut_score(0, []) == 0
    assert max_cut_score(3, [(0, 1), (1, 2), (2, 0)]) == 2
    assert max_cut_score(4, [(0, 1), (1, 2), (2, 3)]) == 3
    assert format_label(' graph ') == 'GRAPH'
