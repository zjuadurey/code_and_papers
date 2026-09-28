"""Additional reviewer-written bounded checks; no generated-code execution."""
from __future__ import annotations

import hashlib
import importlib.util
import itertools as it
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('prior_how_checks', HERE.parent/'v0.1/check_evidence.py')
assert spec and spec.loader
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)


def maxcut() -> dict:
    core = prior.trusted_kernel('pilot/context_adaptations/v0.1/cases/context-001/maintenance.py',
                                'lit-001', 'maintenance.py')
    instances = 0
    for n in range(5):
        edges = list(it.combinations(range(n), 2))
        for weights in it.product(range(3), repeat=len(edges)):
            matrix = [[0]*n for _ in range(n)]
            for (i, j), w in zip(edges, weights):
                matrix[i][j] = matrix[j][i] = w
            cut = {m: sum(w for (i, j), w in zip(edges, weights) if (m >> i & 1) != (m >> j & 1))
                   for m in range(1 << n)}
            total, b = sum(weights), 1 << n
            expected = min(cut, key=lambda m: (-cut[m], m))
            score, (left, right) = core.maxcut_bruteforce(matrix)
            assert score == cut[expected] and sum(1 << i for i in left) == expected
            assert sorted(left+right) == list(range(n))
            # Sol -B*cut+mask and Astra/Flash B*conflict+mask differ by a constant.
            for energies in [{m: -b*s+m for m, s in cut.items()},
                             {m: b*(total-s)+m for m, s in cut.items()}]:
                assert prior.argmins(energies) == {expected}
            # Pro flips variable meaning. All core optima correspond after decoding;
            # no tie construction is supplied by Pro, so do not credit one here.
            pro = {x: sum(w*(1-(x >> i & 1)-(x >> j & 1)+2*(x >> i & 1)*(x >> j & 1))
                          for (i, j), w in zip(edges, weights)) for x in range(b)}
            assert {b-1-x for x in prior.argmins(pro)} == {m for m, s in cut.items() if s == max(cut.values())}
            # Astra's stated Ising expansion, doubled to avoid floating arithmetic.
            for m in range(b):
                z = [1-2*(m >> i & 1) for i in range(n)]
                doubled_ising = b*sum(w*(1+z[i]*z[j]) for (i, j), w in zip(edges, weights))
                doubled_ising += sum((1 << i)*(1-z[i]) for i in range(n))
                assert doubled_ising == 2*(b*(total-cut[m])+m)
            instances += 1
    return {'instances': instances, 'n': [0, 4], 'edge_weights': [0, 2],
            'scope': 'Core objective, variable flip, Sol/Astra/Flash tie and Astra Ising identity; not hardware or reports.'}


def signed_pairs() -> dict:
    core = prior.trusted_kernel('pilot/reference_completion/v0.1.1/cases/lit-007/kernel.py',
                                'lit-007', 'kernel.py')
    instances = 0
    assignments = 0
    for n in range(6):
        edges = list(it.combinations(range(n), 2))
        for weights in it.product((-1, 1), repeat=len(edges)):
            pairs = [(i, j, w) for (i, j), w in zip(edges, weights)]
            scores = {}
            for m in range(1 << n):
                values = [bool(m >> i & 1) for i in range(n)]
                expanded = sum(-w+2*w*values[i]+2*w*values[j]-4*w*values[i]*values[j] for i, j, w in pairs)
                assert expanded == core.score(values, pairs)
                assert -expanded == sum(w*(1-2*values[i])*(1-2*values[j]) for i, j, w in pairs)
                scores[m] = expanded
                assignments += 1
            expected = min(scores, key=lambda m: (-scores[m], m))
            assert core.choose(n, pairs) == [bool(expected >> i & 1) for i in range(n)]
            assert prior.argmins({m: -(1 << n)*s+m for m, s in scores.items()}) == {expected}
            instances += 1
    return {'instances': instances, 'assignments': assignments, 'n': [0, 5], 'weights': [-1, 1],
            'scope': 'All four core polynomials; Sol/Astra scalar tie only. No tie encoding credited to DeepSeek.'}


def boolean_search() -> dict:
    core = prior.trusted_kernel('pilot/reference_completion/v0.1.1/cases/lit-005/kernel.py',
                                'lit-005', 'kernel.py')
    instances = 0
    for n in range(4):
        literals = [(i, value) for i in range(n) for value in (False, True)]
        # Empty rule set or one exactly-three-literal rule, including repetitions.
        clause_sets = [[]] + [[list(c)] for c in it.product(literals, repeat=3)]
        vectors = list(it.product((False, True), repeat=n))
        for clauses in clause_sets:
            for locks in it.product((None, False, True), repeat=n):
                locked = {i: value for i, value in enumerate(locks) if value is not None}
                matches = []
                for values in vectors:
                    predicate = all(values[i] == v for i, v in locked.items()) and all(
                        any(values[i] == v for i, v in clause) for clause in clauses)
                    assert predicate == core.conforms(values, clauses, locked)
                    if predicate:
                        matches.append(values)
                expected = list(matches[0]) if matches else None
                assert core.complete(n, clauses, locked) == expected
                # Classical exact existence stands in for the explicitly unresolved
                # quantum negative-result certification. This is a logical check only.
                prefix = []
                if matches:
                    for i in range(n):
                        prefix.append(False if any(v[:i+1] == tuple(prefix+[False]) for v in matches) else True)
                    assert prefix == expected
                instances += 1
    return {'instances': instances, 'n': [0, 3], 'rules': 'zero or one, each rule exactly three literals',
            'scope': 'Predicate and exact prefix logic; not reversible oracle, Grover, all rule sets or full wrapper.'}


def run() -> dict:
    return {'status': 'AI_PENDING', 'maxcut': maxcut(), 'signed_pairs': signed_pairs(),
            'boolean_search': boolean_search(), 'new_model_calls': 0, 'quantum_runs': 0,
            'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


if __name__ == '__main__':
    print(json.dumps(run(), ensure_ascii=False, indent=2))
