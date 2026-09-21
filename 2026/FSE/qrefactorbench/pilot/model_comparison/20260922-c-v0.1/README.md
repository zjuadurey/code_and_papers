# 两个 GPT 模型的 C 条件首轮测试

2026-09-22 用户授权：“用当前benchmark跑一下llm测试，给我一个小报告”。
执行范围继承此前方案：gpt-5.6-sol、gpt-6-astra，各 10 个当前案例的 C 条件，
每题一次，全新上下文，总计最多 20 次案例调用。仅现有 ChatGPT 订阅登录。

已完成 20/20 次首次调用，20/20 输出验证通过。结果见 [小报告](REPORT.md)、
[机器摘要](SUMMARY.json) 和 [逐例 AI 初审](CONTENT_REVIEW.md)。全部科学标签仍待审。
[实际验证](validation.json) 包含离线重算、输入/原始输出指纹、319 个受保护文件与
文档链接检查；[产物指纹清单](ARTIFACT_HASHES.json) 固定本轮交付文件。

## 运行前固定方案

- 输入：reference_completion/v0.1.1 的十份 C txt，逐字节验证并复制；不给位置提示。
- 参考：provisional_labels/v0.1；全部 DRAFT/PENDING，不修改标签或主 evaluator。
- 模式：Restricted Codex CLI 0.155.1，两个模型均 medium，非 Ultra；最多两个请求并发。
  每个母案例两个模型各运行一次，再进入下一母案例；没有科学重试、修复或反馈。
- 单次超时 600 秒；记录 CLI 原生重连，禁用 unbounded retries；不配置 API key。
- 输入经 stdin 提供；不启用 output-schema 强制解码，保留原始 JSON/非 JSON。
- Bubblewrap 挂载白名单沿用历史 baseline：系统运行时、只读现有订阅认证文件、
  单份公开输入和单次输出目录。研究仓库、标签、其他案例/答案、用户配置/历史均不挂载。
  HOME 保持主机原值，命名空间内该位置是临时空目录；不复制或记录认证内容。
- 禁用 shell、exec、web、apps、plugins、hooks、memory、delegation 等工具；保留同一
  developer wrapper。Codex 内置系统脚手架仍存在，不能称 raw API 或纯裸模型评测。
- 事前本地 preflight 验证登录、模型可见上下文和挂载隔离；不重复 smoke 推理。
- 完成后严格解析/schema/坐标验证；缺失/无效原样保留并报告。若某模型未完整通过输入
  验证，原评分入口的全量分数不可用，不把删题后的结果当作十题成绩。
- WHERE 精确匹配/行重叠仅是诊断；结构标签 7 个已知 YES、3 个未定；计划覆盖以 7 个
  参考 YES 为分母。采用建议一致不能单独用于排名；不生成整题通过率或综合排名。
- 内容审查由当前 Codex 协调者事后完成，明确标记 AI 初审、待研究者复核，非独立专家评审。
- 单次样本用于探索；不作稳定模型排名、显著性或量子优势结论。A/B 未运行。

## 产物

`protocol.json` 固定输入和参考指纹；`preflight/` 保存事前机械检查。
`runs/<model>/<mother>/` 保存请求元数据、events、stderr 和原始 response。
`predictions.<model>.json` / `evaluation.<model>.json` 是无修复的收集与暂定诊断。
完成后的 `REPORT.md` 为小报告，`SUMMARY.json` 为可复算数据摘要。

执行使用已有 palqo 环境。`run.py prepare` 和 `run.py preflight` 不做推理；
`run.py run` 消耗订阅额度，只执行尚无 started 标志的整轮初次运行，拒绝覆盖/重跑。
脚本保留用于审计，不构成未来重复运行的许可。
