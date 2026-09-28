import copy
import json
from itertools import combinations, product
import pytest
from build import control, make_tests
from engine import parse, evaluate, compile_template, arithmetic, syntax, base, InvalidTemplate, TemplateBudget
from run import revision_prompt

TESTS = make_tests()


@pytest.mark.parametrize('variant', ['correct', 'equivalent'])
def test_positive_controls(variant):
    result = evaluate(json.dumps(control(variant)), TESTS['development'] + TESTS['final'])
    assert result['status'] == 'passed', result
    assert result['tests_executed'] == result['tests_planned']
    assert result['task_pass'] is None


@pytest.mark.parametrize('variant,test_id,obligation', [
    ('numeric_mask', 'tuple_not_mask', 'canonical_selection'),
    ('positive_superincreasing', 'single_edge', 'canonical_selection'),
    ('omit_constraints', 'single_edge', 'feasibility'),
    ('omit_tie', 'single_edge', 'canonical_selection'),
    ('wrong_sense', 'single_edge', 'feasibility'),
])
def test_wrong_controls(variant, test_id, obligation):
    result = evaluate(json.dumps(control(variant)), TESTS['development'])
    assert result['format_valid'] is True
    assert result['status'] == 'candidate_error'
    row = next(r for r in result['tests'] if r['id'] == test_id)
    assert any(f['obligation'] == obligation for f in row['failures'])


def test_independent_anchors_and_all_optima():
    rows = {t['id']: t for t in TESTS['development']}
    assert base.expected('cover', rows['single_edge']['input']) == [0]
    assert base.expected('cover', rows['tuple_not_mask']['input']) == [0, 3]
    claim = compile_template(control('omit_tie'), rows['single_edge']['input'])
    assert any(f['actual'] == [1] for f in base.check_claim('cover', rows['single_edge']['input'], claim))


def test_compiler_energy_agrees_with_direct_math():
    # Independent numerical expression, not compiled template as its own oracle.
    p = {'n': 4, 'edges': [[0, 1], [0, 2], [1, 3], [2, 3]]}
    for variant in ('correct', 'equivalent'):
        claim = compile_template(control(variant), p)
        energy = base.polynomial(claim, 4)
        for y in product((0, 1), repeat=4):
            x = y if variant == 'correct' else [1-y[3-i] for i in range(4)]
            wanted = sum((16-2**(3-i))*x[i] for i in range(4)) + 65*sum((1-x[i])*(1-x[j]) for i,j in p['edges'])
            if variant == 'equivalent':
                wanted = -3*base.Fraction(wanted, 2)+7
            assert energy(y) == wanted


@pytest.mark.parametrize('expr', ['__import__("os")', 'n.__class__', '[n]', 'True', '1.2', 'n//2', 'sum(n)', '2 if n else 1'])
def test_reject_executable_or_unsupported_syntax(expr):
    with pytest.raises(InvalidTemplate):
        syntax(expr, {'n'})


@pytest.mark.parametrize('expr', ['2**1000', '2**(2**32)'])
def test_budget_before_large_power(expr):
    with pytest.raises(TemplateBudget):
        arithmetic(syntax(expr, set()), {})


def test_format_not_semantics_and_no_silent_repair():
    assert evaluate('```json\n{}\n```', TESTS['development'])['status'] == 'candidate_format_error'
    with pytest.raises(InvalidTemplate):
        parse('{"version":1,"version":2}')
    obj = control()
    obj['decode']['index'] = '0'
    result = evaluate(json.dumps(obj), TESTS['development'])
    assert result['format_valid'] and result['status'] == 'candidate_error'


def test_final_disjoint_and_branch_input_boundaries():
    key = lambda t: json.dumps(t['input'], sort_keys=True)
    assert not {key(t) for t in TESTS['development']} & {key(t) for t in TESTS['final']}
    baseline = revision_prompt('PUBLIC', 'RAW', 'self_review', {'SECRET': 1})
    enhanced = revision_prompt('PUBLIC', 'RAW', 'counterexample', {'SECRET': 1})
    assert 'RAW' in baseline and 'RAW' in enhanced
    assert 'SECRET' not in baseline and 'SECRET' in enhanced


def test_infrastructure_failure_not_candidate_failure(monkeypatch):
    def broken(*args):
        raise OSError('test infrastructure failure')
    monkeypatch.setattr(base, 'check_claim', broken)
    report = evaluate(json.dumps(control()), TESTS['development'])
    assert report['status'] == 'infrastructure_error' and report['finite_semantic_pass'] is None


def test_domain_upper_boundary_instantiation_only():
    # This verifies representation at n=16, not semantic correctness for all such graphs.
    for variant in ('correct', 'equivalent'):
        claim = compile_template(control(variant), {'n': 16, 'edges': list(combinations(range(16), 2))})
        assert len(claim['terms']) <= 137
        base.decoder(claim, 16)
        base.polynomial(claim, 16)
