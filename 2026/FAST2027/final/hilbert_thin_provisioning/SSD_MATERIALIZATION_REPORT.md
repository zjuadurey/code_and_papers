# SSD MECHANISM RESULT: STRONG

Git commit: `df29e7c1dd932e1b55de5954b028cb754f53124c` (execution provenance; final delivery commit is its descendant).  
Branch: `exp/ssd-materialization`  
Storage environment: **wsl2_ext4_vhdx**  
Filesystem: **ext4**, mount `/dev/sdd`  
Direct I/O supported: **True**, tested with 4096-byte aligned read/write.  
Largest completed q: **28**, old backing **4 GiB**, output **8 GiB**.  
Correctness cases: **2096**, native executions **4256**.  
Correctness failures: **0**.  
Tests passed: **216**, including all 194 predecessor tests.  
Performance runs: **336 completed**, **108 capacity skips** from 444 planned configurations.  

Primary PRODUCT_FUSED versus NAIVE_PRODUCT, random pure product states, largest completed sizes; latency includes fdatasync and ratios use configuration medians:

| q_old | old_size_GiB | gate | algorithmic_traffic_reduction | proc_traffic_reduction | device_traffic_reduction | baseline_latency_s | fused_latency_s | latency_speedup |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 27 | 2 | cx_product_control | 2.3333 | 2.3333 | 2.3334 | 17.535 | 9.3925 | 1.867 |
| 27 | 2 | cx_product_target | 2.3333 | 2.3333 | 2.3332 | 18.405 | 8.1612 | 2.2551 |
| 27 | 2 | cz | 2.3333 | 2.3333 | 2.3332 | 17.915 | 10.103 | 1.7733 |
| 28 | 4 | cx_product_control | 2.3333 | 2.3333 | 2.3331 | 54.527 | 29.727 | 1.8343 |
| 28 | 4 | cx_product_target | 2.3333 | 2.3333 | 2.3335 | 167.45 | 85.877 | 1.9499 |
| 28 | 4 | cz | 2.3333 | 2.3333 | 2.3337 | 158.93 | 86.87 | 1.8295 |

**Counter terminology:** algorithmic=requested pread/pwrite bytes; proc=Linux process-accounted bytes; device=guest-visible shared block-device bytes. Device counters are shared with other guest activity. **These are actual regular-file storage-path measurements, not proven native physical NVMe/NAND traffic.**

Decision aggregate: q=[28], 5 gate/state configurations, median measured device traffic reduction **2.333×**, median latency speedup **1.834×**. The forced CX target-|+⟩ control is excluded from this aggregate because that factor does not mathematically need physicalization. All requested controls remain in raw data and summary.csv. No timing outliers were removed.

Only comparisons with at least three completed repetitions for both methods enter the decision aggregate. Any interrupted-by-capacity partial group remains identifiable by repetition counts and `interpretation_eligible` in summary.csv.

## Q1. Does native fused materialization produce the same state?

Yes at double-precision tolerance: 2096 normalized random cross-file cases (q≤12 old dimensions), 4256 native processes, compared with independent Qiskit eager statevector evolution. Cases include CX(v,p), CX(p,v), CZ, random general 2q unitary, known |0⟩/|1⟩ sparse/basis cases, and supported DIRECT file cases. Maximum elementwise error **2.238e-16**, maximum infidelity **4.441e-16**, threshold 1e-12. Every completed large run additionally checks 32 deterministic amplitudes outside timing and counter windows; maximum error **0**.

The backing file has no header and is flat complex128. New virtual wire v becomes the highest physical address bit q, preserving old physical indices. The local vector is separate metadata. Existing backing may be arbitrarily entangled; the native transformation does not assume it is product. This is a standalone one-event prototype, not a full state simulator or a general logical-wire runtime.

## Q2. What bytes were measured?

Traffic values below are **GiB (2^30 bytes)**; the CSV retains exact byte counts per run:

| q_old | gate | baseline_algorithmic_traffic_GiB | fused_algorithmic_traffic_GiB | baseline_proc_traffic_GiB | fused_proc_traffic_GiB | baseline_device_traffic_GiB | fused_device_traffic_GiB |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 27 | cx_product_control | 14 | 6 | 14 | 6 | 14.003 | 6.0009 |
| 27 | cx_product_target | 14 | 6 | 14 | 6 | 14.002 | 6.0011 |
| 27 | cz | 14 | 6 | 14 | 6 | 14.001 | 6.0009 |
| 28 | cx_product_control | 28 | 12 | 28 | 12 | 28.003 | 12.002 |
| 28 | cx_product_target | 28 | 12 | 28 | 12 | 28.056 | 12.023 |
| 28 | cz | 28 | 12 | 28 | 12 | 28.018 | 12.006 |

Raw process counters also retain rchar, wchar, read_bytes, write_bytes and cancelled_write_bytes. All successful syscall sizes and call counts are instrumented. Device sectors are converted using the Linux stat ABI's 512-byte sectors. When a counter is unavailable its field is NA; no application count substitutes for it.

The accounting boundaries follow the [Linux process-I/O documentation](https://docs.kernel.org/filesystems/proc.html): rchar/wchar count syscall bytes, while read_bytes/write_bytes account storage-layer work with different read/write update points. Sector units and completed-I/O fields follow the [block-stat ABI](https://docs.kernel.org/block/stat.html). Neither counter interface identifies host NAND traffic through a virtual disk.

## Q3. Does 7B → 3B appear at application level?

Every completed run is asserted against the implemented pass count: NAIVE_PRODUCT reads 3B and writes 4B; PRODUCT_FUSED reads B and writes 2B. The resulting theoretical and observed requested-byte reduction is **7/3 = 2.333333×**, with **2× write reduction**. THIN_BASIS reads 3B and writes 3B (6B total) because it omits the initial zero-branch write. It still reads the logical hole during the gate pass and writes the final full output. Sparse-hole reads can consume fewer process/device bytes than requested bytes, which the counters expose.

This one-event ratio has a different denominator and purpose from the previous whole-trace predicted 5.243×. No claim of reproducing that trace aggregate is made.

The baseline is the specified **full expanded-state traversal**. It reads/writes both branches even when a controlled gate acts identically on one branch. A specialized branch-selective baseline for CX(v,p) or CZ could omit that branch in the gate pass, giving an analytical 5B baseline and 5/3 ratio instead; that variant is **not measured here**. Therefore 7/3 is a property of the requested expand-then-full-pass comparison, not a universal lower bound against every optimized controlled-gate implementation. QDAO integration must compare against the actual traversal behavior it replaces.

## Q4. Does traffic reduction survive below the application?

On the decision subset, process-accounted reduction median is **2.3333×**; guest-visible shared block-device reduction median is **2.3335×**. Extra filesystem reads/writes and background activity are left in the observed counters. The block source is `/dev/sdd`, model `Virtual Disk`, rotational flag `1`. Under WSL these describe a virtual disk and do not establish actual SSD/HDD media.

Write amplification is explicitly defined as device bytes written / final logically necessary output bytes (2B). `summary.csv` stores baseline/fused device write amplification and all three write-reduction ratios. It is guest-path amplification under WSL, not NAND FTL write amplification.

## Q5. How much latency is reduced?

Decision-set median speedup is **1.8343×**. Every operation uses the same I/O mode, target, chunk, native kernel family and product vector as its comparison. The baseline syncs the intermediate file and the final output; fused only needs the final output sync. Those completion points are part of the design difference. `operation_elapsed_s` excludes fdatasync call durations; `total_elapsed_s` includes them.

`run_statistics.csv` records median, minimum, maximum, sample standard deviation and coefficient of variation for latency, CPU time, throughput, counters, call counts and RSS. Median larger policy CV across the decision set is **0.13941**. CPU time is measured separately: tensor expansion plus a permutation/phase pass is more CPU/memory work than their combined contraction, so all timing benefit is not attributed solely to SSD transfers. The input generator, file open, buffer setup and post-run sample checks are not timed; ftruncate and both computational passes are timed.

For these configuration medians, CPU/wall-time median is **0.01706** for naive and **0.0161** for fused. The remaining wall time includes I/O waiting and scheduling; it does not identify a specific host-device bottleneck.

The individual primary configurations make the nonuniform variability explicit:

| gate | product_state | baseline_latency_cv | fused_latency_cv | latency_speedup |
| --- | --- | --- | --- | --- |
| cx_product_control | plus | 0.13719 | 0.35326 | 1.903 |
| cx_product_control | random_seeded | 0.13941 | 0.10332 | 1.8343 |
| cx_product_target | random_seeded | 0.10375 | 0.10087 | 1.9499 |
| cz | plus | 0.17 | 0.41903 | 1.7181 |
| cz | random_seeded | 0.019291 | 0.023307 | 1.8295 |

## Q6. Dependence on backing size

Per-size medians over the five nontrivial gate/product-state combinations:

| q_old | algorithmic_traffic_reduction | proc_traffic_reduction | device_traffic_reduction | latency_speedup |
| --- | --- | --- | --- | --- |
| 24 | 2.3333 | 2.3333 | 2.3331 | 1.9883 |
| 26 | 2.3333 | 2.3333 | 2.3333 | 3.0631 |
| 27 | 2.3333 | 2.3333 | 2.3333 | 1.867 |
| 28 | 2.3333 | 2.3333 | 2.3335 | 1.8343 |

The requested-byte ratio is size-independent at 7/3. The measured per-size median latency speedups span **1.834–3.063×**. This is a descriptive size comparison; sequential size order and changing storage-path latency prevent attributing its trend to size alone.

q=24 is a sanity size; q=26/27 are smaller storage-path microbenchmarks. DIRECT bypasses the guest page cache but cannot prove Windows or device caches are cold. These measurements are not end-to-end out-of-core quantum circuit runs. The skipped sizes below exceeded the conservative guest/host free-space budget. Required capacity includes input+working output and a 256 MiB margin; q=29 needs 24.25 GiB and q=30 needs 48.25 GiB. No performance values are imputed for skipped configurations. The full explicit skip list is `skipped_cases.csv` (108 rows).

| q_old | required_GiB | budget_GiB |
| --- | --- | --- |
| 29 | 24.25 | 19.576 |
| 30 | 48.25 | 19.576 |

`capacity_after.json` records free space after cleanup. Ordinary benchmark input/output files are removed, but this does not guarantee that a dynamically growing host VHDX immediately returns its allocated host space. Host free-space changes can also include other activity. No explicit discard/TRIM or VHDX compaction is performed to force reclamation.

## Q7. Chunk sensitivity and target-bit sensitivity

| q_old | chunk_bytes | io_mode | baseline_latency_s | fused_latency_s | latency_speedup | device_traffic_reduction |
| --- | --- | --- | --- | --- | --- | --- |
| 28 | 1048576 | direct | 143.42 | 82.121 | 1.7465 | 2.333 |
| 28 | 4194304 | direct | 151.63 | 69.703 | 2.1753 | 2.3331 |
| 28 | 16777216 | direct | 159.19 | 83.655 | 1.903 | 2.333 |
| 28 | 67108864 | direct | 159.44 | 71.937 | 2.2163 | 2.3334 |

Across completed chunk configurations, measured speedup spans **1.746–2.216×**. Changing chunk size does not change the requested 7B/3B pass counts. Its observed latency effect is entangled with measurement time because the chunk blocks are sequential; no best-chunk tuning claim is made.

Chunk-level repetitions are at least three. Main 16 MiB rows reuse the main repetitions. `chunk_sensitivity.csv` also includes I/O call count, peak RSS and device bytes. The configured native workspace is four chunks, bounded by 256 MiB; observed maximum RSS across performance runs is **260 MiB**. Neither baseline nor fused loads the whole file into RAM.

RSS here is the unmodified RUSAGE_SELF ru_maxrss watermark. [getrusage(2)](https://man7.org/linux/man-pages/man2/getrusage.2.html) preserves resource history across exec, so a Python launcher's earlier watermark can dominate smaller native buffers. An ancillary live `/proc/PID/status` observation is retained in `memory_snapshot.json` when available; it is not substituted for per-run RSS. Buffer bytes are separately asserted and reported, so small-chunk RSS plateaus are not interpreted as kernel workspace growth.

Primary target is bit 3; higher-bit sensitivity uses bit 18, still inside a 16 MiB chunk:

| q_old | target | baseline_latency_s | fused_latency_s | latency_speedup | device_traffic_reduction |
| --- | --- | --- | --- | --- | --- |
| 28 | 3 | 159.19 | 83.655 | 1.903 | 2.333 |
| 28 | 18 | 159.85 | 97.36 | 1.6419 | 2.3358 |

An inter-chunk high-bit gate would need a different I/O access pattern and is not covered by this prototype.

## Q8. DIRECT versus BUFFERED + fdatasync

| q_old | io_mode | baseline_latency_s | fused_latency_s | latency_speedup | proc_traffic_reduction | device_traffic_reduction |
| --- | --- | --- | --- | --- | --- | --- |
| 26 | buffered | 8.5592 | 4.1739 | 2.0507 | 2.3333 | 2.3334 |
| 26 | direct | 8.6868 | 4.0298 | 2.1557 | 2.3333 | 2.3331 |
| 28 | buffered | 150.6 | 67.573 | 2.2287 | 2.3333 | 2.3333 |
| 28 | direct | 159.19 | 83.655 | 1.903 | 2.3333 | 2.333 |

The completed mode/configuration comparisons show speedups of **1.903–2.229×**. Both recorded modes retain a >1.2× latency benefit in these comparisons.

BUFFERED uses POSIX_FADV_DONTNEED after input generation and before measurement; the baseline also advises its synchronized intermediate file before rereading it. Advice return codes are recorded. No root cache-drop command is used. O_DIRECT support is probed, not assumed; all records retain their actual mode. Host/device caching remains possible in both modes.

Modes are measured in separate blocks, with randomized policy order inside each block. The mode contrast also includes possible temporal/thermal/background effects and is a secondary sensitivity, not an isolated causal estimate of caching.

The [Linux open(2) manual](https://man7.org/linux/man-pages/man2/open.2.html) distinguishes O_DIRECT from synchronous completion guarantees; this experiment therefore explicitly calls fdatasync and reports its duration. No direct I/O is outstanding when the native process exits, and buffered sample reads occur after that process has completed.

## Q9. Does THIN_BASIS save actual file allocation?

Allocation is stat.st_blocks×512, sampled after expansion+sync and after the entangler+sync:

| q_old | policy | logical_output_bytes | allocated_output_bytes_before_gate | allocated_output_bytes_after_gate | before_allocation_fraction | after_allocation_fraction |
| --- | --- | --- | --- | --- | --- | --- |
| 24 | FUSED_BASIS | 5.3687e+08 | 0 | 5.3688e+08 | 0 | 1 |
| 24 | NAIVE_BASIS | 5.3687e+08 | 5.3688e+08 | 5.3688e+08 | 1 | 1 |
| 24 | THIN_BASIS | 5.3687e+08 | 2.6844e+08 | 5.3687e+08 | 0.5 | 1 |
| 26 | FUSED_BASIS | 2.1475e+09 | 0 | 2.1475e+09 | 0 | 1 |
| 26 | NAIVE_BASIS | 2.1475e+09 | 2.1475e+09 | 2.1475e+09 | 1 | 1 |
| 26 | THIN_BASIS | 2.1475e+09 | 1.0737e+09 | 2.1475e+09 | 0.5 | 1 |
| 27 | FUSED_BASIS | 4.295e+09 | 0 | 4.295e+09 | 0 | 1 |
| 27 | NAIVE_BASIS | 4.295e+09 | 4.295e+09 | 4.295e+09 | 1 | 1 |
| 27 | THIN_BASIS | 4.295e+09 | 2.1475e+09 | 4.295e+09 | 0.5 | 1 |
| 28 | FUSED_BASIS | 8.5899e+09 | 0 | 8.5899e+09 | 0 | 1 |
| 28 | NAIVE_BASIS | 8.5899e+09 | 8.5899e+09 | 8.5899e+09 | 1 | 1 |
| 28 | THIN_BASIS | 8.5899e+09 | 4.295e+09 | 8.5899e+09 | 0.5 | 1 |

The thin path uses ftruncate and writes only the known branch; the other branch is a real filesystem hole until the gate output is written. Allocated blocks describe guest filesystem allocation, not the physical size of the host VHDX or NAND usage. The dense final write deliberately writes every output byte, even amplitudes that are mathematically zero. This prototype does not perform content sparsification or filesystem COW.

## Q10. Is this environment suitable for publication-grade native SSD claims?

**No: this is useful measured prototype evidence, but a native Linux/NVMe rerun is required for native SSD claims.** The path is wsl2_ext4_vhdx, filesystem ext4. The host-volume audit is D:/NTFS. In WSL, guest O_DIRECT and guest block counters establish elimination of guest-visible storage-path work, not elimination of a particular physical NVMe/controller/NAND traversal.

The supplementary Windows query maps the VHDX host volume to KINGBANK KP130, BusType NVMe. The supplemental reliability query failed; its exact error is retained in host_device_supplement.json. That identity does not turn guest counters into host/controller counters. Temperature and device-internal behavior remain unavailable.

At the initial audit the host volume had 43.165 GiB free of 803.557 GiB (5.37% free). This is a volume-level capacity observation, not an SSD-internal free-block or garbage-collection measurement.

The raw data distinguishes possible distortions: operation versus sync time, CPU time, mode sensitivity, chunk sensitivity, block-versus-process bytes, allocation and repetition CV. It does not provide SSD temperatures, FTL garbage-collection counters, host cache misses or bandwidth saturation proof, so those causal explanations remain hypotheses rather than fabricated measurements. Device counters are shared; no background-system tuning was performed. Load averages and available memory were recorded before every run.

Sizes are processed sequentially in increasing q to bound disk occupancy, and policies are shuffled within each configuration/repetition block. First-versus-last-quarter main-run medians expose temporal variation (the quarters also contain different gate/state groups, so this is descriptive):

| q_old | policy | window_runs | first_quarter_latency_median_s | last_quarter_latency_median_s |
| --- | --- | --- | --- | --- |
| 24 | NAIVE_PRODUCT | 7 | 1.127 | 2.3086 |
| 24 | PRODUCT_FUSED | 7 | 0.58169 | 0.58399 |
| 26 | NAIVE_PRODUCT | 7 | 8.9721 | 8.6868 |
| 26 | PRODUCT_FUSED | 7 | 2.1346 | 4.0298 |
| 27 | NAIVE_PRODUCT | 7 | 18.198 | 18.082 |
| 27 | PRODUCT_FUSED | 7 | 10.103 | 9.1168 |
| 28 | NAIVE_PRODUCT | 7 | 45.99 | 159.19 |
| 28 | PRODUCT_FUSED | 7 | 24.42 | 85.877 |

The size trend and cross-block sensitivities therefore do not isolate size or time as a cause. Every slow sample is retained; actual order and timestamps allow this variation to be audited.

## Scope, recommendation and reproduction

**NEXT STEP: INTEGRATE_QDAO**

Correctness is clean and the measured storage-path traffic benefit supports integrating this bounded mechanism with QDAO; the measured timing variability and native-device validation limitation still apply. This stage validates remapping + product metadata + fused first-entangler only. It establishes no whole-program QDAO speedup. QDAO runtime and partition code were not modified, m/t were not tuned, and no workload corpus was expanded.

```
conda activate htp-static
bash scripts/run_ssd_materialization_all.sh
```

The script builds Release C++17 with compiler-recorded flags, runs all tests and file correctness first, then safely runs and summarizes the configured matrix. `HTP_SSD_BENCH_DIR` overrides the ordinary-file directory. Existing output files are never opened for truncation; each benchmark output is newly created. Temporary input/output files are deleted after results are safely journaled. A manifest records planned order; each raw row records actual order, parameters, product-state seed, modes, counters and binary hash. `input_generation.csv` separately records the input seed, generation ID and size. `execution_plan_consistency.json` verifies the final orchestration source regenerates the measured manifest. No raw block write, mount/format, explicit discard/TRIM or privileged cache-drop operation is performed.

`reproducibility.txt`, `build.json`, `environment.json`, `benchmark_manifest.csv` and per-run command logs provide execution provenance. All earlier characterization and materialization-model artifacts are hash checked and left immutable. Numerical values above are measured or ratios of measured medians except the explicitly labeled 7B/3B theoretical pass count. No publication plots were generated.
