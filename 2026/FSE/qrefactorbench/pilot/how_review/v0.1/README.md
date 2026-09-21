# HOW 审核提案与四模型试审 v0.1

2026-09-22，N-036。**PRIVATE / DRAFT / PENDING，AI 协调者事后审核。**
用户授权“按照这个思路推进，直到需要我确认才能下一步”。本包完成审核规则准备、
现有回答试审及离线检查；不改变任务、参考标签或正式分数，不启动新模型实验。

- [待审规则](RUBRIC.md)：主张的正确性与完成程度分开，按证据逐项审核。
- [试审结果](TRIAL_REVIEW.md)：五个母案例 × 四个系统配置，19 份回答和 1 份预算失败。
- [机器可读记录](review.json)：全部 40 请求清单；试审子集、原文、哈希及未审核项。
- [有限检查与推导](EVIDENCE.md) / [实际检查结果](checks.json)。
- [待确认的具体选择](DECISION_REQUEST.md)：是否采用本包作为下一版待审审核口径。
- [验证记录](validation.json) / [旧材料指纹](protected_before.json)。

这是有目的的失败分析样本，不是随机抽样：lit-002 检查 tie，003 检查替代家族，
004/006 检查系数与诚实留白，009 检查子区域和预算失败。其余五例只列清单，
**没有完成全量 HOW 审核，也没有新的模型总分或能力排名**。
当前十个母案例已用于规则开发；新保留集的选择及实验协议尚未冻结。

## 复现

从项目根目录运行；仅执行人工编写的算术检查和经过阅读的原经典核，不执行模型代码。
不安装依赖、不读取认证、不联网。输出到标准输出，可自行保存到新的临时路径。

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/how_review/v0.1/check_evidence.py
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/how_review/v0.1/build_review.py
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/how_review/v0.1/validate.py
```

`build_review.py` 只把本次人工编码与冻结原文绑定；**不是自动语义评分器**。
`validate.py` 验证覆盖、来源、复现一致性和材料完整性，不证明审核意见正确。
所有人类审核字段保持空；有限枚举不证明任意输入，也不证明量子执行或端到端收益。
