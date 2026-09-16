# GBSA comparison: NOT COMPLETED — SOURCE_BLOCKED

Phase A checkpoint: `79ab9a1`. All Phase A performance processes finished before
GBSA source inspection. Phase A and older results remain hash-verified and frozen.

The requested published baseline could not be faithfully implemented because
the RACS paper's full algorithm and an official artifact were not obtained.
The DOI is [10.1145/3769002.3769982](https://doi.org/10.1145/3769002.3769982).
The [institution record](https://researchoutput.ncku.edu.tw/zh/publications/toward-efficient-quantum-circuit-simulation-with-memory-and-io-re/)
confirms the paper and abstract, but does not specify the selector/storage rules
needed for a fair reproduction. See `notes/gbsa_reproduction.md` and the source
audit for retrieval attempts and exact missing information.

GBSA correctness cases: 0; failures: **NA (not tested)**. GBSA performance runs:
0. All 72 required GBSA runs are explicitly skipped for the source blocker.
No official result, fabricated number or generic greedy proxy is substituted.
The following tables preserve only measured Phase A values. They are incomplete
three-way tables and cannot support a QThin-versus-GBSA claim.

## Runtime

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

## Requested state traffic

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

## Fairness and resumption

Common QPY files and SHA256s are frozen in `results/end_to_end_workloads.csv`.
`fairness_manifest.csv` maps those files to all three intended systems; GBSA
configuration fields remain NA. A later reproduction must validate correctness,
then run the same 24 required points with three repetitions. Reuse of Phase A
would introduce a sequential-batch timing limitation, which must be disclosed.

26q: SKIPPED_TIME_BUDGET. An untimed count-based extrapolation predicts roughly
7.0 hours for QDAO alone at 26q with three repetitions, before
QThin/GBSA and reporting. This is not a measured 26q runtime.
