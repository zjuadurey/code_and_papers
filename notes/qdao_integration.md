# File-backed QDAO integration boundary

Upstream reference: `Zhaoyilunnn/qdao`, commit
`fb360e6670b9818a3d4e106fb21cf605838be0a4`. The read-only reference
checkout remains untouched. `scripts/setup_qdao_integration.py` creates a detached
worktree and applies `patches/qdao_current_qiskit.patch`: optional Quafu imports
and the public QuantumRegister import. No simulator or partition algorithm patch.

## Common execution configuration

- Current htp-static Python/Qiskit/Aer; CPU, double precision, one thread,
  Aer fusion disabled (upstream default).
- Fixed QDAO primary width m=16 and storage-unit width t=12. This means a
  1 MiB compute unit and 64 KiB amplitude storage unit, before NPY headers.
  t=12 was selected before measurements to avoid millions of tiny files under
  upstream t=2 at 24q. It is identical for every workload and system; no search.
- The exact canonical QPY input is shared. Lowering is u/cx, optimization 0,
  with basis support checked against installed Aer. Original QDAO cannot place
  an arbitrary 20-control gate into m=16. A single register also avoids its
  register-local `_index` assumption. No final measurements.
- Eight families/variants from existing generators: basis and superposed CDKM,
  superposed comparator, existing Grover oracle prefix, complete one-iteration
  Grover, QFT, QAOA ring p=3 and four-layer HEA. Requested size variants are not
  an expanded public corpus. Basis-input CDKM is reported separately from
  superposed-input CDKM. No system-specific input substitutions.

## Original QDAO baseline

Actual upstream `Engine.run`, `StaticPartitioner`, `SvManager.load_sv/store_sv`,
Aer execution are used. A manager subclass
only redirects filenames to a per-run directory and counts payload/file bytes.
The counted engine adds traversal/compute-unit counters. Input gates, including
large decomposed MCX sequences, are not simplified by the adapter.

### Shared Aer state-injection compatibility adapter

The initial original-API pilot exposed approximately 50–60 ms per compute unit
under current Qiskit, dominated by the old custom Initialize interface's 2^m
scalar Python parameters. Its measured samples are retained under
`results/qdao_end_to_end/legacy_api_calibration/`; no sample was deleted based on
its performance. Projecting the fixed partition/compute-unit counts made the
full requested matrix exceed the approximate deadline.

The main experiment therefore uses the same current Aer `set_statevector` bridge
for **all** systems. It normalizes a chunk, runs the unchanged gate stream, and
restores its norm, exploiting linearity. A zero chunk is simulated from |0> and
multiplied by zero. This uses the supported public normalized-state interface,
not an unchecked private mutation. Initialization, normalization and rescaling
are inside the timed interval. The upstream Engine, partitioner, compute-unit
schedule and gather/scatter remain unchanged. This is an explicitly adapted
QDAO baseline, not a claim of executing completely unmodified author software.
`HTP_QDAO_LEGACY_INITIALIZE=1` reproduces the original initialization path. Full
three-way correctness is rerun for the shared adapter before primary timings.

## QThin adapter

The original partition list is preserved. Before each partition is executed,
the validated product-state model propagates K0/K1/P/M. A local isometry maps
addressed old backing wires plus known product factors through each gate.
Proved virtual output factors are contracted out; the remaining isometry is
extended to a small unitary on old/new materialized operands. Newly physical
wires start in zero within the resident compute unit, and this unitary applies
their product-state preparation and first entangler together. Thus a source
backing traversal produces the post-gate expanded backing directly, without an
expanded intermediate file. This adapter uses the existing Aer compute kernel;
it does not substitute the previous standalone native microbenchmark kernel.

For a partition that adds k dimensions: compact input is read once, output
at the partition's final width is written once. Multiple activation gates in a
partition share this traversal. Event bytes/time therefore describe the entire
fused partition, not an independently timed gate. They are already included in
total traffic and must not be added to it again.

Expansion temporarily retains both old and new banks. The reported q_peak is
the dimension count of the represented state, not a claim about maximum total
filesystem occupancy during that transition. No crash-atomic transition or peak
disk-capacity reduction is claimed by this adapter.

Physical dimensions are ordered by logical index. A necessary expansion pass
also emits the new mapping. The fixed logical local set remains 0..11;
physically absent wires do not occupy its backing-unit address bits. Therefore
physical t is the number of materialized wires in that fixed logical set, and
physical m is bounded by 16. This is representation compaction, not parameter
tuning or repartitioning. Gather/scatter still use the upstream manager methods.
Once all dimensions exist, subsequent partitions use original Engine._run.

All executions are bound unitary u/cx streams; unsupported inputs must first be
lowered to this common executable basis. The general product model remains
conservative. An invalid isometry is a fatal error, not a silent optimization.

## Timing and traffic boundaries

Each run is a fresh process. QPY loading/imports are untimed and identical.
Timing starts before manager/engine construction and includes partitioning,
metadata analysis, initialization, all compute and file operations, and final
fdatasync of surviving state files. Cleanup is untimed. Obsolete QThin banks
are removed without an extra sync, just as overwritten QDAO state versions are
not separately synchronized. Process cancelled_write_bytes is explicitly kept;
cancelled dirty pages are never credited as completed storage traffic.
An intermediate diagnostic run used extra old-bank barriers only for QThin;
that asymmetry was identified before the main matrix and corrected. All such
samples are retained in `intermediate_sync_calibration`, not pooled into primary
results. This prototype does not implement crash recovery or promise atomicity.

This uses QDAO's ordinary buffered NPY file path, not O_DIRECT. No global cache
drop or artificial memory cap. States at 20–26q fit in available memory: these
are **small-scale file-backed end-to-end results**, not capacity-scale OOC
results. Payload bytes, NPY file bytes, process I/O and shared guest block
counters are separate. Read cache reuse and overwrite coalescing can make
kernel/block traffic much smaller than application requests. WSL guest counters
are not host NVMe/NAND traffic and include unrelated guest background activity.

Repetitions use randomized method order, three per required size. A process-wide
file lock prevents overlapping experiment orchestrators. No timed workloads run
concurrently. Correctness uses exact Qiskit Statevector and both file-based paths.
