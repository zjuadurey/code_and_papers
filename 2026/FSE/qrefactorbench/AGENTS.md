# QRefactorBench — 每个新 Codex 对话的入口

目标：**FSE 2027 / 顶级软件工程研究**。帮助非量子专家理解已有经典软件，
发现候选计算、判断是否值得迁移、选择性重构并验证原软件行为。
长期追求有证据支持的端到端收益；当前做 benchmark 和任务验证。
Python → hybrid Python/Qiskit；正向家族仅 Search/Grover 与 Optimization/QUBO/Ising。

## Mandatory startup procedure for every Codex session

**Never assume that previous chat context is available. Reconstruct project context
from repository documentation. 用户不需要重述研究 idea。**

用户说 **“读取当前目录”／“了解项目”**：只读以下文件，然后汇报，不自动执行下一任务。
用户说 **“继续”／“推进”／“proceed”**：完成同一阅读链后，推进队列中的最高优先安全工作。

1. 本文件。
2. [研究纲领](docs/RESEARCH_CHARTER.md)：长期意图、当前范围、科学边界。
3. [PROJECT_STATUS.md](PROJECT_STATUS.md)：当前阶段、最新结果、版本与限制。
4. [NEXT_ACTIONS.md](NEXT_ACTIONS.md)：当前唯一短队列。
5. 读取状态所指的最新交付 README；据任务查看
   [DECISIONS.md](DECISIONS.md)、[工作规程](docs/CODEX_WORKFLOW.md)、[TODO.md](TODO.md)。
   **任何修改前必须读相关决策、工作规程及对应实现/测试。**

“读取当前目录”的输出保持简短：①研究目的；②当前阶段；③已完成及证据边界；
④当前工作包与历史实验的区别；⑤下一步及是否需要人类决策。不要只列文件名。
遇到文档/实现矛盾先核实并明确报告，不自行选一个当真。

## 科学与操作边界

- quantumizable ≠ worth quantumizing；热点 ≠ 量子机会；能执行 ≠ 语义正确。
  结构、条件计划、实际适用性、最终建议分别记录；允许 REMAIN_CLASSICAL。
- 默认保持原软件合同；近似许可必须显式、逐案例、版本化。未知保持未知。
- 不捏造 ground truth、不把 AI 提案升为 gold、不静默改变已接受决策。
  新家族、主指标、争议标签、论文主张、最终发布等需人类科学决定。
- 先 benchmark → baseline → failure evidence，再设计技术。默认不建 agent。
  未测 WHERE 难度不阻碍案例建设；难度是实验问题。
- 常规已授权的可逆工程直接做；不反复询问已记录信息。默认主线程，无子 Agent。
  读/审/解释任务只读；修改前检查相关 Git 状态，未跟踪文件也视为用户工作。
- 不覆盖历史输入/结果；修复建新版本。旧运行授权不等于新实验授权。
  未授权不安装、提交/推送、发布、付费或运行模型/QPU，不触碰凭据。
- 当前案例包与历史 baseline 输入的**唯一当前指针在 PROJECT_STATUS 的版本表**。
  `pilot/` 同时含私有答案、提案和结果，绝不能整体交给预测模型。

## 工程与文档完成条件

默认中文交流，类型明确的 Python，最小依赖，复用已有环境/测试；源码行号为 1-based inclusive。
`schemas/`、`cases/`、`qrefactorbench/`、`tests/` 为基础设施；`pilot/` 为案例/实验。
重大改动结束前按 [文档同步表](docs/CODEX_WORKFLOW.md#documentation-sync) 更新受影响文档：
当前状态/短队列、变更日志、局部 README、必要的决策或研究记录，附真实验证结果。
纯文档改动检查链接与旧材料完整性即可。只读问答不必改日志。
**没有检查文档同步就不声称任务完成；这是一项操作要求，不是已有自动 CI 保证。**
