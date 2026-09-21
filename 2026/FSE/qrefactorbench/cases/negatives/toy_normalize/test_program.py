from program import normalize_label


def test_normalize_label():
    assert normalize_label(' A ') == 'a'
    assert normalize_label('') == ''
