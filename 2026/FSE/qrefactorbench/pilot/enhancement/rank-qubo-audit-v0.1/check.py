"""Post-hoc exact audit of one quote-bound rank QUBO; no model execution."""
from fractions import Fraction
from itertools import product
import math
from typing import Sequence


def rank_costs(values: Sequence[float]) -> list[int]:
    if not values or len(values) > 12 or not all(math.isfinite(v) for v in values):
        raise ValueError("Audit admits 1..12 finite pivot magnitudes only")
    magnitudes = [abs(v) for v in values]
    return [sum(magnitudes[k] > magnitudes[i] or
                (magnitudes[k] == magnitudes[i] and k < i)
                for k in range(len(values))) for i in range(len(values))]


def energy(costs: Sequence[int], bits: Sequence[int], penalty: Fraction) -> Fraction:
    return sum(c * z for c, z in zip(costs, bits)) + penalty * (sum(bits) - 1) ** 2


def expanded_energy(costs: Sequence[int], bits: Sequence[int], penalty: Fraction) -> Fraction:
    return (penalty + sum((c - penalty) * z for c, z in zip(costs, bits))
            + sum(2 * penalty * bits[i] * bits[k]
                  for i in range(len(bits)) for k in range(i + 1, len(bits))))


def check_instance(values: Sequence[float], penalty: Fraction) -> dict:
    if type(penalty) is not Fraction or penalty <= 0:
        raise ValueError("A positive exact rational penalty is required")
    costs = rank_costs(values)
    assignments = list(product((0, 1), repeat=len(values)))
    energies = [energy(costs, bits, penalty) for bits in assignments]
    expansion_matches = all(e == expanded_energy(costs, bits, penalty)
                            for bits, e in zip(assignments, energies))
    minimum = min(energies)
    winners = [bits for bits, e in zip(assignments, energies) if e == minimum]
    original = max(range(len(values)), key=lambda i: abs(values[i]))
    expected = tuple(int(i == original) for i in range(len(values)))
    return {"costs": costs, "original_offset": original,
            "minimizers": [list(bits) for bits in winners], "minimum_energy": str(minimum),
            "assignments": len(assignments), "expansion_matches": expansion_matches,
            "unique_correct_one_hot": winners == [expected]}
