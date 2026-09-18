"""Requested size variants of the existing generators; common inputs for all methods."""
import warnings
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import CDKMRippleCarryAdder, IntegerComparator
from qiskit_aer import AerSimulator
from htp.workload_generators import generate


def suite(n):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        width = (n-2)//2
        block = CDKMRippleCarryAdder(width)
        assert block.num_qubits == n
        data = [block.find_bit(q).index for q in block.qregs if q.name == 'a' for q in q]
        for prep in ['basis', 'superposed']:
            c = QuantumCircuit(n)
            c.x(data[0])
            if prep == 'superposed':
                c.h(data)
            c.compose(block, inplace=True)
            yield f'cdkm_{prep}', c, f'existing CDKMRippleCarryAdder; width={width}; prep={prep}'
        width = n//2
        block = IntegerComparator(width, 2**(width-1)+1)
        c = QuantumCircuit(n)
        c.x(0); c.h(range(width)); c.compose(block, inplace=True)
        yield 'comparator', c, f'existing IntegerComparator width={width}; superposed input'
    for _, family, c, description, _ in generate([n]):
        if family in {'qft', 'qaoa', 'hea', 'grover_oracle'}:
            yield family, c, 'existing workload_generators.generate: '+description
        if family == 'grover_oracle':
            oracle = QuantumCircuit(n)
            # Exact oracle prefix of the existing Grover generator, without diffusion.
            oracle.h(range(n-1)); oracle.x(n-1); oracle.h(n-1)
            oracle.mcx(list(range(n-1)), n-1)
            yield 'mcx_oracle', oracle, 'existing Grover generator oracle prefix; no diffusion'
            break


def lower(circuit):
    supported = set(AerSimulator().operation_names)
    assert {'u', 'cx'} <= supported
    result = transpile(circuit, basis_gates=['u','cx'], optimization_level=0, seed_transpiler=20260916)
    # Single register avoids upstream QDAO's private register-local _index issue.
    canonical = QuantumCircuit(circuit.num_qubits)
    canonical.global_phase = result.global_phase
    for inst in result.data:
        canonical.append(inst.operation, [result.find_bit(q).index for q in inst.qubits])
    return canonical
