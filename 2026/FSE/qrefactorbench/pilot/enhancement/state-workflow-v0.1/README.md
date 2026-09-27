# N-045：单模型分析／验证工作流的离线初版

2026-09-25。用户委托选择并推进方法，本版落实“动态状态前提检查”的第一步。
**已经运行本地分析、组装四条修订输入并检验信息开关；没有新模型调用或能力提升结论。**
入门解释见 [学习笔记](../../../docs/AGENT_WORKFLOW_LEARNING.md)，授权范围见
[D-032](../../../DECISIONS.md#d-032-delegated-workflow-development-with-stepwise-explanation)。

## 本次实现与效果

[workflow.py](workflow.py) 有三个小部件，均使用 Python 标准库，不导入模型 runner。

1. `analyze_source`：根据候选函数/源码行，解析 AST，收集变量相关赋值、数组根对象更新
   与包围它们的控制语句。会保留后续循环更新，帮助看见下一轮候选使用的状态。
   本例列出 12 条语句，包括第 11 行 rows 构造、第 18 行 factor 和第 20 行 rows 更新。
   **这是词法依赖清单，不是严格程序切片、范围分析或可达性证明**；变量名复用会让回代等
   语句也进入清单，不追踪别名、跨函数副作用或完整调用前提。没有自动证明 finite 不变式。
2. `bound_feedback`：核对响应哈希、formulation 原文和 N-044 轨迹，再提取开发反例。
   反馈只给输入、失败时列值、两种文字解释与原程序结果；不提供修复公式、顺序扫描对照或
   详细依赖清单。新响应无匹配的审核绑定就返回 `insufficient_evidence`。
   本版只支持这条已审核主张，没有通用自动文字裁判。
3. `revision_prompt` / `prepare_demo`：同一历史初稿生成 S/A/V/AV 四个单次修订分支。
   公共指令完全相同，只改变 observation 数组；不发送分支名或“隐藏了结果”提示。
   每支保留输入hash、事件记录、调用上限与 `awaiting_model_not_run` 状态。

旧 C 输入保留为嵌入快照。外层明确这是新修订协议，允许读取附加观测，原来“不请求反馈”
约束适用于初次回答；仍禁止模型执行代码/调用工具、保留 Phase-1 schema 与软件合同。
因此它不是原单轮 baseline 的重复打分，也不是已实现的模型自主选工具 Agent。
分析/反馈在固定工作流里由程序选择，下一步模型修订由未来的显式运行协议承载。

输出：[分析清单](demo/analysis.json)、[开发反馈](demo/development-feedback.json)、
[四分支摘要](demo/summary.json)。例如 [AV输入](demo/analysis_and_verification/prompt.txt)
可以直接阅读，查看模型将看到的确切材料；这个离线输入没有发送给模型。

| 分支 | 观测 | 本次模型调用 | 模型修复结果 |
|---|---|---:|---|
| S | 无外部观测，仅原任务与历史初稿 | 0 | 未运行 |
| A | 词法依赖清单 | 0 | 未运行 |
| V | 审核绑定的开发反例 | 0 | 未运行 |
| AV | 两者 | 0 | 未运行 |

没有伪造修订答案。`experiment_completed=false`、`effect_on_model_quality=null`。
计时仅涵盖本地分析/归档反馈选择/输入生成，不包含历史追踪成本，更不代表模型总成本。

## 对照与消融的下一阶段设计

当前架构选择：D初稿＋S/A/V/AV四个修订条件，固定同一个模型，保持原C任务及输出格式。
比较 AV−V 看分析在验证之外的增量；AV−A 看验证增量；A−S、V−S看各自作用；
AV−A−V+S可作为描述性组合效应。不能凭一次正差宣称统计显著或组件因果贡献已确立。

四条修订共享同一初稿，独立上下文各一次，不互相看答案；轮换分支执行顺序。
若沿用探索性的5组初稿，将需要5＋4×5=25次新调用，**多于N-044三条件草案的15次**。
25是待确定的运行预算，不是本轮调用授权；初稿全对也不挑错题、不加采样制造收益。
5组不是5个独立程序，测试矩阵个数也不能变成独立模型样本。

应分别保存输出有效性、映射主张的有限检查、条件/回退完成度、修复与退化、经典工具时间、
模型token/延迟。D只有一次调用，不能把AV优于D全归于工具；S/A/V/AV次数一致仍非等token。
A只是重组原源码已有信息，V引入开发oracle提供的证据，二者不是等价信息预算。
V含候选位置/失败值等必要语义信息，因此消融测的是两个已定义工具输出包的增量，
不能声称完全隔离了抽象意义上的“分析”与“验证”所有认知成分。

下一步实现新响应的显式主张绑定和独立最终评测接口：同义/等价表述不自动判错，
不能转录者保持未知，修复/合理缩小条件/撤回主张分开记录。模型反馈只用开发证据；
最终评测不进入提示。本版尚未建新最终集，不能称已通过保留集验证。
旧5×5与6×6见证均已暴露；新矩阵仍属同母案例，不是跨程序泛化证据。

## 材料借鉴和边界

按用户提供的 [ai-agent-book](https://github.com/bojieli/ai-agent-book) 阅读了第1、7、9章
及相关实验说明；锁定提交 `04c88c53df962eb4375a0fad9ec041066529b358`。
[source_manifest.json](source_manifest.json)记录读取文件的路径和hash；没有复制其实现、
安装依赖或运行书中模型实验。学习笔记给出固定版本的具体引用与我们采用/保留的判断。
书是工程与教学参考，不是本研究有效性、标签或创新性的证明。

## 实际验证

在仓库根使用已有 palqo：

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -B -m pytest -q -p no:cacheprovider pilot/enhancement/state-workflow-v0.1/test_workflow.py
# 12 passed
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/enhancement/state-workflow-v0.1/workflow.py --output /tmp/qrefactorbench-state-demo-new
# 4 branches prepared; 0 model calls; output must not exist
```

本次实际输出为 `demo/`。测试覆盖循环状态/数组更新、源码仅解析不执行、候选坐标拒绝、
新主张保持未知、反馈不夹带修复对照、四个观测开关、共同初稿、未运行状态与拒绝覆盖。
共享 evaluator/源码/旧实验未改，主套件未重跑。
[validation.json](validation.json)保存真实验证、链接及2347个旧文件完整性记录。
未安装、提交/推送、运行模型或QPU；论文及旧结果保持原样。
