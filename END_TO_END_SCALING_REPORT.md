# Representative end-to-end scaling subset

2 common workload-size points; 18 measured runs; three repetitions per system.
Selected before timing: superposed CDKM arithmetic and QAOA early-physicalization control.
Comparator is an optional additional point if present. This is not the full workload matrix.

## Runtime medians

| Workload | $n$ | QDAO (s) | GBSA repr. (s) | QThin (s) | QDAO/QThin | GBSA/QThin |
|---|---|---|---|---|---|---|
| cdkm_superposed | 26 | 148.654 | 232.937 | 89.108 | 1.668 | 2.614 |
| qaoa | 26 | 223.059 | 325.043 | 176.182 | 1.266 | 1.845 |

## Requested state-payload traffic

| Workload | $n$ | QDAO (GiB) | GBSA repr. (GiB) | QThin (GiB) | QDAO/QThin | GBSA/QThin |
|---|---|---|---|---|---|---|
| cdkm_superposed | 26 | 15.000 | 25.000 | 7.251 | 2.069 | 3.448 |
| qaoa | 26 | 29.000 | 45.000 | 20.143 | 1.440 | 2.234 |

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
