from enum import IntEnum


class Label(IntEnum):
    K0 = 0
    K1 = 1
    Q = 2


K0, K1, Q = Label.K0, Label.K1, Label.Q


class AbstractState(list):
    """Labels plus a conservative accumulated numerical approximation budget."""
    numerical_error = 0.0


def initial(n):
    return AbstractState([K0] * n)
