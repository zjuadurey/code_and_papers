# lit-001：MaxCut到QAOA正向试跑

入口：[整体报告与命令](../README.md)、[协议](protocol.json)、[执行脚本](run.py)。

结果：[摘要](run-20260928/summary.json)、[真实模拟采样](run-20260928/simulation.json)、
[QDK资源与成本](run-20260928/resource-analysis.json)、[实际电路](run-20260928/application.qasm)。
原case不变，使用其合法域内4节点单位权环；QAOA p=1、32 shots，无经典回退即得到正确结果。
此为正向量子实现和接口联调，不是小实例的硬件加速或通用精确QAOA结论。
