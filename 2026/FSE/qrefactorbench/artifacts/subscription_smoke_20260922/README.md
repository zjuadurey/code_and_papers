# Pro 订阅连通性试跑：2026-09-22

用户在确认仅有 Pro 20× 订阅、没有 API 余额后要求“试一下？”。
本次仅执行两个短响应连通性请求，未启动 20 次 benchmark 方案。

| 请求模型 | 实际结果 | 耗时 |
|---|---|---|
| gpt-5.6-sol | `SUBSCRIPTION_SMOKE_OK`，退出码 0 | 6.183 秒 |
| gpt-6-astra | `SUBSCRIPTION_SMOKE_OK`，退出码 0 | 6.884 秒 |

Codex CLI 0.155.1，reasoning=medium，复用现有 ChatGPT 登录；子进程移除
API-key/token override 环境变量并强制 `forced_login_method=chatgpt`。
没有读取、回显或复制认证内容。未使用 API key、安装依赖或启动 QPU。
请求 ID 被接受且收到回答；事件未披露服务端模型快照，不能据此保证快照可复现。

每模型新建空工作目录、ephemeral 会话，禁用项目文档、用户配置与模型工具。
这不是完整文件系统隔离，不能直接当作正式 benchmark runner。
正式实验应复用/验证已有隔离运行方式，并单独确定配置和范围。

原始事件、stderr、最终响应和参数保存在各模型目录；
[SUMMARY.json](SUMMARY.json) 汇总结果，[RAW_HASHES.json](RAW_HASHES.json) 记录原始材料哈希。
[runner.py](runner.py) 是实际运行脚本快照，执行会再次消耗订阅额度；保留它不代表再次运行授权。

首次登录状态检查误用了仅 `exec` 接受的 `--ignore-user-config`；在任何推理调用前
修正，原失败保存在 `preflight_failed/`。两次推理各只调用一次，没有人工重试。
原始 `result.json` 的 `passed=false` 是检查器把 `item.type=error` 的启动警告一并
算成工具调用导致；警告涉及实验性 skill-discovery 配置和刻意禁用 code-mode host。
后续按事件类型核对：均完成响应、无推理错误、无实际工具调用。原始标志未覆盖，
修正解释保存在 SUMMARY；未为改变该标志重复调用模型。

机械验证：30 份公开输入哈希及暂定参考层的全部评测指纹保持一致。
本次不测 benchmark 分数、剩余额度或费用结算，不代表两个模型能力比较已经完成。
