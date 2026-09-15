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
