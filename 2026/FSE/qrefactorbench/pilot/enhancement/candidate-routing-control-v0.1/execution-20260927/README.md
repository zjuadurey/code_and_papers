# N-057 执行交付

15次目录/路由对照完成，见[报告](REPORT.md)。主结果与辅助核查分开保留。

- [协议](../campaign/protocol.json)、[D-035回执](../campaign/authorization.json)
- [准备验收](preparation-validation.json)、[运行器变更](runner-lineage.diff)
- [原结果](../campaign/final-results.json)、[绑定屏障](bindings-frozen-before-evaluation.json)
- [提名变化原文](nomination-audit.json)、[辅助经典验证器检查](auxiliary-verifier-check.json)
- [执行验收](execution-validation.json)、[汇总](summary.json)、[审核计时](review-timing.json)

只读重放（项目根目录、已有palqo Python；无模型调用）：

```sh
python pilot/enhancement/candidate-routing-control-v0.1/execution-20260927/validate_execution.py --check-only
```

此命令校验协议、原文引用、时序和全部主结果；辅助证据在自己的文件中保留转录规则及
已知状态，不混入主结果。campaign已all_slots_terminal，禁止继续next或覆盖prepare/collect。
