"""Finite feature assignments; newly authored from an attributed task definition."""
from itertools import product


def conforms(values, clauses, locked):
    return all(values[i] == value for i, value in locked.items()) and all(
        any(values[i] == value for i, value in clause) for clause in clauses)


def complete(size, clauses, locked):
    for values in product((False, True), repeat=size):
        if conforms(values, clauses, locked):
            return list(values)
    return None
