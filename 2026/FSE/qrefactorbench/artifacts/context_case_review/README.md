# pilot-005 / pilot-009：软件上下文审查

日期：2026-09-21。**AI 辅助分析，不是独立人工标注或 ground truth。**
本次只审查现有案例的功能关系、来源与验证缺口；不改源码、公开要求、标签、
既有实验或评分。审查者看过 curator 文档，不能把本分析用作盲标或模型输入。

## 结论

两个案例都有实际影响程序行为的上下文，不只是无关代码填充；但都是
Codex 辅助合成材料，尚无真实应用来源、用户需求或生产工作负载证据。
它们适合研究软件上下文层的最小组织方式，不能据此宣称覆盖真实软件迁移。
“有功能上下文”“来自真实项目”“有代表性”“有量子收益”需要分别取证。

| 项目 | pilot-005 | pilot-009 |
|---|---|---|
| 当前功能 | 判断可用 offer 的某个子集能否恰好达到数量目标且不超预算 | 求任务左右放置的精确最低成本，并返回名称和数量 |
| 调用链 | handle_request → prepare_offers → feasible_bundle → response | placement_report → validate_jobs → best_cost → report |
| 规模 | program.py 18 行 + support.py 3 行 | program.py 18 行 + support.py 6 行 |
| 有实际意义的上下文 | 筛选改变候选集合和答案；计数反映筛选后集合；不改调用方输入 | 校验规定异常；原顺序 names 和 count 是输出；links 依赖位置索引 |
| 拟议内核边界（非新标注） | feasible_bundle，第 4–12 行；循环第 5–11 行 | best_cost，第 4–12 行；循环第 6–11 行 |
| 主要不足 | sku/available 类型未完整定义；排序的外部必要性不清；只返回可行性 | left/right 的应用含义、成本来源和工作负载未知；只返回成本而非放置方案 |
| 来源 | 原创 synthetic / Codex-assisted；许可与独立审查待完成 | 同左 |

来源：[005 源码](../../cases/pilot/pilot-005/program.py)、
[辅助函数](../../cases/pilot/pilot-005/support.py)、
[公开合同](../../cases/pilot/pilot-005/public_task.json)、
[来源说明](../../cases/pilot/pilot-005/CURATOR_NOTES.md)；
[009 源码](../../cases/pilot/pilot-009/program.py)、
[辅助函数](../../cases/pilot/pilot-009/support.py)、
[公开合同](../../cases/pilot/pilot-009/public_task.json)、
[来源说明](../../cases/pilot/pilot-009/CURATOR_NOTES.md)。
“报价组合”“任务分配”只是便于阅读的功能描述，不是已经核实的应用部署背景。

## 005：可用性筛选是任务的一部分

示例 offer：可用的 a（1 单位、价格 1）、b（2 单位、价格 3），不可用的 c
（3 单位、价格 0）。请求数量 3、预算 3：

- 正确流程筛掉 c，结果为 `{"feasible": false, "considered": 2, "target": 3}`。
- 直接把原列表交给内核，会选中 c，得到 `true`。

因此，迁移时即使内核的子集判定完全正确，只要接入错误的数据，也会产生错误的
应用结果。这里的前处理是语义依赖，不能当作可删的装饰。

条件方案所需的计算对应很明确：每个经过筛选的 offer 对应一个选择位，检查
`sum(units_i*x_i)==target` 且 `sum(price_i*x_i)<=budget`。这只是用于审查的
映射说明，不赋予结构/实用性新标签。存在性返回精确 bool，仍需处理无解认证。

`prepare_offers` 还复制字典并按 sku 排序。对正常类型、可比较 sku、无自定义
副作用的输入，完整子集枚举的存在性、计数和 target 不因排列而改变；现有返回值
也没有被选子集或排序后的 SKU。保持不修改输入，不要求每个实现都复制同样的对象。
但公开合同明确说保留 sorting，所以不能擅自删除。需要研究者澄清：
sorting 是刻意保留的额外过程约束，还是被误写成外部语义的实现细节？
辅助函数是否独立对外公开、sku 类型/可比较性是否有保证，也应明确。
混合类型等未规定输入的异常行为不能由此分析自动决定。

[现有测试](../../cases/pilot/pilot-005/test_program.py)覆盖真/假返回、筛选、
基本报告字段、不修改输入和空请求；没有单独检查排序的外部用途、重复 SKU/
重复 offer、零数量/零价格组合的完整范围。通过这些测试不等于通过完整迁移验证。

## 009：异常、索引和输出都必须接回去

两个任务的 left_cost=0、right_cost=2，若放同侧需付 penalty=5，精确最低
成本是 2。返回的是 `{"cost": 2, "names": [...], "count": 2}`，不是任务的
放置位串。量子内核若返回位串，仍需经典解码、成本复算以及精确最优性认证。

`validate_jobs` 在计算前执行：名称不是字符串、关联索引越界、负 penalty
均触发 ValueError。只接入一个数学上正确的优化器，而遗漏这些异常，也没有
保留现有 API。若内部为编码重排 jobs，需要同步重映射 links，并保留返回 names
的原始顺序；这是待实施方案必须说明的义务，不是当前代码已出现的错误。

[现有测试](../../cases/pilot/pilot-009/test_program.py)覆盖一个带 link 的精确
结果、空输入、无 link 和越界异常。它没有覆盖名称类型/负 penalty 的错误分支，
也未专门用非字母顺序 names 检查报告顺序。这些行为本次用原代码做了少量探查。
先前[目标函数审查](../plan_mapping_audit/README.md)另外检查了重复项、自环和
常数；那是有界算术证据，不是新混合实现的集成测试。

该案例的上下文义务比 005 的排序更直接可观察，适合作为下一版案例组织的
结构参照。但两侧代表什么、同侧惩罚来自什么实际约束、为何用户只要最小成本，
仍然没有来源证据。不能把它描述成已经存在的调度系统或真实业务应用。

## 对 benchmark 的具体建议（待讨论，不是新协议）

1. 保留两个 DRAFT 案例作为合成功能上下文原型，不宣称真实来源或独立验证。
2. 若要画一个端到端案例结构图，优先用 009：输入校验 → 内核 → 解码/精确性
   义务 → 报告。理由是外部行为清晰，不是量子优势更大或 WHERE 已经足够难。
3. 两例的内核仍很显眼；多文件本身不代表具备有挑战性的区域发现任务。当前
   证据不能说明模型能在未知实际应用里发现迁移机会。
4. 下一步优先核查 C2|Q> 的少量实际样本、测试与输出边界，形成来源/任务重叠
   对照，然后再确定一个来源可核实的小程序候选。不要先批量生成更多 wrapper。
5. 新上下文应能回答“删掉/接错它会破坏哪个实际要求”，并为该要求提供测试。
   这是案例设计建议，不是已批准的排除标准或自动评分规则。

本次不选择业务领域、不伪造背景、不扩数据集、不改变原合同。
未知工作负载、编码成本、量子资源和强经典替代方案仍不能支持实际优势判断。

## 实际验证与复现

使用已有 palqo Python；不安装依赖、不运行模型或真机。

```bash
/home/audrey/miniconda3/envs/palqo/bin/python artifacts/context_case_review/check_context.py
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q -p no:cacheprovider cases/pilot/pilot-005/test_program.py
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q -p no:cacheprovider cases/pilot/pilot-009/test_program.py
```

每个测试文件分别 **1 passed in 0.01s**。分进程运行避免两个目录的同名
`program`/`support` 导入相互干扰。[005 日志](pytest_005.txt)、
[009 日志](pytest_009.txt)、[原代码行为探查](observations.json)。
这些是经典代码检查，没有执行或验证新的量子迁移。
717 个受保护文件保持不变；[验证记录](validation.json)与
[修改前哈希](before_hashes.json)。未修改 benchmark 实现，因此未重跑全套测试。
