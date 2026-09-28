# DeepSeek 回答内容审查

当前 Codex 协调者的 AI 事后审查；不是独立专家审核或 gold 标签。
依据首次回答、原公开合同和离线数学检查。无迁移实现/QPU 验证，未改标签或评分器。
原始文本：`runs/<deepseek-v4-pro|deepseek-flash>/<lit-ID>/response.txt`。

## 已复现的两个公式问题：lit-002

原任务要求最小基数 vertex cover；同基数时比较 **已选索引元组的字典序**。
该规则不同于 numeric-mask 最小，也不是最小化低索引上的正大权重。

- **Flash：次级权重方向错误。** 回答建议把正 superincreasing 权重加在 `x_i` 上
  并最小化。两站一条边的最小覆盖为 `(0)`、`(1)`，合同选 `(0)`；权重 `(2,1)`
  却选 `(1)`。取充分的 cardinality/coverage 系数后错误仍存在。
  [可复现脚本](check_tie_counterexample.py) / [实际结果](tie_counterexample.json)。
  只反驳这一编码分支；其另提的精确两阶段方案没有被这个反例否定。
- **Pro：numeric-mask 和 tuple 顺序混同。** 回答明确用正的
  `C*sum(2^i*x_i)` 声称保持 tuple tie。四顶点图，边为
  `(0,1),(0,2),(1,3),(2,3)`，最小覆盖仅 `(0,3)`、`(1,2)`。
  合同选 `(0,3)`，其公式选 mask 更小的 `(1,2)`。取 `A=1,P=10,C=1/32`
  满足其 `0<C<A/2^n` 条件，仍错误。
  [可复现脚本](check_pro_tie_counterexample.py) / [实际结果](pro_tie_counterexample.json)。

以上系数是审查者实例化的反例，不冒充模型给出的数值。两个程序只在经典小实例上
检查数学主张，不执行模型生成程序。正确的经典审核/回退仍可能保住最终外部输出；
它不会使写错的目标函数变正确。因此不能仅据此说整个条件计划必然执行失败。

同题历史 GPT Sol 使用 `sum(2^(n-1-i)*(1-x_i))` 的反向选择项，Astra 明确把 tuple
canonicalization 留作独立精确义务，没有提出上述两种错误公式。这是本次样本中可定位的
内容差异，不是四模型总体能力排名，也不新设自动 task_pass 分数。

## 逐例观察

| 案例 | Pro | Flash | 审核边界 |
|---|---|---|---|
| lit-001 | 核心定位正确；QUBO 中 x=0 表示 window 0，属于可接受的变量翻转；tie 交给后处理 | 核心定位正确；给出 `M*conflict+mask`、`M>2^n-1` 的构造 | 都承认精确性未验证。Pro 的 O(n²) preprocessing 描述没有显式计入任意数量的重复 requirements；不能据此声称资源预算完整 |
| lit-002 | 上述 numeric-mask/tuple 反例成立 | 上述权重方向反例成立 | 标签 YES、家族和“计划存在”均捕捉不到这一错误 |
| lit-003 | QUBO 替代路线；完整函数 28–57；指数 lex 权重、penalty 待证明 | QUBO 替代路线；28–56 漏掉最终 return 行；讨论了返回/异常义务 | 不按首选家族自动判错；Flash 替换接口/保留 return 的位置仍需审查，不能仅以一行差异判行为错误。Pro intent 的 one-session-per-slot 表述与其正确的 one-slot-per-session 公式不一致，按具体公式审查 |
| lit-004 | 24–30 含激活条件；`P>A` 的冲突惩罚配小正 epsilon，可通过删除冲突顶点解释可行性 | 25–29，给出主/次目标和充分惩罚界 | 两种定位均可辩护，不把微小 IoU 差异直接当能力差。两者都保留 preview 与 report |
| lit-005 | 提名 conforms 与 complete 两个区域；Grover 谓词明确，有序搜索只提可能的 less-than wrapper | complete 10–13；承认首解及无解政策未解决，没有给出前缀构造 | 两者均比完整构造留有更多义务。Flash formulation 的“Empty clauses are true”混同空规则集与单条空 clause；合法输入每条恰三文字，故不能据此声称已发现合法输入上的运行失败 |
| lit-006 | 正确识别 DP；slack/penalty 留待推导，tie 不在其标量目标中，要求与 DP 结果核对 | 正确识别 DP；slack/tie 系数仍是草案，practical=null | 对比历史 Astra 的显式 `A>2^n*sum(values)` 界，二者可检验细节更少。无统一输入上界不妨碍导出逐实例 penalty 界，但本轮不据缺少推导直接赋 task_pass=false |
| lit-007 | 正确展开带符号二次 score；最优性及 mask tie 交给经典检查 | 正确展开二次 score；先选最佳已观察样本，再承认 exact fallback 未解决 | 没有把某个最优分数样本等同完整认证；全局 tie 仍是独立义务，未验证执行 |
| lit-008 | 提名 encode 7–9 后结构拒绝，plan=null | 不提名，结构拒绝，plan=null | WHERE 允许提名后拒绝；不把这组差异自动计为错误，也不把未定控制升为 gold NO |
| lit-009 | 提名整个 solve，structural=false；否定 pivot 的理由称必须有已知全局最大值/预计算 target | `finish_reason=length`，16384 completion tokens 全部为 reasoning，最终 content 为空 | Flash 没有可评分最终答案，不从 reasoning 中拼答案。Pro 对整个求解器的范围判断可理解，但“极值搜索必须预知最大值”理由不成立：可用逐步改进 incumbent 的谓词；确切浮点语义、认证、装载成本仍待解决。不能据此自动判整个未定案例对错 |
| lit-010 | 无候选、结构拒绝，识别预算内 recurrence 与 residual trace | 无候选、结构拒绝，同样保留 recurrence/trace | 与两个 GPT 的提名判断接近；参考仍未定，不能称为负例正确率 |

## 通用限制

两模型现有回答继续出现 practical=false 与缺乏证据混用，以及 benchmark_supported
被解释成 generic draft family 或性能证据的情况。本轮公开定义未修改，原始诊断仍保留。
条件计划经常要求经典完整认证/回退；提到它不代表量子部分有用或审核已经完成。
DeepSeek high/direct API 与 GPT medium/Codex 存在提示脚手架、预算和输出上限差异。

lit-009 的算法依据：[Dürr–Høyer 极值搜索](https://arxiv.org/abs/quant-ph/9607014)。
该算法的概率保证不等于本软件需要的确定性合同；这里仅用于核对“必须预知最优值”的
技术主张。原始可信经典程序也已接受两份 tie 反例输入并返回合同要求的解，见
[原程序核验](counterexample_contract_validation.json)。此核验最初一次离线调用交换了
edges/n 参数并报 TypeError，随后以命名参数纠正；不是模型重试，记录原样保留。
