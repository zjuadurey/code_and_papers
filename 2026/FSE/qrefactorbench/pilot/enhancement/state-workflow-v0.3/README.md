# N-047：可恢复的消融运行器与实际请求预检

2026-09-25。当前为**离线实现与预检完成，真实实验待授权**。没有新增模型或 QPU 调用。
研究仍是用程序分析和语义验证增强同一模型；此版本不提供增强效果结论。

## 动作、目的、效果

| 动作 | 目的 | 实际效果 |
|---|---|---|
| 固定25槽位、单次尝试和进程锁 | 防止中断重跑、成功样本筛选和并发超预算 | 模拟完整流程及故障注入通过；真实运行尚未开始 |
| 同一初稿派生 S/A/V/AV | 分离额外修订、分析与验证的贡献 | 四分支使用同一任务与初稿；只改变提供的观察 |
| 初稿审核绑定原文，记录审核时间 | 防止套用历史错误，公开协调者介入 | 未绑定记未知；AI审核保持 `AI_REVIEW_PENDING` |
| 全部修订结束、绑定冻结后才评测 | 防止最终检查结果流回修订 | 提前评测被拒；五份初稿的绑定在开发审核时冻结 |
| 断网、假凭据、本地请求接收器 | 检查CLI真正发送的内容 | 修正后请求不含工具，私有目录不可见；没有模型推理 |

测试与完整性结果见 [validation.json](validation.json)，执行配置见
[campaign/protocol.json](campaign/protocol.json)，预检见
[campaign/preflight/passed.json](campaign/preflight/passed.json)。
此前 [v0.2](../state-workflow-v0.2/README.md) 的开发/保留检查及解释器原样复用。

## 本轮方案与范围

- `gpt-5.6-sol`，medium，现有 ChatGPT 订阅；5份独立初稿，每份各做4种单次修订。
- 共最多25次单轮CLI调用，串行；每次600秒超时；运行器不重试、不补失败样本。
  CLI内部网络重连不当成独立样本；不声称底层HTTP尝试次数等于25。
- 初稿使用原 `lit-009-C.txt`。S仅自检；A加词法依赖清单；V加开发语义反馈；AV同时加入。
  原模型输出为数据，不执行其代码。分析覆盖回答声明的公开文件候选，无法分析记未知。
- 初稿无有效输出：保留失败，四个依赖修订记未运行；单个修订无效不取消其它分支。
  传输、超时、工具调用或不完整turn触发停止；保持每组分母5，包括未运行项。
- 这仍是1个已知失败母案例的诊断。3个开发请求与12个保留请求均属于该母案例，
  不是独立程序保留集；只检查转录的局部pivot主张，不给整题通过或显著性结论。

## 新版CLI的预检发现与修正

CLI 0.156.1 的 bundled Sol 元数据强制 `tool_mode=code_mode_only` 和
`multi_agent_version=v2`。旧feature配置显示关闭，并不能确保序列化请求没有工具。
本地捕获确实发现 `functions.exec/wait/request_user_input` 及协作工具；证据保存在
[diagnostics/before-catalog-override](diagnostics/before-catalog-override/)。这是当前CLI的
离线发现，不据此猜测历史服务实际暴露的工具，也不改历史实验结果。

使用CLI的 `debug models --bundled` 在隔离环境导出
[原Sol元数据](bundled-sol-metadata.json)。新[固定目录](tool-free-sol-catalog.json)只将
`tool_mode`、`multi_agent_version`、`apply_patch_tool_type` 三项置空，再关闭计划和提问工具。
模型名称、其它元数据与原文说明不变；目录只读挂载到 `/model-catalog.json`，不改用户配置。
这构成新的、明确记录的运行条件；本轮五组使用完全相同条件，不混用历史baseline统计。

`features list` 中 `unified_exec` 仍显示true，但最终实际请求在顶层 `tools` 和
`input.additional_tools` 两种位置均不含工具。因此验收检查请求，而非只检查开关。
内置技能/权限等通用说明仍可能存在；不称为raw API baseline或纯用户prompt。

预检使用外部网络隔离、空假认证文件，并将服务路由替换为本地HTTP接收器。
接收器记录请求后返回固定400错误，不生成回答；捕获子进程exit 1是这个故意拒绝。
它保留同一模型、effort、工具配置、公开prompt与隔离挂载，但替换provider路由并关闭
请求压缩；**没有验证真实订阅可用性、服务端行为或返回质量**。真实运行仍逐次检查工具事件。
`--strict-config` 用于exec；本版本不支持在features/debug上使用该参数，已记录本地行为。
参考[官方配置说明](https://learn.chatgpt.com/docs/config-file/config-reference)；实际验收以
本版本CLI的离线输出和捕获请求为准。排查使用了 OpenAI Docs 技能。

## 操作交接

在项目根目录，复用现有环境：

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest pilot/enhancement/state-workflow-v0.3/test_campaign.py -q
/home/audrey/miniconda3/envs/palqo/bin/python pilot/enhancement/state-workflow-v0.3/campaign.py status --campaign pilot/enhancement/state-workflow-v0.3/campaign
```

准备新目录及复验（不调用模型，不覆盖现有campaign）：

```bash
/home/audrey/miniconda3/envs/palqo/bin/python pilot/enhancement/state-workflow-v0.3/campaign.py prepare --campaign /tmp/qrb-new-campaign
/home/audrey/miniconda3/envs/palqo/bin/python pilot/enhancement/state-workflow-v0.3/preflight.py --campaign /tmp/qrb-new-campaign
```

**收到明确新授权后**，协调者将真实用户指令、时间及以下字段写入该campaign的
`authorization.json`：`protocol_sha256`、`maximum_model_calls:25`、
`model:gpt-5.6-sol`、`reasoning_effort:medium`、`simulation:false`、`user_instruction`。
不要把本README或旧实验授权当作新授权；当前目录刻意没有此文件。

随后逐步运行 `campaign.py next --campaign …`。它每次最多发起一个调用，或恢复已完成
传输的结果、记一个依赖跳过。初稿返回后会停在 `await_development_review`。
使用v0.2 `review.py template` 创建绑定草稿；协调者阅读实际新响应与公开源码，
明确转录/歧义/撤回/未知，不用历史绑定自动替代新审核。提交的审核信封格式：

```json
{
  "response_sha256": "实际response.txt的SHA256",
  "reviewer": {"identity": "Codex coordinator", "status": "AI_REVIEW_PENDING"},
  "review_seconds": 0,
  "binding": null,
  "unbound_reason": "无可支持绑定时的具体原因；有绑定时可为null"
}
```

`review_seconds` 必须填实际耗时；`binding`有值时采用v0.2结构并使用相同reviewer。
`campaign.py review --campaign … --slot 01-initial --review-file …` 冻结审核和四份prompt。
此后继续 `next`，不逐次请求用户授权。所有槽位结束后，为每份有效修订提交
`bind-final --slot … --review-file …`，最后执行 `collect`。初稿绑定直接复用开发审核，
不在看过保留结果后改写。`final-results.json` 保留25行、原始usage、模型/工具/审核耗时。

若存在attempt但没有metadata，状态为`recover_attempt`且拒绝新调用。先确认进程及
保留文件；不可删除标记重新发起。若metadata已完成，则可离线恢复而不再调用模型。
需要修改运行代码、CLI、固定元数据或输入时，原协议hash检查会拒绝运行，应建新版本，
不能静默更新已有协议以绕过冻结。
