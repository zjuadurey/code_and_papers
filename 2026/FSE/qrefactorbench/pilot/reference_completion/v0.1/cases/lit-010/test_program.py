from copy import deepcopy
import json
from pathlib import Path
import math
import pytest
import kernel
import program


def example():return json.loads(Path(__file__).with_name('example_request.json').read_text())


def test_one_iteration_is_not_the_exact_solution():
    r=example();before=deepcopy(r);out=program.review(r)
    # Independently hand-derived first iterate: alpha=(1+4)/(6+14)=1/4.
    assert out['proposal']=={'left':0.25,'right':0.5}
    assert out['iterations']==1 and out['trace'][0]['residual_norm']==pytest.approx(math.sqrt(5)/4)
    assert out['proposal']!={'left':1/11,'right':7/11} and r==before


def test_two_iterations_and_direct_residual():
    r=example();r['steps']=2;out=program.review(r)
    assert list(out['proposal'].values())==pytest.approx([1/11,7/11])
    assert out['final_residual_norm']<1e-14


@pytest.mark.parametrize('mode,steps,tolerance',[('inspect',3,0),('advance',0,0),('advance',3,1)])
def test_bypass_and_zero_budget(mode,steps,tolerance,monkeypatch):
    r=example();r.update(mode=mode,steps=steps,relative_tolerance=tolerance)
    if mode=='inspect':monkeypatch.setattr(program,'advance',lambda *_:pytest.fail('inspection'))
    out=program.review(r);assert out['iterations']==0 and out['trace']==[]


def test_zero_initial_residual():
    r=example();r.update(rhs=[5,4],current=[1,1],steps=3)
    out=program.review(r);assert out['iterations']==0 and out['final_residual_norm']==0


def test_sparse_matvec_matches_dense_and_symmetry():
    rows=[[(0,4.0),(1,1.0)],[(0,1.0),(1,3.0)]]
    for x in ([0,0],[1,2],[-2,3]):
        assert kernel.apply(rows,x)==[4*x[0]+x[1],x[0]+3*x[1]]
    x,y=[2,-1],[3,4]
    assert kernel.dot(x,kernel.apply(rows,y))==kernel.dot(y,kernel.apply(rows,x))


def test_wrong_exact_substitution_loses_requested_trace(monkeypatch):
    good=program.review(example())
    monkeypatch.setattr(program,'advance',lambda *args:([1/11,7/11],math.sqrt(5),[]))
    bad=program.review(example());assert bad['final_residual_norm']<good['final_residual_norm']
    assert bad!=good and bad['iterations']==0


@pytest.mark.parametrize('kind',['nonsymmetric','duplicate','not_dominant','bad_steps','nan'])
def test_validation(kind):
    r=example()
    if kind=='nonsymmetric':r['entries'][1]['value']=2
    elif kind=='duplicate':r['entries'].append(deepcopy(r['entries'][0]))
    elif kind=='not_dominant':r['entries'][0]['value']=1
    elif kind=='bad_steps':r['steps']=True
    else:r['rhs'][0]=float('nan')
    with pytest.raises(ValueError):program.review(r)
