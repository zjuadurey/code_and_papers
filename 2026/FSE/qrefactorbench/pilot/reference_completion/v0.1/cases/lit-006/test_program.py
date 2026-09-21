from copy import deepcopy
from itertools import product
import json
from pathlib import Path
import pytest
import kernel
import program


def example():return json.loads(Path(__file__).with_name('example_request.json').read_text())


def oracle(items,cap):
    feasible=[m for m in range(1<<len(items)) if sum(x['weight'] for i,x in enumerate(items) if m&(1<<i))<=cap]
    return min(feasible,key=lambda m:(-sum(x['value'] for i,x in enumerate(items) if m&(1<<i)),m))


def test_original_task_optimum():
    r=example();out=program.review(r);mask=oracle(r['items'],7)
    assert kernel.choose(r['items'],7)==mask==17
    assert out['windows'][0]['proposal']=={'ids':['item0','item4'],'weight':7,'value':8,'feasible':True}
    assert out['windows'][0]['transfers']==[{'id':'item0','offset':0,'length':2},{'id':'item4','offset':2,'length':5}]


def test_bounded_items_capacity_and_ties():
    choices=[{'weight':w,'value':v} for w in (1,2) for v in (0,1,2)]
    for n in range(4):
        for items in product(choices,repeat=n):
            for capacity in range(5):assert kernel.choose(items,capacity)==oracle(items,capacity)


def test_filter_independence_inspection_and_no_mutation(monkeypatch):
    r=example();r['items'][4]['active']=False
    r['windows']=[{'id':m,'capacity':7,'current':['item4'],'mode':m} for m in ('inspect','select')]
    before=deepcopy(r);out=program.review(r)
    assert not out['windows'][0]['current']['feasible']
    assert out['windows'][0]['proposal'] is None
    assert 'item4' not in out['windows'][1]['proposal']['ids'] and r==before
    r['windows']=r['windows'][:1];monkeypatch.setattr(program,'choose',lambda *_:pytest.fail('inspection'))
    program.review(r)


def test_wrong_solver_is_detected(monkeypatch):
    r=example();good=program.review(r)
    monkeypatch.setattr(program,'choose',lambda items,cap:(1<<len(items))-1)
    bad=program.review(r)
    assert bad!=good and not bad['windows'][0]['proposal']['feasible']


@pytest.mark.parametrize('field,value',[('weight',0),('weight',True),('value',-1),('active',1)])
def test_invalid_item(field,value):
    r=example();r['items'][-1][field]=value
    with pytest.raises(ValueError):program.review(r)


def test_invalid_late_window_and_no_partial_work(monkeypatch):
    r=example();r['windows'].append({'id':'bad','capacity':2,'current':['missing'],'mode':'select'})
    monkeypatch.setattr(program,'choose',lambda *_:pytest.fail('must validate entire batch'))
    with pytest.raises(ValueError):program.review(r)
