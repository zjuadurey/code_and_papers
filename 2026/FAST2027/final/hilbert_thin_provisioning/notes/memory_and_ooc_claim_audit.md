# 内存、页缓存与 OOC 证据边界：论文后续改进记录

记录日期：2026-09-18。数据版本：`10e99d302adc6b277dc3c54ad2714ea7be6d0a69`。
本记录为已有实验的只读复核与后续计划，没有新增性能实验，也没有修改原始结果或论文 LaTeX。

## 结论

**全部 243 次端到端运行的进程峰值 RSS 都低于 2 GiB，但实验没有强制实施 2 GiB 内存预算。最大完整状态为 4 GiB，现有实验不能证明状态超过系统有效内存容量时的 OOC 性能。**

现有结果应称为 **file-backed end-to-end evaluation**。它们支持本次环境下的实测执行时间比较与状态文件读写请求量减少；请求字节数不能全部称为 SSD 流量。

进程内存小本身不是缺陷：分块执行本来就应该控制驻留内存。验证容量型 OOC 的关键是状态工作集相对有效内存预算（包括文件页缓存）的大小，而不是要求进程申请超过 RAM。

## 1. 实测内存：不是“总共申请了多少内存”

从三个 `raw_runs.csv` 的 `peak_rss_bytes` 字段按系统取最大值，各系统均有 81 次运行：

| 系统 | 最大峰值 RSS（bytes） | 最大峰值 RSS（MiB） | 对应 workload | repetition（原始编号） |
|---|---:|---:|---|---:|
| QDAO | 711913472 | 678.93 | cdkm_superposed_28 | 1 |
| QThin | 498425856 | 475.34 | cdkm_superposed_28 | 1 |
| GBSA reproduction | 708698112 | 675.87 | cdkm_superposed_28 | 2 |

RSS 是进程的驻留物理内存指标，不是累计分配量、虚拟地址空间大小，也不是“进程 + 系统页缓存”的总内存消耗。该字段来自 `resource.getrusage(RUSAGE_SELF).ru_maxrss`，Linux 单位换算为 bytes；峰值也可能包含计时前的导入/初始化阶段。

固定参数为 `m=16, t=12`，GBSA 使用 `C=16`，complex128、单线程。仅按幅度负载计算，`2^16` 的计算单元为 1 MiB，`2^12` 的存储单元为 64 KiB；这不是整个进程的内存上限，Python/Aer、元数据和缓冲区还会占用内存。

此前对话核查时 `/proc/meminfo` 的 `MemTotal` 为 16289428 KiB（约 15.5 GiB），这是核查时快照，不能冒充每次运行的内存上限。更直接的历史证据是：243 次原始记录中的 `available_memory_before` 范围为 **13072097280–14083694592 bytes**（约 12.17–13.12 GiB）。它是运行前可用内存，不是峰值使用量或受控预算。

**没有配置并验证过统一的 2 GiB cgroup/虚拟机内存限制。** 因此不能把固定计算单元参数或低 RSS 写成“在 2 GiB 内存限制下完成实验”。

## 2. 状态大小与实验覆盖

complex128 完整状态的幅度负载为 `16 × 2^n` bytes，不含 NPY 头、文件系统块舍入和元数据：

| n | 完整状态负载 | 已完成端到端覆盖 |
|---:|---:|---|
| 20 | 16 MiB | 8 个变体，三系统各 3 次 |
| 22 | 64 MiB | 8 个变体，三系统各 3 次 |
| 24 | 256 MiB | 8 个变体，三系统各 3 次 |
| 26 | 1 GiB | cdkm_superposed、qaoa，三系统各 3 次 |
| 28 | 4 GiB | cdkm_superposed，三系统各 3 次 |

端到端最大完整状态负载仍小于记录的运行前可用内存。单次 SSD 物化 microbenchmark 的 `q_old=28` 是 **4 GiB 输入扩展到 8 GiB 输出**，属于另一实验；不能把其输出容量当作本轮 28q 完整电路的状态容量，也不能用单事件结果替代整个程序的容量型 OOC 证据。

## 3. 页缓存影响：实际读取并不等于请求读取

端到端实验使用 buffered 文件路径；普通文件的内核页缓存通常不计入该进程 RSS。低 RSS 与大量缓存命中可以同时出现。

28q `cdkm_superposed` 的三次重复逐列中位数（摘自扩展报告）：

| 系统 | wall（s） | process read（GiB） | process write（GiB） | cancelled write（GiB） | shared guest-device write（GiB） |
|---|---:|---:|---:|---:|---:|
| QDAO | 1003.765 | 0.000366 | 42.500 | 0.000 | 43.168 |
| QThin | 552.486 | 0.000122 | 21.817 | 0.325 | 22.138 |
| GBSA reproduction | 1557.833 | 0.000431 | 63.750 | 0.000 | 64.699 |

相比大量状态负载读取请求，进程实际读取计数很小，说明大多数负载读取命中了页缓存。写回和最终同步确实发生，不能据此反过来说整个实验“没有存储 I/O”。但 CPU、Python/文件管理开销、缓存与写回共同影响时间，不能把全部加速都归因于 SSD。

必须分开报告：

- **Requested/algorithmic state bytes**：应用请求的状态负载字节数。
- **Process-accounted bytes**：`/proc` 记账，写入值要结合 cancelled writes 阅读。
- **Guest-visible block-device bytes**：WSL2 客体可见共享设备计数，可能混有其他活动。
- **Native physical NVMe/NAND traffic**：现有实验没有证明或测得。

上述表格为逐列中位数，不能直接相减构造严格的时间或 I/O 因果分解。最终同步已计时，但不意味着此前所有缓存读取都变成物理存储读取。

## 4. 论文可以保留与必须避免的结论

可以保留：

- 本次 WSL2/ext4 VHDX 环境下，小规模 file-backed 端到端实测比较，以及明确覆盖范围的 26/28q 扩展。
- 进程峰值 RSS 小于 2 GiB这一观测；分块实现具有较小进程驻留内存。
- QThin 减少状态文件负载请求，且这些运行中实测 wall time 改善。
- 独立单事件 SSD microbenchmark 支持 fused materialization 消除冗余遍历；其环境与计数层级必须单独注明。

不能由现有数据推出：

- “在强制 2 GiB 内存预算下执行了 4 GiB 状态”。
- “完成了超过可用 RAM 的大规模 OOC 端到端评测”。
- “全部请求流量减少均为物理 SSD/NAND 流量减少”。
- “所有 wall-time 加速均来自 SSD I/O 优化”。
- “GBSA 为作者官方实现结果”；本项目仍是 **GBSA reproduction**。

建议论文表述：

> We evaluate file-backed end-to-end execution with bounded compute units. The largest full-state payload is 4 GiB, and peak process RSS remains below 2 GiB. Because the experiments do not enforce a memory budget covering both process memory and the page cache, they do not establish beyond-memory capacity performance. Buffered reads are largely cache-served; requested state bytes, process I/O accounting, and guest-visible block-device traffic are reported separately.

## 5. 后续改进优先级（计划，尚未执行）

1. **先补受控内存预算证据。** 复用既有 workload 和固定参数，在三系统相同的受控环境中限制进程及其文件缓存可用的总内存；可评估 cgroup v2 或独立 VM。若选择 2 GiB，先验证运行时本身能安全工作，再执行 4 GiB 状态。记录实际生效的限制，而非只记录配置文件。
2. **同时验证限制与压力。** 记录 cgroup/VM 的匿名内存、file cache、峰值、memory events、swap 和压力指标；避免把 swap 流量混入状态 I/O 后归因给机制。cgroup 页缓存归属可能受预热/既有缓存影响，需要验证测试设置。
3. **保留三方公平性。** 相同输入 hash、精度、m/t/C、线程、I/O 路径、同步和重复规则；明确冷/热缓存协议。不要只限制 baseline 的缓存，也不要将 microbenchmark 的 DIRECT 结果冒充端到端 DIRECT 结果。
4. **补可归属的存储证据。** 优先在 native Linux/NVMe 环境复测；记录设备层计数、进程计数和请求字节，检查后台噪声。若仍为 WSL2，继续保留 guest-visible 标签。
5. **再判断容量与性能结论。** 状态超过有效内存预算、实际读写路径得到验证且正确性通过后，才新增容量型 OOC 结论。先用既有叠加态算术正例与 QAOA 对照，不需要扩大 benchmark corpus 或重新调 m/t。

这些是改进计划，不是新增结果；本次未运行任何补实验。

## 6. 证据与复核

- [端到端报告](../END_TO_END_EVALUATION_REPORT.md)
- [扩展与存储诊断报告](../END_TO_END_SCALING_REPORT.md)
- [独立 SSD 物化报告](../SSD_MATERIALIZATION_REPORT.md)

本次复核输入的 SHA256：

| 文件 | 行数 | SHA256 |
|---|---:|---|
| `results/qdao_end_to_end/raw_runs.csv` | 144 | `ddc4471b1133c84eecc0f318f4dc8f13c650130fcd21da3496270c22ce9311ff` |
| `results/gbsa_comparison/raw_runs.csv` | 72 | `dd386a2f3037a02cdcf03683a24a2fda91c1123981917da1659b5a564e44607b` |
| `results/end_to_end_scaling/raw_runs.csv` | 27 | `36516c209b43bae9700fc9b595a4dbc5746eba3983b82401c8f799c323bf8e6b` |

复核方法：合并三个 CSV，按 `system` 对 `peak_rss_bytes` 取最大值，以 `2^20` 换算 MiB；对 `available_memory_before` 取全体最小/最大值。GiB 使用 `2^30` bytes。原始结果保持不变。
