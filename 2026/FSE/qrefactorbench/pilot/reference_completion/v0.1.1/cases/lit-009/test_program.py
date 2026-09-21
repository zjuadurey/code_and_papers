from copy import deepcopy
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import pytest
import kernel
import program


@pytest.mark.parametrize('sign', [-1, 1])
def test_delta_overflow_rejected_by_api_and_cli(sign):
    import subprocess
    import sys
    request = {'variables': ['x'], 'matrix': [[1e-308]], 'rhs': [float(sign)],
               'current': [-sign * 1e308], 'mode': 'solve', 'residual_limit': 1.0}
    before = deepcopy(request)
    with pytest.raises(ValueError):
        program.review(request)
    assert request == before
    result = subprocess.run([sys.executable, '-B', str(Path(program.__file__))],
                            input=json.dumps(request), text=True, capture_output=True)
    assert result.returncode != 0 and result.stdout == ''
    assert 'ValueError' in result.stderr


def test_large_finite_delta_and_inspect_remain_valid():
    request = {'variables': ['x'], 'matrix': [[1e-308]], 'rhs': [0.5],
               'current': [0.0], 'mode': 'solve', 'residual_limit': 1.0}
    result = program.review(request)
    assert result['deltas']['x'] == result['proposal']['x']
    json.dumps(result, allow_nan=False)
    request.update(rhs=[1.0], current=[-1e308], mode='inspect')
    result = program.review(request)
    assert result['deltas'] is None and result['proposal'] is None
    json.dumps(result, allow_nan=False)


def example():return json.loads(Path(__file__).with_name('example_request.json').read_text())


def test_partial_pivot_and_full_report():
    r=example();before=deepcopy(r);out=program.review(r)
    assert out['proposal']=={'supply':1.0,'return':2.0}
    assert out['proposed_residual']['infinity_norm']==0
    assert out['within_requested_limit'] is True and r==before


def test_two_by_two_exact_rational_reference():
    for a,b,c,d in product(range(-2,3),repeat=4):
        det=a*d-b*c
        if det==0:continue
        x=kernel.solve([[a,b],[c,d]],[1,2])
        expected=[float(Fraction(d-2*b,det)),float(Fraction(2*a-c,det))]
        assert x==pytest.approx(expected,abs=1e-12,rel=1e-12)


def test_inspection_singular_and_empty(monkeypatch):
    r=example();r.update(mode='inspect',matrix=[[0,0],[0,0]])
    monkeypatch.setattr(program,'solve',lambda *_:pytest.fail('no solve'))
    assert program.review(r)['proposal'] is None
    monkeypatch.undo();r['mode']='solve'
    with pytest.raises(ValueError):program.review(r)
    r.update(variables=[],matrix=[],rhs=[],current=[])
    assert program.review(r)['proposal']=={}


def test_wrong_vector_is_visible_and_limit_is_caller_supplied(monkeypatch):
    r=example();monkeypatch.setattr(program,'solve',lambda *_:[0.0,0.0])
    bad=program.review(r)
    assert bad['proposed_residual']['infinity_norm']==7 and not bad['within_requested_limit']
    r['residual_limit']=bad['proposed_residual']['scaled_backward_error']
    assert program.review(r)['within_requested_limit'] is True


@pytest.mark.parametrize('field,value',[('rhs',[True,2]),('matrix',[[1],[2]]),('current',[float('nan'),0]),('residual_limit',-1)])
def test_invalid_request(field,value):
    r=example();r[field]=value
    with pytest.raises(ValueError):program.review(r)
