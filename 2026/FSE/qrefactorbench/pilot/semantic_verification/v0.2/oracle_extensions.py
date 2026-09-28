"""Independent finite mathematical oracles for the six remaining cases."""
from fractions import Fraction as F
from itertools import product
import math
from typing import Any


def optimum(kind: str, p: dict[str, Any]) -> list[int]:
    candidates = []
    for bits in product((0, 1), repeat=p['n']):
        selected = [i for i, bit in enumerate(bits) if bit]
        mask = sum(2 ** i for i in selected)
        if kind == 'knapsack':
            if sum(p['items'][i]['weight'] for i in selected) > p['capacity']:
                continue
            value = sum(p['items'][i]['value'] for i in selected)
        else:
            value = sum(w * (int(bits[u] != bits[v]) if kind == 'maxcut' else
                             (1 if bits[u] != bits[v] else -1)) for u, v, w in p['pairs'])
        candidates.append((-value, mask, selected))
    return min(candidates)[2]


def color_solutions(p: dict[str, Any]) -> list[list[int]]:
    return [list(colors) for colors in product(range(p['colors']), repeat=p['n'])
            if all(colors[u] != colors[v] for u, v in p['edges'])]


def linear(p: dict[str, Any]) -> dict[str, Any]:
    op = p['operation']
    if op == 'pivot':
        col, start = p['column'], p['start']
        return {'pivot': min(range(start, len(col)), key=lambda i: (-abs(col[i]), i))}
    if op == 'solve':
        a, b = p['matrix'], p['rhs']
        if not b:
            return {'solution': []}
        if len(b) == 1:
            return {'error': 'ValueError'} if a[0][0] == 0 else {'solution': [float(F(b[0]) / F(a[0][0]))]}
        # Cramer's rule is independent of the original pivoted elimination.
        det = F(a[0][0]) * F(a[1][1]) - F(a[0][1]) * F(a[1][0])
        if not det:
            return {'error': 'ValueError'}
        return {'solution': [float((F(b[0]) * F(a[1][1]) - F(a[0][1]) * F(b[1])) / det),
                             float((F(a[0][0]) * F(b[1]) - F(b[0]) * F(a[1][0])) / det)]}
    a, b, x = p['matrix'], p['rhs'], p['x']
    vector = [sum(F(v) * F(x[j]) for j, v in enumerate(row)) - F(rhs) for row, rhs in zip(a, b)]
    norm = max(map(abs, vector), default=F(0))
    a_norm = max((sum(map(lambda v: abs(F(v)), row)) for row in a), default=F(0))
    denominator = F(1, 2 ** 52) * (a_norm * max(map(lambda v: abs(F(v)), x), default=F(0))
                                  + max(map(lambda v: abs(F(v)), b), default=F(0))) * len(b)
    return {'vector': list(map(float, vector)), 'infinity_norm': float(norm),
            'scaled_backward_error': float(norm / denominator) if denominator else (0.0 if norm == 0 else None)}


def iteration(p: dict[str, Any]) -> dict[str, Any]:
    """Closed-form zero/one-step evidence, NOT a second implementation of general CG.

    Fixtures use dyadic intermediate arithmetic. We do not introduce a universal
    floating tolerance or equate exact rational CG with binary64 on arbitrary inputs.
    """
    a, x = p['matrix'], list(map(F, p['current']))
    r = [F(b) - sum(F(v) * x[j] for j, v in enumerate(row)) for row, b in zip(a, p['rhs'])]
    rr = sum(v * v for v in r)
    initial, trace = math.sqrt(float(rr)), []
    if rr and p['steps'] and p['tolerance'] < 1:
        if p['steps'] != 1:
            raise ValueError('This oracle only covers zero or one effective iteration')
        denominator = sum(r[i] * F(a[i][j]) * r[j] for i in range(len(r)) for j in range(len(r)))
        alpha = rr / denominator
        x = [v + alpha * residual for v, residual in zip(x, r)]
        residual = [F(b) - sum(F(v) * x[j] for j, v in enumerate(row)) for row, b in zip(a, p['rhs'])]
        norm = math.sqrt(float(sum(v * v for v in residual)))
        trace = [{'iteration': 1, 'residual_norm': norm}]
    final = [sum(F(v) * x[j] for j, v in enumerate(row)) - F(b) for row, b in zip(a, p['rhs'])]
    return {'iterate': list(map(float, x)), 'initial_norm': initial, 'trace': trace,
            'final_residual_norm': math.sqrt(float(sum(v * v for v in final)))}


def expected(kind: str, problem: dict[str, Any]) -> Any:
    if kind in ('maxcut', 'signed', 'knapsack'):
        return optimum(kind, problem)
    if kind == 'coloring':
        solutions = color_solutions(problem)
        return {'solutions': solutions, 'first': solutions[0] if solutions else None}
    if kind == 'linear':
        return linear(problem)
    if kind == 'iteration':
        return iteration(problem)
    raise ValueError(f'Unsupported extension kind: {kind}')
