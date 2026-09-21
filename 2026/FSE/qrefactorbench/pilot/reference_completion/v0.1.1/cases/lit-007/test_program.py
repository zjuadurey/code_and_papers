import ast
from itertools import combinations,product
from pathlib import Path
from types import SimpleNamespace
from copy import deepcopy
import json
import pytest
import kernel
import program


def test_score_matches_extracted_upstream_method():
    source=Path(__file__).resolve().parents[3]/'v0.1/sources/supermarq.py'
    tree=ast.parse(source.read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef))
    node=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='_get_energy_for_bitstring')
    scope={};exec(compile(ast.Module(body=[node],type_ignores=[]),'reviewed_source_method','exec'),scope)
    score=scope[node.name]
    for n in range(5):
        pairs=list(combinations(range(n),2))
        for weights in product((-1,1),repeat=len(pairs)):
            terms=[(i,j,w) for (i,j),w in zip(pairs,weights)]
            outcomes=[]
            for mask in range(1<<n):
                values=[bool(mask&(1<<i)) for i in range(n)]
                actual=score(SimpleNamespace(hamiltonian=terms),''.join('1' if v else '0' for v in values))
                assert kernel.score(values,terms)==actual
                outcomes.append(actual)
            optimum=min(range(len(outcomes)),key=lambda m:(-outcomes[m],m))
            assert kernel.choose(n,terms)==[bool(optimum&(1<<i)) for i in range(n)]


def example():return json.loads(Path(__file__).with_name('example_request.json').read_text())


def test_signed_preferences_full_report_and_tie():
    r=example();before=deepcopy(r);out=program.review(r)
    assert out['current']['score']==-1
    assert out['proposed']=={'groups':[['a','c'],['b']],'score':3,'violated':[]}
    assert out['gain']==4 and out['moves']==['b'] and r==before


def test_inspection_does_not_optimize(monkeypatch):
    r=example();r['mode']='inspect';monkeypatch.setattr(program,'choose',lambda *_:pytest.fail('no selection'))
    assert program.review(r)['proposed'] is None


def test_unweighted_cut_is_not_same_objective(monkeypatch):
    r=example();original=kernel.choose
    monkeypatch.setattr(program,'choose',lambda n,p:original(n,[(i,j,1) for i,j,w in p]))
    assert program.review(r)['proposed']['score'] < 3


@pytest.mark.parametrize('kind',['missing_pair','reversed_duplicate','unknown','bad_bits'])
def test_validation(kind):
    r=example()
    if kind=='missing_pair':r['preferences'].pop()
    elif kind=='reversed_duplicate':r['preferences'].append({'left':'b','right':'a','relation':'apart'})
    elif kind=='unknown':r['preferences'][0]['left']='missing'
    else:r['current']=[0,0,0]
    with pytest.raises(ValueError):program.review(r)
