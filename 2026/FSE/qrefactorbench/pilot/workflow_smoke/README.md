# 两个case的资源工作流试跑

日期：2026-09-28。用户要求选一个case跑通，并明确要求除lit-005外再跑正常支持量子化的case。
**已完成：lit-001 MaxCut/QAOA正向实现＋lit-005 Grover边界检查。**
代码和结果位于独立新目录，复用主线程正在实现的resource_workflow接口；没有修改该接口、
原case、gold、正式评分或历史结果。当前会话提出方案，脚本执行检查；不是独立LLM对照实验。

## 直接看结果

| 环节 | lit-001：正向流程 | lit-005：边界流程 |
|---|---|---|
| 经典输入 | 原维护窗口分组程序，4节点单位权环 | 原命名约束程序，自带3变量实例 |
| 量子方案 | QAOA p=1，4逻辑qubit、20个酉门、4测量 | Grover一轮，14逻辑qubit、121个酉门、3测量 |
| 执行/验证 | 实际QDK理想模拟32 shots，原输出一致，没有触发回退 | 本地完整电路状态模拟；所有8种输出＋无样本经修复保持原结果 |
| QDK估算 | 两个假设配置均成功，共2个资源点 | 两个假设配置均成功，共2个资源点 |
| 本轮用途 | 普通量子化路径的工程验收 | 任意满足解不能直接替代first解的边界验收 |

lit-001得到 `separated_weight=4`，分组 `[[A,C],[B,D]]`。
理想QAOA期望cut为3，均匀随机分组为2；单shot最优概率0.53125。
实际32 shots中12次是最优切分，解码后与原程序结果相同。
这是量子采样路径实际输出的结果，未用经典求解结果预先编码电路。
类比大问题的实用收益尚未证明；这个环也有简单的线性时间经典算法。

资源估算使用固定QDK 1.32.3，SurfaceCode/RoundBasedFactory，物理门错误率1e-4，
测量时间为门时间的5倍，估算器错误预算0.01；两组门时间100ns和1000ns均为假设值。

| 案例 | 物理qubit估计 | 100ns门配置的量子执行时间 | 1000ns门配置的量子执行时间 |
|---|---:|---:|---:|
| lit-001 | 279 | 36µs/shot，32 shots合计1.152ms | 360µs/shot，合计11.52ms |
| lit-005 | 5700 | 840µs，一次执行 | 8.4ms，一次执行 |

物理qubit与逻辑qubit不可混用，估算时间不是模拟器本机耗时，也不含尚未校准的完整部署开销。
原合同仍为精确结果，未因估算器max_error=0.01就改成允许1%软件错误。

## 运行命令

在`qrefactorbench/`根目录、`palqo`环境运行。用户已授权安装QDK，`pip check`通过；
跨机器环境见[ENVIRONMENT](../../docs/quantum_advantage/ENVIRONMENT.md)。
输出目录必须不存在，每轮保留输入hash、实际量子程序、检查、估算、成本账本及结论。

一次运行两个case：

```bash
conda activate palqo
python -B pilot/workflow_smoke/run_all.py --output /tmp/qrefactor-workflow-new
```

也可以分别运行：

```bash
conda activate palqo
python -B pilot/workflow_smoke/lit001-v0.1/run.py --output /tmp/lit001-workflow-new
python -B pilot/workflow_smoke/lit005-v0.1/run.py --output /tmp/lit005-workflow-new
```

其他机器可使用自己创建的`qrefactor-resource`环境替代palqo。若SDK装在另一环境，可传
`--qdk-python /absolute/path/to/python`；lit-001的模拟器仍要求当前Python也能导入QDK。
程序不调用LLM、Azure服务或QPU；退出0表示本次case检查与实际资源后端调用完成。

专项测试分开进程运行，避免两个局部脚本都叫run.py造成模块缓存混淆：

```bash
python -B -m pytest -q -p no:cacheprovider pilot/workflow_smoke/lit001-v0.1/test_smoke.py
python -B -m pytest -q -p no:cacheprovider pilot/workflow_smoke/lit005-v0.1/test_smoke.py
```

## 流程产物及限制

每个run目录中：

- `input-manifest.json`绑定原源码、构造脚本与接口版本；`application.qasm`是实际估算输入。
- `simulation.json`（001）或`semantics.json`（005）记录行为检查和具体输出。
- `host-timings.json`保存本机经典执行/准备耗时；描述性区间，不是统计置信界。
- `resource-request.json`和`controller-context.json`分别保存量子计划与控制器证据。
- `resource-analysis.json`是实际QDK接口完整结果，包含配置及成本账本。
- `summary.json`给本轮结论；`output-manifest.json`绑定结果字节。

两个case均完成“程序→具体方案→检查→真实资源估算→成本分析→结论”的工程链。
**完整成本的数值校准未完成**：通信、部署控制、编译摊销等未知项保持null。
lit-001在这两组假设配置下，仅量子执行小计已超过本机经典耗时范围，不能称加速；
lit-005的前缀枚举修复还保留原经典工作，可给出受限方案的不加速论证。

共享后端目前把物理错误保守传播到任务错误，不建模经典证书/回退恢复，因此原始点的
`quality_not_established`不能读成此次理想模拟的行为检查失败。这里保留原输出并单列限制，
没有在此支线修改主线程接口或降低原任务的精确性要求。

这次是当前会话驱动的工程示范，没有独立模型调用、自动反馈采样或新benchmark成绩；
已有源码和N-061结论对当前会话可见。后续若评估harness对LLM的增强，需另做独立输入与对照。

实际验证见[VALIDATION](VALIDATION.md)。
