# 本稿叙述的证据对应

以下路径以 QRefactorBench 仓库根目录为基准；不在压缩包中复制私有模型响应、参考答案或凭据。
本文只读取资料，未重跑研究实验。

| 论文内容 | 仓库依据 | 允许的陈述 / 边界 |
|---|---|---|
| WHERE/WHETHER/HOW、同模型增强 | `docs/RESEARCH_CHARTER.md`; `DECISIONS.md` D-030 | 已确认研究方向，不代表完整技术已实现 |
| 默认保留原合同 | D-015/D-017；`docs/task_definition.md` | 结构映射、全合同和采用判断分开 |
| 当前案例/输入版本 | `PROJECT_STATUS.md`; `pilot/reference_completion/v0.1.1/README.md` | 当前 DRAFT 包；不混旧 pilot |
| 来源与业务上下文 | `pilot/reference_completion/v0.1/README.md`, `COVERAGE.md`, `sources/manifest.json` | 来源可追溯的合成改编，不称真实部署应用 |
| A/B/C 与谱系 | 当前输入 README；`pilot/how_review/v0.2/HOLDOUT_DRAFT.md` | 同母条件不独立，现有母案例 development-exposed |
| 正确性/完成度双记录 | D-026；`pilot/how_review/v0.2/README.md` | 方法方向已接受，逐例判断仍待审 |
| 局部语义判定 | `pilot/semantic_verification/v0.2/README.md` | 检查有支持范围，不是通用文字判题或整题通过 |
| 数值可达 NaN 谓词问题 | `pilot/model_comparison/20260923-four-model-c-v0.1/REPORT.md` | 原程序可达反例反驳局部谓词；回退/整题另判 |
| 同模型模板反馈原型 | `pilot/enhancement/lit002-v0.1/README.md`, `REPORT.md` | 已实现局部闭环；既有记录无可观察提升，不能包装为有效增强 |
| source-fact / obligation 集成方法 | 本次写作提案，与 D-030 方向一致 | 未实施/未验证，不改变代码或已接受科学协议 |
| 6 RQ、8 实验、A/V/AV、统计计划 | 本次写作提案 | 待评审、配置、授权；不虚构执行和分母 |
| 精确 QUBO 公式 | 原型 README 的正确对照及论文推导 | 数学示例，不是本次模型实验结果或硬件可行性证明 |
| 量子收益、完整自动迁移、开发者收益 | 现有文档没有充分证据 | 不声称已建立 |

论文为可编辑设计稿；新标题和贡献措辞也仍需作者科学审核。
此次文档同步只记录写作交付，不把研究阶段改为最终 Evaluation，也不改 NEXT_ACTIONS 的离线审核任务。
