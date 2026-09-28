# 现有案例的语义验证链 v0.1（N-039）

本次实际交付：**10 题配套契约；4 题的局部判定链已运行对照验证；其余 6 题仅完成
契约整理。** 不新增母案例，不修改模型任务、暂定标签、公开输入或历史成绩。
当前仍是机会识别与条件映射方案任务，不要求生成可执行迁移。

## 修改与实际结果

| 案例 | 本版检查的主张范围 | 测试输入 | 正确／等价对照通过 | 错误对照被拒绝 |
|---|---|---:|---:|---:|
| lit-002 顶点覆盖 | 直接目标的全部 ground states 是否满足覆盖、最小基数、tuple tie 及解码 | 6 | 2/2 | 3/3 |
| lit-004 最大团 | 直接目标的全部 ground states 是否满足兼容、最大基数、numeric-mask tie 及解码 | 5 | 2/2 | 2/2 |
| lit-005 布尔搜索 | 所有赋值的标记谓词；核心的字典序首解／无解 | 7 | 2/2 | 3/3 |
| lit-008 XOR 回执 | 有效请求上的完整、确定、有序报告主张 | 5 | 2/2 | 2/2 |
| lit-001/003/006/007/009/010 | 契约与旧证据已索引；没有本版自动主张判定器 | — | 未运行 | 未运行 |

lit-008 的测试验证软件行为义务，不产生“绝对不可量子化”标签，也不是端到端迁移
验收。前三题的检查同样不覆盖完整上下文、量子电路或求解器成功概率。
**4/10 是具有经对照检验的局部判定器的比例，不是模型整题通过率。**

- [契约与 23 条测试](contracts.json)：原始合同、任务层级、提交要求、允许的等价表示、
  判定来源、每条输入/预期/错误类型、未定标签及原输入 SHA256。
- [独立 oracle](oracles.py)、[判定器](evaluate.py)、[18 个对照的构造](controls.py)、
  [运行入口](run_controls.py)、[回归测试](../../../tests/test_semantic_verification.py)。
- [实际结果](../../../artifacts/semantic_verification_v01/after/evidence/results.json)、
  [完整对照输入](../../../artifacts/semantic_verification_v01/after/evidence/controls.json)、
  [原文绑定的两条主张](../../../artifacts/semantic_verification_v01/after/evidence/reviewed_claims.json)。
- [审查与判定边界](AUDIT.md)说明加载路径、旧分数、隔离、随机性和未解决问题。

## 一个完整的修改前后例子

原题：lit-002 最小顶点覆盖，多个最小覆盖时选已选索引升序 tuple 的字典序最小者。
模型仍提交原 Phase-1 JSON 条件计划；这里没有添加给模型的新字段。

修改前，结构标签一致、计划存在都可成立，但旧评分的 `plan_correct/task_pass` 是 null；
它不会仅因出现 QUBO 就认定语义正确。已发现的错误只存在于专用脚本和审核记录中。

现在将 Pro 的具体公式主张绑定到原回答 `/plan/formulation`、原文和 SHA256，显式登记
审查者选择的 A=1、P=10、C=1/32。私有转录只是数据，不执行模型 Python。

输入 n=4、E={(0,1),(0,2),(1,3),(2,3)}，独立定义 oracle 得出 `(0,3)`；
`tuple_not_mask` 测试精确枚举全部 16 个赋值，发现原公式唯一最优解为 `(1,2)`，
能量 35/16。报告 `candidate_error / canonical_selection`；覆盖和最小基数没有失败。
可信修复构造与经过变量反转、位取反、目标变换的等价构造通过同一测试。
另一个 `single_edge` 测试拒绝 Flash 的正超递增权重分支。

原回答的条件、其他分支、经典验证或回退仍保留；这两条反驳不等于整个计划失败。
转录的忠实性也不是哈希能证明的，Flash 尤其保留“正权重正加到选择位并最小化”解释限定。

## 判定器的使用边界

`evaluate.py` 接收**私有审核者主张转录**，不是替代模型的原提交 schema。表达式仅支持
数据化的精确二次多项式、显式双射解码、谓词真值表和报告示例，不执行任意候选代码。
每份转录必须声明检查范围；只声称核心最小基数、另有规范化或回退的方案，不能强塞进
`direct_canonical_ground_state` 范围。其他家族、辅助变量和尚无转录的文字保留待审。

固定测试来自私有契约，提交者不能自行指定期望值、删测试再计通过。
所有 ground states 都要解码正确。变量重排/取反、常数偏移、正比例缩放和负比例缩放
同时反转优化方向均允许；输出规范化合同不因此放松。谓词正确但缺少首解构造，保留
`predicate_pass=true` 与 `insufficient_evidence`，不伪造完整通过。

状态分为 passed、candidate_error、invalid_format、candidate_budget_exceeded、
infrastructure_error、insufficient_evidence、not_run、review_budget_exceeded。
最后一项是验证器枚举预算不足，不是模型超预算；原始诊断和逐测试状态均保留。
最多 8 个二值变量/256 个项是本地检查预算，不是原题新增输入上限。
全部有限检查使用精确整数/有理数，无浮点容差、采样或固定随机种子假装稳定。

每个报告保留 10 个母案例的分母，同时报告提交数、至少执行一次检查的题数、全部检查
执行数和局部通过数。`task_pass`、迁移执行、实际收益始终未判定。格式与解释不能抵消
语义反例；工程合成对照和真实模型的两条历史主张分开保存，不汇总为模型成绩。

## 正确对照的依据

顶点覆盖：令 A=2^n、R(x)=sum(2^(n-1-i) x_i)、P=A*n+1，最小化
`A*k(x)-R(x)+P*U(x)`。因 0≤R≤A-1，基数差优先；同基数下最早不同位置的选择位为 1
获得更大 R，正好对应所需 tuple 顺序。非惩罚项非负且可行值≤A*n，故 P 足够排除不可行解。

最大团：最小化 `-A*k(x)+M(x)+P*V(x)`，M 为 numeric mask、V 为被同时选择的非边数，
A、P 同上。不可行能量≥1，空团能量为 0；同层最小 mask，跨层优先最大基数。
这些指数权重的构造用于精确有限检查，不证明硬件精度、资源可用或实际量子收益。
两个构造及等价表示另在 n=0..4 的全部 76 张简单图上各自检查。

搜索对照按所有子句与锁定值的合取建立标记，再对解码后的布尔向量排序选首解；
与独立 oracle 的拒绝条件枚举核对，并和原可信经典内核核对。
XOR 对照使用位异或，独立 oracle 逐位用不等关系计算；完整回执再与原程序核对。
这些是审查者编写的测试对照，不是 LLM 金标或独立专家注释。

## 复现与验证

在仓库根目录，使用已有环境，无需安装：

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -B -m pytest -q -p no:cacheprovider tests/test_semantic_verification.py
# 实际：42 passed
/home/audrey/miniconda3/envs/palqo/bin/python -B -m pytest -q -p no:cacheprovider tests
# 实际：139 passed, 15 skipped
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/semantic_verification/v0.1/validate.py \
  --output /tmp/qrefactorbench-verification-new \
  --before artifacts/semantic_verification_v01/protected_before.json
```

输出目录必须不存在；脚本拒绝覆盖结果。最后一条展示复现到新目录的方式，本轮实际
输出是 `artifacts/semantic_verification_v01/after`，完整命令、stdout/stderr 和退出码见
[validation.json](../../../artifacts/semantic_verification_v01/after/validation.json)。
修改前的[基线命令与结果](../../../artifacts/semantic_verification_v01/baseline.json)：
主套件 97 passed/15 skipped；其余七组分别 24、4、12、37、15、11、9 passed。
修改后七组结果不变。15 个跳过源于 palqo 缺 Qiskit/PyYAML，本轮未运行这些可选测试，
也未运行量子实现。1636 个受保护旧文件 SHA256 全部不变。

这批输入和反例已暴露于开发过程，是回归测试，不是新建或冻结的隐藏保留集。
没有新模型调用、QPU、依赖安装、Git 提交、推送或外部操作。
