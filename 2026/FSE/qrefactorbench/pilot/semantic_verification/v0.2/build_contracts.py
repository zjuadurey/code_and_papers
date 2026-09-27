"""Extend the six catalogue-only cases; preserve previous four contracts verbatim."""
import argparse
from copy import deepcopy
import json
from pathlib import Path

from verification import PREVIOUS, HERE, ROOT, base, expected


def pairs(n, rows):
    return {'n': n, 'pairs': rows}


def colors(n, k, edges):
    return {'n': n, 'colors': k, 'edges': edges}


def sack(items, capacity):
    return {'n': len(items), 'items': [{'weight': w, 'value': v} for w, v in items], 'capacity': capacity}


def step(matrix, rhs, current, steps=1, tolerance=0):
    return {'matrix': matrix, 'rhs': rhs, 'current': current, 'steps': steps, 'tolerance': tolerance}


SPECS = {
 'lit-001': ('maxcut', [
    ('empty', 'boundary', pairs(0, []), 'empty partition'),
    ('zero_weight', 'boundary', pairs(3, [[0, 1, 0]]), 'wrong canonical mask on zero objective'),
    ('one_edge', 'normal', pairs(2, [[0, 1, 2]]), 'minimizing rather than maximizing cut'),
    ('weighted_triangle', 'discriminating', pairs(3, [[0, 1, 1], [0, 2, 5], [1, 2, 4]]), 'ignoring weights'),
    ('large_integer', 'discriminating', pairs(3, [[0, 1, 2 ** 60], [0, 2, 2 ** 60], [1, 2, 2 ** 60 + 1]]), 'floating conversion loses integer ordering'),
 ]),
 'lit-003': ('coloring', [
    ('empty', 'boundary', colors(0, 0, []), 'empty assignment versus no solution'),
    ('no_colors', 'boundary', colors(1, 0, []), 'invalid color domain'),
    ('edge', 'normal', colors(2, 2, [[0, 1]]), 'ignored adjacency'),
    ('unsatisfiable', 'discriminating', colors(3, 2, [[0, 1], [0, 2], [1, 2]]), 'false absence/feasibility'),
    ('invalid_binary_code', 'discriminating', colors(1, 3, []), 'unused binary code accepted'),
    ('greedy_trap', 'discriminating', colors(4, 2, [[0, 2], [1, 3], [2, 3]]), 'greedy failure misreported as infeasibility'),
 ]),
 'lit-006': ('knapsack', [
    ('empty', 'boundary', sack([], 0), 'empty item domain'),
    ('zero_capacity', 'boundary', sack([(1, 4)], 0), 'capacity constraint omitted'),
    ('source_example', 'normal', sack([(2, 3), (4, 3), (1, 1), (3, 1), (5, 5)], 7), 'incorrect value/weight correspondence'),
    ('value_not_count', 'discriminating', sack([(3, 10), (1, 1), (1, 1)], 3), 'optimizing item count instead of value'),
    ('mask_tie', 'discriminating', sack([(1, 2), (1, 2)], 1), 'incorrect numeric-mask tie'),
    ('unused_capacity', 'discriminating', sack([(2, 10), (3, 1)], 3), 'equality penalty without slack'),
    ('zero_value', 'boundary', sack([(1, 0), (2, 0)], 2), 'unnecessary zero-value items'),
 ]),
 'lit-007': ('signed', [
    ('empty', 'boundary', pairs(0, []), 'empty membership'),
    ('singleton', 'boundary', pairs(1, []), 'canonical empty mask'),
    ('apart', 'normal', pairs(2, [[0, 1, 1]]), 'optimization sign'),
    ('together', 'discriminating', pairs(2, [[0, 1, -1]]), 'negative preference interpreted as positive'),
    ('mixed', 'discriminating', pairs(3, [[0, 1, 1], [0, 2, -1], [1, 2, 1]]), 'sign dropped'),
 ]),
 'lit-009': ('linear', [
    ('empty', 'boundary', {'operation': 'solve', 'matrix': [], 'rhs': []}, 'empty solution'),
    ('swap', 'normal', {'operation': 'solve', 'matrix': [[0, 2], [1, 3]], 'rhs': [4, 7]}, 'ignoring rhs / missing pivot'),
    ('singular', 'boundary', {'operation': 'solve', 'matrix': [[1, 1], [2, 2]], 'rhs': [1, 2]}, 'inventing solution for singular system'),
    ('pivot_abs', 'discriminating', {'operation': 'pivot', 'column': [-5, 3, 0], 'start': 0}, 'signed rather than absolute pivot comparison'),
    ('pivot_tie', 'discriminating', {'operation': 'pivot', 'column': [2, -2, 1], 'start': 0}, 'last rather than first index tie'),
    ('pivot_suffix', 'discriminating', {'operation': 'pivot', 'column': [9, -2, 3], 'start': 1}, 'searching outside active row suffix'),
    ('residual', 'normal', {'operation': 'residual', 'matrix': [[2, 0], [0, 1]], 'rhs': [0, 0], 'x': [1, 2]}, 'wrong residual/scaled backward error'),
    ('zero_residual', 'boundary', {'operation': 'residual', 'matrix': [[0]], 'rhs': [0], 'x': [0]}, 'zero denominator handling'),
 ]),
 'lit-010': ('iteration', [
    ('empty', 'boundary', step([], [], []), 'empty recurrence'),
    ('one_step', 'normal', step([[4, 1], [1, 3]], [1, 2], [0, 0]), 'exact solution substituted for required iterate'),
    ('zero_budget', 'boundary', step([[4, 1], [1, 3]], [1, 2], [0, 0], 0), 'ignoring iteration budget'),
    ('already_solved', 'boundary', step([[4, 1], [1, 3]], [5, 4], [1, 1], 3), 'running after zero initial residual'),
    ('tolerance_stop', 'boundary', step([[4, 1], [1, 3]], [1, 2], [0, 0], 3, 1), 'ignoring stopping condition'),
    ('nonzero_current', 'discriminating', step([[2, 0], [0, 2]], [4, 0], [1, 1]), 'discarding supplied starting point'),
    ('other_step', 'discriminating', step([[2, 0], [0, 6]], [1, 1], [0, 0]), 'hardcoded sample / missing trace'),
 ]),
}


def build():
    suite = deepcopy(base.load_document(PREVIOUS / 'contracts.json'))
    suite.update(version='0.2', scope_policy='All ten mothers retain their original task; six prior unimplemented scopes now have controls. Numerical checks are bounded behavior claims, not opportunity labels.')
    for path in sorted(PREVIOUS.glob('*')):
        if path.is_file() and path.suffix in ('.py', '.json'):
            suite['source_sha256'][str(path.relative_to(ROOT))] = base.digest(path)
    for relative in ['pilot/reference_completion/v0.1.1/cases/lit-009/kernel.py',
                     'pilot/reference_completion/v0.1.1/cases/lit-010/kernel.py',
                     'pilot/source_adaptations/v0.2-where/cases/lit-003/agenda.py']:
        suite['source_sha256'][relative] = base.digest(ROOT / relative)
    for case in suite['cases']:
        if case['case_id'] not in SPECS:
            continue
        kind, tests = SPECS[case['case_id']]
        case.update(oracle_kind=kind,
                    claim_scope='direct_canonical_ground_state' if kind in ('maxcut', 'signed', 'knapsack') else
                    'color_relation_and_core_selection' if kind == 'coloring' else 'bounded_numerical_behavior',
                    verification_scope={
                        'maxcut': 'B: weighted cut objective and smallest window-0 mask, after input aggregation. Full context unverified.',
                        'signed': 'B: signed pair objective and canonical membership mask. Full context unverified.',
                        'knapsack': 'B: value maximization, capacity, indivisibility, mask tie and auxiliary slack decoding. Caller filtering/reports unverified.',
                        'coloring': 'B: binary marking OR one-hot feasible-energy constraint equivalence plus extremum bound, and lex-first/absence on the core. Greedy/context/circuits unverified.',
                        'linear': 'Behavior obligations: active-suffix pivot rules, small dyadic systems and residual diagnostics. Structural eligibility remains PENDING/null.',
                        'iteration': 'Behavior obligations: zero/one effective iteration, starting point, stopping condition and full core trace on dyadic fixtures. No general floating equivalence or quantum eligibility verdict.',
                    }[kind],
                    oracle_basis='Definition enumeration or independent closed-form arithmetic in oracle_extensions.py; controls use different constructions/trusted original kernels.')
        case['equivalences'] = ('Explicit binary permutations/complements, exact constant shifts and objective scaling with matching sense; knapsack auxiliary bits ignored only after logical item decoding. Coloring accepts both binary predicate and one-hot feasibility formulations.'
                                if kind not in ('linear', 'iteration') else
                                'Object key order and exact int/float numeric equality allowed. Only chosen exactly representable arithmetic fixtures; no universal tolerance or bitwise HPL matching requirement introduced.')
        case['tests'] = [{'id': name, 'category': category, 'input': p, 'expected': expected(kind, p),
                          'expected_source': 'Original public contract; independent oracle with hand-derived anchors in regression tests.',
                          'target_error': error, 'premises': 'Valid normalized core input; numerical domain further limited to explicitly chosen finite fixtures.'}
                         for name, category, p, error in tests]
    return suite


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with args.output.open('x') as out:
        json.dump(build(), out, indent=2, ensure_ascii=False, allow_nan=False)
        out.write('\n')
