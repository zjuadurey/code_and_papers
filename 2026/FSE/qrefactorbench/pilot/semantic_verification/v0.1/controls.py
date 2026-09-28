"""Reviewed synthetic controls. These compile claims, never expected answers.

Positive constructions and individual mutants are separate from definition oracles.
Not model responses, new benchmark tasks, or quantum executions.
"""
from fractions import Fraction
from itertools import combinations, product
from typing import Any


def identity(n: int) -> dict[str, list[int]]:
    return {'permutation': list(range(n)), 'complement': [0] * n}


def graph_claim(kind: str, problem: dict[str, Any], variant: str) -> dict[str, Any]:
    n, edges = problem['n'], {tuple(e) for e in problem['edges']}
    a, penalty = 2 ** n, 2 ** n * n + 1
    terms = []

    def term(coefficient, *indices):
        terms.append({'coefficient': str(coefficient), 'variables': list(indices)})

    if kind == 'cover':
        for i in range(n):
            tie = -2 ** (n - 1 - i)
            if variant == 'numeric_mask':
                tie = 2 ** i
            if variant == 'positive_superincreasing':
                tie = 2 ** (n - 1 - i)
            term(a + tie, i)
        if variant != 'omit_constraints':
            for u, v in edges:
                term(penalty)
                term(-penalty, u)
                term(-penalty, v)
                term(penalty, u, v)
    else:
        for i in range(n):
            term(-a + 2 ** i, i)
        if variant != 'omit_constraints':
            for u, v in combinations(range(n), 2):
                if (u, v) not in edges:
                    term(penalty, u, v)
    claim = {'kind': kind, 'sense': 'min', 'decode': identity(n), 'terms': terms}
    if variant == 'wrong_direction':
        claim['sense'] = 'max'
    if variant == 'equivalent':
        # Substitute x_i=1-y[n-1-i], then E'=-3 E + 7, maximizing.
        transformed = []
        for item in terms:
            indices = [n - 1 - i for i in item['variables']]
            for size in range(len(indices) + 1):
                for chosen in combinations(indices, size):
                    transformed.append({'coefficient': str(-3 * Fraction(item['coefficient']) * (-1) ** size),
                                        'variables': list(chosen)})
        transformed.append({'coefficient': '7', 'variables': []})
        claim.update(terms=transformed, sense='max',
                     decode={'permutation': list(reversed(range(n))), 'complement': [1] * n})
    return claim


def predicate_claim(problem: dict[str, Any], variant: str) -> dict[str, Any]:
    n = problem['n']
    decode = identity(n) if variant != 'equivalent' else {
        'permutation': list(reversed(range(n))), 'complement': [1] * n}
    marked, solutions = [], []
    for encoded in product((0, 1), repeat=n):
        values = [encoded[decode['permutation'][i]] ^ decode['complement'][i] for i in range(n)]
        locks = [] if variant == 'ignore_locks' else problem['locked']
        ok = all(values[i] == v for i, v in locks) and all(
            any(values[i] == (1 - v if variant == 'wrong_polarity' else v) for i, v in clause)
            for clause in problem['clauses'])
        marked.append(ok)
        if ok:
            solutions.append((values, list(encoded)))
    solutions.sort()
    selected = (solutions[-1 if variant == 'arbitrary_solution' else 0][1] if solutions else None)
    return {'kind': 'predicate', 'decode': decode, 'marked': marked, 'selected': selected}


def receipt_claim(problem: dict[str, Any], variant: str) -> dict[str, Any]:
    output, checksum = [], 0
    for row in problem['records']:
        value = row['left'] ^ row['right']
        bits = format(value, '08b')
        if variant == 'wrong_endian':
            bits = bits[::-1]
        checksum = (checksum + value) % 256
        output.append({'id': row['id'], 'bits': bits, 'set_bits': bits.count('1'),
                       'counts': {bits: problem['repetitions']} if problem['mode'] == 'counts' else None,
                       'prefix_checksum': checksum})
    if variant == 'sample_only':
        output = output[:1]
    report = {'record_count': len(output), 'receipts': output, 'checksum': checksum}
    if variant == 'equivalent':
        report = dict(reversed(list(report.items())))  # Object key order isn't contractual.
    return {'kind': 'receipts', 'report': report}


VARIANTS = {
    'cover': ['correct', 'equivalent', 'numeric_mask', 'positive_superincreasing', 'omit_constraints'],
    'clique': ['correct', 'equivalent', 'omit_constraints', 'wrong_direction'],
    'predicate': ['correct', 'equivalent', 'ignore_locks', 'wrong_polarity', 'arbitrary_solution'],
    'receipts': ['correct', 'equivalent', 'wrong_endian', 'sample_only'],
}


def submission(case: dict[str, Any], variant: str) -> dict[str, Any]:
    kind = case['oracle_kind']
    claims = {}
    for test in case['tests']:
        problem = test['input']
        if kind in ('cover', 'clique'):
            claim = graph_claim(kind, problem, variant)
        elif kind == 'predicate':
            claim = predicate_claim(problem, variant)
        else:
            claim = receipt_claim(problem, variant)
        claims[test['id']] = claim
    return {'case_id': case['case_id'], 'control': variant, 'claim_scope': case['claim_scope'],
            'provenance': {'kind': 'synthetic_control', 'is_model_result': False,
                           'author': 'Codex-authored finite evaluator control; not expert annotation'},
            'claims': claims}
