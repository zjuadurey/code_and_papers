# 当前环境与跨机器测试

核对日期：2026-09-28。此页是环境快照和测试说明；用户随后明确授权安装QDK，状态已更新。

**Mac接续增补：** 最新[Mac交接](../MAC_HANDOFF.md)采用Python3.11独立环境方案，
兼容lqcloud0.5.0的Python3.11/3.12要求。下文Python3.10是Linux历史环境，不是云SDK环境要求。
已确认QDK1.32.3及pyqir0.12.5有macOS arm64/x86_64发行wheel；Mac实际运行尚未验收。

## 当前实际使用的环境

**最近的lit-005分析与资源估算接口准备使用Conda环境 `palqo`。**

- 本机环境路径：`/home/audrey/miniconda3/envs/palqo`
- Python：`3.10.21`，conda-forge构建。
- 本机平台：Linux x86_64 / WSL2。该平台上的已有结果不代表Windows/macOS已经验证。
- 已按用户“那你安装啊”的授权，在palqo安装`qdk[qre]==1.32.3`和新增依赖`pyqir==0.12.5`。
  `pip check`通过，QDK导入和两qubit OpenQASM资源估算通过；不是只有导入检查。
  未另装独立`qsharp`包（使用`qdk.qsharp`）；Qiskit仍未安装。

| 包 | palqo中实际版本 | 用途 |
|---|---|---|
| pytest | 9.1.1 | 测试 |
| jsonschema | 4.26.0 | 项目schema验证 |
| referencing | 0.37.0 | schema引用 |
| numpy | 1.26.4 | 已有数值依赖，不是lit-005纯Python诊断必需项 |
| pandas | 2.2.3 | 已有表格依赖；QDK估算扩展也依赖pandas |
| qdk | 1.32.3 | 微软资源估算库，已安装并实际估算验证 |
| pyqir | 0.12.5 | 本次随QDK安装的依赖 |
| pip | 26.2.1 | 本机包管理器版本 |

项目声明的依赖以[pyproject.toml](../../pyproject.toml)为准；当前`resources`可选依赖声明`qdk[qre]==1.32.3`。
历史lit-005运行命令与结果见[局部README](../../pilot/benefit_analysis/lit005-v0.1/README.md)。

## 在另一台机器建立隔离测试环境

建议使用独立名称 `qrefactor-resource`，无需复制本机palqo里的其他项目依赖。
下面是供用户在其他机器执行的安装步骤；本机复用了palqo，未另建此名称的环境。
先切换到同一份源码的 `qrefactorbench/` 根目录：

```bash
conda create -n qrefactor-resource -c conda-forge python=3.10.21 pip
conda activate qrefactor-resource
python -m pip install -e ".[test]"
python -m pip check
```

这会安装项目基础依赖和pytest。Python小版本与本机对齐；跨平台仍可能解析出不同的
传递依赖。这里提供的是最小重建步骤，不是完整的跨平台依赖锁文件。

如要测试微软资源估算库，再执行：

```bash
python -m pip install "qdk[qre]==1.32.3" "pandas==2.2.3"
python -m pip check
python -c "from qdk.qre import estimate; from qdk.qre.models import GateBased, SurfaceCode, RoundBasedFactory; print('QDK resource-estimation imports OK')"
```

`1.32.3`是本次核对的[PyPI版本](https://pypi.org/project/qdk/1.32.3/)，选择固定版本便于比较；
已在本机通过小电路实际估算；完整case工作流的状态应查看其独立运行报告。微软[官方安装说明](https://learn.microsoft.com/en-us/azure/quantum/install-run-resource-estimator)
使用`qdk[qre]`与`qdk.qre`，本地估算不要求Azure账户。上面的导入检查仅验证API可导入，
不等于估算运行或完整harness集成已通过。具体后端测试以后续实现的说明为准。

仅在需要项目现有Qiskit测试/电路功能时，额外安装项目锁定的可选依赖：

```bash
python -m pip install -e ".[quantum]"
```

纯Python局部诊断不需要这个可选项；不要把缺少可选Qiskit导致的skip误读为测试失败。

## 可以立即复现的已存在诊断

新增两个case的真实资源后端试跑已完成，见[workflow_smoke说明](../../pilot/workflow_smoke/README.md)：
lit-001执行QAOA模拟和资源估算，lit-005执行边界检查和资源估算。当前使用上面已安装QDK的palqo环境。

在项目根目录一次重跑（输出目录必须不存在）：

```bash
python -B pilot/workflow_smoke/run_all.py --output /tmp/qrefactor-workflow-new
```

以下为原N-061诊断，保留作独立复现入口。

在 `qrefactorbench/` 根目录运行：

```bash
python -B -m pytest -q -p no:cacheprovider pilot/benefit_analysis/lit005-v0.1/test_analysis.py
python -B pilot/benefit_analysis/lit005-v0.1/check_wrapper.py
```

历史结果分别为8项和11项通过；这是N-061记录，本次环境文档任务没有重跑它们。
第一条是oracle/成本诊断的专项测试，第二条是注入局部经典求解器后的原wrapper测试。
它们都不是QDK估算器测试。

重放诊断时必须使用新的输出路径，不能覆盖已归档results/replay。以下命令适用于
Linux、WSL、macOS的shell，在项目根目录执行：

```bash
qrefactor_replay_dir=$(mktemp -d)
python -B pilot/benefit_analysis/lit005-v0.1/run.py --output "$qrefactor_replay_dir/results.json"
```

Windows PowerShell可自行选择一个不存在的输出文件路径传给`--output`。
成功时应报告1809个公式/锁定实例、4633次基态检查、6442次修复检查全部通过。
脚本会验证参考输入hash，所以需同步相同版本的源码与案例材料，不能只复制单个脚本。

## 实际 LLM workflow：lit-001

2026-09-28 已完成[四轮实际模型闭环](../../pilot/llm_workflow/lit001-v0.1/README.md)：
读取源码 → 模型生成电路 → 行为验证 → QDK 资源与完整成本 → 模型结论。
环境仍为本页 `palqo`，没有再次安装依赖。

跨机器先重放已保存的模型产物（不调用模型），在项目根目录执行：

```bash
conda activate qrefactor-resource
python -B pilot/llm_workflow/lit001-v0.1/replay.py \
  --run pilot/llm_workflow/lit001-v0.1/run-20260928-01 \
  --output /tmp/lit001-replay-new
```

重新运行模型则用 `python -B pilot/llm_workflow/lit001-v0.1/run.py --output /tmp/lit001-llm-new`。
该命令另需 Linux/WSL 的 `bwrap`、已登录 Codex CLI（本次 0.157.1）及原有模型订阅；
会实际调用 gpt-5.6-sol，最多八轮。无凭据写入项目。详细输入、成本假设和证据见上方说明。
每次使用新的输出目录；同步整个项目的新文件，不仅同步已提交内容。
上面的环境名指本页新建环境；若按Mac交接建环境则激活`qrefactor-mac`。
原生Mac不支持该bwrap模型runner；这里的replay不调用模型，可单独验证，不能据此宣称Mac模型运行已通过。

## 不同机器的结果怎么对齐

每次测试记录操作系统/CPU架构、`python --version`、实际运行命令和完整测试输出。
同时保存所用源码commit；若含未提交修改，需同步相同修改并记录相关文件hash，
仅commit相同不足以保证当前工作区相同。

在新建的测试环境中，可记录已安装依赖用于比较：

```bash
python -m pip list --format=json
python -m pip check
```

真实资源估算还必须对齐量子应用、硬件/纠错配置、错误预算、工作负载和QDK版本。
同一配置的预测量子时间与本机执行估算器所花的时间是不同量，不要混在一起比较。

## 本页验证范围

初次仅执行版本和文档检查；随后按用户授权完成QDK安装，`pip check`报告无依赖冲突。
真实小电路估算使用H/T/CX和测量，GateBased(error_rate=1e-4, gate_time=100ns,
measurement_time=500ns)、SurfaceCode/RoundBasedFactory、max_error=0.01。
返回1个Pareto点：177物理qubit、9000ns、错误上界0.000791000035。
这是指定假设下的估算器烟雾测试，不是硬件测量或端到端收益结论；无QPU调用。
主线程源码、历史实验和队列未因这次安装被改写。
