"""Single-qubit product factors with bounded local isometry proofs."""
from dataclasses import dataclass
import numpy as np
from qiskit.circuit import Gate, ControlledGate
from qiskit.quantum_info import Operator
from qiskit.exceptions import QiskitError
from .abstract_state import initial, Q
from .gate_semantics import transfer, trusted


@dataclass
class Cell:
    label: str = 'K0'
    vector: object = None
    physical_slot: object = None


class ProductStateModel:
    def __init__(self, n, tolerance=1e-10, numerical_budget=1e-12):
        self.n = n
        self.cells = [Cell('K0', np.array([1., 0.], complex)) for _ in range(n)]
        self.basis = initial(n)
        self.tolerance = tolerance
        self.budget = numerical_budget
        self.error = 0.
        self.next_slot = 0

    @property
    def q_physical(self):
        return sum(c.label == 'M' for c in self.cells)

    @property
    def q_logical(self):
        return self.basis.count(Q)

    def reserve(self, error):
        if self.error + error > self.budget:
            return False
        self.error += error
        return True

    def set_vector(self, i, vector):
        vector = np.asarray(vector, complex)
        vector = vector / np.linalg.norm(vector)
        label = 'P'
        bit = int(np.argmax(np.abs(vector)))
        residual = float(abs(vector[1-bit]))
        if residual <= self.tolerance and self.reserve(residual):
            phase = vector[bit] / abs(vector[bit])
            vector = np.zeros(2, complex)
            vector[bit] = phase
            label = f'K{bit}'
        self.cells[i] = Cell(label, vector)

    def local(self, op, i):
        cell = self.cells[i]
        if cell.label == 'M':
            return
        if cell.vector is None or op.is_parameterized():
            self.cells[i] = Cell('P', None)
            return
        try:
            self.set_vector(i, Operator(op).data @ cell.vector)
        except (QiskitError, TypeError, ValueError):
            self.cells[i] = Cell('P', None)

    def physicalize(self, ids):
        added = []
        for i in ids:
            if self.cells[i].label != 'M':
                self.cells[i] = Cell('M', None, self.next_slot)
                self.next_slot += 1
                added.append(i)
        return added

    def local_isometry(self, op, ids):
        """Prove each virtual output factor for all states of addressed M wires."""
        if len(ids) > 3 or op.is_parameterized():
            return None
        try:
            matrix = Operator(op).data
        except (QiskitError, TypeError, ValueError):
            return None
        if not np.allclose(matrix.conj().T @ matrix, np.eye(len(matrix)), atol=1e-12, rtol=0):
            return None
        materialized = [j for j, i in enumerate(ids) if self.cells[i].label == 'M']
        virtual = [j for j in range(len(ids)) if j not in materialized]
        if any(self.cells[ids[j]].vector is None for j in virtual):
            return None
        columns = []
        for basis_index in range(1 << len(materialized)):
            factors = []
            for j, i in enumerate(ids):
                if j in materialized:
                    bit = (basis_index >> materialized.index(j)) & 1
                    factors.append(np.eye(2, dtype=complex)[:, bit])
                else:
                    factors.append(self.cells[i].vector)
            state = np.array([1.], complex)
            for factor in factors:
                state = np.kron(factor, state)
            columns.append(matrix @ state)
        output = np.stack(columns, axis=1)
        proofs = {}
        for j in virtual:
            tensor = output.reshape([2]*len(ids)+[len(columns)])
            flatten = np.moveaxis(tensor, len(ids)-1-j, 0).reshape(2, -1)
            u, singular, _ = np.linalg.svd(flatten, full_matrices=False)
            # Frobenius residual bounds operator error for arbitrary backing input.
            residual = float(np.linalg.norm(singular[1:]))
            if residual <= self.tolerance and self.reserve(residual):
                proofs[ids[j]] = u[:, 0]
        return proofs

    def _controlled_shortcut(self, op, ids):
        if not (isinstance(op, ControlledGate) and
                op.num_qubits == op.num_ctrl_qubits+1 and
                op.base_gate.num_qubits == 1):
            return False
        controls, target = ids[:-1], ids[-1]
        required = [(op.ctrl_state >> j) & 1 for j in range(len(controls))]
        if any(self.cells[i].label == f'K{1-bit}' for i, bit in zip(controls, required)):
            return True
        if all(self.cells[i].label == f'K{bit}' for i, bit in zip(controls, required)):
            self.local(op.base_gate, target)
            return True
        # Exact +1 target eigenvector makes controlled-U identity, even with many controls.
        cell = self.cells[target]
        if cell.label != 'M' and cell.vector is not None and not op.base_gate.is_parameterized():
            try:
                error = float(np.linalg.norm(Operator(op.base_gate).data @ cell.vector-cell.vector))
                if error <= self.tolerance and self.reserve(error):
                    return True
            except (QiskitError, TypeError, ValueError):
                pass
        return False

    def step(self, op, ids):
        before = self.q_physical
        old_labels = [c.label for c in self.cells]
        old_vectors = {i: (None if self.cells[i].vector is None else self.cells[i].vector.copy()) for i in ids}
        transfer(self.basis, op, ids)
        added = []
        if trusted(op) and op.name == 'swap':
            a, b = ids
            self.cells[a], self.cells[b] = self.cells[b], self.cells[a]
            reason = 'swap_mapping'
        elif len(ids) == 1 and isinstance(op, Gate):
            self.local(op, ids[0])
            reason = 'local_unitary_metadata'
        elif self._controlled_shortcut(op, ids):
            reason = 'known_control_or_identity_eigenvector'
        elif all(self.cells[i].label == 'M' for i in ids):
            reason = 'backing_gate'
        else:
            proofs = self.local_isometry(op, ids)
            if proofs is not None:
                for i, vector in proofs.items():
                    self.set_vector(i, vector)
            unresolved = [i for i in ids if self.cells[i].label != 'M' and (proofs is None or i not in proofs)]
            # A prior-stage basis proof is also a safe factorization proof; retain
            # those operands even when a large gate's local isometry is unavailable.
            to_materialize = []
            for i in unresolved:
                if self.basis[i] != Q:
                    self.cells[i] = Cell(f'K{int(self.basis[i])}', np.eye(2, dtype=complex)[:, int(self.basis[i])])
                else:
                    to_materialize.append(i)
            added = self.physicalize(to_materialize)
            if op.name == 'cx':
                reason = 'cx_materialized_control' if old_labels[ids[0]] == 'M' else 'cx_product_control'
            elif op.name in {'cz', 'cp', 'crz', 'rzz'}:
                reason = 'cz_product_pair' if all(old_labels[i] != 'M' for i in ids) else 'controlled_diagonal_backing'
            elif isinstance(op, ControlledGate):
                reason = 'controlled_rotation' if len(ids) == 2 else 'multi_qubit_gate'
            else:
                reason = 'generic_entangler' if len(ids) <= 2 else 'multi_qubit_gate'
            if not added:
                reason = 'local_isometry_product_proof'
        after = self.q_physical
        assert after >= before
        assert after <= self.q_logical <= self.n, (op.name, before, after, self.q_logical)
        assert len(added) == after-before
        if len(ids) == 1 and isinstance(op, Gate):
            assert after == before
        return dict(old_q=before, new_q=after, materialization_batch_size=len(added),
                    qubits=added, trigger_reason=reason, before_vectors=old_vectors)
