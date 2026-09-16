# END-TO-END RESULT: PROMISING

**Required task partially complete: Phase A is STRONG; Phase B is source-blocked.**
This label summarizes the available integration evidence, not an unmeasured
victory over GBSA. The requested published-baseline comparison is still missing.

- QDAO integration: completed, checkpoint `79ab9a1`.
- GBSA reproduction: NOT IMPLEMENTED / NOT RUN — missing verifiable algorithm/artifact.
- Workloads completed: 8 variants × 3 sizes = 24 points; 144 timed runs.
- 20q: completed QDAO/QThin; GBSA not run.
- 22q: completed QDAO/QThin; GBSA not run.
- 24q: completed QDAO/QThin; GBSA not run.
- 26q: SKIPPED_TIME_BUDGET.
- Correctness: 195 three-way exact cases, 0 QDAO/QThin failures; GBSA failures NA.
- Tests at Phase A freeze: 229 passed.
- Environment: WSL2/ext4 VHDX, buffered file-backed state, m=16/t=12,
  complex128, one CPU thread, shared current-Aer state-injection adapter.

## Primary runtime table: measured medians, seconds

| Workload | n | QDAO s | GBSA repr. s | QThin s | QThin vs QDAO | QThin vs GBSA |
|---|---:|---:|---:|---:|---:|---:|
| cdkm_basis | 20 | 1.524 | NA | 0.094 | 16.290× | NA |
| cdkm_superposed | 20 | 1.534 | NA | 1.099 | 1.397× | NA |
| comparator | 20 | 2.008 | NA | 1.389 | 1.445× | NA |
| grover_oracle | 20 | 26.611 | NA | 21.523 | 1.236× | NA |
| hea | 20 | 2.021 | NA | 1.134 | 1.782× | NA |
| mcx_oracle | 20 | 22.859 | NA | 17.216 | 1.328× | NA |
| qaoa | 20 | 2.109 | NA | 1.751 | 1.204× | NA |
| qft | 20 | 7.863 | NA | 2.767 | 2.842× | NA |
| cdkm_basis | 22 | 7.143 | NA | 0.102 | 69.714× | NA |
| cdkm_superposed | 22 | 7.346 | NA | 4.693 | 1.566× | NA |
| comparator | 22 | 8.576 | NA | 6.017 | 1.425× | NA |
| grover_oracle | 22 | 163.069 | NA | 125.875 | 1.295× | NA |
| hea | 22 | 9.523 | NA | 4.016 | 2.371× | NA |
| mcx_oracle | 22 | 143.641 | NA | 104.824 | 1.370× | NA |
| qaoa | 22 | 8.667 | NA | 7.108 | 1.219× | NA |
| qft | 22 | 54.973 | NA | 15.229 | 3.610× | NA |
| cdkm_basis | 24 | 28.356 | NA | 0.115 | 246.435× | NA |
| cdkm_superposed | 24 | 28.510 | NA | 19.438 | 1.467× | NA |
| comparator | 24 | 40.902 | NA | 25.825 | 1.584× | NA |
| grover_oracle | 24 | 668.044 | NA | 566.727 | 1.179× | NA |
| hea | 24 | 46.415 | NA | 15.382 | 3.017× | NA |
| mcx_oracle | 24 | 578.149 | NA | 465.751 | 1.241× | NA |
| qaoa | 24 | 41.404 | NA | 33.727 | 1.228× | NA |
| qft | 24 | 244.512 | NA | 65.400 | 3.739× | NA |

## Requested state traffic: measured at actual manager calls

| Workload | n | QDAO requested GiB | GBSA requested GiB | QThin requested GiB | QDAO/QThin |
|---|---:|---:|---:|---:|---:|
| cdkm_basis | 20 | 0.1094 | NA | 1.49e-08 | 7340032.000× |
| cdkm_superposed | 20 | 0.1094 | NA | 0.04712 | 2.321× |
| comparator | 20 | 0.2031 | NA | 0.1114 | 1.824× |
| grover_oracle | 20 | 3.0156 | NA | 2.184 | 1.381× |
| hea | 20 | 0.2656 | NA | 0.1152 | 2.305× |
| mcx_oracle | 20 | 2.5781 | NA | 1.746 | 1.477× |
| qaoa | 20 | 0.2656 | NA | 0.1895 | 1.402× |
| qft | 20 | 1.1719 | NA | 0.2031 | 5.769× |
| cdkm_basis | 22 | 0.6875 | NA | 1.49e-08 | 46137344.000× |
| cdkm_superposed | 22 | 0.6875 | NA | 0.3282 | 2.095× |
| comparator | 22 | 0.9375 | NA | 0.563 | 1.665× |
| grover_oracle | 22 | 24.5625 | NA | 17.98 | 1.366× |
| hea | 22 | 1.4375 | NA | 0.4746 | 3.029× |
| mcx_oracle | 22 | 21.8125 | NA | 15.23 | 1.432× |
| qaoa | 22 | 1.1875 | NA | 0.8301 | 1.431× |
| qft | 22 | 8.8125 | NA | 1.312 | 6.714× |
| cdkm_basis | 24 | 2.7500 | NA | 1.49e-08 | 184549376.000× |
| cdkm_superposed | 24 | 2.7500 | NA | 1.254 | 2.193× |
| comparator | 24 | 4.7500 | NA | 2.758 | 1.722× |
| grover_oracle | 24 | 97.2500 | NA | 77.75 | 1.251× |
| hea | 24 | 7.2500 | NA | 1.912 | 3.792× |
| mcx_oracle | 24 | 82.2500 | NA | 62.75 | 1.311× |
| qaoa | 24 | 6.2500 | NA | 4.393 | 1.423× |
| qft | 24 | 40.7500 | NA | 5.75 | 7.087× |

These are amplitude payload requests, not physical SSD traffic. NPY file bytes,
process counters and shared guest-device counters are separately retained in
Phase A CSVs. The sizes fit in available RAM; these are **small-scale file-backed
end-to-end integration results**, not capacity-scale out-of-core results.

## Q1–Q3: runtime, traffic and benefiting families

QThin is faster at all 24 measured workload/size medians. Overall
median speedup is 1.456×; the 21 eventually fully
materialized points have median 1.425× and median requested
traffic reduction 1.722×. Basis-input
CDKM never materializes, so its much larger gains are shown separately.

Across the fully materialized points, Spearman correlation between request-byte
reduction and runtime speedup is 0.921 (descriptive, not a causal estimate).
Lower backing width also reduces compute-unit execution and staging. This
combined experiment cannot attribute all speedup to storage or fusion alone.

| Variant | Median runtime speedup | Median request reduction |
|---|---:|---:|
| cdkm_basis | 69.714× | 46137344.000× |
| qft | 3.610× | 6.714× |
| hea | 2.371× | 3.029× |
| cdkm_superposed | 1.467× | 2.193× |
| comparator | 1.445× | 1.722× |
| mcx_oracle | 1.328× | 1.432× |
| grover_oracle | 1.236× | 1.366× |
| qaoa | 1.219× | 1.423× |

## Q4: earlier-entangling controls

QAOA/HEA show no median-time slowdown in this set: speedups range from
1.204× to 3.017×. This does not prove
zero overhead on every fully entangled circuit. Small exact tests exercise the
full-materialization fallback; they are correctness checks, not a performance
ablation. QFT is not assumed negative: on the frozen lowered zero-input stream,
dimensions activate progressively despite a product final state.

## Q5–Q6: comparison with GBSA

**Unanswered.** Neither QThin superiority nor GBSA superiority can be inferred.
The source audit is in `notes/gbsa_reproduction.md`; the unavailable baseline
cells deliberately remain NA. Do not put a GBSA win/loss claim in the paper.

## Q7: consistency across sizes

| n | Points | Median speedup | Fully materialized median |
|---:|---:|---:|---:|
| 20 | 8 | 1.421× | 1.397× |
| 22 | 8 | 1.495× | 1.425× |
| 24 | 8 | 1.525× | 1.467× |

The sign is consistent, but magnitude is workload dependent. For example, 24q
Grover and MCX provide modest gains; they are retained alongside stronger cases.
All three repetitions, min/max, standard deviation and CV are available.

## Q8: optional 26q

Not run. Using actual 26q partition counts and measured 24q seconds per compute
unit predicts approximately 7.0 hours for QDAO alone at three
repetitions, before QThin or GBSA. This exceeds the remaining approximate
seven-hour window. `optional_26_planning.csv` marks this explicitly as an
extrapolation, not a performance measurement. No fast-only 26q subset is
presented as completion of the common suite.

## Q9: evidence types

- Measured: wall/CPU/sync time, manager payload/file requests, /proc counters,
  shared guest-device deltas, correctness errors and per-run event counts.
- Derived: medians, CV, ratios, correlations and aggregates.
- Planning estimate: 26q extrapolation from compute-unit counts.
- Unavailable: GBSA timings/correctness; native physical NVMe/NAND traffic.

The final sync covers surviving files for both systems. Intermediate buffered
writes may be coalesced/cancelled; process cancelled_write_bytes is retained.
Shared guest-device deltas are not uniquely attributable to this process.

## Q10: defensible FAST claims

1. A minimal QThin runtime integrated with upstream QDAO's fixed partitions and
   compute-unit storage path is numerically correct on 195 small exact cases.
2. On this eight-variant 20/22/24q suite, with common current-Aer compatibility
   adaptation, it reduces median end-to-end time and requested state bytes.
   Quote the fully materialized subset (1.425× median
   runtime speedup) alongside the overall 1.456×.
3. These results demonstrate file-backed integration on WSL2, complementing
   the previous independently measured event-level storage prototype. They do
   not establish native-NVMe large-capacity speedup or superiority over GBSA.

QDAO baseline caveat: the upstream engine, partitioner, scheduling and
gather/scatter are retained, but both systems use a shared public Aer
set_statevector/norm-restoration bridge. It is not completely unmodified author
software. Original-API diagnostic samples are preserved and excluded from the
primary matrix. All previous stage results and Phase A files remain unchanged.

## Artifacts and remaining blocker

- `QDAO_INTEGRATION_REPORT.md`: complete Phase A analysis.
- `GBSA_COMPARISON_REPORT.md`: explicit missing baseline and resume requirements.
- `results/end_to_end_summary.csv`: measured A with unavailable B fields.
- `results/end_to_end_tables.tex`: four LaTeX table environments; GBSA cells NA.

A readable GBSA paper or verified author artifact is required to complete Phase
B fairly. No paper draft was edited and no results were pushed.
