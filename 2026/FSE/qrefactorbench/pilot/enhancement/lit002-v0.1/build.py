"""Freeze protocol, tests and provenance BEFORE inference. No model calls."""
from __future__ import annotations
import hashlib
from itertools import combinations
import json
from pathlib import Path
import random
import subprocess
from datetime import datetime, timezone
from engine import HERE, ROOT, base


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def control(variant='correct'):
    obj = {'version': 'qubo-template-v1', 'sense': 'min',
           'decode': {'index': 'i', 'complement': False}, 'explanation': 'Synthetic evaluator control.',
           'terms': [
               {'over': 'vertices', 'coefficient': '2**n - 2**(n-1-i)',
                'factors': [{'index': 'i', 'complement': False}]},
               {'over': 'edges', 'coefficient': 'n*2**n+1',
                'factors': [{'index': 'i', 'complement': True}, {'index': 'j', 'complement': True}]}]}
    if variant == 'numeric_mask':
        obj['terms'][0]['coefficient'] = '2**n + 2**i'
    elif variant == 'positive_superincreasing':
        obj['terms'][0]['coefficient'] = '2**n + 2**(n-1-i)'
    elif variant == 'omit_constraints':
        obj['terms'].pop()
    elif variant == 'omit_tie':
        obj['terms'][0]['coefficient'] = '2**n'
    elif variant == 'wrong_sense':
        obj['sense'] = 'max'
    elif variant == 'equivalent':
        obj['sense'] = 'max'
        obj['decode'] = {'index': 'n-1-i', 'complement': True}
        for term in obj['terms']:
            term['coefficient'] = '-3*(' + term['coefficient'] + ')/2'
            for factor in term['factors']:
                factor['index'] = 'n-1-' + factor['index']
                factor['complement'] = not factor['complement']
        obj['terms'].append({'over': 'once', 'coefficient': '7', 'factors': []})
    elif variant != 'correct':
        raise ValueError(variant)
    return obj


def make_tests():
    suite = base.load_suite()
    development = next(c for c in suite['cases'] if c['case_id'] == 'lit-002')['tests']
    development = [{'id': t['id'], 'input': t['input'], 'expected': t['expected'],
                    'source': 'Original vertex-cover definition; existing v0.1 definition oracle',
                    'purpose': t.get('targets', t.get('purpose', 'coverage/cardinality/canonical tie'))}
                   for t in development]
    def key(p):
        return (p['n'], tuple(tuple(e) for e in p['edges']))
    seen = {key(t['input']) for t in development}
    final = []
    def add(n, edges, purpose):
        p = {'n': n, 'edges': [list(e) for e in sorted(edges)]}
        if key(p) not in seen:
            seen.add(key(p))
            final.append({'id': f'final-{len(final):03}', 'input': p,
                          'expected': base.expected('cover', p), 'source': 'Definition-based exhaustive subset oracle',
                          'purpose': purpose})
    for n in range(5):
        pairs = list(combinations(range(n), 2))
        for mask in range(2**len(pairs)):
            add(n, [e for j, e in enumerate(pairs) if mask & (1 << j)],
                'Exhaustive small-graph coverage; all ground states must obey full contract')
    rng = random.Random(20260923)
    for n in (5, 6):
        for _ in range(12):
            add(n, [e for e in combinations(range(n), 2) if rng.random() < 0.4],
                'Precommitted larger graphs: penalties, decoder, cardinality and canonical tie')
    for n in (8,):
        add(n, [], 'Empty-edge boundary')
        add(n, list(combinations(range(n), 2)), 'Dense graph and tie boundary')
        add(n, [(0, i) for i in range(1, n)], 'Unique optimum, index-order discrimination')
        add(n, [(i, i+1) for i in range(n-1)], 'Path and multiple equal-cardinality covers')
    return {'development': development, 'final': final}


def main():
    save(HERE / 'tests.json', make_tests())
    controls = {v: control(v) for v in ('correct', 'equivalent', 'numeric_mask',
                                       'positive_superincreasing', 'omit_constraints', 'omit_tie', 'wrong_sense')}
    save(HERE / 'controls.json', controls)
    protected = {str(p.relative_to(ROOT)): digest(p)
                 for folder in ('pilot/reference_completion', 'pilot/provisional_labels', 'pilot/model_comparison',
                                'pilot/semantic_verification', 'schemas', 'qrefactorbench')
                 for p in (ROOT / folder).rglob('*')
                 if p.is_file() and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts}
    save(HERE / 'protected_before.json', protected)
    paths = [HERE / name for name in ('engine.py', 'build.py', 'run.py', 'prompt.txt', 'tests.json',
                                      'controls.json', 'test_experiment.py')]
    paths += [ROOT / 'pilot/model_comparison/20260922-c-v0.1/run.py',
              ROOT / 'pilot/semantic_verification/v0.1/evaluate.py',
              ROOT / 'pilot/semantic_verification/v0.1/oracles.py']
    save(HERE / 'protocol.json', {
        'authorization': 'D-031: user explicitly selected lit-002 direct structured QUBO; GPT-5.6 Sol; max 15 subscription requests.',
        'created_utc': datetime.now(timezone.utc).isoformat(), 'model': 'gpt-5.6-sol',
        'replicates': 5, 'arms': ['initial', 'self_review', 'counterexample'], 'maximum_requests': 15,
        'operator_retries': 0, 'wall_timeout_per_request_seconds': 600,
        'cli_version': subprocess.check_output(['/home/audrey/.local/bin/codex', '--version'], text=True).strip(),
        'reasoning_effort': 'medium', 'temperature': None, 'seed': None, 'server_snapshot': None,
        'max_output_tokens': None, 'max_response_bytes_for_evaluator': 32768,
        'design': 'Each independent initial answer is shared by two fresh-context one-revision branches; always run both, even if initial passes.',
        'branch_order': 'Odd replicates self_review then counterexample; even reverse. Serial calls.',
        'feedback': 'One first failing development example with exact optimum/decoded answer; if none, finite-pass notice. No reference formula.',
        'primary_observable': 'Per-arm count of responses passing every final finite semantic check, denominator five; format and failure categories separate.',
        'comparison': 'Paired self_review vs counterexample; two model turns per path. Initial has one. Tool and token costs recorded separately, not matched compute.',
        'stop': 'Stop all further requests on transport/account/tool/infrastructure errors. No retry. Invalid candidate data still permits the two planned revision branches.',
        'limits': ['One development-exposed mother case, five replicates, no model ranking or independent holdout.',
                   'New restricted mapping representation, not the unchanged Phase-1 benchmark.',
                   'Final graphs disjoint from development graphs, but same task and known failure mechanism.',
                   'Finite checks through n=8; no theorem for n<=16, quantum execution, production migration or speedup.',
                   'CLI/provider internal retries may be opaque; 15 bounds operator case invocations.'],
        'baseline_tests': {'command': '/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q tests/test_semantic_verification.py tests/test_semantic_verification_v02.py',
                           'passed': 126, 'seconds': 1.72},
        'source_sha256': {str(p.relative_to(ROOT)): digest(p) for p in paths}})


if __name__ == '__main__':
    main()
