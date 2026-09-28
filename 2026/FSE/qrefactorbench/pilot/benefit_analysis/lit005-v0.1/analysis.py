"""Scoped, source-derived CNF diagnostic; no QPU or quantum state simulation."""
from collections import Counter
from dataclasses import dataclass
from itertools import product

Literal = tuple[int, bool]
Clauses = list[list[Literal]]
Gate = tuple[str, tuple[int, ...]]


def predicate(bits: tuple[bool, ...], clauses: Clauses, locks: dict[int, bool]) -> bool:
    return all(bits[i] == v for i, v in locks.items()) and all(
        any(bits[i] == v for i, v in clause) for clause in clauses)


def assignments(n: int, locks: dict[int, bool]):
    free = [i for i in range(n) if i not in locks]
    for values in product((False, True), repeat=len(free)):
        values_by_index = dict(zip(free, values))
        yield tuple(locks[i] if i in locks else values_by_index[i] for i in range(n))


def enumerate_first(n: int, clauses: Clauses, locks: dict[int, bool]):
    calls = 0
    for bits in assignments(n, locks):
        calls += 1
        if predicate(bits, clauses, locks):
            return list(bits), calls
    return None, calls


def prefix_repair(n: int, clauses: Clauses, locks: dict[int, bool], proposed):
    """Proposed is None or a Boolean assignment; the wrapper validates input first."""
    calls = int(proposed is not None)
    valid = proposed is not None and predicate(proposed, clauses, locks)
    for bits in assignments(n, locks):
        if valid and bits == tuple(proposed):
            return list(bits), calls
        calls += 1
        if predicate(bits, clauses, locks):
            return list(bits), calls
    return None, calls


def lex_dpll(n: int, clauses: Clauses, locks: dict[int, bool]):
    """Small exact comparator, NOT a competitive CDCL implementation."""
    def solve(fixed):
        fixed = dict(fixed)
        while True:
            units = []
            for clause in clauses:
                if any(i in fixed and fixed[i] == v for i, v in clause):
                    continue
                remaining = set((i, v) for i, v in clause if i not in fixed)
                if any((i, not v) in remaining for i, v in remaining):
                    continue
                if not remaining:
                    return None
                if len(remaining) == 1:
                    units.append(next(iter(remaining)))
            if not units:
                break
            for i, v in units:
                if i in fixed and fixed[i] != v:
                    return None
                fixed[i] = v
        if len(fixed) == n:
            return [fixed[i] for i in range(n)]
        i = next(i for i in range(n) if i not in fixed)
        for v in (False, True):
            answer = solve({**fixed, i: v})
            if answer is not None:
                return answer
        return None
    return solve(locks)


@dataclass
class Oracle:
    free: list[int]
    width: int
    gates: list[Gate]
    constant: bool | None

    def apply_basis(self, free_bits):
        bits = list(free_bits) + [False] * (self.width - len(self.free))
        phase = -1 if self.constant is True else 1
        for name, ids in self.gates:
            if name == "Z":
                if bits[ids[0]]:
                    phase *= -1
            elif all(bits[i] for i in ids[:-1]):
                bits[ids[-1]] = not bits[ids[-1]]
        return bits, phase

    def resources(self):
        return {"logical_qubits": self.width,
                "gate_counts": dict(sorted(Counter(g[0] for g in self.gates).items())),
                "serialized_gate_count": len(self.gates),
                "constant_preprocessing_result": self.constant}


def build_oracle(n: int, clauses: Clauses, locks: dict[int, bool]) -> Oracle:
    """Compile clauses, not a truth table or precomputed marked assignments.

    Implements |x,0> -> (-1)^CNF(x) |x,0> using X/CX/CCX/Z.
    Constant formulas are detected classically and require no quantum dispatch.
    """
    free = [i for i in range(n) if i not in locks]
    indices = {old: new for new, old in enumerate(free)}
    reduced = []
    for clause in clauses:
        if any(i in locks and locks[i] == v for i, v in clause):
            continue
        literals = set((indices[i], v) for i, v in clause if i not in locks)
        if any((i, not v) in literals for i, v in literals):
            continue
        if not literals:
            return Oracle(free, len(free), [], False)
        reduced.append(sorted(literals))
    if not reduced:
        return Oracle(free, len(free), [], True)
    flags = list(range(len(free), len(free) + len(reduced)))
    phase_bit = len(free) + len(reduced)
    scratch_size = max(0, max(len(reduced), max(map(len, reduced))) - 2)
    scratch = list(range(phase_bit + 1, phase_bit + 1 + scratch_size))
    gates = []

    def emit(name, *ids):
        gates.append((name, tuple(ids)))

    def mcx(controls, target):
        k = len(controls)
        if k <= 2:
            emit(("X", "CX", "CCX")[k], *controls, target)
            return
        chain = [("CCX", (controls[0], controls[1], scratch[0]))]
        for j in range(2, k - 1):
            chain.append(("CCX", (scratch[j - 2], controls[j], scratch[j - 1])))
        gates.extend(chain)
        emit("CCX", scratch[k - 3], controls[-1], target)
        gates.extend(reversed(chain))

    for literals, flag in zip(reduced, flags):
        emit("X", flag)
        # Literal (i, True) is false at 0: turn that into a positive control.
        for i, v in literals:
            if v:
                emit("X", i)
        mcx([i for i, _ in literals], flag)
        for i, v in literals:
            if v:
                emit("X", i)
    compute_clauses = list(gates)
    start = len(gates)
    mcx(flags, phase_bit)
    conjunction = gates[start:]
    emit("Z", phase_bit)
    gates.extend(reversed(conjunction))
    gates.extend(reversed(compute_clauses))
    return Oracle(free, phase_bit + 1 + scratch_size, gates, None)
