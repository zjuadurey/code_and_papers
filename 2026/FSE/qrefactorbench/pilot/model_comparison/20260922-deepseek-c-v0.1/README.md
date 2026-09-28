# DeepSeek Pro / Flash：当前 C 条件补测

授权：2026-09-22 用户“加上deepseek的 pro and flash”，继承当前十个 C 案例、每题一次。
共 20 次首次请求。用户另行指定本机密钥文件；密钥不进入消息、元数据或产物。

**已完成：20 次 HTTP 返回，Pro 有效 10/10，Flash 有效 9/10。** Flash lit-009
触及 token 上限、没有最终答案，保留失败且未重试。见 [四模型小报告](REPORT.md)、
[数据摘要](SUMMARY.json)、[AI 内容审查](CONTENT_REVIEW.md) 和 [实际验证](validation.json)。
[交付指纹清单](ARTIFACT_HASHES.json) 固定本轮产物；旧 GPT 运行与参考材料没有覆盖。

## 运行前配置

- 官方 `https://api.deepseek.com/chat/completions`，`deepseek-v4-pro` 和 `deepseek-flash`。
  文档当前对应 V4-Pro-0813 / V4.1-Flash；保留 API 返回的实际 model/fingerprint，
  不把动态别名当冻结权重版本。[官方型号](https://api-docs.deepseek.com/quick_start/pricing/)。
- thinking enabled、high、max_tokens=16384；不设 temperature/seed，不强制 JSON decoding。
  GPT 旧运行是 Codex medium、未设输出上限。本轮是相同任务下的系统配置比较，
  不是等推理预算或统一系统提示的裸模型排名。
- 输入逐字节复用上轮十份 C txt；相同 restricted wrapper 放 system message。
  API 只接收 wrapper 与单份公开输入，没有工具定义、仓库文件、私有标签或历史回答。
- 每母案例两个模型各请求一次，最多两请求并发；socket I/O timeout=600 秒，
  不是严格总墙钟上限。HTTP/传输错误、异常工具调用或 API envelope 错误后停止剩余队列。
  不自动重试、不续写截断、不修复 JSON、不跳过失败题计算全量成绩。
- 不额外做计费 smoke：第一题即首次正式响应。账户不可用时保留失败并停止。
- 采用相同 provisional_labels/v0.1 诊断。support 定义歧义、实际适用性未定、
  替代家族和候选边界问题照实保留，不修改本轮 prompt/标签来制造区分。

## 运行与验证

使用已有 palqo Python 和标准库，无安装。`run.py prepare` / `collect` 均离线；
`run.py run --key-file <用户指定路径>` 执行本次已授权首次请求，拒绝重跑已有轮次。
`test_run.py` 使用隔离临时目录和 mock transport，无网络、无真实密钥、无模型调用。
原始请求（无认证 header）、API 响应、最终回答、状态/usage/时间各自保留在 `runs/`。
运行后以 `SUMMARY.json` / `REPORT.md` 为实际结果；准备工作和测试夹具不算模型成绩。
