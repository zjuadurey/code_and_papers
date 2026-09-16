# GBSA REPRODUCTION: COMPLETED

195 exact cases, zero failures; 72 serial timed runs, all required sizes.

| Workload | $n$ | QDAO (s) | GBSA repr. (s) | QThin (s) | QDAO/QThin | GBSA/QThin |
|---|---|---|---|---|---|---|
| cdkm_basis | 20 | 1.524 | 1.827 | 0.094 | 16.290 | 19.534 |
| cdkm_superposed | 20 | 1.534 | 1.802 | 1.099 | 1.397 | 1.640 |
| comparator | 20 | 2.008 | 1.859 | 1.389 | 1.445 | 1.338 |
| grover_oracle | 20 | 26.611 | 21.739 | 21.523 | 1.236 | 1.010 |
| hea | 20 | 2.021 | 1.334 | 1.134 | 1.782 | 1.177 |
| mcx_oracle | 20 | 22.859 | 17.074 | 17.216 | 1.328 | 0.992 |
| qaoa | 20 | 2.109 | 2.109 | 1.751 | 1.204 | 1.205 |
| qft | 20 | 7.863 | 3.124 | 2.767 | 2.842 | 1.129 |
| cdkm_basis | 22 | 7.143 | 8.417 | 0.102 | 69.714 | 82.146 |
| cdkm_superposed | 22 | 7.346 | 8.630 | 4.693 | 1.566 | 1.839 |
| comparator | 22 | 8.576 | 8.705 | 6.017 | 1.425 | 1.447 |
| grover_oracle | 22 | 163.069 | 142.086 | 125.875 | 1.295 | 1.129 |
| hea | 22 | 9.523 | 5.992 | 4.016 | 2.371 | 1.492 |
| mcx_oracle | 22 | 143.641 | 120.307 | 104.824 | 1.370 | 1.148 |
| qaoa | 22 | 8.667 | 12.525 | 7.108 | 1.219 | 1.762 |
| qft | 22 | 54.973 | 17.789 | 15.229 | 3.610 | 1.168 |
| cdkm_basis | 24 | 28.356 | 35.992 | 0.115 | 246.435 | 312.804 |
| cdkm_superposed | 24 | 28.510 | 37.551 | 19.438 | 1.467 | 1.932 |
| comparator | 24 | 40.902 | 46.017 | 25.825 | 1.584 | 1.782 |
| grover_oracle | 24 | 668.044 | 780.470 | 566.727 | 1.179 | 1.377 |
| hea | 24 | 46.415 | 25.031 | 15.382 | 3.017 | 1.627 |
| mcx_oracle | 24 | 578.149 | 691.110 | 465.751 | 1.241 | 1.484 |
| qaoa | 24 | 41.404 | 54.180 | 33.727 | 1.228 | 1.606 |
| qft | 24 | 244.512 | 81.169 | 65.400 | 3.739 | 1.241 |

## Requested state traffic

| Workload | n | QDAO GiB | GBSA repr. GiB | QThin GiB | QDAO/QThin | GBSA/QThin |
|---|---|---|---|---|---|---|
| cdkm_basis | 20 | 0.109 | 0.172 | 1.49e-08 | 7340032.000 | 11534336.000 |
| cdkm_superposed | 20 | 0.109 | 0.172 | 0.047 | 2.321 | 3.648 |
| comparator | 20 | 0.203 | 0.172 | 0.111 | 1.824 | 1.543 |
| grover_oracle | 20 | 3.016 | 2.016 | 2.184 | 1.381 | 0.923 |
| hea | 20 | 0.266 | 0.109 | 0.115 | 2.305 | 0.949 |
| mcx_oracle | 20 | 2.578 | 1.328 | 1.746 | 1.477 | 0.761 |
| qaoa | 20 | 0.266 | 0.266 | 0.189 | 1.402 | 1.402 |
| qft | 20 | 1.172 | 0.203 | 0.203 | 5.769 | 1.000 |
| cdkm_basis | 22 | 0.688 | 0.938 | 1.49e-08 | 46137344.000 | 62914560.000 |
| cdkm_superposed | 22 | 0.688 | 0.938 | 0.328 | 2.095 | 2.857 |
| comparator | 22 | 0.938 | 0.938 | 0.563 | 1.665 | 1.665 |
| grover_oracle | 22 | 24.562 | 17.438 | 17.979 | 1.366 | 0.970 |
| hea | 22 | 1.438 | 0.562 | 0.475 | 3.029 | 1.185 |
| mcx_oracle | 22 | 21.812 | 14.562 | 15.229 | 1.432 | 0.956 |
| qaoa | 22 | 1.188 | 1.938 | 0.830 | 1.431 | 2.334 |
| qft | 22 | 8.812 | 1.688 | 1.312 | 6.714 | 1.286 |
| cdkm_basis | 24 | 2.750 | 4.250 | 1.49e-08 | 184549376.000 | 285212672.000 |
| cdkm_superposed | 24 | 2.750 | 4.250 | 1.254 | 2.193 | 3.389 |
| comparator | 24 | 4.750 | 5.250 | 2.758 | 1.722 | 1.904 |
| grover_oracle | 24 | 97.250 | 111.250 | 77.754 | 1.251 | 1.431 |
| hea | 24 | 7.250 | 2.250 | 1.912 | 3.792 | 1.177 |
| mcx_oracle | 24 | 82.250 | 96.750 | 62.754 | 1.311 | 1.542 |
| qaoa | 24 | 6.250 | 8.250 | 4.393 | 1.423 | 1.878 |
| qft | 24 | 40.750 | 6.750 | 5.750 | 7.087 | 1.174 |
## Measurement contract and limitations

Small-scale **file-backed end-to-end** execution on WSL2/ext4 VHDX. These states
fit system RAM; no large-scale capacity/OOC claim. All methods: complex128,
fixed m=16/t=12, one thread, identical lowered u/cx QPY hashes, Aer 0.17.2/Qiskit
2.5.2, fusion disabled, buffered NPY, final surviving-state fdatasync. Phase A
uses QDAO upstream `fb360e6670b9818a3d4e106fb21cf605838be0a4` with the documented
shared modern-Aer state-injection adapter. It is not an untouched historical
author binary. Phase B shares the exact runtime source hash.

GBSA is an independent Algorithms 1/2 **policy reproduction on that substrate**,
with unrestricted C=16 chunk selection and charged physical layout swaps.
It is not the authors' optimized native SSDGBSA implementation. Algorithm 2 has
printed ambiguities resolved using Section 3.3 and tested against Figure 4.
See `notes/gbsa_reproduction.md` for exact decisions, omitted kernels and license.
No official artifact commit is available (NA).

Wall/CPU time, counter deltas, request counts and sync time are measured. Ratios,
medians, std/CV and correlations are derived. Request bytes count actual state
payload loads/stores, including initialization and layout swaps. They are not
native SSD bytes. Process read/write/cancelled-write counters and shared
guest-visible device counters remain separate in raw/summary CSV. Buffered reads
can hit cache and truncated writes can be cancelled. Device counters are not
uniquely attributable and do not measure native NVMe/NAND traffic.

Every required point has three repetitions; no slow sample was removed. Phase A
interleaved QDAO/QThin order. Phase B ran later, serially with shuffled workload
order; cross-phase background drift remains a limitation. Search, initialization,
swaps, execution and final sync are timed; QPY loading/import/cleanup are outside
all timing windows. No overlapping performance experiments were allowed.
Counts of wins refer only to sample medians, not statistical significance.
Near-unity ratios, especially differences of a few percent, should be read
alongside the individual samples and CV rather than as resolved superiority.
## Answers and applicability

1. **QDAO runtime:** QThin median speedup across 24 points is 1.456x;
   among 21 eventually fully materialized points it is 1.425x.
   Basis-only CDKM is separated because it never allocates an amplitude dimension.
2. **Traffic correlation:** strict-subset median requested-byte reduction is
   1.722x; descriptive Spearman correlation
   with runtime speedup is 0.921. This does not isolate SSD causality: fewer
   Aer compute units and staging operations also save CPU time.
3. **Families:** use the family table below. These 8 workload variants from 7
   families are small controlled instantiations of existing generators, not a
   rerun of the earlier 251-circuit corpus. Do not generalize a family-wide win
   from one size/variant or pool basis-only and eventually entangled inputs.
4. **Negative controls:** all QAOA/HEA Phase A median speedups lie between
   1.204x and 3.017x, with no median
   slowdown. QFT also benefits here; the actual lowered ordering does not make it
   an immediate-full-materialization control. Noise/CV is retained in CSV.
5. **Published policy comparison:** QThin beats this GBSA reproduction at
   23/24 points (20/21 eventually fully materialized). Overall median
   GBSA/QThin runtime ratio is 1.465x; strict-subset
   median is 1.377x. Ratios below one favor GBSA.
   This supports only the documented reproduction comparison, not superiority
   to the authors' full system.
6. **GBSA wins and costs:** GBSA wins at: mcx_oracle 20q.
   QThin's largest median advantages over this reproduction are: cdkm_basis (82.146x), cdkm_superposed (1.839x), qaoa (1.606x).
   Its gate-block reuse and QThin's delayed physicalization are different
   mechanisms. The diagnostic table separates search and layout-swap costs;
   median per-run layout-swap time fraction is 28.1%, while search
   consumes 0.016%. These fractions are measured execution-time
   decompositions, not ablation results. Common-substrate swap overhead is not
   an inherent bound on native GBSA.
7. **Size consistency:** all required 20/22/24q points completed; see size table.
8. **26q:** not included in this required-core dataset. A separately authorized,
   preselected scaling subset is tracked in `results/end_to_end_scaling/`.
   Untimed full-suite planning predicted about 6.99 hours for QDAO alone at three
   repetitions; that extrapolation is not the cost of the smaller subset and
   is not a measured 26q result. Any scaling claims must cite the separate data.
9. **Measured vs derived:** see the measurement contract; paper-reported results
   and earlier trace-model reductions are not inserted into these tables.
10. **FAST claims:** a validated QThin integration reduces measured file-backed
    runtime and instrumented state traffic against the documented QDAO baseline;
    a separate, transparent GBSA policy reproduction supplies a qualified
    three-way comparison. Do not claim author-artifact reproduction, native SSD
    byte reduction, capacity-scale OOC speedup, or a universal family advantage.

## Execution diagnostics

| Variant | n | Gate blocks | Swap passes | Search s | Swap s | Time CV |
|---|---|---|---|---|---|---|
| cdkm_basis | 20 | 3.000 | 2.000 | 0.000552 | 0.331 | 0.022 |
| cdkm_superposed | 20 | 3.000 | 2.000 | 0.000569 | 0.324 | 0.023 |
| comparator | 20 | 3.000 | 2.000 | 0.000575 | 0.299 | 0.003 |
| grover_oracle | 20 | 28.000 | 36.000 | 0.040 | 4.940 | 0.022 |
| hea | 20 | 2.000 | 1.000 | 0.00038 | 0.154 | 0.029 |
| mcx_oracle | 20 | 20.000 | 22.000 | 0.030 | 3.038 | 0.017 |
| qaoa | 20 | 4.000 | 4.000 | 0.000606 | 0.562 | 0.011 |
| qft | 20 | 3.000 | 3.000 | 0.002 | 0.433 | 0.010 |
| cdkm_basis | 22 | 3.000 | 4.000 | 0.000621 | 2.393 | 0.014 |
| cdkm_superposed | 22 | 3.000 | 4.000 | 0.000642 | 2.525 | 0.016 |
| comparator | 22 | 3.000 | 4.000 | 0.000652 | 2.248 | 0.057 |
| grover_oracle | 22 | 52.000 | 87.000 | 0.116 | 52.049 | 0.007 |
| hea | 22 | 2.000 | 2.000 | 0.000388 | 1.184 | 0.007 |
| mcx_oracle | 22 | 44.000 | 72.000 | 0.088 | 42.607 | 0.027 |
| qaoa | 22 | 5.000 | 10.000 | 0.000646 | 5.639 | 0.012 |
| qft | 22 | 4.000 | 9.000 | 0.002 | 4.989 | 0.014 |
| cdkm_basis | 24 | 3.000 | 5.000 | 0.000687 | 11.615 | 0.011 |
| cdkm_superposed | 24 | 3.000 | 5.000 | 0.00077 | 11.635 | 0.025 |
| comparator | 24 | 4.000 | 6.000 | 0.000843 | 15.672 | 0.008 |
| grover_oracle | 24 | 63.000 | 159.000 | 0.180 | 386.134 | 0.004 |
| hea | 24 | 2.000 | 2.000 | 0.000472 | 4.883 | 0.017 |
| mcx_oracle | 24 | 55.000 | 138.000 | 0.130 | 342.636 | 0.012 |
| qaoa | 24 | 5.000 | 11.000 | 0.000683 | 26.037 | 0.016 |
| qft | 24 | 4.000 | 9.000 | 0.003 | 22.123 | 0.018 |
