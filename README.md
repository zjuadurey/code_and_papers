# Hilbert-Space Thin Provisioning — static characterization

本项目回答：真实电路从全零态及其显式 preparation 开始时，有多少 logical qubits 可以被证明仍是 factorized computational-basis state？主报告见 [FINAL_REPORT.md](FINAL_REPORT.md)。所有 opportunity 数字是理想 Hilbert-volume 或静态 traffic oracle，**不是实测运行加速或 SSD traffic**。

本阶段只实现 CPU 静态分析与 n≤8 的精确验证，没有 SSD layout、QDAO runtime integration、GPU 或 m/t planner。当前 QDAO 与其他 external 仓库只读，未安装 QDAO。

## 环境

实际安装：Python 3.11.16、Qiskit 2.5.2、Aer 0.17.2；完整版本锁见 `requirements.lock.txt`。机器信息在 `results/manifests/environment.txt`。Conda defaults 源要求交互接受条款，使用 conda-forge 的独立环境完成安装，未改全局 conda 配置。

```bash
conda create -y -n htp-static --override-channels -c conda-forge python=3.11
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate htp-static
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.lock.txt
```

或 `conda env create -f environment.yml` 后安装 lock 文件。`environment.yml` 来自 from-history export，移除机器 prefix 并显式修正为实际使用的 conda-forge/nodefaults；原始 export 保存于 `results/manifests/environment.from-history.yml`。直接依赖在 `requirements.txt`，不包含整个 freeze。

## 外部输入

从项目根目录克隆；如果已存在则不重复 clone：

```bash
mkdir -p external
gh repo clone Zhaoyilunnn/qdao external/qdao
gh repo clone pnnl/QASMBench external/QASMBench
gh repo clone Veri-Q/Benchmark external/veriq-benchmark
gh repo clone Zhaoyilunnn/qcs external/qcs
```

`qcs` 是 QDAO `constants.py`/engine tests 明确引用的 corpus；GitHub 当前重定向到 `Zhaoyilunnn/quantum-computing-resources`。其电路 source 标为 `qdao`，SHA 对应 QCS，不冒充 QDAO 自身电路。所有确切 SHA、分支和 clone 日期保存在 `results/manifests/external_repositories.csv` 和 `external/EXTERNAL_SOURCES.md`。复现冻结输入时，在新建 external clones 中 checkout CSV 给出的 SHA；本次参考工作副本始终未切换版本。

QDAO 当前 main 含 `v0.1.0` tag 和 `stable/0.1` branch，本轮不解决其运行兼容问题。`external/*` 全部 gitignored，不 vendoring 外部源码；来源清单的可追踪副本保存在 `results/manifests/`。

可选旧本地电路，始终只读：

```bash
export HTP_PRIOR_QDAO_REPO=/absolute/path/to/old/repository
python scripts/discover_workloads.py --prior-repo /absolute/path/to/old/repository
```

不配置时正常继续，并在报告写 `prior local repository: not provided`。未知 Python generators 只列出、不执行。

## 一条命令复现

```bash
conda activate htp-static
bash scripts/run_all.sh
```

或逐步运行：

```bash
python scripts/bootstrap_check.py
pytest -q
python scripts/discover_workloads.py
python scripts/run_characterization.py
python scripts/validate_small_exact.py
python scripts/analyze_results.py
python scripts/plot_results.py
python scripts/audit_artifacts.py
```

所有脚本将当前工作路径规范化为项目根目录。无需 `pip install .`。`run_all.sh` 使用 `set -euo pipefail`；精确验证发现 false-known 立即失败，报告生成要求 verification PASS 且代码 hash 匹配。

## 方法与可复现性

- `configs/workloads.yaml` 冻结 sizes、seed、按来源/family/width/gate-count 的分层数量；`configs/analysis.yaml` 冻结 gate/width 上限、t=2、m 集合和 validation 配置。主结果 n≤64，主要决策区间 20–40；65–128 只作为结构证据。
- 输入格式：QASM2、QASM3、QPY（支持单文件多个电路）。SHA256 基于输入原始字节；归一化结构 hash 进一步去重。已成功解析且 SHA 相同的 manifest metadata 可缓存；删除 `results/manifests/{qdao,qasmbench,veriq}.csv` 可强制重扫，失败文件每次重试。缓存只保留 metadata，不缓存分析结果。
- QASM2 首先用官方 `qiskit.qasm2.load`；必要时补充 legacy builtins，并保留声明过的自定义 gate bodies。补充旧 exporter 未声明的 `c3sx` 和固定 arity `mcx_gray`。有歧义的重复 gate 定义和损坏语法保留为 parse failure，不改外部输入。QASM3 使用当前 `qiskit.qasm3.load` 与 `qiskit-qasm3-import` 0.6.0；不降级 API。
- QASM 常已包含 decomposition。semantic 透明展开没有可证明规则的 composite，保留可信的高层 reversible primitives；记录原始、semantic、lowered 三种门数。transfer 规则基于类型，不能仅凭自定义 gate 的名字断言语义。详见 `notes/gate_semantics.md`。
- 当前 Qiskit 的部分 OrGate wrappers 无法从 QPY 重载，因此 generated arithmetic 先透明展开并保存实际分析的同一份输入，写出后立即 reload。QPY 的 uint32 control-mask 限制也使可选 generated Grover 只做到 32 qubits；要求的 QFT/QAOA/HEA/random 四类完整覆盖至 40 qubits。未降级环境或修改 Qiskit。
- Aer 的本机 target 有按 RAM 推算的 29-qubit 限制。静态 lowering 从实际 Aer target 复制全部 operation 到 `Target(num_qubits=None)`，optimization_level=0；允许分析超过 RAM 的 circuit metadata。**这不是扩大真实模拟内存上限。** Exact Aer 仅使用原 CPU backend，最多 8 qubits。
- q(t) gate metric 是每个逻辑门后的 2^q 之和。layer metric 另行在 ASAP 层顺序 replay；barriers 只作同步，terminal measurement/readout suffix 去除。mid-circuit measure/reset/control flow 被明确排除。
- QDAO partition 根据固定 commit 的 union/flush 源码转录；100 个随机输入的 partition 边界对照源码 class AST。只执行提取的纯 partition class，使用 fake circuit wrappers，无 QDAO imports/engine。
- QDAO oracle 使用每个 partition 起点的 full-state read 和终点的 write 体积；提供 end/end 替代约定。固定 t=2，不优化。n≤m 或单门超出 capacity 的情况不伪造合法结果。
- 每次表征新建 `results/raw/<UTC timestamp>/`，原始 per-circuit JSON.gz 与 generated QPY 不覆盖。顶层 CSV/报告是最新运行的导出。`run_manifest.json` 包含 code/config/output hashes；`latest_run.json` 指定权威运行。调试期早期 run 只保留溯源，不进入最新结果。
- `scripts/audit_artifacts.py` 独立检查 CSV/原始记录行数、每门 K/Q 总数、事件增量、直接求和体积比值、输入 SHA、代码 SHA、外部仓库清洁状态和图文件。验收记录见 `results/manifests/artifact_audit.json`。
- 精确验证包含 500 个随机 n≤8 电路的两个表示、逐前缀单-qubit reduced density matrix 检查、20 次 Aer 最终态交叉验证，以及入选小电路检查。Q 标记允许保守高估；任何错误 K 标记禁止使用结果。

## 主要产物

| 文件 | 内容 |
|---|---|
| `FINAL_REPORT.md` | 阶段判断与 Q1–Q9 |
| `results/circuit_summary.csv` | 每个电路每种表示的指标和来源 |
| `results/q_trace.csv` | 每门后的 K0/K1/Q 数量（含初始行） |
| `results/qubit_activation.csv` | 每 logical qubit 首次 Q 与触发原因 |
| `results/materialization_events.csv` | q 增长事件、大小、间隔 |
| `results/parse_failures.csv` | 所有尝试后失败的解析记录 |
| `results/analysis_failures.csv` | 动态电路和静态处理限制 |
| `results/verification.json` | 实际测试/精确验证结果 |
| `results/qdao_oracle.csv` | 各合法 m 的次级静态 oracle |
| `results/family_statistics_20_40.csv` | realistic 区间按 family 的 median/geomean/p90/max |
| `results/figures/` | 六张主图，PNG 与 PDF |

不把 basis-only reversible circuits 等同于一般量子算法输入，不把 q_peak=n 的 delayed allocation 叫 peak capacity reduction，不将 generated/synthetic circuits 混入 real-workload aggregate。

## 第二阶段：materialization mechanism study

报告：[MATERIALIZATION_REPORT.md](MATERIALIZATION_REPORT.md)。此阶段只读取冻结的上一阶段输入和结果，所有新输出位于 `results/materialization_model/`。重现本阶段请使用以下独立入口；上面的第一阶段命令会重建第一阶段结果，不属于本轮执行流程。

```bash
conda activate htp-static
bash scripts/run_materialization_all.sh
```

逐步执行：

```bash
pytest -q
python scripts/run_materialization_model.py
python scripts/validate_product_virtualization.py
python scripts/benchmark_fused_materialization.py
python scripts/analyze_materialization_results.py
python scripts/plot_materialization_results.py
python scripts/audit_materialization_results.py
```

- `notes/materialization_model_semantics.md` 定义 K0/K1/P/M、bounded local isometry proof、SWAP remapping、四种 policy 及计费假设。每个 virtual qubit 必须与 rest factorized；M 不 dematerialize。符号单比特 unitary 保留为未知 local pure factor。
- 主集为冻结的 90 个 20–40q lowered real circuits。固定 m=16、t=2 的 common-valid 集合为 86；其余 4 个完整分析但单门超过 oracle 分区容量。其余 m 仅用于 sensitivity，n≤m 的结果明确标记 in-memory analytical extension。
- 主计费为 conservative additive checkpoints：正常 QDAO traversal 加物化 read/write；另给 boundary fusion 和 resident 乐观界。BASIS_THIN 的 ZERO 插入无 amplitude I/O，但 dense gate output 仍计费，因此主表 BASIS_THIN=BASIS_REWRITE。这不意味着文件系统 sparse extents 免费，也不证明 ZERO extents 没有实现价值。
- PRODUCT_FUSED 的两标量 metadata 延迟 backing dimension，直到不能证明保持 factorization 的 interaction。NumPy correctness prototype 验证直接生成 post-gate output，不分配 expanded input。性能 microbenchmark 只测 CPU RAM，逐 trial 独立进程，q≤24；没有 SSD backend 或 measured SSD traffic。
- 测试及 exact validation 结果记录于新的 `verification.json`；前一阶段全部结果的 SHA256 保存在 `prior_results_frozen.json` 并在每阶段复核。`run_manifest.json`、`reproducibility.txt` 和 `artifact_audit.json` 记录源代码、配置、输入、外部仓库、输出与当前 commit 的溯源。
- `policy_summary.csv` 是主集汇总；`workload_policy_results.csv` 保留所有表示、policy、m 的独立行；其余主要表为 `qubit_lifetimes.csv`、`physicalization_events.csv`、`gate_event_trace.csv`、`sensitivity.csv`。never-physicalized lifetimes 为右删失，不虚构 circuit-end 物化事件。七张图各提供 PNG/PDF。
- 本轮结果是 **trace-driven static model — NOT measured SSD traffic**。不把模型 byte reduction 或 RAM microbenchmark 叫 SSD speedup。特别单列 all-product/no-event 输入与实际发生物化的 circuits，避免由巨大 scalar-backing 比例掩盖适用边界。

## 第三阶段：QThin SSD/storage-path materialization prototype

本阶段入口为 `scripts/run_ssd_materialization_all.sh`，报告为 `SSD_MATERIALIZATION_REPORT.md`，所有新数据位于 `results/ssd_materialization/`。没有修改前两阶段结果，也没有集成 QDAO runtime 或增加 workload。

```bash
conda activate htp-static
bash scripts/run_ssd_materialization_all.sh
```

该入口依次 probe、CMake Release build、pytest、至少 2,000 个 native cross-file correctness cases、真实普通文件 microbenchmark、Markdown/CSV 分析。单独运行完整 pytest 前先执行 `python scripts/build_ssd_materialization.py`，因为新增测试会调用 native binary。构建使用 C++17、POSIX I/O 与 `-O3`，无需新 Python 依赖或 sudo。

`HTP_SSD_BENCH_DIR` 可设置 benchmark 目录；默认 `results/ssd_materialization/workdir/`。目录必须容纳 input + working output，运行时同时检查 guest 文件系统及可识别的 WSL VHDX 宿主卷，最多采用可用空间的 70% 并预留少量 metadata 空间。普通文件输出使用 O_EXCL/O_NOFOLLOW，禁止 raw-device 写入。每个 run 将指标安全写入 journal 后删除输出，每个 size 完成后删除输入；不自动清理其他用户文件。现有 `raw_runs.jsonl` 的已完成 configuration ID 会恢复使用，避免意外重复 TB 级写入；重新测量前应将本阶段结果目录另存，并保留 `prior_results_frozen.json`。

协议见 `notes/ssd_materialization_protocol.md`。原生 loop 的工作内存为四个 chunk，最大 256 MiB；支持 CX 两个方向、CZ 和 correctness 用 generic 2q unitary。目标 bit 必须位于 chunk 内。Application、process 和 mapped block-device counters 分列；在 WSL2 下 block counters 是 **guest-visible storage-path traffic**，不能称为原生 NVMe/NAND 流量。DIRECT 与 BUFFERED+fdatasync 分开统计。仅验证单次物化机制，不声称 whole-program QDAO speedup。

本阶段不生成 publication figures。主要产物为 `summary.csv`、完整 `raw_runs.csv`、含 median/min/max/std/CV 的 `run_statistics.csv`、`allocation_behavior.csv`、`chunk_sensitivity.csv`、`direct_vs_buffered.csv`、明确的 `skipped_cases.csv`，以及环境、构建、correctness 和 reproducibility 记录。

## 第四阶段：小规模 file-backed QDAO end-to-end evaluation

在项目根目录、现有 `htp-static` 环境中运行以下命令。继续使用已构建的第三阶段 native binary 运行完整回归测试；本阶段不重跑或覆盖此前实验结果。

```bash
conda activate htp-static
python scripts/setup_qdao_integration.py
python scripts/prepare_end_to_end.py
pytest -q
python scripts/validate_qdao_integration.py
python scripts/run_qdao_end_to_end.py --sizes 20 22 24
python scripts/analyze_qdao_end_to_end.py
```

参考 QDAO checkout 保持只读；兼容性修改位于独立 worktree，补丁和上游 SHA 均保留。两组使用相同的 current-Aer state-injection adapter、固定 m=16/t=12、单线程、complex128、buffered NPY 文件，以及最终状态 `fdatasync`。这不是完全未修改的作者软件；旧 Initialize 接口对照及一次同步策略诊断完整保留，详见 `notes/qdao_integration.md`。

共同输入见 `results/end_to_end_workloads.csv`。主结果和逐次原始 JSON 位于 `results/qdao_end_to_end/`，报告为 `QDAO_INTEGRATION_REPORT.md`。入口按已完成 run ID 恢复，使用文件锁防止重叠实验。不得同时运行此前 SSD microbenchmark。GBSA 阶段必须等待 Phase A 数据审计、封存和 checkpoint commit 完成。

这里测量的是小规模文件后端执行，不是超出 RAM 容量的 OOC 结果。state-payload requests、process accounting 和 shared guest-visible block-device counters 分列；不能把前两者称为物理 SSD bytes。最终表格输出到 `results/end_to_end_tables.tex`，不生成 publication plots。

Phase A 已在 `79ab9a1` 冻结，144 个计时样本、195 个三方 exact cases。`results/qdao_end_to_end/phase_a_hashes.json` 保存完整结果哈希；复现实验请使用独立 checkout，避免覆盖归档结果。

GBSA 全文已由用户提供，Algorithms 1/2 的依赖传播、最大前驱门数搜索、跨 chunk 布局交换已独立复现。明确标为 **GBSA reproduction**，不是作者的完整 native SSDGBSA 实现。Figure 4 的三个 blocks 和 195 个真实文件 exact cases 已验证。伪代码歧义、实现边界和参数见 `notes/gbsa_reproduction.md`；此前 source-blocked 审计保存在 `results/gbsa_comparison/source_blocked_checkpoint/`。

在独立 checkout 中复现 Phase B（计时程序持有与 Phase A 相同的排他锁）：

```bash
pytest -q
python scripts/validate_gbsa_reproduction.py
python scripts/run_gbsa_comparison.py
python scripts/analyze_end_to_end.py
```

组合报告和四张 LaTeX 表可从已冻结数据再生：

```bash
python scripts/analyze_end_to_end.py
```

该命令先核验 Phase A 与所有旧结果哈希、24 个三次重复的 GBSA 测量及共同后端哈希，再生成三方统计。最终状态见 `END_TO_END_EVALUATION_REPORT.md`。GBSA 搜索不受 QDAO 固定低位 qubits 限制，但其布局交换通过共同 QDAO/Aer 文件后端执行且计入开销；不能把本复现成绩冒充官方 artifact 成绩。
