# 回答内容初审

审查者：当前 Codex 协调者，AI 事后初审；不是独立注释、人类复核或 gold 判定。
依据：原始回答、同版公开源码/合同及私有待审 checklist。没有执行回答中的迁移方案，
没有运行量子电路，也没有给 `plan_correct` / `task_pass` 赋值。
以下是可供研究者复核的具体观察，不是新增评分量表。

原始证据统一在 `runs/<model>/<lit-ID>/response.txt`；两模型为 `gpt-5.6-sol`、
`gpt-6-astra`。不修改任何原始回答或参考标签。

| 案例 | 回答中观察到的共同内容 | 差异或待复核点 |
|---|---|---|
| lit-001 维护分窗 | 两者定位整个枚举函数；写出加权 cut 映射、numeric-mask tie、精确认证/回退，并保留重复边累加、报告与排序 | 两者均给出用 `2^n` 分离主目标与 mask 的构造；Sol practical=false，Astra=null。不能据计划文字判定迁移已正确实现 |
| lit-002 最小顶点覆盖 | 两者保留最小基数和 selected-index tuple 的字典序，以及覆盖所有权/检查单语义 | Sol 给出高位反向选择权重表达 tuple tie；Astra 给出 `A=n+1` 的覆盖惩罚，再把精确 canonicalization 列为义务。不能把 tuple tie 混同 numeric-mask tie |
| lit-003 议程排程 | 两者定位 `complete`，识别 preview 失败才激活、首个字典序解、失败采样不能证明无解 | Sol 主选 QUBO，Astra 主选 Grover 前缀存在性搜索；Astra 同时写出备选 one-hot QUBO。Sol 对 Grover contract applicability 判 false，Astra 判 true，反映对“可进一步构造”边界的不同理解。替代家族不能自动判错 |
| lit-004 版本组合 | 两者只圈定 `program.py:25–29`，保留 preview、last-record-wins、最大基数和最小 mask | 暂定锚点为 25–30，差一行是把 `best` 转成名字的解码语句；两者文字都保留该依赖。Astra 给出 `B=2^n, A=nB+1` 及惩罚界；Sol 提出两阶段方案，把具体惩罚证明留待完成。精确边界差异不是已证实定位错误 |
| lit-005 配置搜索 | 两者选 Grover 前缀搜索，保留 False-before-True、锁定值、三文字规则、空规则集及无解义务 | Astra 更明确指出零 feature 的有效 current 不会触发 completion。Sol 将来源署名解释为 benchmark_supported=true；Astra=null。这个字段的语义问题见下文 |
| lit-006 背包 | 两者识别现有动态规划、capacity 约束、最大值/最小 mask、独立窗口及 active 过滤 | Astra 写出 slack QUBO、`A>2^n*sum(values)` 界，明确与 `O(nC)` DP 比较；Sol 保留 penalty/slack/Ising 展开的推导义务。Sol 对普通 slack 超范围额外谨慎；Astra 解释正权重与等式约束下超范围 slack 不影响精确 ground state。以上均只是公式层面初审 |
| lit-007 带符号分组 | 两者给出带符号二次目标、numeric-mask tie、互补解对称性和 dense coupling；不添加平衡/容量限制 | Astra 明确化简为 `E=sum(w_ij Z_i Z_j)`；Sol 给出 QUBO 展开，保留完整 Ising 展开的检查义务。两者都不把 finite-shot QAOA 当作精确证书 |
| lit-008 XOR 回执 | 两者 structural=false、regions=[]、plan=null，识别 XOR、完整有序输出、prefix checksum 和确定性 multiplicities | 当前参考 structural=null；这里记录两模型都拒绝正向提名，不能称“负例判对”。两者对 scope 的强否定仍待研究者审核 |
| lit-009 带 pivot 的线性求解 | 两者都提名 `kernel.py:13` 的 pivot argmax，而非整个线性求解器；都指出动态 rows 依赖、首索引 tie、精确浮点与回退义务，structural=true、有搜索计划 | 暂定参考为 unresolved，锚点为整个 solve。Astra 用 incumbent-improvement predicate，并把非有限中间值回退到原 max；Sol 提出 first-argmax predicate，承认一次 oracle 可能线性扫描，binary64/NaN 比较语义尚待构造。两者均保留 inspect/残差/overflow 行为。这是候选粒度边界的新审查材料，不是已确认假阳性或已验证正例 |
| lit-010 预算内迭代 | 两者 structural=false、regions=[]、plan=null，保留给定迭代步数、停止规则、迭代轨迹和独立重算残差；没有用精确线性系统解替代指定 recurrence | Sol practical=false，Astra=null；两者没有把 validation scan 当成充分候选。当前结构参考仍未定，不能统计为负例正确 |

## 跨案例观察

- **支持字段含义不一致。** 私有参考 `shared_rationale.benchmark_supported` 指审核后的
  admissible migration contracts / acceptance harness。公开说明仅要求分别判断 support，
  schema 对该字段只有 boolean/null 类型，没有清楚给出这一定义。Sol 在 lit-005/006
  用出处支持 true、lit-004 用缺少性能 benchmark 支持 false；Astra 多用缺少测量支持 null。
  数字不一致既可能来自模型理解，也可能来自任务说明不足；不能直接归因为能力错误。
  保留原诊断，不事后改提示、标签或评分。
- **适用性 NO 与未知的边界。** Sol 的多个 false 理由包含“缺少 workload/resource
  evidence”；Astra 对七个结构正向案例使用 null。当前实际适用性参考全部未定，不能
  用这些不同答案直接判胜负；应由研究者区分有证据不适用与证据不足。
- **条件计划与可执行迁移不同。** 说明经典认证/回退保证外部结果，并不证明量子部分
  有用。两模型的计划都留有 exactness、oracle/encoding、precision 或资源义务。
- **当前已见定位指标趋同。** 短函数和完整公开合同可能使这些定位题较容易；本轮只跑
  C，不能据此证明位置提示没有作用，也不能外推 repository-scale 定位能力。
- **未定控制并非已知负例。** lit-009 的两模型首次回答都发现了更小的搜索子步骤，
  说明把“主任务不属于支持家族”直接等同于“所有内部区域都不可提名”会漏掉候选。
  是否允许/如何评价这类很小且可能无收益的子步骤，仍需研究者审核边界标准。
