"""Run fixed finite controls and the two previously reviewed formula witnesses.

No model call, candidate Python execution, resampling or historical score rewrite.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import json
from pathlib import Path
import platform

from controls import VARIANTS, submission
from evaluate import ROOT, HERE, aggregate, digest, evaluate, load_suite


def reviewed_counterexamples(case):
    archive_path = ROOT / 'pilot/how_review/adjudications/20260922-lit002/review.json'
    archive = json.loads(archive_path.read_text())
    out = []
    for source in archive['claims']:
        flash = source['model'] == 'deepseek-flash'
        test_id = 'single_edge' if flash else 'tuple_not_mask'
        n, edges = ((2, [(0, 1)]) if flash else (4, [(0, 1), (0, 2), (1, 3), (2, 3)]))
        a, penalty = (3, 10) if flash else (1, 10)
        weights = [2, 1] if flash else [Fraction(2 ** i, 32) for i in range(n)]
        terms = [{'coefficient': str(a + w), 'variables': [i]} for i, w in enumerate(weights)]
        for u, v in edges:
            terms.extend([{'coefficient': '10', 'variables': []},
                          {'coefficient': '-10', 'variables': [u]},
                          {'coefficient': '-10', 'variables': [v]},
                          {'coefficient': '10', 'variables': [u, v]}])
        provenance = {'kind': 'reviewer_transcription',
                      'response_path': source['response_path'], 'response_sha256': source['response_sha256'],
                      'pointer': source['claim_pointer'], 'quote': source['claim_text_verbatim'],
                      'interpretation': source['interpretation_condition'],
                      'parameters_source': 'Reviewer-instantiated prior witness: A=3 B=10 w=(2,1)' if flash else
                                           'Reviewer-instantiated prior witness: A=1 P=10 C=1/32',
                      'review_source': str(archive_path.relative_to(ROOT)), 'review_sha256': digest(archive_path),
                      'transcription_author': 'Codex; exact-quote binding is not independent expert validation',
                      'whole_plan_verified': False}
        claim = {'case_id': case['case_id'], 'model': source['model'], 'provenance': provenance,
                 'claim_scope': case['claim_scope'],
                 'claims': {test_id: {'kind': 'cover', 'sense': 'min',
                                    'decode': {'permutation': list(range(n)), 'complement': [0] * n},
                                    'terms': terms}}}
        out.append(claim)
    return out


def run(output: Path):
    suite = load_suite()
    output.mkdir(exist_ok=False, parents=True)
    controls, results = [], []
    for case in suite['cases']:
        if not case['tests']:
            continue
        for variant in VARIANTS[case['oracle_kind']]:
            candidate = submission(case, variant)
            controls.append(candidate)
            report = evaluate(case, candidate)
            intended = 'passed' if variant in ('correct', 'equivalent') else 'candidate_error'
            results.append({'case_id': case['case_id'], 'control': variant,
                            'expected_status': intended, 'matched_expected': report['status'] == intended,
                            **report})
    cover = next(c for c in suite['cases'] if c['case_id'] == 'lit-002')
    witnesses = reviewed_counterexamples(cover)
    witness_results = [{'model': w['model'], 'provenance': w['provenance'], **aggregate(suite, [w])} for w in witnesses]
    source_files = list(HERE.glob('*.py')) + [HERE / 'contracts.json', ROOT / 'tests/test_semantic_verification.py']
    report = {
        'created_utc': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
        'purpose': 'Evaluator regression, not model ranking or end-to-end migration',
        'population': {'mother_cases': 10, 'input_conditions': 30, 'contract_sidecars': 10,
                       'cases_with_scoped_oracle': 4, 'cases_actually_checked': 4,
                       'cases_controls_verified': sum(all(r['matched_expected'] for r in results if r['case_id'] == cid)
                                                      for cid in {r['case_id'] for r in results}),
                       'cases_without_new_scoped_oracle': 6,
                       'test_inputs': sum(len(c['tests']) for c in suite['cases']),
                       'synthetic_controls': len(results), 'correct_controls_passed': sum(r['control'] in ('correct', 'equivalent') and r['status'] == 'passed' for r in results),
                       'wrong_controls_rejected': sum(r['control'] not in ('correct', 'equivalent') and r['status'] == 'candidate_error' for r in results),
                       'model_calls': 0, 'whole_task_passed': None},
        'source_sha256': {str(p.relative_to(ROOT)): digest(p) for p in source_files},
        'controls': results, 'reviewed_counterexamples': witness_results,
        'limitations': ['Four scoped finite contracts, not four universally correct plans.',
                        'Controls are reviewer authored, not independently annotated model outputs.',
                        'Two archived formula branches only; fallback/full plans remain unverified.',
                        'Six other case sidecars are design/catalogue only.',
                        'No quantum solver, resource/stability experiment or model rerun.'],
    }
    for name, value in [('controls.json', controls), ('reviewed_claims.json', witnesses), ('results.json', report)]:
        with (output / name).open('x') as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write('\n')
    print(json.dumps(report['population'], ensure_ascii=False))
    return 0 if all(r['matched_expected'] for r in results) and all(
        r['status_counts'].get('candidate_error') == 1 for r in witness_results) else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    raise SystemExit(run(parser.parse_args().output))
