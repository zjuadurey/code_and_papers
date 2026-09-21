# 加入 DeepSeek 后的四模型小报告

2026-09-22。**Pro/Flash 已完成授权的 20 次首次请求。Pro 有效 10/10，Flash 有效
9/10；另外复现了两个粗标签指标看不见的 HOW 公式错误。** 这支持优先完善内容验证，
不能简单归因于“模型没有差异”或“所有题目都太容易”。

## 运行事实与对比边界

官方 API：`deepseek-v4-pro` / `deepseek-flash`；均 thinking enabled、high，
`max_tokens=16384`。使用同版十份 C 输入（完整程序、无位置提示）、相同公共 wrapper、
相同待审标签，每模型每题一次，无工具、重试、修复或反馈。
每案例两模型并发，全轮 **26.3 分钟**。20 次 HTTP 均为 200，19 份完整最终回答。

此前 GPT 是 medium/Codex，本轮 DeepSeek 是 high/direct API，系统脚手架和输出预算
并不相同。这是同任务下的系统配置比较，不能解释成严格等预算的裸模型排名。
官方文档当时列出 Pro-0813 / V4.1-Flash；API 实际返回模型别名及 fingerprint，
都已保存，不声称冻结了服务端权重快照。

## 描述性结果

| 指标 | GPT Sol | GPT Astra | DeepSeek Pro | DeepSeek Flash |
|---|---:|---:|---:|---:|
| 有效回答 / 请求数 | 10/10 | 10/10 | 10/10 | 9/10 |
| 与七个暂定结构 YES 一致 | 7/7 | 7/7 | 7/7 | — |
| 七个暂定正例的计划覆盖 | 7/7 | 7/7 | 7/7 | — |
| 七个定位锚点精确匹配 | 6/7 | 6/7 | 5/7 | — |
| 七个定位锚点平均行 IoU | 0.9762 | 0.9762 | 0.9260 | — |
| 与暂定首选家族相同 | 6/7 | 7/7 | 6/7 | — |
| 全部最终回答中的 structural YES / NO | 8 / 2 | 8 / 2 | 7 / 3 | 7 / 2，另 1 份缺失 |
| 最终回答中建议保持经典 | 10/10 | 10/10 | 10/10 | 9/9，另 1 份缺失 |
| 平均单次请求耗时 | 103.8 秒 | 50.4 秒 | 157.6 秒 | 49.3 秒 |

所有参考仍为 PENDING；上表不是 gold accuracy。替代家族不自动判错，定位锚点也不是
唯一可接受边界。Pro 在 lit-004 包含模式判断、lit-005 额外提名谓词函数，导致精确
匹配/重叠下降；这些边界选择需要内容审核，不能据此认定定位能力更差。

Flash 的破折号表示按预设完整集规则不输出全量诊断：不能删除失败题再冒充完整十题
成绩。其七份结构正向回答实际都有计划，此处仅记录输出行为，不新设评分分母。

## 关键发现

**1. 两个可复现的 HOW 错误。** lit-002 要求 minimum vertex cover，并以已选索引
元组的字典序打破平局。Flash 提出最小化加在 `x_i` 上的正 superincreasing 权重，
两顶点一条边就会选错：合同选 `(0)`，权重 `(2,1)` 选 `(1)`。Pro 则用正 numeric-mask
项冒充 tuple tie：四顶点反例中合同选 `(0,3)`，其 QUBO 选 `(1,2)`。
两份输入均通过原始经典程序的验证与求解核对。

这些反例否定具体公式分支，不否定所有可能的经典回退方案。历史 GPT Sol 使用反向
选择权重，Astra 把精确 tuple canonicalization 独立列为义务，未给出这两种错误构造。
这是可定位的内容差异，尚不是经过完整盲审的 HOW 总分。
[Flash 反例](tie_counterexample.json) · [Pro 反例](pro_tie_counterexample.json) ·
[原程序核验](counterexample_contract_validation.json)。

**2. 候选范围存在真实分歧。** 两个 GPT 在 lit-009 提名了 pivot 搜索；Pro 分析整个
solve 后拒绝，并声称搜索需要预知全局最大值。后一个理由不充分：可构造改进 incumbent
的谓词，极值搜索有正式算法依据；但它并未自动解决精确浮点/异常、认证和资源问题。
这仍是未定案例的边界审核，不自动计为假阴性。
[Dürr–Høyer 原论文](https://arxiv.org/abs/quant-ph/9607014)。

**3. Flash 的缺失是预算失败。** lit-009 的 `completion_tokens=16384`，其中
`reasoning_tokens=16384`，最终 content 为空，`finish_reason=length`。没有从推理文本
拼答案、补写或增加预算重跑。不能据这次失败宣称它不会做该题；若需补测应另立协议。
[原始元数据](runs/deepseek-flash/lit-009/metadata.json)。

**4. 粗标签仍较饱和，定义问题仍在。** Pro 的七个暂定正例全部一致、计划全部存在，
但其中仍含上面的公式错误。Pro 的 practical 全为 false，Flash 为 8 false / 1 null /
1 缺失；适用性参考全未定。support 又被解释成 generic draft family 或性能证据，
其原始诊断保留，不拿来排名。更多逐例依据见 [AI 内容审查](CONTENT_REVIEW.md)。

## 消耗与实际验证

DeepSeek usage 共 **201,332 prompt tokens、227,360 completion tokens**；completion
已经包括 reasoning，不能重复相加。按本轮 UTC 非高峰时段及当时官方公开单价估算，
Pro 约 $0.297、Flash 约 $0.080，合计 **约 $0.38**。这是 usage 推算，未查询实际账单。
[计算明细](USAGE_ESTIMATE.json) · [官方价格](https://api-docs.deepseek.com/quick_start/pricing/)。

9 项离线 runner/collector 测试通过；20 请求/19 有效回答逐项保存，两个公式反例已复现。
原输入、参考、评测代码和 GPT 实验共 458 个受保护文件保持不变。
[运行验证](validation.json) · [原始/派生数据](README.md) ·
[四模型数据表](FOUR_MODEL_COMPARISON.json)。

本次已完成 D-024 的有界授权。现有证据更支持下一步把“公式对应、tie-break、精确性
义务和反例”做成可判定的 HOW 检查；新增模型和重复采样仍有价值，但不能替代评分改进。
不在本轮冻结新科学标签、改变评分器、建立稳定排名或据此直接确定 Agent 架构。
