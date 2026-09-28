"""Quote-bound finite review of lit-001/002; not an automatic prose grader.

Only explicitly transcribed objectives are compiled. No candidate code is executed.
Primary-only objectives are NOT judged as if they promised a canonical ground state.
"""
from fractions import Fraction
import argparse
import json
from pathlib import Path

import run as runner

HERE, ROOT = runner.HERE, runner.ROOT
v = runner.module('repeat_scoped_verification', 'pilot/semantic_verification/v0.2/verification.py')


def polynomial(recipe, p):
    n, terms = p['n'], []

    def add(c, *indices):
        if c:
            terms.append({'coefficient': str(c), 'variables': list(indices)})

    if recipe in ('cut_negative', 'cut_conflict', 'cut_primary'):
        scale = 1 if recipe == 'cut_primary' else 2 ** n
        for u, w, weight in p['pairs']:
            if recipe == 'cut_conflict':
                add(scale * weight)
            add(-scale * weight, u)
            add(-scale * weight, w)
            add(2 * scale * weight, u, w)
        if recipe != 'cut_primary':
            for i in range(n):
                add(2 ** i, i)
    elif recipe in ('cover_negative_tie', 'cover_primary'):
        cardinality = 2 ** n if recipe == 'cover_negative_tie' else 1
        penalty = n * cardinality + 1
        for i in range(n):
            add(cardinality - (2 ** (n - 1 - i) if recipe == 'cover_negative_tie' else 0), i)
        for u, w in p['edges']:
            add(penalty)
            add(-penalty, u)
            add(-penalty, w)
            add(penalty, u, w)
    else:
        raise ValueError('Unknown manually reviewed recipe')
    return {'kind': 'maxcut' if recipe.startswith('cut_') else 'cover', 'sense': 'min',
            'variable_count': n, 'decode': {'permutation': list(range(n)), 'complement': [0] * n},
            'terms': terms}


def primary_check(case, submission):
    """Inspect every optimum against definition-level feasibility/primary value only."""
    v.base.check_provenance(submission, case)
    rows = []
    for test in case['tests']:
        p, failures = test['input'], []
        claim = submission['claims'][test['id']]
        energy = v.base.polynomial(claim, p['n'])
        values = [(energy(bits), bits) for bits in v.base.assignments(p['n'])]
        low = min(e for e, _ in values)
        truth = v.expected(case['oracle_kind'], p)
        expected_cut = (sum(weight for u, w, weight in p.get('pairs', []) if (u in truth) != (w in truth)))
        for e, bits in values:
            if e != low:
                continue
            chosen = [i for i, bit in enumerate(bits) if bit]
            if case['oracle_kind'] == 'maxcut':
                good = sum(weight for u, w, weight in p['pairs'] if bool(bits[u]) != bool(bits[w])) == expected_cut
            else:
                good = all(bits[u] or bits[w] for u, w in p['edges']) and len(chosen) == len(truth)
            if not good:
                failures.append({'actual': chosen, 'reference_canonical': truth})
        rows.append({'test_id': test['id'], 'status': 'candidate_error' if failures else 'passed',
                     'failures': failures, 'scope': 'primary_objective_only'})
    return {'status': 'candidate_error' if any(r['failures'] for r in rows) else 'passed',
            'tests': rows, 'scope': 'primary_objective_only', 'canonical_selection_pass': None,
            'task_pass': None, 'migration_execution_success': None, 'practical_advantage': None}


# Curated after reading the named response fields. No implicit tie repair is added.
RECIPES = {
    ('gpt-5.6-sol', 'lit-001'): ('cut_negative', 'E(x)=-(2^n)*C(x)+sum_i(2^i*x_i)',
                             'All coefficients and scale are explicit in the response.'),
    ('gpt-6-astra', 'lit-001'): ('cut_conflict', 'Minimize F(x)=B*C(x)+M(x).',
                             'Response explicitly defines B=2^n, C and M; retain the constant.'),
    ('deepseek-flash', 'lit-001'): ('cut_conflict', 'minimize 2**n * conflict_weight + sum_i 2**i x_i',
                                'Explicit scale and mask; conflict polynomial expanded by reviewer.'),
    ('deepseek-v4-pro', 'lit-001'): ('cut_primary', 'minimize Q(x)=sum_{i<j} w_ij*(2*x_i*x_j-x_i-x_j)',
                                 'Response separates canonical postprocessing; do not add a tie term.'),
    ('gpt-5.6-sol', 'lit-002'): ('cover_negative_tie', 'minimizing C*sum_i x_i-sum_i 2^(n-1-i)*x_i',
                             'Reviewer instantiates C=2^n and P=n*C+1, satisfying stated strict ranges. These numbers are not quoted model output.'),
    ('gpt-6-astra', 'lit-002'): ('cover_primary', 'with P=n+1.',
                             'Penalty n+1 is explicit. Canonical classical certification is separate and not executed here.'),
    ('deepseek-flash', 'lit-002'): ('cover_primary', 'with lambda > n',
                                'Reviewer instantiates lambda=n+1. Model explicitly leaves tie postprocessing unresolved.'),
}


def review(output):
    runner.verify()
    suite = {case['case_id']: case for case in v.load_suite()['cases']}
    output.mkdir(parents=True, exist_ok=False)
    submissions, records = [], []
    for (model, case_id), (recipe, anchor, parameters) in RECIPES.items():
        raw = HERE / 'runs' / model / case_id / 'response.txt'
        response = runner.deep.load_document(raw)
        quote = response['plan']['formulation']
        if anchor not in quote:
            raise ValueError('Curated transcription no longer matches response')
        case = suite[case_id]
        primary = recipe.endswith('_primary')
        submission = {'case_id': case_id, 'claim_scope': case['claim_scope'] if not primary else 'primary_objective_only',
                      'provenance': {'kind': 'reviewer_transcription', 'response_path': str(raw.relative_to(ROOT)),
                                     'response_sha256': runner.digest(raw), 'pointer': '/plan/formulation', 'quote': quote,
                                     'interpretation': f'{recipe}; finite objective review only, not the fallback or whole plan.',
                                     'parameters_source': parameters},
                      'claims': {t['id']: polynomial(recipe, t['input']) for t in case['tests']}}
        report = primary_check(case, submission) if primary else v.evaluate(case, submission)
        submissions.append({'model': model, 'recipe': recipe, **submission})
        records.append({'model': model, 'case_id': case_id, 'recipe': recipe,
                        'review_status': 'AI_TRANSCRIPTION_PENDING_INDEPENDENT_REVIEW',
                        'scope': submission['claim_scope'], 'parameters_source': parameters, **report})
    runner.save(output / 'transcriptions.json', submissions)
    runner.save(output / 'results.json', {'models': runner.MODELS, 'planned_requests': 40,
                'reviewed_responses': len(records), 'local_test_executions': sum(len(r['tests']) for r in records),
                'task_pass': None, 'records': records,
                'limitations': ['Purposive lit-001/002 review; not a performance denominator.',
                                'Finite classical enumeration, not quantum execution or whole-plan verification.',
                                'Reviewer-selected coefficients and prose transcription require independent review.']})
    print(json.dumps([{'model': r['model'], 'case': r['case_id'], 'scope': r['scope'], 'status': r['status']} for r in records], indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    review(parser.parse_args().output)
