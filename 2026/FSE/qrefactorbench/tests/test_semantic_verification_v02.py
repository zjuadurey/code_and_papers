"""Six remaining cases, alternative mappings, numerical boundaries and inheritance."""
from copy import deepcopy
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'pilot/semantic_verification/v0.2'
sys.path.insert(0, str(PACKAGE))
import verification as v
from control_extensions import VARIANTS, submission

SUITE = v.load_suite()
CASES = {c['case_id']: c for c in SUITE['cases']}
NEW = ['lit-001', 'lit-003', 'lit-006', 'lit-007', 'lit-009', 'lit-010']


@pytest.mark.parametrize('cid,variant', [(cid, variant) for cid in CASES for variant in VARIANTS[CASES[cid]['oracle_kind']]])
def test_all_cases_with_correct_equivalent_and_wrong_controls(cid, variant):
    report = v.evaluate(CASES[cid], submission(CASES[cid], variant))
    wanted = 'passed' if variant in ('correct', 'equivalent', 'one_hot', 'one_hot_equivalent') else 'candidate_error'
    assert report['status'] == wanted, report
    assert report['format_valid'] is True
    assert report['test_counts']['executed'] == len(CASES[cid]['tests'])
    assert report['task_pass'] is None


WITNESSES = [
    ('lit-001', 'ignore_weights', 'weighted_triangle', 'objective_or_canonical_decode'),
    ('lit-001', 'wrong_direction', 'one_edge', 'objective_or_canonical_decode'),
    ('lit-001', 'round_weights', 'large_integer', 'objective_or_canonical_decode'),
    ('lit-003', 'ignore_edges', 'edge', 'color_predicate'),
    ('lit-003', 'invalid_codes', 'invalid_binary_code', 'color_predicate'),
    ('lit-003', 'missing_one_hot', 'edge', 'zero_energy_iff_valid_coloring'),
    ('lit-003', 'greedy_absence', 'greedy_trap', 'lex_first_or_absence'),
    ('lit-003', 'negative_penalty', 'edge', 'feasible_energy_is_bound'),
    ('lit-006', 'ignore_capacity', 'zero_capacity', 'capacity'),
    ('lit-006', 'ignore_values', 'value_not_count', 'objective_or_canonical_decode'),
    ('lit-006', 'wrong_tie', 'mask_tie', 'objective_or_canonical_decode'),
    ('lit-006', 'no_slack', 'unused_capacity', 'objective_or_canonical_decode'),
    ('lit-007', 'ignore_sign', 'together', 'objective_or_canonical_decode'),
    ('lit-007', 'wrong_direction', 'apart', 'objective_or_canonical_decode'),
    ('lit-009', 'signed_pivot', 'pivot_abs', 'pivot'),
    ('lit-009', 'last_tie', 'pivot_tie', 'pivot'),
    ('lit-009', 'ignore_rhs', 'swap', 'solution'),
    ('lit-010', 'exact_substitution', 'one_step', 'iterate'),
    ('lit-010', 'ignore_budget', 'zero_budget', 'iterate'),
    ('lit-010', 'omit_trace', 'one_step', 'trace'),
]


@pytest.mark.parametrize('cid,variant,test_id,obligation', WITNESSES)
def test_each_wrong_control_has_specific_discriminating_witness(cid, variant, test_id, obligation):
    report = v.evaluate(CASES[cid], submission(CASES[cid], variant))
    row = next(r for r in report['tests'] if r['test_id'] == test_id)
    assert row['status'] == 'candidate_error'
    assert any(f['obligation'] == obligation for f in row['failures']), row


def test_hand_derived_anchors():
    get = lambda cid, name: next(t['expected'] for t in CASES[cid]['tests'] if t['id'] == name)
    assert get('lit-001', 'weighted_triangle') == [0, 1]
    assert get('lit-001', 'large_integer') == [1]
    assert get('lit-003', 'greedy_trap')['first'] == [0, 1, 1, 0]
    assert get('lit-003', 'empty') == {'solutions': [[]], 'first': []}
    assert get('lit-003', 'no_colors') == {'solutions': [], 'first': None}
    assert get('lit-006', 'source_example') == [0, 4]
    assert get('lit-006', 'unused_capacity') == [0]
    assert get('lit-007', 'mixed') == [1]
    assert get('lit-009', 'swap') == {'solution': [1.0, 2.0]}
    assert get('lit-009', 'residual')['scaled_backward_error'] == 2 ** 50
    assert get('lit-010', 'one_step') == {'iterate': [0.25, 0.5], 'initial_norm': math.sqrt(5),
        'trace': [{'iteration': 1, 'residual_norm': math.sqrt(5) / 4}], 'final_residual_norm': math.sqrt(5) / 4}


def test_coloring_two_families_are_accepted_without_promoting_labels():
    case = CASES['lit-003']
    for variant in ['correct', 'one_hot']:
        assert v.evaluate(case, submission(case, variant))['status'] == 'passed'
    assert case['reference']['status'] == 'PENDING' and case['reference']['gold'] is False
    candidate = submission(case, 'correct')
    del candidate['claims']['edge']['selected']
    assert v.evaluate(case, candidate)['status'] == 'insufficient_evidence'
    candidate['claims']['edge']['representation'] = 'different_valid_encoding_needing_review'
    assert v.evaluate(case, candidate)['status'] == 'insufficient_evidence'


def test_coloring_zero_set_alone_does_not_validate_minimization():
    case = CASES['lit-003']
    candidate = submission(case, 'one_hot')
    # Negating all penalties keeps precisely the same zeros but rewards violations.
    for claim in candidate['claims'].values():
        for term in claim['terms']:
            term['coefficient'] = str(-v.base.rational(term['coefficient']))
    report = v.evaluate(case, candidate)
    assert report['status'] == 'candidate_error'
    assert any(f['obligation'] == 'feasible_energy_is_bound' for row in report['tests'] for f in row.get('failures', []))


def test_numeric_behavior_is_not_structural_no_or_full_migration():
    for cid in ['lit-009', 'lit-010']:
        case = CASES[cid]
        assert case['reference']['structural_eligibility'] is None
        result = v.evaluate(case, submission(case, 'correct'))
        assert result['scoped_semantic_pass'] is True
        assert result['task_pass'] is None and result['practical_advantage'] is None
    # Exact substitution actually gives a lower residual but violates the requested iterate.
    case = CASES['lit-010']
    right = submission(case, 'correct')['claims']['one_step']['result']
    wrong = submission(case, 'exact_substitution')['claims']['one_step']['result']
    assert wrong['final_residual_norm'] < right['final_residual_norm']
    assert wrong['iterate'] != right['iterate']


def test_budget_failure_and_missing_tests_do_not_pass():
    case = CASES['lit-006']
    candidate = submission(case, 'correct')
    candidate['claims']['source_example']['variable_count'] = 100
    assert v.evaluate(case, candidate)['status'] == 'review_budget_exceeded'
    candidate = submission(case, 'correct')
    del candidate['claims']['source_example']
    assert v.evaluate(case, candidate)['status'] == 'insufficient_evidence'
    candidate = {'case_id': 'lit-009', 'delivery_status': 'candidate_budget_exceeded'}
    assert v.evaluate(CASES['lit-009'], candidate)['status'] == 'candidate_budget_exceeded'


def test_auxiliary_variable_decode_must_be_valid():
    case = CASES['lit-006']
    candidate = submission(case, 'equivalent')
    candidate['claims']['mask_tie']['decode']['permutation'] = [0, 0, 0]
    assert v.evaluate(case, candidate)['status'] == 'invalid_format'


def test_fixed_ten_case_denominator_and_no_false_whole_task_pass():
    report = v.aggregate(SUITE, [submission(c, 'correct') for c in CASES.values()])
    assert report['population']['mother_cases'] == 10
    assert report['population']['cases_with_scoped_oracle'] == 10
    assert report['population']['fully_executed_cases'] == 10
    assert report['population']['scoped_passed_cases'] == 10
    assert report['task_pass'] is None
    partial = v.aggregate(SUITE, [submission(CASES['lit-001'], 'correct')])
    assert partial['status_counts']['not_run'] == 9


def test_numerical_nonfinite_and_boolean_are_not_valid_exact_results():
    case = CASES['lit-009']
    for bad in [float('nan'), float('inf'), True]:
        candidate = submission(case, 'correct')
        candidate['claims']['swap']['result']['solution'][0] = bad
        assert v.evaluate(case, candidate)['status'] == 'candidate_error'


def test_engine_error_not_a_candidate_error(monkeypatch):
    original = v.expected
    def broken(kind, problem):
        if kind == 'knapsack':
            raise RuntimeError('test injected outage')
        return original(kind, problem)
    monkeypatch.setattr(v, 'expected', broken)
    assert v.evaluate(CASES['lit-006'], submission(CASES['lit-006'], 'correct'))['status'] == 'infrastructure_error'


def test_inherited_cases_and_public_inputs_unchanged():
    old = json.loads((v.PREVIOUS / 'contracts.json').read_text())
    for c in old['cases']:
        if c['case_id'] not in NEW:
            assert CASES[c['case_id']] == c
    for path, sha in SUITE['source_sha256'].items():
        assert v.base.digest(ROOT / path) == sha


def test_regeneration_and_cli(tmp_path):
    path = tmp_path / 'contracts.json'
    result = subprocess.run([sys.executable, '-B', str(PACKAGE / 'build_contracts.py'), '--output', str(path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert path.read_bytes() == (PACKAGE / 'contracts.json').read_bytes()
    claims, output = tmp_path / 'claims.json', tmp_path / 'result.json'
    claims.write_text(json.dumps([submission(CASES[cid], 'correct') for cid in NEW]))
    command = [sys.executable, '-B', str(PACKAGE / 'verification.py'), '--claims', str(claims), '--output', str(output)]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text())['population']['scoped_passed_cases'] == 6
    before = output.read_bytes()
    assert subprocess.run(command, capture_output=True).returncode == 2
    assert output.read_bytes() == before


def test_runner_records_every_control(tmp_path):
    result = subprocess.run([sys.executable, '-B', str(PACKAGE / 'run_verification.py'), '--output', str(tmp_path / 'run')], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    report = json.loads((tmp_path / 'run/results.json').read_text())
    assert report['population']['cases_actually_checked'] == 10
    assert report['population']['correct_controls_passed'] == 22
    assert report['population']['wrong_controls_rejected'] == 30
