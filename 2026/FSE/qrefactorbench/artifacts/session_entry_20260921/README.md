# N-032 — 新对话入口整理记录

2026-09-21；纯文档工作，无实验或科学标签变更。当前状态仍只在
[PROJECT_STATUS](../../PROJECT_STATUS.md)，本目录是证据归档。

## 做了什么

- 在 FSE/ 增加转到 qrefactorbench/ 的 AGENTS 入口；项目入口明确区分“读取当前目录”
  （只读恢复与汇报）和“继续”（推进已授权安全任务）。不启动另一模型来测试入口。
- 状态从527行、短队列从212行压缩，历史原文保留如下；不删除旧任务或实验记录。
- 研究纲领增加中文初始意图摘要：帮助非量子专家、选择性迁移、原软件合同、长期收益，
  及 benchmark 如何支撑研究。摘要不是伪造的逐字聊天档案。
- 当前案例包与历史冻结 baseline 输入分开，版本表集中在状态文件；README 历史
  collector 示例明确限定旧 pilot，避免误用于新 A/B/C 条件。
- 工作规程增加文档同步表和交付前检查，不引入依赖或自动语义一致性保证。

## 完整原文归档

下列是整理前的**逐字节副本**，用 .txt 保留历史 Markdown；内部相对路径按原项目根
或原 docs/ 位置理解，不作为当前导航或执行队列。

- [旧项目入口](before/AGENTS.md.txt)
- [旧完整状态（527行）](before/PROJECT_STATUS.md.txt)
- [旧完整队列（212行）](before/NEXT_ACTIONS.md.txt)
- [旧 README](before/README.md.txt)
- [旧研究纲领](before/docs__RESEARCH_CHARTER.md.txt)
- [旧工作规程](before/docs__CODEX_WORKFLOW.md.txt)
- [原文件哈希和长度](before.json)

## 新对话预期恢复的事实

1. 研究目标：已有软件的 WHERE/WHETHER/HOW，选择性混合重构，默认保持原软件合同。
2. 当前阶段：Phase 1 benchmark/task validation，不是全功能 Agent 或冻结 benchmark。
3. 当前集合：十组来源母案例、30个 A/B/C 条件，修订版 reference_completion/v0.1.1。
4. 已有实验：旧 pilot 一次 Restricted Codex CLI baseline＋一次受控诊断；非两个独立 baseline。
5. 下一步：人类确认当前案例与评审口径后，明确下一次实验配置/授权；不先扩案例或重复修复。

## 验证与限制

[validation.json](validation.json) 记录原文归档、1383个受保护文件哈希、入口路径、
本地 Markdown 链接/锚点和两层阅读链的静态检查。校验源码为 [check_docs.py](check_docs.py)，
命令为 `python -B artifacts/session_entry_20260921/check_docs.py`（项目根目录）。
首轮发现本页链接的 validation.json 尚未生成，输出首轮报告后该目标已存在；
首轮记录保留为 [validation_initial.json](validation_initial.json)，再次检查确认全部路径。
检查不会判断所有文字语义是否一致，也不保证任何未来会话绝不会漏读；未调用新模型。
没有重跑 Python/Qiskit 套件；状态中的73/97/5通过数均明确指向上轮真实日志。
未改 case、schema、evaluator、预测、旧输入包或原研究决策正文；未暂存/提交/推送。
