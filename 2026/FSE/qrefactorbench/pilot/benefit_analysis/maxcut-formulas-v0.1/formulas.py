"""Structure-derived QAOA resources and conditional exact-output benefit formulas."""
from __future__ import annotations

import math
import random
from collections import Counter

import numpy as np

Edge = tuple[int, int, int]
Gate = tuple[str, tuple[int, ...], float | None]


def graph(n: int, seed: int) -> list[Edge]:
    if n < 3:
        raise ValueError('graph generator needs n >= 3')
    rng = random.Random(seed+n)
    pairs = {tuple(sorted((i, (i+1) % n))) for i in range(n)} | {(0, 2)}
    while len(pairs) < min(2*n, n*(n-1)//2):
        pairs.add(tuple(sorted(rng.sample(range(n), 2))))
    return [(u, v, rng.randint(1, 5)) for u, v in sorted(pairs)]


def matchings(edges: list[Edge]) -> list[list[Edge]]:
    groups: list[list[Edge]] = []
    occupied: list[set[int]] = []
    for edge in edges:
        u, v, _ = edge
        for i, used in enumerate(occupied):
            if u not in used and v not in used:
                groups[i].append(edge)
                used.update((u, v))
                break
        else:
            groups.append([edge])
            occupied.append({u, v})
    return groups


def resources(n: int, m: int, p: int, colors: int) -> dict:
    if n < 1 or m < 0 or p < 0 or colors < 0:
        raise ValueError('Invalid resource dimensions')
    counts = {'h': n, 'cx': 2*p*m, 'rz': p*m, 'rx': p*n, 'measure': n}
    return {'logical_qubits': n, 'counts': counts,
            'unitary_gate_count': n+p*(3*m+n),
            'scheduled_depth_with_measurement': 2+p*(3*colors+1),
            'two_qubit_layers': 2*p*colors,
            'scope': 'Explicit matching-barrier schedule, pre-synthesis, all-to-all logical connectivity; not optimized physical depth'}


def layers(n: int, edges: list[Edge], p: int) -> list[list[Gate]]:
    result: list[list[Gate]] = [[('h', (i,), None) for i in range(n)]]
    for _ in range(p):
        for group in matchings(edges):
            result.extend([
                [('cx', (u, v), None) for u, v, _ in group],
                [('rz', (v,), -w*math.pi/4) for u, v, w in group],
                [('cx', (u, v), None) for u, v, _ in group],
            ])
        result.append([('rx', (i,), math.pi/4) for i in range(n)])
    result.append([('measure', (i,), None) for i in range(n)])
    return result


def qasm(n: int, edges: list[Edge], p: int) -> str:
    text = ['OPENQASM 3.0;', 'include "stdgates.inc";', f'qubit[{n}] q;', f'bit[{n}] r;']
    for layer in layers(n, edges, p):
        for name, bits, angle in layer:
            if name == 'measure':
                text.append(f'r[{bits[0]}] = measure q[{bits[0]}];')
            elif name == 'cx':
                text.append(f'cx q[{bits[0]}], q[{bits[1]}];')
            elif name == 'rz':
                # Preserve exact pi multiples rather than float angle synthesis.
                text.append(f'rz(-{round(-angle*4/math.pi)}*pi/4) q[{bits[0]}];')
            elif name == 'rx':
                text.append(f'rx(pi/4) q[{bits[0]}];')
            else:
                text.append(f'{name} q[{bits[0]}];')
    return '\n'.join(text)+'\n'


def costs(n: int, edges: list[Edge]) -> np.ndarray:
    if n > 16:
        raise ValueError('Small-state validation is capped at 16 qubits')
    indices = np.arange(1 << n)
    return sum((w*(((indices >> u) ^ (indices >> v)) & 1) for u, v, w in edges),
               np.zeros(1 << n, dtype=int))


def rx(state: np.ndarray, bit: int, theta: float) -> None:
    indices = np.arange(len(state))
    lo = indices[(indices & (1 << bit)) == 0]
    hi = lo | (1 << bit)
    a, b = state[lo].copy(), state[hi].copy()
    cosine, sine = math.cos(theta/2), -1j*math.sin(theta/2)
    state[lo], state[hi] = cosine*a+sine*b, sine*a+cosine*b


def hamiltonian_state(n: int, edges: list[Edge], p: int,
                      gamma: float = math.pi/4, beta: float = math.pi/8) -> np.ndarray:
    score = costs(n, edges)
    state = np.ones(1 << n, dtype=complex)/math.sqrt(1 << n)
    for _ in range(p):
        state *= np.exp(-1j*gamma*score)
        for i in range(n):
            rx(state, i, 2*beta)
    return state


def gate_state(n: int, edges: list[Edge], p: int) -> np.ndarray:
    if n > 16:
        raise ValueError('Small-state validation is capped at 16 qubits')
    state = np.zeros(1 << n, dtype=complex)
    state[0] = 1
    indices = np.arange(len(state))
    for layer in layers(n, edges, p):
        for name, bits, angle in layer:
            if name == 'cx':
                a = indices[((indices >> bits[0]) & 1 == 1) & ((indices >> bits[1]) & 1 == 0)]
                b = a | (1 << bits[1])
                state[a], state[b] = state[b].copy(), state[a].copy()
            elif name == 'rz':
                state *= np.exp((-1j*angle/2)*(1-2*((indices >> bits[0]) & 1)))
            elif name == 'rx':
                rx(state, bits[0], angle)
            elif name == 'h':
                a = indices[(indices & (1 << bits[0])) == 0]
                b = a | (1 << bits[0])
                left, right = state[a].copy(), state[b].copy()
                state[a], state[b] = (left+right)/math.sqrt(2), (left-right)/math.sqrt(2)
    return state


def batch_success(s: float, shots: int) -> float:
    if not 0 <= s <= 1 or type(shots) is not int or shots < 1:
        raise ValueError('Expected probability and positive integer shots')
    return 1.0 if s == 1 else -math.expm1(shots*math.log1p(-s))


def expected_time(s: float, shots: int, shot_seconds: float, fixed_seconds: float,
                  per_shot_seconds: float, fallback_seconds: float) -> float:
    if any(not math.isfinite(x) or x < 0 for x in
           (shot_seconds, fixed_seconds, per_shot_seconds, fallback_seconds)):
        raise ValueError('Costs must be finite and nonnegative')
    return fixed_seconds+shots*(shot_seconds+per_shot_seconds)+(1-batch_success(s, shots))*fallback_seconds


def required_success(shots: int, shot_seconds: float, fixed_seconds: float,
                     per_shot_seconds: float, classical_seconds: float,
                     fallback_seconds: float | None = None) -> dict:
    """Strict benefit threshold for iid certified shots and paid exact fallback."""
    fallback = classical_seconds if fallback_seconds is None else fallback_seconds
    expected_time(0, shots, shot_seconds, fixed_seconds, per_shot_seconds, fallback)
    if not math.isfinite(classical_seconds) or classical_seconds <= 0:
        raise ValueError('Classical baseline must be positive and finite')
    paid = fixed_seconds+shots*(shot_seconds+per_shot_seconds)
    if paid >= classical_seconds:
        return {'status': 'impossible_at_this_budget', 's_strictly_greater_than': None}
    if fallback == 0 or paid+fallback < classical_seconds:
        return {'status': 'all_probabilities', 's_strictly_greater_than': None}
    target = (paid+fallback-classical_seconds)/fallback
    threshold = -math.expm1(math.log1p(-target)/shots)
    return {'status': 'conditional', 's_strictly_greater_than': threshold,
            'batch_success_strictly_greater_than': target,
            'paid_before_fallback_seconds': paid}


def conservative_certified_probability(ideal_exact_pair: float, error_bound: float) -> float:
    """Conditional lower bound if logical error bound controls output event deviation.

    Requires a sound, complete certificate for the target canonical optimum pair.
    Does not implement that certificate or infer it from QDK's physical error model.
    """
    if not 0 <= ideal_exact_pair <= 1 or not 0 <= error_bound <= 1:
        raise ValueError('Expected probabilities')
    return max(0.0, ideal_exact_pair-error_bound)


def verify_structure(n: int, edges: list[Edge], p: int) -> dict:
    schedule = layers(n, edges, p)
    predicted = resources(n, len(edges), p, len(matchings(edges)))
    observed = Counter(name for layer in schedule for name, _, _ in layer)
    assert {name: observed[name] for name in predicted['counts']} == predicted['counts']
    assert len(schedule) == predicted['scheduled_depth_with_measurement']
    for layer in schedule:
        used = [i for _, bits, _ in layer for i in bits]
        assert len(used) == len(set(used))
    degree = Counter(v for u, v, _ in edges)+Counter(u for u, v, _ in edges)
    assert not degree or len(matchings(edges)) <= 2*max(degree.values())-1
    return predicted
