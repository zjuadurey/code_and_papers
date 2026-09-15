import math
import pytest
from qiskit import QuantumCircuit
from htp.analyzer import analyze
from htp.metrics import volume_metrics

def test_hand_volume():
    r=volume_metrics(3,[1,2,3]); assert r['reduction_factor_if_representable']==pytest.approx(24/14)

def test_overflow_and_empty():
    assert volume_metrics(10000,[0,0])['reduction_factor_if_representable'] is None
    assert volume_metrics(10000,[10000,10000])['log2_reduction']==pytest.approx(0)
    assert volume_metrics(3,[])['log2_reduction'] is None

def test_layer_replay_not_serial_max():
    c=QuantumCircuit(3)
    c.h(0); c.z(0); c.z(0); c.h(1); c.x(2)
    r=analyze(c)
    assert [row['q_live'] for row in r['layers']]==[2,2,2]
    assert r['summary']['ideal_layer_reduction']==pytest.approx(2)
    assert r['summary']['ideal_gate_reduction']==pytest.approx(40/14)

def test_delayed_vs_peak():
    c=QuantumCircuit(2); c.h(0); c.z(0); c.h(1)
    s=analyze(c)['summary']; assert s['full_materialization_reached'] and s['peak_storage_reduction']==1

def test_layer_swap_dependencies():
    c=QuantumCircuit(3); c.h(0); c.swap(0,1); c.h(0); c.z(2)
    r=analyze(c); assert [x['q_live'] for x in r['layers']]==[1,1,2]
