"""Positive constructions and isolated semantic mutants, independent of new oracles."""
from fractions import Fraction
from itertools import combinations, product
import math
from typing import Any

from verification import ROOT, load, old_controls

linear_kernel = load('linear_trusted_control', ROOT / 'pilot/reference_completion/v0.1.1/cases/lit-009/kernel.py')
iteration_kernel = load('iteration_trusted_control', ROOT / 'pilot/reference_completion/v0.1.1/cases/lit-010/kernel.py')
color_kernel = load('color_trusted_control', ROOT / 'pilot/source_adaptations/v0.2-where/cases/lit-003/agenda.py')


class Polynomial:
    def __init__(self):
        self.terms = {}

    def add(self, coefficient, *indices):
        key = tuple(sorted(set(indices)))  # y_i^2 = y_i for binary variables.
        self.terms[key] = self.terms.get(key, 0) + Fraction(coefficient)

    def square(self, coefficients, constant, scale):
        self.add(scale * constant * constant)
        for i, a in enumerate(coefficients):
            self.add(scale * (a * a + 2 * constant * a), i)
            for j in range(i + 1, len(coefficients)):
                self.add(2 * scale * a * coefficients[j], i, j)

    def serialize(self):
        return [{'coefficient': str(value), 'variables': list(indices)} for indices, value in sorted(self.terms.items()) if value]


def equivalent(claim):
    n = claim['variable_count']
    transformed = Polynomial()
    for term in claim['terms']:
        indices = [n - 1 - i for i in term['variables']]
        for size in range(len(indices) + 1):
            for chosen in combinations(indices, size):
                transformed.add(3 * Fraction(term['coefficient']) * (-1) ** size, *chosen)
    transformed.add(7)
    claim.update(terms=transformed.serialize(), decode={'permutation': list(reversed(range(n))), 'complement': [1] * n})
    return claim


def optimization(kind: str, p: dict[str, Any], variant: str) -> dict[str, Any]:
    n = p['n']
    count = n + (p['capacity'].bit_length() if kind == 'knapsack' and variant != 'no_slack' else 0)
    poly = Polynomial()
    a = 2 ** n
    for i in range(n):
        poly.add((-1 if variant == 'wrong_tie' else 1) * 2 ** i, i)
    if kind == 'knapsack':
        for i, item in enumerate(p['items']):
            poly.add(-a * (1 if variant == 'ignore_values' else item['value']), i)
        if variant != 'ignore_capacity':
            coefficients = [item['weight'] for item in p['items']] + [2 ** j for j in range(count - n)]
            poly.square(coefficients, -p['capacity'], a * (sum(item['value'] for item in p['items']) + 1))
    else:
        for u, v, weight in p['pairs']:
            if variant == 'ignore_weights':
                weight = 1 if weight else 0
            if variant == 'round_weights':
                weight = int(float(weight))
            if variant == 'ignore_sign':
                weight = abs(weight)
            factor = a * weight * (2 if kind == 'signed' else 1)
            poly.add(-factor, u)
            poly.add(-factor, v)
            poly.add(2 * factor, u, v)
    claim = {'kind': kind, 'variable_count': count, 'decode': old_controls.identity(count),
             'sense': 'max' if variant == 'wrong_direction' else 'min', 'terms': poly.serialize()}
    return equivalent(claim) if variant == 'equivalent' else claim


def coloring(p: dict[str, Any], variant: str) -> dict[str, Any]:
    n, k = p['n'], p['colors']
    neighbors = {i: [v if i == u else u for u, v in p['edges'] if i in (u, v)] for i in range(n)}
    try:
        chosen = color_kernel.complete(neighbors, k)
    except ValueError:
        chosen = None
    if variant == 'greedy_absence':
        matrix = [[int(j in neighbors[i]) for j in range(n)] for i in range(n)]
        try:
            chosen = color_kernel.preview(matrix, k)
        except ValueError:
            chosen = None
    if variant in ('one_hot', 'one_hot_equivalent', 'missing_one_hot', 'negative_penalty'):
        count, poly = n * k, Polynomial()
        if variant != 'missing_one_hot':
            for i in range(n):
                coefficients = [int(i * k <= j < (i + 1) * k) for j in range(count)]
                poly.square(coefficients, -1, 1)
        for u, v in p['edges']:
            for color in range(k):
                poly.add(1, u * k + color, v * k + color)
        claim = {'kind': 'coloring', 'variable_count': count, 'decode': old_controls.identity(count),
                 'representation': 'one_hot_qubo', 'sense': 'min', 'terms': poly.serialize(), 'selected': chosen}
        if variant == 'negative_penalty':
            for term in claim['terms']:
                term['coefficient'] = str(-Fraction(term['coefficient']))
        if variant == 'one_hot_equivalent':
            equivalent(claim)
            claim['feasible_energy'] = '7'
        return claim
    width = max(1, (k - 1).bit_length())
    count = n * width
    decode = old_controls.identity(count) if variant != 'equivalent' else {
        'permutation': list(reversed(range(count))), 'complement': [1] * count}
    table = []
    for encoded in product((0, 1), repeat=count):
        bits = [encoded[decode['permutation'][i]] ^ decode['complement'][i] for i in range(count)]
        colors = [sum(bits[i * width + j] * 2 ** j for j in range(width)) for i in range(n)]
        valid_domain = variant == 'invalid_codes' or all(c < k for c in colors)
        valid_edges = variant == 'ignore_edges' or all(colors[u] != colors[v] for u, v in p['edges'])
        table.append(valid_domain and valid_edges)
    return {'kind': 'coloring', 'variable_count': count, 'decode': decode,
            'representation': 'binary_predicate', 'marked': table, 'selected': chosen}


def linear(p: dict[str, Any], variant: str) -> dict[str, Any]:
    if p['operation'] == 'pivot':
        active = range(p['start'], len(p['column']))
        key = (lambda i: p['column'][i]) if variant == 'signed_pivot' else lambda i: abs(p['column'][i])
        if variant == 'last_tie':
            active = reversed(list(active))
        result = {'pivot': max(active, key=key)}
    elif p['operation'] == 'solve':
        try:
            # Trusted original elimination; independent of determinant-based oracle.
            rhs = [0] * len(p['rhs']) if variant == 'ignore_rhs' else p['rhs']
            result = {'solution': linear_kernel.solve(p['matrix'], rhs)}
        except ValueError:
            result = {'error': 'ValueError'}
    else:
        result = linear_kernel.residual(p['matrix'], p['rhs'], p['x'])
    if variant == 'equivalent':
        result = dict(reversed(list(result.items())))
    return {'kind': 'linear', 'result': result}


def iteration(p: dict[str, Any], variant: str) -> dict[str, Any]:
    matrix = p['matrix']
    rows = [[(j, float(value)) for j, value in enumerate(row) if value] for row in matrix]
    steps = max(1, p['steps']) if variant == 'ignore_budget' else p['steps']
    x, initial, trace = iteration_kernel.advance(rows, p['rhs'], p['current'], steps, p['tolerance'])
    if variant == 'exact_substitution':
        x = linear_kernel.solve(matrix, p['rhs'])
    if variant == 'omit_trace':
        trace = []
    residual = [sum(v * x[j] for j, v in enumerate(row)) - b for row, b in zip(matrix, p['rhs'])]
    result = {'iterate': x, 'initial_norm': initial, 'trace': trace,
              'final_residual_norm': math.sqrt(sum(v * v for v in residual))}
    if variant == 'equivalent':
        result = dict(reversed(list(result.items())))
    return {'kind': 'iteration', 'result': result}


VARIANTS = {
    **old_controls.VARIANTS,
    'maxcut': ['correct', 'equivalent', 'ignore_weights', 'wrong_direction', 'round_weights'],
    'signed': ['correct', 'equivalent', 'ignore_sign', 'wrong_direction'],
    'knapsack': ['correct', 'equivalent', 'ignore_capacity', 'ignore_values', 'wrong_tie', 'no_slack'],
    'coloring': ['correct', 'equivalent', 'one_hot', 'one_hot_equivalent', 'ignore_edges', 'invalid_codes', 'missing_one_hot', 'greedy_absence', 'negative_penalty'],
    'linear': ['correct', 'equivalent', 'signed_pivot', 'last_tie', 'ignore_rhs'],
    'iteration': ['correct', 'equivalent', 'exact_substitution', 'ignore_budget', 'omit_trace'],
}


def submission(case: dict[str, Any], variant: str) -> dict[str, Any]:
    kind = case['oracle_kind']
    if kind in old_controls.VARIANTS:
        return old_controls.submission(case, variant)
    claims = {}
    for test in case['tests']:
        p = test['input']
        claims[test['id']] = (optimization(kind, p, variant) if kind in ('maxcut', 'signed', 'knapsack') else
                              coloring(p, variant) if kind == 'coloring' else
                              linear(p, variant) if kind == 'linear' else iteration(p, variant))
    return {'case_id': case['case_id'], 'claim_scope': case['claim_scope'], 'control': variant,
            'provenance': {'kind': 'synthetic_control', 'is_model_result': False,
                           'author': 'Codex-authored evaluator controls, not model results or expert labels'},
            'claims': claims}
