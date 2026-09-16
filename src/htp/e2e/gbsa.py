"""Paper Algorithms 1/2 reproduction, with explicit interpretation of errata.

Full dependency propagation, maximum predecessor-count selection and fragmented
gate aggregation. See notes/gbsa_reproduction.md; this is not author software.
"""
from dataclasses import dataclass
import time
import numpy as np
from qiskit import QuantumCircuit
from qdao.circuit import QdaoCircuit, StaticPartitioner
from htp.e2e.runtime import DiskManager, CountedEngine, configure


@dataclass
class Block:
    qubits: tuple
    gates: list


def extract_ready(remaining, operands, selected):
    """Take maximal executable gates wholly inside selected; preserve wire order."""
    blocked = set()
    taken, rest = [], []
    for i in remaining:
        qs = operands[i]
        if qs <= selected and not qs & blocked:
            taken.append(i)
        else:
            rest.append(i)
            blocked.update(qs)
    return taken, rest


def dependencies(remaining, operands, n):
    """Transitive wire predecessors, including self, as integer bit sets."""
    wire_dep, wire_req = [0]*n, [0]*n
    rows = []
    for position, i in enumerate(remaining):
        dep, req = 0, 1 << position
        for q in operands[i]:
            dep |= (1 << q) | wire_dep[q]
            req |= wire_req[q]
        for q in operands[i]:
            wire_dep[q], wire_req[q] = dep, req
        rows.append((dep, req.bit_count()))
    return rows


def search_blocks(circuit, capacity):
    """Algorithms 1/2: initial low chunk then global maximum-REQ candidates.

    Algorithm 2's False guard and inner-loop reset would make it empty/infinite.
    Follow section 3.3 prose: scan ALL candidates, then update/remove/repeat.
    Last equal-score candidate wins, matching printed <= tie condition.
    """
    n = circuit.num_qubits
    if not 1 <= capacity <= n:
        raise ValueError('Invalid chunk capacity')
    operands = [set(circuit.find_bit(q).index for q in ins.qubits) for ins in circuit.data]
    if any(len(qs) > capacity for qs in operands):
        raise ValueError('Gate wider than chunk')
    if any(ins.clbits for ins in circuit.data):
        raise ValueError('Unitary circuits only')
    remaining = list(range(len(operands)))
    first, remaining = extract_ready(remaining, operands, set(range(capacity)))
    blocks = [Block(tuple(range(capacity)), first)] if first else []
    while remaining:
        mask, taken = 0, []
        while remaining and mask.bit_count() < capacity:
            best, score = None, -1
            for dep, count in dependencies(remaining, operands, n):
                candidate = dep | mask
                if candidate.bit_count() <= capacity and count >= score:
                    best, score = candidate, count
            if best is None:
                break
            mask = best
            selected = {q for q in range(n) if mask >> q & 1}
            new, remaining = extract_ready(remaining, operands, selected)
            if not new:
                raise AssertionError('GBSA search made no progress')
            taken.extend(new)
        if not taken:
            raise AssertionError('Empty GBSA block')
        blocks.append(Block(tuple(q for q in range(n) if mask >> q & 1), taken))
    assert sorted(i for b in blocks for i in b.gates) == list(range(len(operands)))
    return blocks


class GBSAReproduction:
    """Published selector + virtual swaps on the common QDAO/Aer file substrate.

    Selected chunk bits are unrestricted: unlike QDAO they need NOT contain
    fixed low t wires. Physical SWAP passes and logical remapping implement the
    paper's addSwaps; their full I/O and CPU cost are included. No virtual P/K.
    """
    def __init__(self, circuit, m, t, directory, counters):
        self.circuit, self.n, self.m, self.t = circuit, circuit.num_qubits, m, t
        self.counters = counters
        self.manager = DiskManager(self.n, m, t, directory, counters)
        self.engine = CountedEngine(circuit=circuit, num_primary=m, num_local=t,
                                    manager=self.manager)
        configure(self.engine)
        self.logical_to_physical = list(range(self.n))
        self.swap_count = self.swap_passes = self.gate_blocks = 0
        self.search_s = self.swap_s = 0.

    def run(self):
        start = time.perf_counter()
        blocks = search_blocks(self.circuit, self.m)
        self.search_s = time.perf_counter()-start
        self.manager.initialize()
        self.gate_blocks = len(blocks)
        for block in blocks:
            selected = set(block.qubits)
            # Retain already-resident selected wires, move only required outsiders.
            outside = sorted(q for q in selected if self.logical_to_physical[q] >= self.m)
            vacant = sorted(self.logical_to_physical[q] for q in range(self.n)
                            if q not in selected and self.logical_to_physical[q] < self.m)
            swaps = QuantumCircuit(self.n)
            for logical, destination in zip(outside, vacant):
                source = self.logical_to_physical[logical]
                displaced = self.logical_to_physical.index(destination)
                swaps.swap(source, destination)
                self.logical_to_physical[logical] = destination
                self.logical_to_physical[displaced] = source
                self.swap_count += 1
            if len(swaps):
                start = time.perf_counter()
                swap_blocks = StaticPartitioner(np=self.m, nl=self.t).run(swaps)
                for sub in swap_blocks:
                    self.engine._run(sub)
                self.swap_passes += len(swap_blocks)
                self.swap_s += time.perf_counter()-start
            resident = QuantumCircuit(self.m)
            for i in block.gates:
                ins = self.circuit.data[i]
                ids = [self.logical_to_physical[self.circuit.find_bit(q).index] for q in ins.qubits]
                assert all(q < self.m for q in ids)
                resident.append(ins.operation, ids)
            resident.save_state()
            self.engine._run(QdaoCircuit(resident, list(range(self.m))))
        self.manager.sync()

    def full_small_state(self):
        assert self.n <= 12
        raw = self.manager.full_small_state()
        indices = np.arange(1 << self.n, dtype=np.int64)
        physical = np.zeros_like(indices)
        for logical, position in enumerate(self.logical_to_physical):
            physical |= ((indices >> logical) & 1) << position
        return raw[physical]*np.exp(1j*float(self.circuit.global_phase))
