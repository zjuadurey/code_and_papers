"""QThin adapter: unchanged upstream partitions, gather/scatter and Aer backend.

New dimensions are embedded only in the resident compute unit, with the first
entangler, before a single expanded-output store. No expanded intermediate file.
"""
from pathlib import Path
import os
import shutil
import time
import numpy as np
from scipy.linalg import null_space
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qdao.engine import Engine
from qdao.manager import SvManager
from qdao.circuit import QdaoCircuit
from htp.product_state_model import ProductStateModel


class Counters:
    def __init__(self):
        self.read_bytes = self.write_bytes = 0
        self.file_read_bytes = self.file_write_bytes = 0
        self.compute_units = self.traversals = 0
        self.events = []
        self.sync_s = 0.
        self.sync_barrier_count = self.fdatasync_calls = 0


class DiskManager(SvManager):
    """Only file naming/accounting differ; upstream load_sv/store_sv are inherited."""
    def __init__(self, n, m, t, directory, counters):
        super().__init__(n, m, t, False, 'disk')
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.counters = counters
        self.dirty = set()

    def path(self, filename):
        return self.directory / Path(filename).name

    def save(self, filename, vector):
        path = self.path(filename)
        np.save(path, vector)
        self.counters.write_bytes += vector.nbytes
        self.counters.file_write_bytes += path.stat().st_size
        self.dirty.add(path)

    def _init_single_su(self, i):
        vector = np.zeros(1 << self._nl, complex)
        if i == 0:
            vector[0] = 1
        self.save(f'sv{i}.npy', vector)

    def _load_single_su(self, isub, fn):
        path = self.path(fn)
        vector = np.load(path, allow_pickle=False)
        self.counters.read_bytes += vector.nbytes
        self.counters.file_read_bytes += path.stat().st_size
        start = isub << self._nl
        self._chunk[start:start + len(vector)] = vector

    def _store_single_su(self, isub, fn):
        start = isub << self._nl
        self.save(fn, self._chunk[start:start + (1 << self._nl)])

    def sync(self):
        start = time.perf_counter()
        self.counters.sync_barrier_count += 1
        for path in self.dirty:
            fd = os.open(path, os.O_RDONLY)
            try:
                os.fdatasync(fd)
                self.counters.fdatasync_calls += 1
            finally:
                os.close(fd)
        self.dirty.clear()
        self.counters.sync_s += time.perf_counter() - start

    def full_small_state(self):
        assert self._nq <= 12, 'Full reconstruction is correctness-only'
        return np.concatenate([np.load(self.path(f'sv{i}.npy')) for i in range(1 << (self._nq-self._nl))])


class CountedEngine(Engine):
    def _run(self, sub):
        self._manager.counters.traversals += 1
        self._manager.counters.compute_units += self._num_chunks
        return super()._run(sub)


def configure(engine):
    engine._sim._sim.set_options(max_parallel_threads=1, max_parallel_experiments=1,
                                max_parallel_shots=1, precision='double')
    if os.environ.get('HTP_QDAO_LEGACY_INITIALIZE') == '1':
        return
    # Shared current-Aer API bridge, including for the QDAO baseline. The old
    # custom Initialize expands 2**m scalar Python instruction parameters per CU.
    # State injection accepts a single array. QDAO chunks need not be normalized:
    # linearity permits normalized simulation followed by restoring the norm.
    from qdao.simulator import QdaoSimObj
    helper = engine._circ_helper
    run = engine._sim.run

    def initialize(vector):
        scale = float(np.linalg.norm(vector))
        normalized = vector/scale if scale else np.zeros_like(vector)
        if not scale:
            normalized[0] = 1
        circuit = QuantumCircuit(helper.circ.num_qubits)
        circuit.set_statevector(normalized)
        circuit.compose(helper.circ, inplace=True)
        obj = QdaoSimObj(vector, circuit)
        obj.qthin_shared_norm = scale
        return obj

    def simulate(obj):
        return run(obj) * obj.qthin_shared_norm

    helper.init_circ_from_sv = initialize
    engine._sim.run = simulate


def embedding(ids, cells):
    """Isometric embedding of addressed backing wires into all gate operands."""
    material = [i for i in ids if cells[i].label == 'M']
    out = np.zeros((1 << len(ids), 1 << len(material)), complex)
    for col in range(out.shape[1]):
        v = np.ones(1, complex)
        for i in ids:
            f = np.eye(2)[:, (col >> material.index(i)) & 1] if i in material else cells[i].vector
            if f is None:
                raise ValueError('Unbound virtual state is not executable')
            v = np.kron(f, v)
        out[:, col] = v
    return out, material


def reduced_gate(op, ids, model):
    """Contract proved virtual output factors; extend the remaining isometry.

    The extension acts on new physical wires initially in |0>. Only its valid
    input subspace is used. This includes phases induced on existing backing.
    """
    if all(model.cells[i].label == 'M' for i in ids):
        event = model.step(op, ids)
        return op, ids, 0., event
    before, old = embedding(ids, model.cells)
    matrix = Operator(op).data
    event = model.step(op, ids)
    after, new = embedding(ids, model.cells)
    reduced = after.conj().T @ matrix @ before
    residual = np.linalg.norm(after @ reduced - matrix @ before)
    if residual > 1e-10:
        raise AssertionError(f'Invalid factorization contraction: {residual}')
    if not new:
        return None, [], float(np.angle(reduced[0, 0])), event
    dimension = 1 << len(new)
    columns = [sum(((j >> old.index(i)) & 1) << new.index(i) for i in old)
               for j in range(1 << len(old))]
    unitary = np.zeros((dimension, dimension), complex)
    unitary[:, columns] = reduced
    remaining = [j for j in range(dimension) if j not in columns]
    if remaining:
        unitary[:, remaining] = null_space(reduced.conj().T)
    if not np.allclose(unitary.conj().T @ unitary, np.eye(dimension), atol=1e-10, rtol=0):
        raise AssertionError('Reduced operation is not an isometry')
    from qiskit.circuit.library import UnitaryGate
    return UnitaryGate(unitary), new, 0., event


class QThinEngine:
    def __init__(self, circuit, m, t, directory, counters, partitioner=None):
        self.n, self.m, self.t = circuit.num_qubits, m, t
        self.root, self.counters = Path(directory), counters
        self.model = ProductStateModel(self.n)
        self.physical = []
        self.manager = DiskManager(0, 0, 0, self.root/'bank0', counters)
        self.engine = CountedEngine(circuit=circuit, num_primary=m, num_local=t,
                                   manager=self.manager, partitioner=partitioner)
        configure(self.engine)
        self.circuit = circuit
        self.phase = float(circuit.global_phase)
        self.gate_index = 0
        self.block_count = 0

    def run(self):
        blocks = self.engine._part.run(self.circuit)
        self.block_count = len(blocks)
        self.manager.initialize()
        for index, block in enumerate(blocks):
            if len(self.physical) == self.n:
                self.engine._manager = self.manager
                self.engine._num_chunks = 1 << (self.n-self.m)
                self.engine._run(block)
                continue
            self.run_block(block, index)
        self.manager.sync()

    def run_block(self, block, index):
        start = time.perf_counter()
        old = self.physical.copy()
        planned = []
        events = []
        for instruction in block.circ.data:
            op = instruction.operation
            if op.name.startswith('save_'):
                continue
            ids = [block.real_qubits[block.circ.find_bit(q).index] for q in instruction.qubits]
            gate, wires, phase, event = reduced_gate(op, ids, self.model)
            self.gate_index += 1
            self.phase += phase
            if gate is not None:
                planned.append((gate, wires))
            if event['qubits']:
                events.append(dict(gate_index=self.gate_index, gate=op.name,
                                   old_q=event['old_q'], new_q=event['new_q'],
                                   batch=len(event['qubits']), trigger=event['trigger_reason']))
        new = [i for i, cell in enumerate(self.model.cells) if cell.label == 'M']
        if not planned:
            assert new == old
            return
        added = len(new)-len(old)
        new_width = min(self.m, len(new))
        old_width = new_width-added
        old_local = sum(i < self.t for i in old)
        new_local = sum(i < self.t for i in new)
        old_real = [old.index(i) for i in block.real_qubits if i in old]
        new_real = [new.index(i) for i in block.real_qubits if i in new]
        assert len(old_real) <= old_width and len(new_real) <= new_width
        source = self.manager
        source._np = old_width
        source._chunk = np.zeros(1 << old_width, complex)
        assert source._nl == old_local
        destination = (DiskManager(len(new), new_width, new_local, self.root/f'bank{index+1}', self.counters)
                       if added else source)
        destination._np = new_width
        # QDAO packs explicit real wires first, then its unused physical wires.
        old_order = [old[i] for i in old_real] + [i for i in old if old.index(i) not in old_real][:old_width-len(old_real)]
        new_order = [new[i] for i in new_real] + [i for i in new if new.index(i) not in new_real][:new_width-len(new_real)]
        assert set(old_order) <= set(new_order)
        resident = QuantumCircuit(new_width)
        for gate, wires in planned:
            resident.append(gate, [new_order.index(i) for i in wires])
        resident.save_state()
        sub = QdaoCircuit(resident, new_real)
        indices = np.arange(1 << old_width, dtype=np.uint64)
        expanded_indices = np.zeros(len(indices), dtype=np.uint64)
        for j, logical in enumerate(old_order):
            expanded_indices |= ((indices >> j) & 1) << new_order.index(logical)
        count = 1 << (len(old)-old_width)
        r0, w0 = self.counters.read_bytes, self.counters.write_bytes
        self.counters.traversals += 1
        for chunk in range(count):
            source.chunk_idx = chunk
            compact = source.load_sv(old_real)
            if added:
                expanded = np.zeros(1 << new_width, complex)
                expanded[expanded_indices] = compact
            else:
                expanded = compact
            self.engine._circ_helper.circ = resident
            simobj = self.engine._circ_helper.init_circ_from_sv(expanded)
            output = self.engine._sim.run(simobj)
            assert len(output) == 1 << new_width
            destination.chunk_idx = chunk
            destination.chunk = output
            destination.store_sv(new_real)
            self.counters.compute_units += 1
        if added:
            # Same completion policy as QDAO: sync the final surviving state.
            # Old temporary-bank write cancellation is reported via /proc/io;
            # it must not be confused with completed device traffic.
            shutil.rmtree(source.directory)
            for event in events:
                event.update(block=index)
            self.counters.events.append(dict(block=index, gate_events=events,
                old_q=len(old), new_q=len(new), batch=added,
                read_bytes=self.counters.read_bytes-r0,
                write_bytes=self.counters.write_bytes-w0,
                elapsed_s=time.perf_counter()-start))
        self.manager, self.physical = destination, new

    def full_small_state(self):
        assert self.n <= 12
        compact = self.manager.full_small_state()
        out = np.zeros(1 << self.n, complex)
        for j in range(len(out)):
            k = sum(((j >> i) & 1) << p for p, i in enumerate(self.physical))
            value = compact[k]
            for i, cell in enumerate(self.model.cells):
                if cell.label != 'M':
                    value *= cell.vector[(j >> i) & 1]
            out[j] = value * np.exp(1j*self.phase)
        return out


def original(circuit, m, t, directory, counters, partitioner=None):
    manager = DiskManager(circuit.num_qubits, m, t, directory, counters)
    engine = CountedEngine(circuit=circuit, num_primary=m, num_local=t,
                           manager=manager, partitioner=partitioner)
    configure(engine)
    engine.run()
    manager.sync()
    return manager
