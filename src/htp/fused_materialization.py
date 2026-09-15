"""Small correctness kernels; only the explicit microbenchmark uses larger q."""
import numpy as np
from qiskit.quantum_info import Statevector, Operator


def eager_expand_then_gate(backing, factors, unitary, gate_qubits):
    n = int(np.log2(len(backing)))+len(factors)
    if n > 12:
        raise ValueError('Correctness reference limit is 12 qubits')
    state = np.asarray(backing, complex)
    for factor in factors:
        state = np.kron(factor, state)
    return Statevector(state).evolve(Operator(unitary), qargs=gate_qubits).data


def fused_materialize_and_gate(backing, factors, unitary, gate_qubits):
    """Contract compact amplitudes and factors directly into post-gate output."""
    q = int(np.log2(len(backing)))
    n = q+len(factors)
    if n > 12 or len(backing) != 1 << q:
        raise ValueError('Correctness fused kernel limit is 12 qubits')
    output = np.zeros(1 << n, dtype=complex)
    indices = np.arange(len(output), dtype=np.int64)
    out_bits = sum(((indices >> bit) & 1) << j for j, bit in enumerate(gate_qubits))
    mask = sum(1 << bit for bit in gate_qubits)
    for incoming in range(1 << len(gate_qubits)):
        source = indices & ~mask
        for j, bit in enumerate(gate_qubits):
            source |= ((incoming >> j) & 1) << bit
        contribution = np.asarray(backing)[source & ((1 << q)-1)].copy()
        for j, factor in enumerate(factors):
            contribution *= np.asarray(factor)[(source >> (q+j)) & 1]
        output += unitary[out_bits, incoming]*contribution
    return output


def fused_cx_product_control(backing, factor, target=0):
    """Microbenchmark kernel: write each output amplitude once; no expanded input."""
    output = np.empty((2, len(backing)), dtype=backing.dtype)
    np.multiply(backing, factor[0], out=output[0])
    inp = backing.reshape(-1, 2, 1 << target)
    out = output[1].reshape(-1, 2, 1 << target)
    np.multiply(inp[:, 1, :], factor[1], out=out[:, 0, :])
    np.multiply(inp[:, 0, :], factor[1], out=out[:, 1, :])
    return output.reshape(-1)


def naive_cx_product_control(backing, factor, target=0):
    expanded = np.empty((2, len(backing)), dtype=backing.dtype)
    np.multiply(backing, factor[0], out=expanded[0])
    np.multiply(backing, factor[1], out=expanded[1])
    output = expanded.copy()
    old = expanded[1].reshape(-1, 2, 1 << target)
    new = output[1].reshape(-1, 2, 1 << target)
    new[:, 0, :] = old[:, 1, :]
    new[:, 1, :] = old[:, 0, :]
    return output.reshape(-1)
