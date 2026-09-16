# Representative end-to-end scaling subset

3 common workload-size points; 27 measured runs; three repetitions per system.
Selected before timing: superposed CDKM arithmetic and QAOA early-physicalization control.
28q, if present, covers only the arithmetic point; QAOA at 28q was not measured.
This is not the full workload matrix. Exact coverage and unselected points are in `coverage.csv`.

## Runtime medians

| Workload | $n$ | QDAO (s) | GBSA repr. (s) | QThin (s) | QDAO/QThin | GBSA/QThin |
|---|---|---|---|---|---|---|
| cdkm_superposed | 26 | 148.654 | 232.937 | 89.108 | 1.668 | 2.614 |
| qaoa | 26 | 223.059 | 325.043 | 176.182 | 1.266 | 1.845 |
| cdkm_superposed | 28 | 1003.765 | 1557.833 | 552.486 | 1.817 | 2.820 |

## Requested state-payload traffic

| Workload | $n$ | QDAO (GiB) | GBSA repr. (GiB) | QThin (GiB) | QDAO/QThin | GBSA/QThin |
|---|---|---|---|---|---|---|
| cdkm_superposed | 26 | 15.000 | 25.000 | 7.251 | 2.069 | 3.448 |
| qaoa | 26 | 29.000 | 45.000 | 20.143 | 1.440 | 2.234 |
| cdkm_superposed | 28 | 76.000 | 116.000 | 37.063 | 2.051 | 3.130 |

All three systems use identical QPY hashes, fixed m=16/t=12 (GBSA C=16), complex128,
one thread, buffered NPY and the same final-state synchronization policy.
The case runners and runtime source are unchanged from the core experiments.
Correctness evidence is the existing 195 Phase A and 195 GBSA small exact cases,
with zero failures and unchanged validated runtime hashes; the large scaling runs
are not new exact-state validation cases.
Methods rotate in seeded shuffled order within each repetition; timed runs are serial.
Individual samples, min/max/std/CV, CPU time and process/device counters are retained.
No slow samples are discarded. Ratios are derived from sample medians, not significance tests.

This remains a file-backed WSL2/ext4 VHDX experiment. Full states are 1 GiB at 26q and 4 GiB at 28q;
these data establish size trends rather than exceeding-memory capacity capability.
GBSA is an independent published-policy reproduction on the common QDAO/Aer substrate,
not the authors' native SSDGBSA artifact. Shared guest-device counters are not uniquely
attributable, and requested payload bytes are not native SSD/NAND bytes.

The earlier 28q SSD result is a single materialization event, not a full-circuit run.
See execution-order records and pre-run plans for actual coverage and selection.

## 28q storage-path diagnostics

| System | Wall s | User + system CPU s | Final sync s | Process read GiB | Process write GiB | Cancelled write GiB | Guest-device write GiB |
|---|---:|---:|---:|---:|---:|---:|---:|
| GBSA reproduction | 1557.833 | 790.565 | 76.451 | 0.000431 | 63.750 | 0.000 | 64.699 |
| QDAO | 1003.765 | 597.469 | 79.744 | 0.000366 | 42.500 | 0.000 | 43.168 |
| QThin | 552.486 | 334.334 | 75.521 | 0.000122 | 21.817 | 0.325 | 22.138 |

These are per-column medians, not a causal runtime decomposition. Small process-accounted read volumes indicate that most payload reads hit the page cache. Final sync is timed for every method; these runs also incur writeback during execution. CPU work and storage stalls both affect wall time. Guest-device counters are shared, and process write counters must be read alongside cancelled writes. No native NVMe/NAND or capacity-scale OOC claim follows from this table.

## Capacity-safety pause

After four completed 28q samples the original uniform 3B (12 GiB) preflight reserve exceeded 70% of host free space. Temporary state files were already removed. Execution paused before the next timed run; incomplete-set analysis correctly refused to proceed. Source inspection bounded simultaneous source/destination amplitude banks by 1.5B, and the revised conservative guard reserves 2B + 1 GiB (9 GiB at 28q), including NPY file allocation and metadata allowance for fixed t=12 and 4 KiB blocks. Six capacity tests passed; the 70% free-space limit was retained. Only the pre-run capacity estimator changed; timed case runners, kernels, inputs and parameters remained unchanged. No completed sample was discarded. The pause and changing host-space conditions are part of this small-sample experiment, not controlled native-device conditions. See `capacity_revision.json` and the preserved performance log.
