# 暂定参考标签 v0.1：可比较，待审核

**DRAFT / PENDING；AI 提案，不是金标，尚无新模型运行。**
研究者懂量子，明确要求先提供可用于模型比较的标签并保留待审状态（D-022）。
该授权不是对具体标签逐项背书，不记录虚构的审核人或独立注释。

当前材料：[labels.json](labels.json) · [评分入口](evaluate.py) ·
[版本指纹](provenance.json) · [实际验证](validation.json)。
原输入仍为 [reference_completion/v0.1.1](../../reference_completion/v0.1.1/README.md)。
本目录是**私有参考层**；模型仍只接收那里的单份 txt，不能接收标签或评分输出。
原 case.json、输入、主 evaluator、schema 和历史实验没有改写。

## 标签覆盖

| 母案例 | 结构适用性暂定值 | 主要参考家族／意图 |
|---|---|---|
| lit-001 | YES | Optimization：加权最大割 |
| lit-002 | YES | Optimization：最小顶点覆盖 |
| lit-003 | YES | Search：完整图着色；也提供 one-hot QUBO 依据 |
| lit-004 | YES | Optimization：最大团；阈值搜索亦可讨论 |
| lit-005 | YES | Search：带锁定条件的布尔可满足性搜索 |
| lit-006 | YES | Optimization：0/1 背包，原实现为 DP |
| lit-007 | YES | Optimization：带正负号的二分组偏好 |
| lit-008 | 未定 | 确定性 XOR、全量有序回执 |
| lit-009 | 未定 | 浮点线性求解与残差诊断 |
| lit-010 | 未定 | 有预算、可观察轨迹的数值迭代 |

每例都有源码区域、具体数学映射或未定理由、核心/上下文分别适用的合同义务。
十例均有暂定 `REMAIN_CLASSICAL`；实际适用性仍为 null，因为没有成本收益证据。
`benchmark_supported=false` 指当前没有经过审核的迁移合同及完整迁移验收，并非
不能评价分析响应。审核成熟度与标签内容独立，YES 不意味着已审核或推荐部署。

后三例不能因为暂时没有映射就标为普遍 NO，也不能为制造类别平衡强填。
尤其残差最小化可能有离散 QUBO 路径，必须审变量编码与对应关系。它们仍完整保留在
响应和人工评审中；null 对 null 不得计为正确。当前没有已知结构 NO，**无法评价该维度
的负类识别率**。模型之间有无实际差异需运行后才能知道。

## 现在如何比较

1. WHERE：沿用既有精确区域/行重叠计算，作为定位诊断，不设武断通过阈值。
   控制例中的关注区域不代表必须提名；合法的空候选或替代边界由人工检查。
2. WHETHER：对已知参考字段计算一致/不一致/未定，并报告分母。
   七例结构 YES 可检查是否漏识别；固定的采用建议和支持度只能做诊断。
3. 家族：参考家族一致只说明粗粒度识别；其他受支持家族进入人工核查，不能直接判错。
4. HOW：以**参考要求的七例**为分母报告计划覆盖，不能只统计模型自己判 YES 的题。
   每例的 checklist 用于人工检查变量/谓词/目标、关键行为义务和错误主张；有计划不等于正确。

所有机器输出注明待审、参考一致性和覆盖率，**无总分、无整题通过率、无自动文本打分**。
不按已解决项的一致率单独排名：报告 matched/mismatched/unresolved、已知参考数和
matched/known-reference；否则全答 null 的模型会逃掉分母。
这里是临时诊断协议，不改变旧主指标或重新解释历史分数。

## 使用现有模型响应

每个模型、每个条件分别提交一个 JSON 数组，恰好十个原 Phase-1 响应。
`case_id` 使用输入中 `public_task.case_id`，不是强改为母案例 ID；B/C 的 ID 相同，
必须分开收集，A 的 ID 又不同。评分器验证 schema、文件/行坐标、计划家族一致性、
覆盖率及输入/参考哈希。它只读响应，不运行模型或响应中的代码。

```bash
# 在项目根目录，使用已有环境；输出文件必须不存在。
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/provisional_labels/v0.1/evaluate.py \
  --condition C --model-id MODEL_CONFIG_ID --predictions /path/to/model-C.json \
  --output /path/to/new-model-C-diagnostics.json
```

缺失、重复、错误 ID、非法 JSON/schema 或越界定位均明确报错，不自动修复或静默删题；
实际实验仍需保存原始失败、记录失败数并报告评分不可用，不能把缺失响应当成功或
以其余案例冒充十例成绩。正式失败计分和采样/预算配置仍待研究者决定。

人工 checklist 输出先为 null。建议每项记录 `supported` / `contradicted` /
`not_addressed` / `uncertain`、响应原文位置、理由和真实审核人；这是逐项语义审查，
不按关键词命中计分。允许条件计划诚实说明未解决义务，不要求它假称已实现。
新颖但成立的映射、合理替代边界应保留并在新参考版本中审议，不能覆盖旧结果。
本版尚不自动汇总人工评分，也不声称整题成功定义已经确定。

## 证据与版本

案例公式基于当前源码推导；[Lucas 的 Ising 建模工作](https://arxiv.org/abs/1302.5843v3)
及 [Grover 原论文](https://arxiv.org/abs/quant-ph/9605043v3)提供方法背景。
公式不是文献逐字移植，也不是关于原程序完整迁移正确性的证明。
结构真值、候选边界、备用家族和合同义务均仍待研究者审核。

`test_labels.py` 检查输入绑定和关键评分边界，并用有限小实例核对主要映射；
构造响应只验证评分器是否区分已知差异，绝不是模型能力结果。
变更标签/评测规则须建新版本，保存原版及其哈希。未运行新模型、QPU 或量子优化器。
