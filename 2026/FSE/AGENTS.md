# FSE 工作区入口

本目录的研究项目在 [qrefactorbench/](qrefactorbench/)，目标为 FSE 2027。
当前论文编辑目录是 [paper/](paper/)，主文件 [main.tex](paper/main.tex)。
该目录由用户指定的论文目录重命名而来；不要改回旧名或继续编辑历史草稿副本。
不要把本目录当成空仓库，也不要在这里重新初始化项目。

新对话开始工作前，自动按以下阅读链恢复上下文；这是 Agent 的职责，
不要求用户提供文件路径、粘贴交接提示或重述研究 idea。
用户只需直接说任务，或说 **“继续”**。用户说 **“读取当前目录”** 时只读恢复并汇报。

阅读链：

1. [项目 AGENTS.md](qrefactorbench/AGENTS.md)
2. [研究意图](qrefactorbench/docs/RESEARCH_CHARTER.md)
3. [当前状态](qrefactorbench/PROJECT_STATUS.md)
4. [下一步](qrefactorbench/NEXT_ACTIONS.md)
5. [论文交接](paper/HANDOFF.md)；论文任务再读 [paper/AGENTS.md](paper/AGENTS.md)。

随后按项目入口规定简短汇报：研究目标、当前阶段、已有证据、当前版本、下一步。
这是只读恢复上下文的请求，不自动修改文件、跑测试或启动模型/真机实验。
用户说“继续”时才按项目队列推进已授权的安全工作。
无需用户重新解释研究 idea；不要用历史日志取代当前状态，也不要覆盖未提交内容。
研究状态以 PROJECT_STATUS 为准，论文编辑位置以 paper/ 为准；旧草稿和 latex.zip 是交付快照，
不会自动同步。论文中的拟议方法和实验不代表代码已经实现，也不授权新实验。
