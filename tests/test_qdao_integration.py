"""Focused adapter tests; the separate validation script exercises all families."""
from pathlib import Path
import sys
import numpy as np
import pytest
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'build/qdao-qthin-src'))
pytest.importorskip('qdao')
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from htp.e2e.runtime import Counters,QThinEngine,original

@pytest.mark.parametrize('kind',['product','staged','full','basis','phase_kickback'])
def test_file_backed_equivalence(tmp_path,kind):
    c=QuantumCircuit(6)
    if kind=='basis':c.x(0);c.cx(0,4)
    else:
        c.ry(.7,range(6));c.rz(.3,range(6))
        if kind in {'staged','full'}:
            c.cx(0,5);c.cx(2,3);c.cx(5,1)
        if kind=='full':c.cx(1,4);c.cx(4,3);c.h(2)
        if kind=='phase_kickback':c.h(5);c.cx(0,5)
    counters=Counters();thin=QThinEngine(c,4,2,tmp_path/'thin',counters);thin.run()
    baseline=original(c,4,2,tmp_path/'base',Counters()).full_small_state()
    assert Statevector(c).equiv(thin.full_small_state())
    assert Statevector(c).equiv(baseline)
    assert counters.sync_barrier_count==1
    assert counters.fdatasync_calls==1<<(len(thin.physical)-thin.manager._nl)
    assert all(e['write_bytes']==16*(1<<e['new_q']) for e in counters.events)
    assert all(e['read_bytes']==16*(1<<e['old_q']) for e in counters.events)
    if kind=='product':assert not counters.events and len(thin.physical)==0
    if kind=='staged':assert len(counters.events)>=2
    if kind=='full':assert len(thin.physical)==6

@pytest.mark.parametrize('scale',[0.,.001,1.,7.])
@pytest.mark.parametrize('legacy',[False,True])
def test_shared_state_injection_unnormalized(scale,legacy,monkeypatch):
    from htp.e2e.runtime import CountedEngine,configure
    if legacy:monkeypatch.setenv('HTP_QDAO_LEGACY_INITIALIZE','1')
    else:monkeypatch.delenv('HTP_QDAO_LEGACY_INITIALIZE',raising=False)
    c=QuantumCircuit(3);c.h(0);c.cx(0,2);c.ry(.7,1)
    rng=np.random.default_rng(197)
    vector=rng.normal(size=8)+1j*rng.normal(size=8)
    vector=vector/np.linalg.norm(vector)*scale
    expected=Statevector(vector).evolve(c).data
    c.save_state()
    engine=CountedEngine(circuit=c,num_primary=3,num_local=1);configure(engine)
    engine._circ_helper.circ=c
    result=engine._sim.run(engine._circ_helper.init_circ_from_sv(vector))
    assert np.max(np.abs(result-expected))<1e-12
