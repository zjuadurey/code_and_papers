# QDAO execution model relevant to HTP

Source: https://github.com/Zhaoyilunnn/qdao, current default `main`; exact SHA and clone timestamp are recorded in `results/manifests/external_repositories.csv` and `external/EXTERNAL_SOURCES.md`. Both `v0.1.0` and `origin/stable/0.1` exist. No version switch, install, import of the package, engine run, or source edit is performed.

Frozen source commit for the transcription: `fb360e6670b9818a3d4e106fb21cf605838be0a4`, file `qdao/circuit.py`, class `StaticPartitioner`, method `run` (lines 145–190 in the inspected source). Partition tests verify the method against this locally cloned reference.

- `qdao/engine.py:Engine.__init__` accepts the circuit, reads full `num_qubits`, constructs `SvManager(n,m,t)`, and fixes `num_chunks=1<<(n-m)`. It defaults to `StaticPartitioner`.
- `qdao/manager.py:SvManager.initialize` creates `2^(n-t)` storage units, each a complex128 vector of length `2^t`; only amplitude zero is initialized to one. This is eager full logical and physical state allocation. The resident compute buffer is `2^m` complex128 amplitudes.
- `qdao/circuit.py:StaticPartitioner.run` traverses instructions in their input order. Each partition accumulates the union of operand IDs >=t. It appends an instruction when union size <=m-t, otherwise flushes the current partition and starts one with the new instruction. Local IDs 0..t-1 are reserved in every partition. A source FIXME notes that a single instruction can itself exceed capacity; our oracle rejects this case explicitly.
- `qdao/qiskit/circuit.py:QiskitCircuitWrapper` consumes Qiskit `CircuitInstruction` objects from `circuit.data`; copies `instruction.operation`; maps operands into a size-m circuit; appends `save_state`. It rejects measurement/classical operands. It uses private `q._index` rather than `circuit.find_bit(q).index`. This can alias IDs from different registers. Our oracle explicitly canonicalizes the logical register into a single indexed register before partitioning; it models this corrected input adapter, not execution of a potentially broken multi-register source circuit.
- `Engine.run` partitions, initializes, then `_run` loops all `2^(n-m)` chunks for each partition. Each chunk loads then stores via the manager. The secondary model counts one full-state read and one full-state write per partition. It excludes initial eager initialization (a separate possible benefit), filesystem/serialization costs, and materialization overhead.
- `examples/getting_started.py` and engine tests transpile with an Aer backend before passing circuits to Engine. Engine does not itself offer a semantic analysis pass or automatically lower arbitrary circuits. Gate support depends on the backend, not a hardcoded H/T/CX basis.
- QDAO has no checked-in QASM/QPY corpus at this commit. `constants.py:QCS_URL` and `tests/qdao/engine_test.py` reference `Zhaoyilunnn/qcs` and its `benchmarks/qasm/`. We clone that referenced corpus as a third public repository for source=qdao, recording **its own** SHA. No unknown generator or engine test is executed. `qdao/tools/example_circ.py` only references now-absent paths. QCS is not installed.

## Static traffic oracle choices

`src/htp/qdao_model.py` independently transcribes the above union-and-flush logic. A test extracts only the original StaticPartitioner class AST and compares boundaries through fake wrappers, without importing or executing QDAO infrastructure. Fixed t=2 is the source default; m in {16,18,20,22,24}, only 2<m<n. There is no tuning objective or planner.

For partition j, thin bytes are `16*(2^q_start + 2^q_end)` (one read before, one write after); eager bytes `32*2^n`. Thus growth inside a partition is accounted for at its endpoints. We also publish a conservative end/end convention. Neither convention models a working virtualized executor. Partition boundaries are those of the full logical circuit, with no thin-aware repartitioning.

**This ignores materialization overhead and is NOT measured SSD traffic.**
