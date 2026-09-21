from program import materialize


def test_full_output_and_aliasing():
    rows = [[1, -1], [0, 0], []]
    output = materialize(rows, 2)
    assert output == [[0.5, -0.5], [0.5, -0.5], [0.0, 0.0], [0.0, 0.0], [], []]
    output[0][0] = 9
    assert output[1][0] == 0.5
    assert rows == [[1, -1], [0, 0], []]
    assert materialize(rows, 0) == []
