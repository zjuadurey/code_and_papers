# 四组参考案例：补齐搜索与保持经典的对照

2026-09-21 · **DRAFT / AI 辅助策展，不是科学金标准。**

研究者要求先打磨参考样例再考虑十几份扩展。本轮增加两组，汇合原两组，形成
**4 个母问题、8 份核心/功能上下文视图**。这些是配对设计，不是 8 个独立来源问题。
原 v0.1、源程序、旧 pilot、模型结果与科学标签不变。没有新模型或量子实验。

## 明天从这张表开始

| 母问题 | 第一层 | 第二层及真正依赖 | 最重要的审查点 |
|---|---|---|---|
| 设备维护 | core-001：加权分组 | context-001：当前/建议冲突、设备移动 | 软偏好；近似比例已定、阈值未定，旧精确合同仍保留 |
| 连接检查 | core-002：端点覆盖 | context-002：漏检、逐站任务、任务移交 | 硬覆盖不能因“近似”而漏掉；最少站点和并列规则仍精确 |
| **配置兼容性** | [core-003](core_specs/core-003.json)：布尔约束存在性 | [context-003](cases/context-003/program.py)：命名规则、固定设置、逐方案检查与汇总 | 部分设置之外的选项仍可自由补全；未找到不能直接声称不存在 |
| **批次封存对照** | [core-004](core_specs/core-004.json)：有序摘要与审计 | [context-004](cases/context-004/program.py)：整批校验、规范编码、逐条检查点、组件回执 | 最终摘要相同仍不够：所有回调顺序和异常行为也是合同 |

前两组代码和四份公共材料逐字复用 [v0.1](../v0.1/README.md)，没有重写。
本轮新增两个 context manifest；核心视图复用已有 pilot-001/002 源函数。
分组/文件 hash 见 [PAIR_INDEX.json](PAIR_INDEX.json)，当前核函数逐字对应已测试。
“搜索候选”和“保持经典对照”是策展目的；新 case 的结构/实用/支持/决策/意图/家族
字段仍全为 null。暂定 positive/hard_negative 分类满足旧 schema，不是审定标签。

## 配置方案兼容性：从功能需求理解

应用的可选功能存在依赖、互斥和“至少启用一项”的要求。不同部署方案固定部分开关，
管理员需要知道每个方案是否还能补全为合法配置，而不是要求系统随意挑一个配置。

```text
功能目录、依赖/互斥/组选项规则、多个部分配置
  → 校验全部名字、规则和方案（包括后面的非法记录）
  → 命名规则转换、合入各方案的固定开关
  → 分别判断是否存在完整配置
  → 按原方案顺序报告结论、固定/未固定选项及兼容/不兼容 ID
```

[实际例子](cases/context-003/example_request.json)：sync 要求 encrypted，sync 与 offline
互斥，同时至少启用 sync/offline 之一。[报告](cases/context-003/example_report.json) 为：

- `connected` 固定 sync：兼容，因为 encrypted 可由未固定状态补为启用。
- `conflicting` 同时固定 sync/offline：不兼容。
- `offline-only` 固定 offline 并关闭 encrypted：兼容。

忽略固定设置会把冲突方案错判为可行；反转依赖方向会改变合法配置；把未固定当成
关闭会误拒绝合法方案；返回结果串错 profile_id 会误导操作。它们都是真实功能后果。
空组表示不可满足，空规则允许空配置；重复规则合法。没有为模拟方便新增功能数上限。
详见 [公共合同](cases/context-003/public_task.json)。

**条件量子化提案（私有、待审）：** 候选在有限配置判定，命名映射/固定设置和报告留在
经典侧。用赋值作为候选、合取规则作为判定条件，是可讨论的搜索映射入口。还必须明确
可逆谓词/辅助位、构造成本、未知解数、失败与无解的区别，以及最终精确 bool 合同。
本轮只验证经典规则转换与功能衔接，没有实现或验证量子 oracle，也没有实用性结论。
维护案例的近似质量许可不允许在这里随意接受错误 True/False。

## 批次封存：为什么值得作为保持经典的对照

假设性功能：为一批变更记录生成可重算的摘要回执，并按顺序向调用者提交每条记录的
检查点，以便调用者记录进度或拒绝继续。输入含批次 ID、事件 ID、组件和消息。
这是摘要/审计接口示例，不是数字签名或真实外部账本提交。

```text
变更事件批次
  → 全量校验（任何后续非法事件都必须在首次审计前发现）
  → 规范 JSON 编码，保留事件次序，按组件计数
  → 每次以前一个摘要与当前事件生成新摘要，并立即调用审计
  → 若回调成功完成则返回批次回执；若抛异常则原样传播、停止后续调用
```

[例子](cases/context-004/example_request.json) 有 api、worker、api 三条变更。
[实际 CLI 报告](cases/context-004/example_report.json) 含 api=2、worker=1 的汇总及三个
不同检查点。回调可以产生调用者可见效果；CLI 为了本地演示只在内存收集，不写外部服务。

**对照假设（待审）：** 该合同要求有序消耗所有记录和发出所有检查点，当前没有识别出
与两种受支持迁移合同匹配的候选。不能因为看到循环或哈希运算，就强行把任务改成
“找到一个事件”或“求哈希原像”。这不是关于所有量子算法都不可能改善它的证明。
WHERE 可以讨论可疑循环，WHETHER 再据合同拒绝；不强制把空候选当成唯一正确标注。

具体语义风险：排序/并行分块后重排检查点、只给最终摘要、在校验到一半就调用审计、
吞掉回调异常、失败后继续处理，都可能返回看似合理的回执却违反原行为。
详见 [公共合同](cases/context-004/public_task.json)。

## 来源、评测和材料边界

新两个核函数来自本仓库已有 **Codex 辅助合成 pilot-001/002**；不是新找到的顶刊
代码或真实业务系统。新上下文同样是明确标注的合成需求。外部来源 null，许可证
NOASSERTION，不把前两组的 CC-BY 声明套用过来。[来源记录](provenance.json) 保留
源文件/函数 hash，未复制原科学标签。未来划分还需与旧 pilot 同 lineage 成组。

新测试采用：

- 配置：直接在命名规则上计算真值表，不复用编译出的 clauses；139 组小规则目录、
  1,163 个部分配置判断，另查 17 功能合法输入、空域、重复、非法后缀和报告顺序。
- 封存：121 种事件序列的完整回执和回调轨迹；独立固定编码字节检查、回调异常对象
  与已执行前缀、全量校验先于效果。错误替身证明“摘要正确但漏掉审计”仍不合格。
- 两层：核函数逐字一致、导出可重复且拒绝覆盖、原四份公共材料不变、新导出程序能
  在临时目录独立运行。源码命名仍显露结构，不能声称已证明 WHERE 更难。

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q pilot/reference_cases/v0.2/cases/context-003/test_program.py
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q pilot/reference_cases/v0.2/cases/context-004/test_program.py
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q pilot/reference_cases/v0.2/test_views.py
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench validate pilot/reference_cases/v0.2/cases/
python pilot/reference_cases/v0.2/prepare_inputs.py --output /tmp/qrefactor-eight-views-new
```

测试文件按独立进程运行，遵循每例都使用自己的 program 模块的既有约定。
[review_inputs](review_inputs/) 有八份源码/公共合同及哈希清单，共 20 个公共文件。
只给模型单个视图，不给本 README、case.json、测试、示例答案、审查提案或配对答案。
公共要求必须保留规则/效果语义，不因它们透露结构就删除；未加入量子家族和类别提示。
本包不是新模型基线，未准备假预测。完整验证见 [validation.json](validation.json)。

实测：配置上下文 **37 passed**、封存上下文 **26 passed**、配对/导出 **5 passed**；
原两个核案例测试 **1/2 passed**，核心回归 **97 passed, 15 skipped**（可选依赖）。
新两个 DRAFT manifest 与原 14 案例均验证通过，JSON 汇总成功；867 个原有文件不变。
本轮未改量子实现，因此未重复可选量子套件，也没有安装依赖。

**下一步：** 用 [TOMORROW_REVIEW.md](TOMORROW_REVIEW.md) 审四组，再决定仿照扩展范围。
目前只完成参考样例，没有自动生成十几个案例或赋予科学金标准。
