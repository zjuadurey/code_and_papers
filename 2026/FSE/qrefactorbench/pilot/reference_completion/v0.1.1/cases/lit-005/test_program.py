import json
from copy import deepcopy
from itertools import product
from pathlib import Path
import pytest
import kernel
import program


@pytest.mark.parametrize('mode', ['inspect', 'complete'])
def test_locked_failures_follow_feature_order_not_mapping_order(mode):
    from itertools import permutations
    for order in permutations(['b', 'z', 'a']):
        request = {'features': ['z', 'a', 'b'], 'rules': [],
                   'locked': {key: True for key in order},
                   'current': [False, True, False], 'mode': mode}
        before = deepcopy(request)
        result = program.review(request)
        assert result['locked_failures'] == ['z', 'b']
        assert result['status'] == ('inspected' if mode == 'inspect' else 'completed')
        assert request == before


def example():
    return json.loads(Path(__file__).with_name("example_request.json").read_text())


def test_source_formula_truth_table_and_output():
    r=example();clauses=[[(int(v['feature'][1:])-1,v['enabled']) for v in row['any']] for row in r['rules']]
    valid=[bits for bits in product((False,True),repeat=3) if all(any(bits[i]==v for i,v in c) for c in clauses)]
    assert valid==[(False,True,False),(False,True,True)]
    # Reverse feature order only for Qiskit's textual q2 q1 q0 outcome convention.
    assert {''.join(str(int(x)) for x in reversed(bits)) for bits in valid}=={'010','110'}
    out=program.review(r)
    assert out['proposal']=={'x1':False,'x2':True,'x3':False}
    assert out['failed_rules']==['r1'] and out['changes']==['x2']


def test_bounded_clause_subsets_and_locks():
    source=example();base=[[(int(v['feature'][1:])-1,v['enabled']) for v in row['any']] for row in source['rules']]
    for mask in range(64):
        clauses=[c for i,c in enumerate(base) if mask&(1<<i)]
        for locks in product((None,False,True),repeat=3):
            fixed={i:v for i,v in enumerate(locks) if v is not None}
            expected=next((list(x) for x in product((False,True),repeat=3)
                           if all(x[i]==v for i,v in fixed.items()) and all(any(x[i]==v for i,v in c) for c in clauses)),None)
            assert kernel.complete(3,clauses,fixed)==expected


@pytest.mark.parametrize('mode',['inspect','complete'])
def test_inspect_or_valid_current_skips_completion(mode,monkeypatch):
    r=example();r.update(mode=mode,current=[False,True,True])
    monkeypatch.setattr(program,'complete',lambda *_:pytest.fail('unexpected completion'))
    out=program.review(r)
    assert out['status']==('inspected' if mode=='inspect' else 'retained')
    if mode=='complete':assert out['proposal']['x3'] is True


def test_locks_absence_and_input_identity():
    r=example();r['locked']={'x2':False};before=deepcopy(r)
    out=program.review(r);assert out['status']=='unavailable' and out['proposal'] is None
    assert r==before


def test_wrong_dependency_and_wrong_region_change_contract(monkeypatch):
    r=example();r['locked']={'x3':True}
    good=program.review(r);original=program.complete
    monkeypatch.setattr(program,'complete',lambda n,c,l:original(n,c,{}))
    assert program.review(r)!=good
    monkeypatch.undo();r['current']=[False,True,True]
    monkeypatch.setattr(program,'conforms',lambda *_:False)
    assert program.review(r)['status']=='completed'  # Different from required retained path.


@pytest.mark.parametrize('edit',[lambda r:r.update(current=[0,1,0]),lambda r:r['rules'][-1]['any'][0].update(feature='missing'),lambda r:r.update(locked={'bad':True})])
def test_invalid_request_before_solver(edit,monkeypatch):
    r=example();edit(r);monkeypatch.setattr(program,'complete',lambda *_:pytest.fail('validate first'))
    with pytest.raises(ValueError):program.review(r)
