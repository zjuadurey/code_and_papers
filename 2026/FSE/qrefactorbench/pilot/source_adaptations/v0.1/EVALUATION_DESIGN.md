# 这两例如何借鉴已有评测方法

这是 **PROVISIONAL 评测设计/经典测试实现**，没有产生模型准确率、量子程序或新评分语义。
复用现有 [evaluation_protocol](../../../docs/evaluation_protocol.md) 的分层接口；
不能因为新案例测试通过，就把旧 evaluator 的未知结果改成通过。

## 有出处的方法 → 本次具体落地

| 来源及可核查位置 | 借鉴什么 | 两例中的落地 | 不直接照搬的部分 |
|---|---|---|---|
| [C2\|Q>](https://doi.org/10.1145/3803018)，[固定数据镜像](https://huggingface.co/datasets/boshuai1/c2q-dataset/tree/c5b457cf425c31e91bae829503ece6e92646dd0a)，[validate_dataset.py](https://github.com/C2-Q/C2Q/blob/42e9cb642d4300662274c859e96f131a26d0a714/src/parser/validate_dataset.py) | 经典程序实例、问题分类与单独的数据实现/多样性检查入口 | 固定两条具体记录、检查实际函数与输入域，再建立可执行行为合同；来源标签留在私有策展材料 | 原 classification label 不等于迁移可行/实用标签；分类分数不等于局部重构与语义保持；未复现其评测，也不对其全套测试覆盖下结论 |
| [Qiskit HumanEval test_solutions.py](https://github.com/qiskit-community/qiskit-human-eval/blob/c98ba538239fcfd554aa89627ee8026f4b5de450/scripts/test_solutions.py#L124) | 固定 entry_point、canonical implementation 与逐题 executable tests、机器可读结果 | 固定两个 API，保留来源计算函数，分别运行 pytest；用不调用原 kernel 的独立小规模枚举 oracle 检查输出 | 函数测试通过不是全部域正确性证明；不复制其执行器，也不把 exec namespace 当安全沙箱；未运行模型，不能报告 Pass@k |
| [SupermarQ 论文](https://arxiv.org/abs/2202.11045v3)及 [QAOA proxy API](https://superstaq.readthedocs.io/en/v0.5.37/autoapi/supermarq/benchmarks/qaoa_vanilla_proxy/index.html) | 面向应用输出的指标，与量子硬件/线路特征分开解释 | 同时记录任务输出、可行性、目标值；未来资源字段独立记录 | proxy 能量/分布得分不是“返回精确最佳命名解”；这两例并非来自 SupermarQ，不借其名义证明任务真实性或优势 |

这里只导入 C2|Q> 的两个计算实例；另外两项是**评测方法借鉴**，未导入其任务或代码。
Qiskit HumanEval 此处作为公开可执行基准参考，不把其发表场合与 TOSEM/HPCA 混为一谈。

## 分层评测清单

| 层次 | lit-001 / MaxCut | lit-002 / 顶点覆盖 | 当前状态 |
|---|---|---|---|
| WHERE | 函数/枚举主体与矩阵依赖 | 函数/枚举主体与边集依赖 | 私有提案；无经审定 span，无新 overlap 阈值 |
| 结构/意图/家族 | 能否恢复带权分组目标 | 能否恢复选点目标及逐边覆盖约束 | 科学标签 null；ADAPTATION 有待核查代数表达 |
| Practical / 决策 | 负载、编码、系数精度、资源缺失 | 负载、惩罚缩放、资源缺失 | null；不得按 missing 自动判 NO 或 YES |
| 条件 HOW | 变量、目标符号、解码、精确性、并列解 | 变量、约束、惩罚/可行域、解码、精确性 | 待将来按 D-014 单独评测；本次无模型计划 |
| 集成 | 端点校验、重复权重、名称/窗口顺序、不修改输入 | 校验、去重、名称/连接数、不修改输入 | 经典测试已实现 |
| 可行性 | 每个设备恰好属于一组 | 每条边至少有一个端点入选 | 需与目标质量分开；在测试中检查 |
| 目标质量 | 精确最大分数；诊断可记最优值减实际值 | 精确最小数量；仅对可行解记实际值减最优值 | 小域独立 oracle；未采用容差或近似通过线 |
| 完整语义 | 分数、指定并列分组、顺序、异常和效果 | 数量、指定并列集合、顺序、异常和效果 | 当前比较经典实现；未来同样验证迁移 API |
| 量子资源 | 编码/精度、比特、线路层级、深度/门、shots | 同左，加约束处理所需资源 | 未构建线路，字段未知；不测模拟器“加速比” |

`semantic_oracle` 是 DRAFT 描述，并未假装配置字符串可以自动执行测试。
未来可用现有 `SemanticOracles.register` 注册经过审查的 property hook，组合具体输入的
可行性、目标和全 API 检查；不要把 scalar objective hook 当作完整软件行为验证。
现在已可直接运行 classical tests，静态评估器不会自动运行这些文件。

## 反例思维：避免指标替代任务

- MaxCut：零权图任意分组分数都是 0，但原实现总选 mask=0；只检查分数会放过并列行为变化。
- 覆盖：三角形全选三点合法，最少只需两点；只检查覆盖性会放过目标错误。
- 三角形的任意二点都是最优解，但原函数返回输入序的前两点；只检查最优值会遗漏并列规则。
- “经典验证测得样本合法”无法证明没有更好的解；不能给 QAOA 样本自动盖精确最优章。
- 公共输入保留原函数名；它们可能让 WHAT/WHERE 更容易。当前两例验证构建路线，
  不足以回答模型在真实软件中发现未知候选区域的能力。后续可设计独立版本的命名消融，
  但本任务没有执行或自动批准该实验。

## 扩充前的人类审查

先审查合成业务规则与原计算结构是否自然对应、原函数边界/并列规则是否值得纳入研究、
来源许可及署名是否充分。随后独立标注结构、实用性、合同适用性及 candidate spans。
不要根据我们选择了 MaxCut/覆盖，就回填 TRUE；也不要将两例重复运行当作两个新问题。
没有修订任何既有 schema、评测算法、候选阈值、成功概率、标签或 benchmark split。
