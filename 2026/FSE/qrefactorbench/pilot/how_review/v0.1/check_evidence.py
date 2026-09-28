"""Reviewer-transcribed finite arithmetic checks; no model code or quantum execution."""
from __future__ import annotations

import hashlib
import importlib.util
import itertools as it
import json
import re
from fractions import Fraction
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[3]
INPUTS = ROOT / 'pilot/reference_completion/v0.1.1/review_inputs'


def trusted_kernel(relative: str, case: str, filename: str) -> ModuleType:
    path = ROOT / relative
    packet = (INPUTS / f'{case}-C.txt').read_text()
    section = packet.split(f'FILE {filename}\n', 1)[1]
    lines = []
    for line in section.splitlines():
        match = re.fullmatch(r'(\d+): ?(.*)', line)
        if not match:
            break
        assert int(match[1]) == len(lines) + 1
        lines.append(match[2])
    assert '\n'.join(lines).rstrip() == path.read_text().rstrip(), relative
    spec = importlib.util.spec_from_file_location(f'review_{case}', path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def graphs(n: int):
    pairs = list(it.combinations(range(n), 2))
    for bits in range(1 << len(pairs)):
        yield [p for i, p in enumerate(pairs) if bits >> i & 1]


def selected(mask: int, n: int) -> tuple[int, ...]:
    return tuple(i for i in range(n) if mask >> i & 1)


def argmins(energies: dict) -> set:
    best = min(energies.values())
    return {key for key, value in energies.items() if value == best}


def check_vertex_cover() -> dict:
    core = trusted_kernel('pilot/reference_cases/v0.1/cases/context-002/inspection.py',
                          'lit-002', 'inspection.py')
    count = 0
    for n in range(6):
        for edges in graphs(n):
            masks = range(1 << n)
            violations = {m: sum(not (m >> u & 1 or m >> v & 1) for u, v in edges) for m in masks}
            feasible = [m for m in masks if violations[m] == 0]
            expected = min(feasible, key=lambda m: (m.bit_count(), selected(m, n)))
            assert selected(expected, n) == tuple(sorted(core.min_vertex_cover_bruteforce(edges=edges, n=n)))
            # Sol's explicitly allowed scales, instantiated by reviewer.
            a = 1 << n
            p = a * n + a
            energy = {m: a * m.bit_count() + sum((1 << (n-1-i)) * (1 - (m >> i & 1)) for i in range(n))
                      + p * violations[m] for m in masks}
            assert argmins(energy) == {expected}
            # Astra claims only cardinality, explicitly not a tie encoding.
            energy = {m: m.bit_count() + (n+1) * violations[m] for m in masks}
            minimum_size = expected.bit_count()
            assert argmins(energy) == {m for m in feasible if m.bit_count() == minimum_size}
            count += 1

    witnesses = []
    for name, n, edges in [('flash', 2, [(0, 1)]), ('pro', 4, [(0, 1), (0, 2), (1, 3), (2, 3)])]:
        names = [f's{i}' for i in range(n)]
        request = {'stations': names, 'connections': [[names[u], names[v]] for u, v in edges],
                   'current_stations': []}
        checked_names, checked_edges, _ = core.prepare_request(request)
        expected = tuple(sorted(core.min_vertex_cover_bruteforce(edges=checked_edges, n=len(checked_names))))
        energies = {}
        for m in range(1 << n):
            uncovered = sum(not (m >> u & 1 or m >> v & 1) for u, v in edges)
            if name == 'flash':
                energies[m] = 3*m.bit_count() + 10*uncovered + 2*(m & 1) + (m >> 1 & 1)
            else:
                energies[m] = m.bit_count() + 10*uncovered + Fraction(m, 32)
        winners = sorted(selected(m, n) for m in argmins(energies))
        assert expected not in winners
        witnesses.append({'model_branch': name, 'n': n, 'edges': edges, 'expected': expected,
                          'energy_minimizers': winners, 'full_input_validation': True})
    assert witnesses[0]['expected'] == (0,) and witnesses[0]['energy_minimizers'] == [(1,)]
    assert witnesses[1]['expected'] == (0, 3) and witnesses[1]['energy_minimizers'] == [(1, 2)]
    return {'graphs': count, 'n_range': [0, 5], 'sol_exact_tuple': True,
            'astra_all_minimum_covers': True, 'counterexamples': witnesses}


def check_clique() -> dict:
    count = 0
    for n in range(6):
        b = 1 << n
        for nonedges in graphs(n):
            violations = {m: sum((m >> u & 1) * (m >> v & 1) for u, v in nonedges) for m in range(b)}
            expected = min((m for m in range(b) if not violations[m]), key=lambda m: (-m.bit_count(), m))
            for label, cardinality, penalty, tie in [
                ('astra', b, n*b+1, 1),
                ('flash', b, n*b+b, 1),
                ('pro', 1, 2, Fraction(1, 2*b)),
            ]:
                energy = {m: -cardinality*m.bit_count() + penalty*violations[m] + tie*m for m in range(b)}
                assert argmins(energy) == {expected}, (label, n, nonedges)
            count += 1
    return {'graphs': count, 'n_range': [0, 5], 'three_formulas_checked': True,
            'pro_flash_scales': 'reviewer instances of response conditions; not model-supplied numbers',
            'limit': 'Core subset contract only; no full program or quantum execution.'}


def check_knapsack() -> dict:
    core = trusted_kernel('pilot/reference_completion/v0.1.1/cases/lit-006/kernel.py', 'lit-006', 'kernel.py')
    count = 0
    for n in range(4):
        b = 1 << n
        for pairs in it.product(list(it.product(range(1, 4), range(3))), repeat=n):
            items = [{'weight': w, 'value': v} for w, v in pairs]
            totals = {m: (sum(w for i, (w, _) in enumerate(pairs) if m >> i & 1),
                          sum(v for i, (_, v) in enumerate(pairs) if m >> i & 1)) for m in range(b)}
            a = b*sum(v for _, v in pairs) + 1
            for capacity in range(5):
                expected = min((m for m, (w, _) in totals.items() if w <= capacity),
                               key=lambda m: (-totals[m][1], m))
                assert core.choose(items, capacity) == expected
                # Standard nonnegative binary slack may represent values above C;
                # include every bit pattern, not just feasible slack integers.
                energies = {(m, slack): -b*v+m+a*(w+slack-capacity)**2
                            for m, (w, v) in totals.items()
                            for slack in range(1 << capacity.bit_length())}
                assert {m for m, _ in argmins(energies)} == {expected}
                count += 1
    return {'instances': count, 'n_range': [0, 3], 'weight_range': [1, 3], 'value_range': [0, 2],
            'capacity_range': [0, 4], 'astra_formula_matches_original_kernel': True,
            'limit': 'Reviewer-chosen standard slack encoding; response does not supply an implementation.'}


def check_coloring_order() -> dict:
    vectors = 0
    for n in range(5):
        for k in range(5):
            assignments = list(it.product(range(k), repeat=n))
            # Encoding objective on feasible one-hot vectors, not a check of penalties.
            for variant in ('flash', 'pro'):
                energies = [sum(s*((k if variant == 'flash' else k+1)**(n-1-i if variant == 'flash' else n-i))
                                for i, s in enumerate(a)) for a in assignments]
                assert all(x < y for x, y in zip(energies, energies[1:])), (n, k, variant)
            vectors += len(assignments)
    return {'assignment_vectors': vectors, 'n_and_k_range': [0, 4], 'two_lex_objectives': True,
            'limit': 'Ordering only; QUBO penalties, one-hot enforcement and whole-program behavior unresolved.'}


def check_pivot_predicate() -> dict:
    count = 0
    for n in range(1, 6):
        for column in it.product((-2., -1., 0., 1., 2.), repeat=n):
            expected = max(range(n), key=lambda i: abs(column[i]))
            for start in range(n):
                incumbent = start
                while True:
                    better = [i for i in range(n) if abs(column[i]) > abs(column[incumbent])
                              or (abs(column[i]) == abs(column[incumbent]) and i < incumbent)]
                    if not better:
                        break
                    incumbent = better[-1]
                assert incumbent == expected
            count += 1
    return {'finite_columns': count, 'all_start_indices': True,
            'limit': 'Classical predicate/termination witness, not Grover execution or performance; excludes NaN/Inf.'}


def run() -> dict:
    return {'review_status': 'AI_PENDING', 'model_calls': 0, 'quantum_runs': 0,
            'vertex_cover': check_vertex_cover(), 'clique': check_clique(),
            'knapsack': check_knapsack(), 'coloring_order': check_coloring_order(),
            'pivot': check_pivot_predicate(),
            'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


if __name__ == '__main__':
    print(json.dumps(run(), ensure_ascii=False, indent=2))
