# HOW v0.2：条件计划的双维度审核

2026-09-22，N-037 / D-026。研究者选择 A：**保留条件计划任务，分别记录主张正确性
与义务完成度，允许明确留白，不合成总分。** 该方法方向已接受；逐条审核仍 AI/PENDING。

- [独立版本协议](PROTOCOL.md)：方法状态、字段、证据范围、缺失/替代路线政策。
- [全量审核报告](REPORT.md) / [逐条记录](review.json)：40 请求，39 份有效回答的四项
  记录；1 份截断保留。继承 v0.1 的19份试审，补齐另外20份，未重新运行模型。
- [新增证据](EVIDENCE.md) / [实际离线检查](checks.json)：001/005/007。
- [评审准备包](reviewer_packet/GUIDE.md)：十个原始 C 输入、合同义务、空白表；
  不包含模型回答、协调者判断或私有标签。是供人类建立参考的材料，不是模型运行输入。
- [保留集协议草案](HOLDOUT_DRAFT.md)：没有建设/冻结新测试集，也没有新运行授权。
- [需要审核的事项](REVIEW_HANDOFF.md) / [完整性验证](validation.json)。

旧 [v0.1](../v0.1/README.md)、模型原文、公共输入、暂定结构标签和主 evaluator 保持不变。
v0.2 是独立的 HOW 人工证据协议，不强制模型提交实现，不追溯改变历史诊断分数。
按本协议完整登记不表示每条主张都经过证明；仍可 unresolved / not_addressed。

## 离线复现

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/how_review/v0.2/check_evidence.py
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/how_review/v0.2/build_review.py
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/how_review/v0.2/validate.py
```

前两命令输出 JSON；第三命令检查覆盖、原文、双维度记录、盲包 allowlist、复现和
旧材料指纹。审核编码为人工 AI 判断，脚本只绑定和汇总，不是自动语义裁判。
不读认证、不联网、不执行模型代码、不运行量子任务。无新总分、稳定排名或 gold。
