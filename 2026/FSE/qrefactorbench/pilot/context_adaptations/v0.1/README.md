# 第二层案例：维护方案评估与调整

2026-09-21 · **DRAFT / AI-ASSISTED ADAPTATION — NOT GROUND TRUTH**

研究者同意在原 MaxCut 样例之上实现完整功能流程。新案例 `context-001` 单独版本化；
原 [lit-001](../../source_adaptations/v0.1/cases/lit-001/ADAPTATION.md) 不变。
这里的“第二层”表示增加真实数据依赖的功能上下文，不更改现有 context_level enum，
也不宣称已经证明 WHERE 更难。两个版本共享同一来源核心，不是两个独立来源任务。

## 从用户功能开始读

用户提交设备清单、希望分开维护的设备对及权重、当前两个时段的安排。
程序检查请求，评估当前冲突，计算建议安排，再输出哪些设备需要移动、哪些冲突被解决、
哪些新冲突被引入、哪些冲突仍然存在。建议供人工查看，不自动部署。

```text
JSON 请求
  → 全量校验设备/要求/当前安排
  → 名称映射与重复权重累加
  → 当前安排评分和冲突明细
  → 建议安排计算
  → 建议安排评分和冲突明细
  → 新旧差异、移动清单、解释报告
```

直接看 [入口 program.py](cases/context-001/program.py)，
[功能模块 maintenance.py](cases/context-001/maintenance.py)，
[完整公共合同](cases/context-001/public_task.json)。程序没有专门的 `kernel.py` 文件；
计算函数与评分/校验/比较函数一起放在维护业务模块中，没有人为混淆函数名。

## 跑一个例子

在仓库根目录：

```bash
python pilot/context_adaptations/v0.1/cases/context-001/program.py \
  < pilot/context_adaptations/v0.1/cases/context-001/example_request.json
```

示例三台设备原本都在第 0 时段：pump–fan 权重 4，fan–chiller 权重 3，
pump–chiller 权重 1。报告给出：

- 当前冲突权重 8；建议第 0 时段只有 fan，第 1 时段为 pump、chiller。
- 建议冲突权重 1，减少 7；移动 pump、chiller，顺序遵循设备输入序。
- 解决 pump–fan 与 fan–chiller 冲突；pump–chiller 冲突仍存在；无新增冲突。

检查 [example_report.json](cases/context-001/example_report.json) 可看到完整实际输出。

## 新增上下文为什么有用

| 部分 | 用户需要 | 删除或错误实现的后果 |
|---|---|---|
| 当前安排校验 | 每台设备必须恰好出现一次，两个时段可为空 | 漏设备、重复设备或未知设备会令评估/移动清单无意义 |
| 当前安排评估 | 知道原安排有哪些冲突 | 无法解释改善幅度及解决了什么 |
| 建议安排计算 | 精确减少冲突权重 | 仅返回可行分组不满足最佳分数要求 |
| 结果评估 | 从分组得到分数与正权重冲突明细 | 仅信任一个求解器自报分数可能掩盖解码/分组错误 |
| 差异报告 | 正确移动设备并了解代价变化 | 最佳分数正确也可能给出错误操作建议 |

本例没有加入容量、时长、人员或设备可用时间。**移动数量只是报告，不是优化目标**。
继承原函数的确定性并列规则：选择第 0 时段设备对应的最小 bitmask。因此旧安排已经
最优时，建议仍可能要求移动；改善为 0 不代表无需移动。此行为已明示并测试。
若之后希望“并列时尽量少移动”或“不改善则沿用原计划”，需要另行版本化合同，
不能悄悄把这些规则加到当前函数中。

## 来源与改编记录

- 上游：C2|Q>，Ye et al., [TOSEM DOI](https://doi.org/10.1145/3803018)。
  本地已保存的 [固定数据来源说明](../../source_adaptations/v0.1/SOURCES.md) /
  [原始第 164 条记录](../../source_adaptations/v0.1/sources/lit-001.row.json)。
- 原函数 `maxcut_bruteforce` **正文逐字保留**，从独立 kernel 移入 maintenance 模块；
  可定位行号、函数 SHA-256、CSV 版本/哈希见 [provenance.json](provenance.json)。
- 名称/权重校验沿用 lit-001 的逻辑并增加当前安排校验；评分、差异和报告是本项目
  Codex 辅助新增代码。整个情境是合成需求，未声称来自实际维护系统或原作者业务案例。
- 上游片段沿用 CC-BY-4.0 声明及署名，[许可](https://creativecommons.org/licenses/by/4.0/)；
  修改包括移除原示例运行、移动函数位置并增加应用代码。上游不被视为认可改编。
  新代码/整体包的发布许可仍为 NOASSERTION，没有发布或冻结行为。

## 测试与评测边界

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q \
  pilot/context_adaptations/v0.1/cases/context-001/test_program.py
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench validate \
  pilot/context_adaptations/v0.1/cases/
```

[测试](cases/context-001/test_program.py) 独立从命名请求与 Cartesian product 计算预期结果，
不调用生产矩阵构造/评分/求解/比较函数。0–4 点所有简单无权图共 76 个图，结合每个图的
所有当前分组共 **1,099 个请求**；另有 27 个重复/反向加权输入和具体边界用例。
这是一个 benchmark case 的测试输入数，不是 1,099 个 benchmark cases。

覆盖完整报告相等、异常、不修改输入、空输入、正权重冲突顺序、任意精度整数、
当前已最优但并列变更、新引入低权重冲突及 CLI。一个有意省略移动清单的 reporting
mutant 保留正确最佳分数，但被完整报告比较识别，展示“只测目标值”的不足。
有限测试不构成全域证明；没有量子程序或模型参与。

借鉴方法继续使用 [两例评测设计](../../source_adaptations/v0.1/EVALUATION_DESIGN.md)：
固定入口和执行测试；分开检查可行性、目标质量与完整软件合同；资源与收益另行评价。
本次没有自动注册 quantum oracle hook、增加统计阈值或修改 evaluator。

## 给模型/独立标注者什么

只有 public_task.json、program.py、maintenance.py；公共 prose 不指明替换位置、
量子算法或正负类别。用以下命令导出到新目录：

```bash
python pilot/context_adaptations/v0.1/prepare_inputs.py --output /tmp/qrefactor-context-review-new
```

已有 [review_input](review_input/) 是这些文件加哈希清单。不要分发本 README、case.json、
测试 oracle、provenance、原标注或旧模型答案。此目录是本地准备材料，非新 baseline；
外部分发时须处理保留来源署名/许可与可能产生的额外提示。原算法函数名在源码中仍可见，
不能宣称无任务线索。未预制任何模型预测。

## 待审查，不自动判定

- case.json 的 positive 是既有 schema 必填的采样提案，候选函数区间是私有提案。
  structural/practical/support/intent/family/decision 均为 null，annotation_status=DRAFT。
- 用小例子确认功能是否自然、固定并列行为是否符合研究需要；扩充上下文并非难度证据。
- WHERE 应包含求解函数、枚举主体还是其他依赖，仍需人工标注；未改最终定位度量。
- 与 lit-001 的共同来源应记录在未来划分/比较中，不能冒充独立算法或直接跨 split。
- 实用收益、量子编码资源、精确性保证和独立审查仍缺失；本任务不决定这些标签。

实测日志和旧文件保护检查：[validation/results.json](validation/results.json)。
