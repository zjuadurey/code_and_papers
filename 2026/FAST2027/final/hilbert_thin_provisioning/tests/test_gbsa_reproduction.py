"""Published example, ordering, unrestricted chunks and file-backed evolution."""
import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'build/qdao-qthin-src'))
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from htp.e2e.gbsa import search_blocks, GBSAReproduction
from htp.e2e.runtime import Counters


def test_paper_figure4():
    c = QuantumCircuit(5)
    c.h(4); c.h(1); c.h(0); c.cz(3,2); c.cz(3,1); c.cz(2,1)
    c.h(3); c.cz(4,2); c.h(4); c.h(0)
    blocks = search_blocks(c,3)
    assert [b.gates for b in blocks] == [[1,2,9],[3,4,5,6],[0,7,8]]
    assert set(blocks[1].qubits) == {1,2,3}


@pytest.mark.parametrize('seed',range(12))
def test_wire_order_and_exact_file_execution(tmp_path,seed):
    rng=np.random.default_rng(seed); c=QuantumCircuit(7)
    c.global_phase=.123
    for _ in range(50):
        if rng.random()<.55:c.u(*rng.normal(size=3),int(rng.integers(7)))
        else:c.cx(*rng.choice(7,2,replace=False))
    blocks=search_blocks(c,4)
    order=[i for b in blocks for i in b.gates]
    for q in c.qubits:
        expected=[i for i,ins in enumerate(c.data) if q in ins.qubits]
        assert [i for i in order if q in c.data[i].qubits]==expected
    counters=Counters();run=GBSAReproduction(c,4,2,tmp_path,counters);run.run()
    assert np.max(np.abs(run.full_small_state()-Statevector(c).data))<1e-12
    assert counters.traversals==len(blocks)+run.swap_passes
    assert counters.read_bytes==16*(1<<7)*counters.traversals
    assert counters.write_bytes==16*(1<<7)*(counters.traversals+1)
    assert counters.sync_barrier_count==1


def test_empty_and_invalid():
    assert search_blocks(QuantumCircuit(4),3)==[]
    c=QuantumCircuit(2);c.cx(0,1)
    with pytest.raises(ValueError):search_blocks(c,1)
