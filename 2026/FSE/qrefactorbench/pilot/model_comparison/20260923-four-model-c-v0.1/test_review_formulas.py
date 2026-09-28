"""Check the new transcription plumbing independently of model success."""
import importlib.util
from pathlib import Path
import sys

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
try:
    spec = importlib.util.spec_from_file_location('repeat_formula_test', HERE / 'review_formulas.py')
    r = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r)
finally:
    sys.path.remove(str(HERE))


@pytest.mark.parametrize('recipe,case_id', [('cut_negative', 'lit-001'), ('cut_conflict', 'lit-001'),
                                         ('cover_negative_tie', 'lit-002')])
def test_transcription_compilers_preserve_actual_energy(recipe, case_id):
    case = next(c for c in r.v.load_suite()['cases'] if c['case_id'] == case_id)
    for test in case['tests']:
        p, n = test['input'], test['input']['n']
        claim = r.polynomial(recipe, p)
        energy = r.v.base.polynomial(claim, n)
        for bits in r.v.base.assignments(n):
            if recipe.startswith('cut_'):
                cut = sum(w for u, v, w in p['pairs'] if bits[u] != bits[v])
                primary = -cut if recipe == 'cut_negative' else sum(w for _, _, w in p['pairs']) - cut
                wanted = 2**n * primary + sum(2**i * b for i, b in enumerate(bits))
            else:
                uncovered = sum(not(bits[u] or bits[v]) for u, v in p['edges'])
                wanted = 2**n * sum(bits) - sum(2**(n-1-i) * b for i, b in enumerate(bits)) + (n*2**n+1)*uncovered
            assert energy(bits) == wanted


@pytest.mark.parametrize('case_id,recipe', [('lit-001', 'cut_primary'), ('lit-002', 'cover_primary')])
def test_primary_scope_does_not_accidentally_require_tie_and_detects_reversed_sense(case_id, recipe):
    case = next(c for c in r.v.load_suite()['cases'] if c['case_id'] == case_id)
    candidate = {'case_id': case_id, 'provenance': {'kind': 'synthetic_control', 'is_model_result': False},
                 'claims': {t['id']: r.polynomial(recipe, t['input']) for t in case['tests']}}
    report = r.primary_check(case, candidate)
    assert report['status'] == 'passed'
    assert report['canonical_selection_pass'] is None and report['task_pass'] is None
    for claim in candidate['claims'].values():
        for term in claim['terms']:
            term['coefficient'] = str(-int(term['coefficient']))
    bad = r.primary_check(case, candidate)
    assert bad['status'] == 'candidate_error'
