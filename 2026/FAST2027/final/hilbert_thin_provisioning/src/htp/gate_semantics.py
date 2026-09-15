"""Sound overapproximation, subject to documented numerical tolerances."""
import math
import numpy as np
from qiskit.circuit import Gate, ControlledGate
from qiskit.quantum_info import Operator
from qiskit.exceptions import QiskitError
from .abstract_state import K0, K1, Q

DIAGONAL = {'id', 'z', 's', 'sdg', 't', 'tdg', 'p', 'rz', 'u1',
            'cz', 'cp', 'crz', 'rzz', 'ccz', 'mcp', 'mcphase', 'cu1'}
NAMED = DIAGONAL | {'x', 'y', 'h', 'sx', 'sxdg', 'rx', 'ry', 'cx', 'ccx',
                    'mcx', 'mcx_gray', 'swap'}


def trusted(op):
    return op.base_class.__module__.startswith('qiskit.circuit.library.standard_gates')


def has_rule(op):
    if trusted(op) and op.name in NAMED:
        return True
    return (isinstance(op, ControlledGate) and trusted(op.base_gate)
            and op.num_qubits == op.num_ctrl_qubits + 1
            and op.base_gate.num_qubits == 1
            and op.base_gate.name in {'x', 'z', 'p', 'rz'})


def flip(value):
    return Q if value == Q else (K1 if value == K0 else K0)


def reserve_numerical_error(state,error):
    # Unitary error adds in operator norm; marginal density-entry error <=2e.
    # Once exhausted, use Q instead of accumulating almost-special rotations.
    if error == 0:
        return True
    if not hasattr(state,'numerical_error'):
        return False  # Plain lists have no history; only exact proofs allowed.
    if state.numerical_error + error <= 5e-11:
        state.numerical_error += error
        return True
    return False


def transfer(state, op, qubits, angle_tol=1e-10):
    """Modify labels; return (reason, unrecognized). Never invoke large Operator."""
    name = op.name
    if name in {'barrier', 'delay'} and op.base_class.__module__.startswith('qiskit.circuit'):
        return 'directive', False
    if name in {'initialize', 'state_preparation'}:
        for i in qubits:
            state[i] = Q
        return 'conservative_state_preparation', False
    if trusted(op) and name == 'swap':
        a, b = qubits
        state[a], state[b] = state[b], state[a]
        return 'swap_label_transport', False
    if has_rule(op):
        if isinstance(op, ControlledGate):
            base = op.base_gate.name
            if base in {'z', 'p', 'rz'}:
                return 'computational_basis_diagonal', False
            if base == 'x':
                controls, target = qubits[:op.num_ctrl_qubits], qubits[-1]
                required = [(op.ctrl_state >> j) & 1 for j in range(len(controls))]
                if any(state[c] != Q and int(state[c]) != bit for c, bit in zip(controls, required)):
                    return 'known_control_short_circuit', False
                if all(state[c] != Q for c in controls):
                    state[target] = flip(state[target])
                    return 'known_controls_apply_x', False
                if len(controls) == 1:
                    state[target] = Q
                else:
                    for i in qubits:
                        state[i] = Q
                return 'unknown_control_entanglement', False
        if name in DIAGONAL:
            return 'computational_basis_diagonal', False
        if name in {'x', 'y'}:
            state[qubits[0]] = flip(state[qubits[0]])
            return 'basis_bit_flip', False
        if name in {'rx', 'ry'}:
            try:
                theta = float(op.params[0])
                reduced = math.remainder(theta, 2 * math.pi)
                roundoff=np.finfo(float).eps*abs(theta)
                if abs(reduced) <= angle_tol and reserve_numerical_error(state,(abs(reduced)+roundoff)/2):
                    return 'rotation_identity_angle', False
                residual=abs(abs(reduced)-math.pi)
                if residual <= angle_tol and reserve_numerical_error(state,(residual+roundoff)/2):
                    state[qubits[0]] = flip(state[qubits[0]])
                    return 'rotation_pi_angle', False
            except (TypeError, ValueError, OverflowError):
                pass
        for i in qubits:
            state[i] = Q
        return 'superposition_gate', False
    # Numerical structural proof, bounded independently of circuit size.
    if isinstance(op, Gate) and len(qubits) <= 3 and not op.is_parameterized():
        try:
            mat = np.asarray(Operator(op).data)
            mask = np.abs(mat) > 1e-14
            if np.allclose(mat.conj().T @ mat, np.eye(len(mat)), atol=1e-12, rtol=0):
                if not np.any(mask & ~np.eye(len(mat), dtype=bool)):
                    ideal=np.diag(np.exp(1j*np.angle(np.diag(mat))))
                    error=float(np.linalg.norm(mat-ideal,ord=2))
                    if reserve_numerical_error(state,error):
                        return 'matrix_proven_diagonal', False
                if all(state[i] != Q for i in qubits) and np.all(mask.sum(0) == 1) and np.all(mask.sum(1) == 1):
                    ideal=np.zeros_like(mat)
                    positions=np.argmax(np.abs(mat),axis=0)
                    ideal[positions,np.arange(len(mat))]=np.exp(1j*np.angle(mat[positions,np.arange(len(mat))]))
                    error=float(np.linalg.norm(mat-ideal,ord=2))
                    if not reserve_numerical_error(state,error):
                        for i in qubits: state[i]=Q
                        return 'numerical_proof_budget_exhausted',False
                    col = sum(int(state[i]) << j for j, i in enumerate(qubits))
                    row = int(np.argmax(np.abs(mat[:, col])))
                    for j, i in enumerate(qubits):
                        state[i] = K1 if ((row >> j) & 1) else K0
                    return 'matrix_proven_basis_permutation', False
        except (TypeError, ValueError, NotImplementedError, QiskitError):
            pass
    for i in qubits:
        state[i] = Q
    # Standard mixing gates have understood conservative semantics.
    understood = trusted(op) and name in {'u', 'u2', 'u3', 'r', 'rxx', 'ryy', 'rzx', 'ecr',
                                         'cy', 'crx', 'cry', 'cu', 'cu3', 'csx', 'cswap', 'rccx', 'rc3x'}
    return ('known_gate_conservative' if understood else 'unknown_gate_fallback'), not understood
