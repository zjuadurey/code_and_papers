"""Classical eight-bit operation specified in Qiskit HumanEval task 53.

New classical implementation; no circuit/simulator code imported.
"""


def encode(a, b):
    value = a ^ b
    return value, format(value, "08b")
