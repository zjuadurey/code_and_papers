import pytest
from htp.workload_discovery import infer_family

@pytest.mark.parametrize('path,family',[
    ('benchmarks/qasm/head_1000_circuit_n28_m14_s7.qasm','unknown'),
    ('generated/hea_28.qpy','hea'),
    ('variational/EfficientSU2/circuit.qasm','hea'),
    ('combinational/rev_circuit/2of5.qasm','reversible'),
    ('small/mystery_n8/thing.qasm','unknown'),
    ('medium/bigadder_n18/bigadder_n18.qasm','arithmetic')])
def test_family_requires_evidence(path,family):
    assert infer_family(path)==family
