"""The private case verifier must reject plausible wrong answers, not just parse them."""
import copy
import importlib.util
import json
from itertools import combinations
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'pilot/semantic_verification/v0.1'
sys.path.insert(0, str(PACKAGE))
spec = importlib.util.spec_from_file_location('semantic_claim_evaluation', PACKAGE / 'evaluate.py')
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)
from controls import VARIANTS, graph_claim, submission
from oracles import expected

SUITE = evaluation.load_suite()
CASES = {c['case_id']: c for c in SUITE['cases']}
ACTIVE = [cid for cid, case in CASES.items() if case['tests']]


@pytest.mark.parametrize('cid', ACTIVE)
@pytest.mark.parametrize('variant', ['correct', 'equivalent'])
def test_correct_and_equivalent_controls(cid, variant):
    report = evaluation.evaluate(CASES[cid], submission(CASES[cid], variant))
    assert report['status'] == 'passed', report
    assert report['format_valid']
    assert report['test_counts']['executed'] == len(CASES[cid]['tests'])
    assert report['task_pass'] is None
    assert report['migration_execution_success'] is None


MUTANTS = [
    ('lit-002', 'numeric_mask', 'tuple_not_mask', 'canonical_selection'),
    ('lit-002', 'positive_superincreasing', 'single_edge', 'canonical_selection'),
    ('lit-002', 'omit_constraints', 'single_edge', 'feasibility'),
    ('lit-004', 'omit_constraints', 'no_edges', 'feasibility'),
    ('lit-004', 'wrong_direction', 'complete', 'optimal_cardinality'),
    ('lit-005', 'ignore_locks', 'locked', 'predicate_equivalence'),
    ('lit-005', 'wrong_polarity', 'force_true', 'predicate_equivalence'),
    ('lit-005', 'arbitrary_solution', 'lex', 'canonical_selection_or_absence'),
    ('lit-008', 'wrong_endian', 'endian', 'full_ordered_report'),
    ('lit-008', 'sample_only', 'normal', 'full_ordered_report'),
]


@pytest.mark.parametrize('cid,variant,test_id,obligation', MUTANTS)
def test_semantically_wrong_controls_are_valid_and_fail_for_the_right_reason(cid, variant, test_id, obligation):
    report = evaluation.evaluate(CASES[cid], submission(CASES[cid], variant))
    assert report['status'] == 'candidate_error'
    assert report['format_valid']
    row = next(t for t in report['tests'] if t['test_id'] == test_id)
    assert any(f['obligation'] == obligation for f in row['failures']), report
    assert report['scoped_semantic_pass'] is False and report['task_pass'] is None


def test_independent_definition_anchors():
    """Hand-calculated anchors prevent generated expectations and oracle drifting together."""
    get = lambda cid, name: next(t['expected'] for t in CASES[cid]['tests'] if t['id'] == name)
    assert get('lit-002', 'tuple_not_mask') == [0, 3]
    assert get('lit-002', 'single_edge') == [0]
    assert get('lit-002', 'star') == [0]
    assert get('lit-004', 'path') == [0, 1]
    assert get('lit-004', 'no_edges') == [0]
    assert get('lit-005', 'lex') == {'marked': [[0, 1], [1, 0], [1, 1]], 'first': [0, 1]}
    assert get('lit-005', 'empty') == {'marked': [[]], 'first': []}
    assert get('lit-005', 'unsatisfiable') == {'marked': [], 'first': None}
    report = get('lit-008', 'overflow')
    assert [r['prefix_checksum'] for r in report['receipts']] == [255, 1]
    assert [r['bits'] for r in report['receipts']] == ['11111111', '00000010']


def test_every_ground_state_must_decode_correctly():
    case = CASES['lit-002']
    candidate = submission(case, 'correct')
    # Cost=k+3U gives BOTH minimum covers of single edge; do not accept just x0.
    candidate['claims']['single_edge']['terms'] = [
        {'coefficient': 3, 'variables': []}, {'coefficient': -2, 'variables': [0]},
        {'coefficient': -2, 'variables': [1]}, {'coefficient': 3, 'variables': [0, 1]}]
    report = evaluation.evaluate(case, candidate)
    row = next(r for r in report['tests'] if r['test_id'] == 'single_edge')
    assert row['status'] == 'candidate_error'
    assert row['failures'][0]['actual'] == [1]


def test_no_decoder_oracle_sharing_and_wrong_bit_order_detected():
    case = CASES['lit-002']
    candidate = submission(case, 'equivalent')
    candidate['claims']['star']['decode']['permutation'] = list(range(4))
    report = evaluation.evaluate(case, candidate)
    assert next(r for r in report['tests'] if r['test_id'] == 'star')['status'] == 'candidate_error'


def test_cannot_skip_test_or_supply_own_expected_answer():
    case = CASES['lit-002']
    candidate = submission(case, 'correct')
    del candidate['claims']['star']
    report = evaluation.evaluate(case, candidate)
    assert report['status'] == 'insufficient_evidence'
    assert report['scoped_semantic_pass'] is None
    candidate = submission(case, 'numeric_mask')
    candidate['claims']['tuple_not_mask']['expected'] = [1, 2]
    assert evaluation.evaluate(case, candidate)['status'] == 'candidate_error'


def test_predicate_correct_does_not_imply_ordered_selection_complete():
    case = CASES['lit-005']
    candidate = submission(case, 'correct')
    for claim in candidate['claims'].values():
        del claim['selected']
    report = evaluation.evaluate(case, candidate)
    assert report['status'] == 'insufficient_evidence'
    assert all(row['predicate_pass'] is True for row in report['tests'])


def test_unknowns_missing_and_delivery_failures_do_not_become_passes():
    case = CASES['lit-002']
    assert evaluation.evaluate(case, None)['status'] == 'not_run'
    assert evaluation.evaluate(case, {'case_id': 'lit-002'})['status'] == 'insufficient_evidence'
    for state in ['candidate_budget_exceeded', 'infrastructure_error', 'not_run']:
        report = evaluation.evaluate(case, {'case_id': 'lit-002', 'delivery_status': state, 'diagnostic': 'test'})
        assert report['status'] == state and report['scoped_semantic_pass'] is None
    report = evaluation.aggregate(SUITE, [submission(case, 'numeric_mask')])
    assert report['population'] == {'mother_cases': 10, 'input_conditions': 30, 'cases_with_scoped_oracle': 4,
                                    'submitted_cases': 1, 'cases_with_executed_checks': 1,
                                    'fully_executed_cases': 1, 'scoped_passed_cases': 0}
    assert report['status_counts']['not_run'] == 9
    for cid in ['lit-008', 'lit-009', 'lit-010']:
        assert CASES[cid]['reference']['structural_eligibility'] is None
    report = evaluation.evaluate(CASES['lit-009'], {'case_id': 'lit-009', 'delivery_status': 'candidate_budget_exceeded'})
    assert report['status'] == 'candidate_budget_exceeded'


def test_mixed_missing_checks_do_not_inflate_execution_denominator():
    candidate = submission(CASES['lit-002'], 'numeric_mask')
    del candidate['claims']['star']
    report = evaluation.aggregate(SUITE, [candidate])
    assert report['results'][1]['status'] == 'candidate_error'
    assert report['population']['fully_executed_cases'] == 0


def test_oracle_crash_is_infrastructure_not_candidate_error(monkeypatch):
    def broken(*args):
        raise RuntimeError('deliberate oracle outage')
    monkeypatch.setattr(evaluation, 'expected', broken)
    report = evaluation.evaluate(CASES['lit-002'], submission(CASES['lit-002'], 'correct'))
    assert report['status'] == 'infrastructure_error'
    assert report['scoped_semantic_pass'] is None
    assert 'deliberate oracle outage' in report['tests'][0]['reason']


def test_review_budget_is_not_candidate_budget_or_failure(monkeypatch):
    monkeypatch.setattr(evaluation, 'MAX_VARIABLES', 0)
    report = evaluation.evaluate(CASES['lit-002'], submission(CASES['lit-002'], 'correct'))
    assert report['status'] == 'review_budget_exceeded'
    assert report['scoped_semantic_pass'] is None


@pytest.mark.parametrize('change', ['float', 'nonbijective', 'invalid_terms', 'extra_test'])
def test_invalid_representation_classified_without_execution(change):
    case = CASES['lit-002']
    candidate = submission(case, 'correct')
    claim = candidate['claims']['single_edge']
    if change == 'float':
        claim['terms'][0]['coefficient'] = 0.1
    elif change == 'nonbijective':
        claim['decode']['permutation'] = [0, 0]
    elif change == 'invalid_terms':
        claim['terms'] = '__import__("os").system("false")'
    else:
        candidate['claims']['invented'] = claim
    assert evaluation.evaluate(case, candidate)['status'] == 'invalid_format'


def test_unsupported_representation_is_unjudged_not_false():
    case = CASES['lit-002']
    candidate = submission(case, 'correct')
    for claim in candidate['claims'].values():
        claim['kind'] = 'alternative_two_stage_construction'
    assert evaluation.evaluate(case, candidate)['status'] == 'insufficient_evidence'
    candidate = submission(case, 'numeric_mask')
    candidate['claim_scope'] = 'core_cardinality_only_with_separate_exact_fallback'
    assert evaluation.evaluate(case, candidate)['status'] == 'insufficient_evidence'


def test_contract_regeneration_and_pinned_sources(tmp_path, monkeypatch):
    target = tmp_path / 'contracts.json'
    command = [sys.executable, '-B', str(PACKAGE / 'build_contracts.py'), '--output', str(target)]
    result = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0, result.stderr
    assert target.read_bytes() == (PACKAGE / 'contracts.json').read_bytes()
    monkeypatch.setattr(evaluation, 'digest', lambda _: 'tampered')
    with pytest.raises(evaluation.DataError, match='Pinned source changed'):
        evaluation.load_suite()


def test_cli_reports_fixed_population_and_refuses_overwrite(tmp_path):
    source, output = tmp_path / 'claims.json', tmp_path / 'results.json'
    source.write_text(json.dumps([submission(CASES[cid], 'correct') for cid in ACTIVE]))
    command = [sys.executable, '-B', str(PACKAGE / 'evaluate.py'), '--claims', str(source), '--output', str(output)]
    first = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)
    assert first.returncode == 0, first.stderr
    report = json.loads(output.read_text())
    assert report['population']['scoped_passed_cases'] == 4
    assert report['population']['mother_cases'] == 10
    before = output.read_bytes()
    assert subprocess.run(command, capture_output=True).returncode == 2
    assert output.read_bytes() == before


def test_duplicate_unknown_or_malformed_population_rejected():
    candidate = submission(CASES['lit-002'], 'correct')
    for rows in [[candidate, candidate], [{'case_id': 'fake'}], {}, [None]]:
        with pytest.raises(evaluation.DataError):
            evaluation.aggregate(SUITE, rows)


def test_published_test_inputs_do_not_contain_private_new_claims():
    # A narrow allowlist/byte-binding check, not proof of OS sandbox isolation.
    for case in SUITE['cases']:
        text = (ROOT / case['input_path']).read_text()
        assert 'semantic_verification' not in text
        assert 'positive_superincreasing' not in text
        assert evaluation.digest(ROOT / case['input_path']) == case['input_sha256']


def test_old_coarse_diagnostics_do_not_imply_new_semantic_pass():
    path = ROOT / 'pilot/provisional_labels/v0.1/test_labels.py'
    spec = importlib.util.spec_from_file_location('original_reference_test_helpers', path)
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    predictions = helpers.predictions()
    predictions[1]['plan']['formulation'] = 'min A*sum(x)+P*uncovered+C*sum(2**i*x_i), C>0'
    coarse = helpers.evaluation.evaluate(predictions, 'C', 'SYNTHETIC_CONTROL')
    assert coarse['aggregate']['structural_eligibility']['matched'] == 7
    assert coarse['plan_coverage']['present'] == 7
    assert coarse['results'][1]['task_pass'] is None
    assert evaluation.evaluate(CASES['lit-002'], submission(CASES['lit-002'], 'numeric_mask'))['status'] == 'candidate_error'


@pytest.mark.parametrize('kind', ['cover', 'clique'])
def test_graph_constructions_on_all_simple_graphs_through_four_vertices(kind):
    checked = 0
    for n in range(5):
        pairs = list(combinations(range(n), 2))
        for mask in range(2 ** len(pairs)):
            problem = {'n': n, 'edges': [list(edge) for i, edge in enumerate(pairs) if mask & 2 ** i]}
            for variant in ['correct', 'equivalent']:
                assert evaluation.check_claim(kind, problem, graph_claim(kind, problem, variant)) == []
            checked += 1
    assert checked == 76


def test_reviewed_model_witnesses_and_tampered_quote():
    from run_controls import reviewed_counterexamples
    case = CASES['lit-002']
    for candidate in reviewed_counterexamples(case):
        report = evaluation.evaluate(case, candidate)
        assert report['status'] == 'candidate_error'
        executed = [r for r in report['tests'] if r['status'] == 'candidate_error']
        assert len(executed) == 1
        assert executed[0]['failures'][0]['obligation'] == 'canonical_selection'
        expected = [1] if candidate['model'] == 'deepseek-flash' else [1, 2]
        assert executed[0]['failures'][0]['actual'] == expected
        candidate['provenance']['quote'] = 'This quote never occurred in the response.'
        assert evaluation.evaluate(case, candidate)['status'] == 'infrastructure_error'


def test_original_programs_agree_with_new_receipt_and_search_oracles():
    """Execute ONLY reviewed repository source in separate Python processes."""
    for cid in ['lit-005', 'lit-008']:
        folder = ROOT / 'pilot/reference_completion/v0.1.1/cases' / cid
        inputs = [t['input'] for t in CASES[cid]['tests']]
        code = ('import kernel,json,sys; print(json.dumps([kernel.complete(p["n"],p["clauses"],dict(p["locked"])) for p in json.load(sys.stdin)]))'
                if cid == 'lit-005' else
                'import program,json,sys; print(json.dumps([program.review(p) for p in json.load(sys.stdin)]))')
        completed = subprocess.run([sys.executable, '-B', '-c', code], input=json.dumps(inputs),
                                   capture_output=True, text=True, cwd=folder, check=True)
        actual = json.loads(completed.stdout)
        for problem, row in zip(inputs, actual):
            wanted = expected(CASES[cid]['oracle_kind'], problem)
            if cid == 'lit-005':
                assert row == wanted['first']
            else:
                assert row == wanted


def test_controls_runner_emits_reviewable_evidence(tmp_path):
    output = tmp_path / 'controls'
    command = [sys.executable, '-B', str(PACKAGE / 'run_controls.py'), '--output', str(output)]
    result = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0, result.stderr
    report = json.loads((output / 'results.json').read_text())
    assert report['population']['correct_controls_passed'] == 8
    assert report['population']['wrong_controls_rejected'] == 10
    assert all(row['matched_expected'] for row in report['controls'])
