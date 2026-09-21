# 两组参考案例：核心任务与功能上下文

2026-09-21 · **DRAFT / AI 辅助策展；待研究者审查，不是科学金标准。**

本轮打磨已有 MaxCut 与最小顶点覆盖两组。现在有 **2 个母问题、4 份可单独阅读的
两层视图**，不是 4 个独立算法/来源。旧 source/context 案例、原 pilot 和实验结果均保留。
新增一个 context-002 manifest；核心视图复用旧源函数并补公共合同，没有另造算法。
下一轮搜索与经典对照尚未制作；本包仅覆盖组合优化，暂不批量扩到十几个。

## 先看这张表

| 组 | 第一层：核心任务 | 第二层：完整功能 | 不能放宽的要求 | 当前科学状态 |
|---|---|---|---|---|
| 设备维护 | [core-001 合同](core_specs/core-001.json)＋[原 MaxCut 核心](../../source_adaptations/v0.1/cases/lit-001/kernel.py) | [context-001 程序](../../context_adaptations/v0.1/cases/context-001/program.py)：当前冲突、建议安排、设备移动和新旧冲突 | 每设备恰好安排一次；权重累加与报告正确 | 精确版保留；另有研究者许可的近似草案，ρ 定义已定、阈值未定 |
| 连接检查 | [core-002 合同](core_specs/core-002.json)＋[原顶点覆盖核心](../../source_adaptations/v0.1/cases/lit-002/kernel.py) | [context-002 程序](cases/context-002/program.py)：当前覆盖、建议站点、逐站清单和任务移交 | **建议必须覆盖每条连接**；清单只能交给所选端点且不重不漏 | 精确最少站点及原并列规则保留；没有批准近似阈值 |

第一层只规定合法核心输入；不凭空要求原函数有完整业务输入校验。第二层对原始请求
负责全量校验、名字/索引转换和完整报告。两个层次对应共同问题而非相同外部 API。
数据关系和 hash 见 [PAIR_INDEX.json](PAIR_INDEX.json)。

## 维护组：哪些地方已够用，哪些不能伪装成完成

现有 context-001 的上下文已经影响真实输出：名称顺序、重复权重、当前安排都会
影响评分或调整报告。沿用它，不通过添加无关逻辑增加代码量。

- 原三设备例子从冲突 8 降到 1，已满足权重 7；残余 1 是软偏好代价，不是安排非法。
- [精确合同](../../context_adaptations/v0.1/cases/context-001/public_task.json) 和 43 个测试保留。
- [近似合同草案](../../context_adaptations/v0.2-draft/CONTRACT_CONTEXT_001.md) 明确
  ρ=(W−C)/(W−C*)，报告可行性、差距和质量，**95% 未批准**。它还缺容差与选择/并列政策，
  因此本包公共视图仍导出完整可执行的精确合同，不能偷偷改成已可验收的近似任务。
- [实际 Qiskit 原型](../../../demo/context001_qiskit/artifacts/device_limit_v011/README.md)
  是独立实现证据；两个 16 设备输出不满足旧精确合同。近似草案不反向修改旧失败。
- 原型权重上限和有限抽样精确性问题保留；并非参考案例业务合同中新增的限制。

## 连接检查组：本轮补齐的第二层

假设性功能需求：在连接的任一端点站点进行检查即可覆盖该连接；所有站点均可用、
成本相同，一个站点可检查全部相邻连接。运维者已有一份站点名单，需要查漏并形成
更精简的建议，再把每条连接交给一个具体站点，生成可核对的工作清单。
这些是假设性业务规则，不冒充真实单位需求；无地理路径、容量、人员、时长限制。

```text
站点、连接、当前名单
  → 全量校验、无向连接去重、名字映射
  → 当前覆盖与漏检、当前逐站清单
  → 建议站点集合
  → 建议覆盖与逐站清单
  → 增撤站点、新覆盖连接、任务移交报告
```

[示例请求](cases/context-002/example_request.json) 是 north—south—west—east 的链，
含一条反向重复声明；当前四站点全部入选。实际[报告](cases/context-002/example_report.json)
选 north 与 west，撤下 south/east，把 south—west 的检查责任从 south 移交给 west。
另一个[当前漏检示例](cases/context-002/incomplete_current_report.json) 只从 north 开始，
建议**增加** west 后覆盖全部连接。因此不能错误地要求“建议站点数总比当前少”。

每条连接只分派给一个入选端点；两端都入选时按输入顺序选择较早端点，保留空清单。
这是合成应用中明确写出的确定性规则，便于避免重复派工；其现实代表性需研究者审查。
全局解并列规则继承原函数；最少变更/不变更优先没有被偷偷增加。
详见 [完整公共合同](cases/context-002/public_task.json)。

| 去掉或写错哪部分 | 可观察后果 |
|---|---|
| 无向去重 | 重复派工、连接数和覆盖数错误 |
| 当前名单评估 | 漏检不能报告，任务移交起点错误 |
| 建议的覆盖约束 | 站点数可能更小，但有连接无人检查 |
| 逐站清单 | 总数量正确仍可能派给未入选站点、重检或漏检 |
| 变化报告 | 建议集合正确仍可能让操作者撤错站点或漏移交 |

## 来源与量子条件的边界

两个核心沿用本地固定 C2|Q> 镜像第 164/427 条；新 inspection 模块中的核心函数
与原 lit-002 **逐字一致**。出处、固定版本和许可沿用
[已有来源说明](../../source_adaptations/v0.1/SOURCES.md)；新改编见 [provenance.json](provenance.json)。
源片段 CC-BY-4.0；新增情境/实现 Codex 辅助合成，整体发布许可仍 NOASSERTION。

MaxCut 已有具体映射证据；顶点覆盖的变量、覆盖约束及惩罚表达仍见
[原 lit-002 审查提案](../../source_adaptations/v0.1/cases/lit-002/ADAPTATION.md)。本轮没有
把数学提案升级为独立验证或实际量子求解。尤其对约束问题，惩罚函数能量低不能
代替对每条连接硬覆盖的检查；不允许用“近似”解释漏检。
context-002 所有结构/实用/支持/意图/家族/决策科学字段为 null，保持 DRAFT。
schema 必需的 positive 类别和候选区间是私有策展提案，不是 ground truth。

## 测试、公共导出与可复现性

新 [test_program.py](cases/context-002/test_program.py) 用原始名称、Cartesian product
和独立报告计算检查完整输出，覆盖 0–4 点的 76 个简单图与所有当前名单，共 1,099
个请求，另测重复/反向连接、输入次序、空域、16 站点边界、非法后缀及不修改输入。
显式错误替身覆盖“可行但非最少”“最少但错误并列”“漏检”“数量正确但清单错误”。
这支持测试辨错能力，不等于已经验证迁移或穷尽所有输入。

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q \
  pilot/reference_cases/v0.1/cases/context-002/test_program.py
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q pilot/reference_cases/v0.1/test_views.py
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench validate pilot/reference_cases/v0.1/cases/
python pilot/reference_cases/v0.1/cases/context-002/program.py \
  < pilot/reference_cases/v0.1/cases/context-002/example_request.json
python pilot/reference_cases/v0.1/prepare_inputs.py --output /tmp/qrefactor-reference-views-new
```

已有 [review_inputs](review_inputs/) 只包含四份公共合同及各自源码、hash 清单。
**不要把整个本包发给模型**：README、case.json、测试、实际报告和来源讨论含私有信息。
每次只供一个视图；独立实验不能先给对应核心答案再测上下文发现。
函数名/精确功能要求仍透露计算结构，尤其核心文件名暴露边界；本包不宣称 WHERE
定位有难度或已消除所有任务线索。公开分发前仍需解决署名与盲化之间的包装问题。

实际验证记录：[validation.json](validation.json)。没有新模型、QPU 或量子模拟实验。
新上下文测试 **37 passed**，配对/公共导出测试 **7 passed**；原两来源案例分别
**24/22 passed**，原维护上下文 **43 passed**。核心回归 **97 passed, 15 skipped**
（可选依赖不在核心环境；本轮无量子代码修改，未重复量子套件）。新 manifest 和
原 14 案例验证通过，原 JSON 汇总成功；823 个原有文件保持不变。
下一步先用 [REVIEW.md](REVIEW.md) 审核两组，再补搜索/经典对照母案例，最后扩展数量。
