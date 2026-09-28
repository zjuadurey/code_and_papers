# 资源估算作为harness工具

2026-09-28；D-042 / N-063。采用研究者选择：复用微软开源估算库，
我们实现接口、完整成本和工作流集成。当前是工具入口，不是已运行的LLM增强实验。

## 已实现的调用链

```text
LLM提出OpenQASM 3方案及硬件配置
 → harness取得独立的行为/经典对照证据与成本上下文
 → analyze_resources(request, context)
 → 子进程调用qdk.qre估算量子资源
 → 汇总端到端成本及错误上界
 → 返回结构化反馈，供LLM修订方案/说明未知
```

[Python工具入口](../../qrefactorbench/resource_workflow.py)与CLI使用同一实现。
[SDK适配器](../../qrefactorbench/_qdk_resource_worker.py)固定qdk 1.32.3，使用
OpenQASMApplication、GateBased、SurfaceCode、RoundBasedFactory及PSSPC/LatticeSurgery。
qubit输出明确为物理qubit，runtime原单位ns，在成本汇总层转换为秒。
后端估计已含量子侧测量与纠错模型；外层readout_decode只记未包含的主机解码/处理，避免重复计费。
第一版模型和转换族固定，硬件profile可提供1..8组；不宣称覆盖所有架构或算法方案。

采用`use_graph=False`：已检查1.32.3源码，图剪枝默认路径可能遗漏某些全局Pareto点；
本入口使用枚举路径，但仍只代表指定模型/查询范围。默认每profile超时60秒，上限300秒。
空结果、缺依赖、超时、后端错误分别返回，不转成“案例没有量子机会”。

## 两份输入各由谁提供

request：版本、plan_id、量子应用source/coverage、硬件profile及量子执行错误预算。
方案应包含声明范围内完整量子调用；只交oracle时不能把返回时间冒充整条算法时间。
支持自包含OpenQASM 3和标准门include，不要求case源码转成Q#。

context由harness控制端构造，不能作为LLM自行填写的“验证通过”工具参数：

| 字段 | 意义 |
|---|---|
| application_sha256 | 绑定本次量子方案，拒绝旧方案证据复用 |
| comparison_id / evidence_source | 原任务、规模、质量、经典对照及外部检查证据的身份/来源 |
| same_task | 外部检查是否支持相同行为；true/false/null，工具本身不证明它 |
| classical_seconds | 完整经典任务时间区间及依据，未知填null |
| overheads_seconds | 准备、经典控制、通信、主机读出/解码、验证/回退、编译摊销；每项区间与依据 |
| quantum_executions | 每请求量子应用总调用数，shots/重试只计一次 |
| max_failure_probability | 原任务允许的失败概率，不能照抄估算器的max_error |
| algorithm_failure_bound | 理想算法及未计入硬件项的失败上界；缺证据填null |

所有成本统一为同一请求和串行调度；区间应已包含全部重试/回退的聚合成本，
编译摊销为明确复用条件下每请求的份额。只相加，当前不支持重叠调度或自动推导重试策略。
重复调用采用union bound加总硬件错误，再加算法错误，不假设独立性。
这是保守质量依据；上界超预算表示尚未建立质量保证，不证明真实失败率必然超标。
v0.1不自动证明经典证书/回退怎样将输出错误降为零，该路径需后续专门模型。

接口拒绝未知字段、负数、布尔型计数、非有限数字和倒置区间；缺失成本不当零。
先区分合同冲突/证据不足/质量未建立，再给出conditional_benefit、no_timing_benefit或uncertain。
这些是条件分析反馈，不写入正式benchmark的decision/gold或已有严格成功指标。
预测只对提供的成本区间和模型有效；输入上下文的真伪需要外部独立审核。

## 调用方法

从项目根目录，在已有palqo环境中调用；QDK可位于另一个已授权安装的隔离环境：

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -B -m qrefactorbench estimate-resources \
  examples/resource_workflow/request.json \
  --context examples/resource_workflow/context.json \
  --qdk-python /path/to/qdk-environment/bin/python \
  --json
```

Python中直接调用`analyze_resources(request, controller_context, python=...)`即可由harness接入。
这里不会自动启动LLM或修改旧campaign。CLI成功返回0；参数/依赖错误、超时或空估算返回2，
JSON保留各profile结果。示例是两qubit工程电路，行为和经典比较均未知，不能输出优势建议。

QDK为可选依赖`resources`，固定1.32.3；现有必需依赖不改变。SDK在新子进程中运行，
关闭QDK遥测，使用临时工作目录，不需要Azure账号或提交QPU任务。
进程隔离和超时不是安全沙箱；接入不可信模型循环时仍需工程运行隔离与调用预算。
实际测试/SDK联调状态见PROJECT_STATUS与本轮验证记录，不将mock当作SDK成功。

## 来源与当前边界

- [官方本地Python用法](https://learn.microsoft.com/en-us/azure/quantum/install-run-resource-estimator)
- [结果字段及ns单位](https://learn.microsoft.com/en-us/azure/quantum/qre-estimation-results)
- [QDK源码](https://github.com/microsoft/qdk)；本轮静态检查PyPI 1.32.3 Linux wheel内
  `_openqasm.py`、`_estimation.py`、`_results.py`、telemetry.py及相关模型。
  wheel SHA256：`9a434491e284036d2fe4e32aec6db5f384114bcb59c913d10e8e6df8bf30cee9`。

本工具不负责经典源码到量子方案的自动生成，不提供行为证明/强经典时间测量；
相关检查器与成本测量需由工作流接入。已实现的是可复用估算与条件成本反馈入口，
尚未证明LLM任务表现提升或任何benchmark案例的实际量子优势。
