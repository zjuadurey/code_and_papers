"""Deterministic algorithm/control generators, never counted as external circuits."""
import warnings
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import library as lib
from qiskit.circuit.random import random_circuit
from qiskit.synthesis import synth_qft_full


def generate(sizes, seed=20260915):
    for n in sizes:
        yield f'qft_{n}', 'qft', synth_qft_full(n), 'qiskit.synthesis.synth_qft_full', False
        qc = QuantumCircuit(n)
        qc.h(range(n))
        for _ in range(3):
            for i in range(n):
                qc.rzz(0.71, i, (i+1) % n)
            qc.rx(0.37, range(n))
        yield f'qaoa_{n}', 'qaoa', qc, 'QAOA MaxCut ring p=3 gamma=.355 beta=.185', False
        qc = QuantumCircuit(n)
        rng = np.random.default_rng(seed+n)
        for _ in range(4):
            for i in range(n):
                qc.ry(float(rng.uniform(-np.pi, np.pi)), i)
                qc.rz(float(rng.uniform(-np.pi, np.pi)), i)
            for i in range(n-1):
                qc.cx(i, i+1)
        yield f'hea_{n}', 'hea', qc, 'RY/RZ linear-CX hardware-efficient ansatz reps=4', False
        yield f'random_{n}', 'random', random_circuit(n, 12, max_operands=2, seed=seed+n), 'qiskit.circuit.random.random_circuit depth=12 max_operands=2', False
        qc = QuantumCircuit(n)
        qc.h(range(n-1))
        qc.x(n-1)
        qc.h(n-1)
        qc.mcx(list(range(n-1)), n-1)
        qc.h(range(n-1))
        qc.x(range(n-1))
        qc.h(n-2)
        qc.mcx(list(range(n-2)), n-2)
        qc.h(n-2)
        qc.x(range(n-1))
        qc.h(range(n-1))
        # Optional Grover controls stop at 32: QPY's uint32 ctrl_state cannot
        # round-trip a closed MCX with >32 controls in current Qiskit. Required
        # QFT/QAOA/HEA/random controls above still cover every requested size.
        if n <= 32:
            yield f'grover_{n}', 'grover_oracle', qc, 'single marked-state Grover iteration with phase-kickback ancilla', False
    # Size is an operand width, actual total including ancillas is recorded.
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        for width in [3, 5, 7, 9, 11, 13]:
            blocks = [('cdkm', lib.CDKMRippleCarryAdder(width)),
                      ('vbe', lib.VBERippleCarryAdder(width)),
                      ('comparator', lib.IntegerComparator(width, 2**(width-1)+1)),
                      ('draper', lib.DraperQFTAdder(width)),
                      ('modular_adder', QuantumCircuit(2*width))]
            blocks[-1][1].append(lib.ModularAdderGate(width), range(2*width))
            if width <= 9:
                blocks.append(('multiplier', lib.HRSCumulativeMultiplier(width)))
            for kind, block in blocks:
                data_register=next((r for r in block.qregs if r.name in {'a','state'}),None)
                input_ids=([block.find_bit(q).index for q in data_register]
                           if data_register is not None else list(range(width)))
                for prep in ['basis', 'superposed_input']:
                    qc = QuantumCircuit(block.num_qubits)
                    qc.x(input_ids[0])
                    if prep == 'superposed_input':
                        qc.h(input_ids)
                    qc.compose(block, inplace=True)
                    typename='ModularAdderGate' if kind=='modular_adder' else type(block).__name__
                    yield f'{kind}_{width}_{prep}', 'arithmetic', qc, f'qiskit.circuit.library.{typename} width={width} preparation={prep} input_qubits={input_ids}', False
    qc = QuantumCircuit(40)
    for start, end in [(0, 8), (8, 16), (16, 24), (24, 40)]:
        qc.h(range(start, end))
        for _ in range(12):
            for i in range(end-1):
                qc.cx(i, i+1)
    yield 'staged_40', 'synthetic_staged', qc, 'four stages 8/16/24/40 active with CX dwell', True
