# lit-005：Grover与原行为的边界试跑

入口：[整体报告与命令](../README.md)、[协议](protocol.json)、[执行脚本](run.py)。

结果：[摘要](run-20260928/summary.json)、[行为检查](run-20260928/semantics.json)、
[QDK资源与成本](run-20260928/resource-analysis.json)、[实际电路](run-20260928/application.qasm)。
任意满足解直接返回为明确标记的错误对照；前缀修复对所有测量输出及无样本保留原first要求。
该修复方案保留经典搜索工作，限定串行条件下无时间收益；不推广到所有量子方案。
