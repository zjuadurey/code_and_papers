import hashlib
import re
from pathlib import Path
from qiskit import QuantumCircuit, qasm2, qasm3, qpy, transpile
from qiskit.circuit import ControlFlowOp, Gate
from qiskit.circuit.library import C3SXGate, MCXGate
from qiskit_aer import AerSimulator
from qiskit.transpiler import Target
from .gate_semantics import has_rule, trusted

EXTENSIONS = {'.qasm', '.qasm2', '.qasm3', '.qpy'}


class UnsupportedDynamic(ValueError):
    pass


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def load_circuits(path):
    path = Path(path)
    if path.suffix.lower() == '.qpy':
        with path.open('rb') as f:
            return list(qpy.load(f))
    with path.open(errors='replace') as f:
        header = f.read(4096)
    if path.suffix.lower() == '.qasm3' or re.search(r'OPENQASM\s+3', header):
        return [qasm3.load(str(path))]
    # Default parser honors user definitions; legacy compatibility only if undefined.
    try:
        return [qasm2.load(str(path))]
    except qasm2.QASM2ParseError as e:
        if 'not defined' not in str(e) and 'not a valid parameter' not in str(e):
            raise
        # Only supplement missing builtins; don't override source gate definitions.
        content = path.read_text(errors='replace')
        defined = set(re.findall(r'\b(?:gate|opaque)\s+(\w+)', content))
        legacy = [x for x in qasm2.LEGACY_CUSTOM_INSTRUCTIONS if x.name not in defined]
        if 'c3sx' not in defined:
            legacy.append(qasm2.CustomInstruction('c3sx',0,4,C3SXGate,builtin=True))
        # Old Aer exporters emitted mcx_gray without a declaration. Fixed arity
        # is inferred only if every invocation agrees; never replace a definition.
        if 'mcx_gray' not in defined:
            calls=re.findall(r'\bmcx_gray\s+([^;{}]+);',content)
            arities={len(call.split(',')) for call in calls}
            if len(arities)==1:
                arity=arities.pop()
                legacy.append(qasm2.CustomInstruction('mcx_gray',0,arity,lambda: MCXGate(arity-1),builtin=True))
        return [qasm2.load(str(path), custom_instructions=tuple(legacy))]


def unitary_prefix(circuit):
    """Strip terminal readout only; reject dynamics anywhere else."""
    end = len(circuit.data)
    while end and circuit.data[end - 1].operation.name in {'measure', 'barrier'}:
        end -= 1
    out = QuantumCircuit(circuit.num_qubits, name=circuit.name)
    out.global_phase = circuit.global_phase
    for inst in circuit.data[:end]:
        op = inst.operation
        if inst.clbits or isinstance(op, ControlFlowOp) or op.name in {'measure', 'reset', 'store'} or getattr(op, 'condition', None) is not None:
            raise UnsupportedDynamic(f'Nonunitary/dynamic operation: {op.name}')
        out.append(op, [circuit.find_bit(q).index for q in inst.qubits])
    return out, len(circuit.data) - end


def semantic_circuit(circuit, limit=100000):
    """Expand transparent definitions, retaining trusted semantic primitives."""
    out = QuantumCircuit(circuit.num_qubits, name=circuit.name)
    out.global_phase = circuit.global_phase

    def append(op, ids, level=0):
        if len(out.data) >= limit:
            raise ValueError('ExpandedGateLimit')
        if isinstance(op, ControlFlowOp) or op.num_clbits or op.name in {'measure', 'reset'}:
            raise UnsupportedDynamic(f'Nested dynamic operation: {op.name}')
        if level > 40:
            raise ValueError('DefinitionRecursionLimit')
        if (has_rule(op) or trusted(op) or op.name in {'barrier', 'delay', 'initialize', 'state_preparation'}):
            out.append(op, ids)
        elif isinstance(op, Gate) and op.definition is not None:
            definition = op.definition
            out.global_phase += definition.global_phase
            for inst in definition.data:
                append(inst.operation, [ids[definition.find_bit(q).index] for q in inst.qubits], level + 1)
        else:
            out.append(op, ids)

    for inst in circuit.data:
        append(inst.operation, [circuit.find_bit(q).index for q in inst.qubits])
    return out


def backend():
    return AerSimulator(method='statevector', device='CPU', max_parallel_threads=1)


def lower(circuit):
    # Aer advertises a RAM-derived width limit, irrelevant to static transpilation.
    # Copy its actual supported operations into an unbounded *compiler* target;
    # the real Aer backend used for <=8-qubit validation keeps its memory limit.
    original=backend().target
    target=Target(description='Aer operations, unbounded static analysis width',num_qubits=None)
    for name in original.operation_names:
        target.add_instruction(original.operation_from_name(name),name=name)
    return transpile(circuit, target=target, optimization_level=0, seed_transpiler=20260915)
