import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import library as lib
from qiskit.quantum_info import Statevector, random_unitary
from .abstract_state import initial, Q
from .analyzer import scheduled_operations
from .gate_semantics import transfer


def validate_prefixes(circuit, tolerance=1e-10):
    n = circuit.num_qubits
    if n > 8:
        raise ValueError('Exact validation hard limit is n<=8')
    sv, labels = Statevector.from_int(0, 2**n), initial(n)
    claims, maximum = 0, 0.0
    for k, (op, ids, _) in enumerate(scheduled_operations(circuit), 1):
        sv = sv.evolve(op, qargs=ids)
        transfer(labels, op, ids)
        for i, value in enumerate(labels):
            if value == Q:
                continue
            # Little endian qubits: axis n-1-i is qubit i.
            matrix = np.moveaxis(sv.data.reshape([2]*n), n-1-i, 0).reshape(2, -1)
            rho = matrix @ matrix.conj().T
            expected = np.zeros((2, 2), complex)
            expected[int(value), int(value)] = 1
            error = float(np.max(np.abs(rho-expected)))
            maximum = max(maximum, error)
            claims += 1
            if error > tolerance:
                raise AssertionError(f'FALSE-KNOWN n={n} prefix={k} gate={op.name} qubit={i} label={value} rho={rho} error={error}')
    return dict(prefixes=len(scheduled_operations(circuit)), known_claims=claims, max_density_error=maximum,
                false_known_violations=0)


def random_validation_circuit(seed):
    rng = np.random.default_rng(seed)
    n = int(rng.integers(1, 9))
    qc = QuantumCircuit(n)
    angles = [0., np.pi, -np.pi, 2*np.pi, np.pi/2, -0.43]
    # Basis-heavy prefixes and late mixing explicitly exercise K1 and short circuits.
    for step in range(60):
        p = int(rng.integers(0, 18))
        i = int(rng.integers(n))
        theta = float(rng.choice(angles))
        if p < 6:
            [qc.x, qc.y, qc.z, qc.s, qc.t, qc.rz][p](theta, i) if p == 5 else [qc.x, qc.y, qc.z, qc.s, qc.t][p](i)
        elif p < 9:
            if step < 15:
                qc.rx(float(rng.choice([0., np.pi])), i)
            elif p == 6:
                qc.h(i)
            else:
                (qc.rx if p == 7 else qc.ry)(theta, i)
        elif n >= 2 and p < 15:
            a, b = list(map(int, rng.choice(n, 2, replace=False)))
            if p < 11:
                qc.cx(a, b)
            elif p == 11:
                qc.cz(a, b)
            elif p == 12:
                qc.swap(a, b)
            elif p == 13:
                qc.cp(theta, a, b)
            else:
                qc.rzz(theta, a, b)
        elif n >= 3 and p < 17:
            count = min(n-1, int(rng.integers(2, 5)))
            ids = list(map(int, rng.choice(n, count+1, replace=False)))
            qc.append(lib.MCXGate(count, ctrl_state=int(rng.integers(2**count))), ids)
        elif step >= 35:
            qc.append(lib.UnitaryGate(random_unitary(2, seed=seed+step)), [i])
        else:
            qc.x(i)
    return qc
