# QDAO INTEGRATION RESULT: STRONG

Small-scale file-backed end-to-end evaluation on WSL2/ext4 VHDX. This is not a
capacity-scale out-of-core experiment and does not measure host NVMe/NAND traffic.

- Common workloads completed: 24; three repetitions per system.
- Correctness: 195 three-way exact comparisons; 0 failures.
- Maximum phase-aligned QThin amplitude error: 6.113e-16.
- Fixed m=16, t=12, complex128, one CPU thread, buffered NPY files, final fdatasync.
- Median runtime speedup across workload/size points: 1.456×.
- Geometric mean runtime speedup: 2.621×.
- Eventually fully materialized subset: 21 points; median speedup 1.425×.
- Negative-control (QAOA/HEA) maximum slowdown: 0.00%; minimum speedup 1.204×.

## Primary measured runtime and requested payload traffic

| Workload | n | QDAO s | QThin s | Speedup | QDAO requested GiB | QThin requested GiB | Reduction |
|---|---:|---:|---:|---:|---:|---:|---:|
| cdkm_basis | 20 | 1.524 | 0.094 | 16.290× | 0.1094 | 1.49e-08 | 7340032.000× |
| cdkm_superposed | 20 | 1.534 | 1.099 | 1.397× | 0.1094 | 0.0471 | 2.321× |
| comparator | 20 | 2.008 | 1.389 | 1.445× | 0.2031 | 0.1114 | 1.824× |
| grover_oracle | 20 | 26.611 | 21.523 | 1.236× | 3.0156 | 2.1836 | 1.381× |
| hea | 20 | 2.021 | 1.134 | 1.782× | 0.2656 | 0.1152 | 2.305× |
| mcx_oracle | 20 | 22.859 | 17.216 | 1.328× | 2.5781 | 1.7461 | 1.477× |
| qaoa | 20 | 2.109 | 1.751 | 1.204× | 0.2656 | 0.1895 | 1.402× |
| qft | 20 | 7.863 | 2.767 | 2.842× | 1.1719 | 0.2031 | 5.769× |
| cdkm_basis | 22 | 7.143 | 0.102 | 69.714× | 0.6875 | 1.49e-08 | 46137344.000× |
| cdkm_superposed | 22 | 7.346 | 4.693 | 1.566× | 0.6875 | 0.3282 | 2.095× |
| comparator | 22 | 8.576 | 6.017 | 1.425× | 0.9375 | 0.5630 | 1.665× |
| grover_oracle | 22 | 163.069 | 125.875 | 1.295× | 24.5625 | 17.9785 | 1.366× |
| hea | 22 | 9.523 | 4.016 | 2.371× | 1.4375 | 0.4746 | 3.029× |
| mcx_oracle | 22 | 143.641 | 104.824 | 1.370× | 21.8125 | 15.2285 | 1.432× |
| qaoa | 22 | 8.667 | 7.108 | 1.219× | 1.1875 | 0.8301 | 1.431× |
| qft | 22 | 54.973 | 15.229 | 3.610× | 8.8125 | 1.3125 | 6.714× |
| cdkm_basis | 24 | 28.356 | 0.115 | 246.435× | 2.7500 | 1.49e-08 | 184549376.000× |
| cdkm_superposed | 24 | 28.510 | 19.438 | 1.467× | 2.7500 | 1.2539 | 2.193× |
| comparator | 24 | 40.902 | 25.825 | 1.584× | 4.7500 | 2.7579 | 1.722× |
| grover_oracle | 24 | 668.044 | 566.727 | 1.179× | 97.2500 | 77.7540 | 1.251× |
| hea | 24 | 46.415 | 15.382 | 3.017× | 7.2500 | 1.9121 | 3.792× |
| mcx_oracle | 24 | 578.149 | 465.751 | 1.241× | 82.2500 | 62.7540 | 1.311× |
| qaoa | 24 | 41.404 | 33.727 | 1.228× | 6.2500 | 4.3926 | 1.423× |
| qft | 24 | 244.512 | 65.400 | 3.739× | 40.7500 | 5.7502 | 7.087× |


Times are measured medians; ratios are derived from medians. Requested amplitude
bytes are instrumented at actual upstream storage-unit reads/writes. NPY headers
are separately counted in raw_runs.csv. All slow repetitions remain in the data;
summary.csv includes min/max/sample standard deviation and coefficient of variation.

## Largest-size kernel counters

| 24q workload | QDAO process MiB | QThin process MiB | QDAO guest device MiB | QThin guest device MiB | Guest ratio |
|---|---:|---:|---:|---:|---:|
| cdkm_basis | 1632.000 | 0.004 | 1366.984 | 1.246 | 1097.016 |
| cdkm_superposed | 1632.000 | 819.066 | 1368.633 | 549.961 | 2.489 |
| comparator | 2720.004 | 1638.289 | 2460.305 | 1368.121 | 1.798 |
| grover_oracle | 53040.227 | 42435.285 | 52952.641 | 42172.879 | 1.256 |
| hea | 4080.023 | 1176.191 | 3822.660 | 638.262 | 5.989 |
| mcx_oracle | 44880.156 | 34275.270 | 44768.582 | 33984.695 | 1.317 |
| qaoa | 3536.012 | 2525.578 | 3278.750 | 2185.867 | 1.500 |
| qft | 22304.137 | 3989.828 | 22102.746 | 3299.391 | 6.699 |


Process totals are read_bytes + write_bytes, including writes later cancelled.
The CSV separately preserves cancelled_write_bytes and write-minus-cancelled.
Guest counters are shared-device observation-window deltas, not uniquely
attributable physical NVMe/NAND traffic. These cache-sensitive quantities must
not be substituted for the instrumented state-payload requests above.

## Scope and interpretation

The adapter retains upstream StaticPartitioner, storage-unit gather/scatter and
Aer compute-unit execution. Once fully materialized, subsequent blocks use the
original Engine._run. Details and the exact compatibility patch are in
notes/qdao_integration.md and patches/qdao_current_qiskit.patch.

QDAO here means the upstream engine with a **shared current-Aer state-injection
adapter**, used identically by QThin. It replaces the old scalar-parameter
Initialize bridge with public set_statevector plus norm restoration. It does not
change partitioning or gates. This is not completely unmodified author software.
Original-bridge calibration samples remain in legacy_api_calibration; the main
matrix was restarted in full after independent correctness validation.

Basis-input arithmetic can remain virtual; report it separately from superposed
arithmetic. Although QFT on zero input has a product final state, its lowered CX
stream temporarily entangles and progressively materializes dimensions. It is
therefore not presumed to be a negative result. QAOA and HEA are the earlier
entangling controls. The exact lowered gate order is frozen in the common QPY
files; optimization level zero still reconstructs a dependency-respecting order.
These are requested-size instantiations of existing generators, not the entire
251-circuit corpus and not 24 independent benchmark families.

Application requests are not physical traffic. /proc read_bytes/write_bytes and
shared guest device counters are separately present in summary.csv. Buffered
cache reuse and overwrite coalescing are allowed by the real QDAO file path.
No global cache flush or artificial memory restriction was introduced. Background
guest traffic cannot be uniquely attributed to the benchmark from device counters.
Process write_bytes includes dirtied pages that may subsequently be cancelled by
NPY file truncation; cancelled_write_bytes and write-minus-cancelled are retained
separately. Neither process counter is a physical SSD byte measurement.
Wall time includes metadata planning, initialization, execution and final sync;
imports, shared circuit loading and cleanup are excluded. Reduced compute-unit
execution and smaller state sizes contribute alongside I/O reduction; the whole
speedup must not be attributed exclusively to the storage device.
The evaluated improvement is for the combined remapping/product/fusion mechanism,
not an ablation proving that fusion alone accounts for all end-to-end gains.

Materialization event counters cover fused partitions, including gates in that
partition. Their bytes/time are subsets of totals, not additive overhead terms.

## Reproduction

```bash
conda activate htp-static
python scripts/setup_qdao_integration.py
python scripts/prepare_end_to_end.py
pytest -q
python scripts/validate_qdao_integration.py
python scripts/run_qdao_end_to_end.py --sizes 20 22 24
python scripts/analyze_qdao_end_to_end.py
```

26q is deferred until required Phase B results are safely complete.
