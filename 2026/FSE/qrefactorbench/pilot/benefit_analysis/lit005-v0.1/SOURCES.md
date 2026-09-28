# 本次实际核查的依据

日期2026-09-28。PDF URL/字节/SHA256见[source-manifest.json](source-manifest.json)，
本地sources含PDF及pdftotext文本。不是完整综述或最新算法排名；前沿范围仍参考N-059/N-060。

| 原始来源 | 本次阅读范围 | 支持与边界 |
|---|---|---|
| [Boyer–Brassard–Høyer–Tapp, Tight bounds on quantum searching, v1](https://arxiv.org/abs/quant-ph/9605034v1) | §§3–4，已知/未知解数、零解超时 | 解概率公式；超时可能把有解判成无解；不提供first合同 |
| [Dürr–Høyer, A Quantum Algorithm for Finding the Minimum, v1](https://arxiv.org/abs/quant-ph/9607014v1) | 算法、定理1及成功概率证明 | minimum finding是应考虑的既有替代；高概率保证不等于当前exact合同 |
| [Dalzell等, Quantum algorithms: A survey of applications and end-to-end complexities, v2](https://arxiv.org/abs/2310.03011v2) | §4.1 search的复杂度、资源及caveats | SAT谓词构造/数据访问成本需区分；非全书精读，资源段引用他人结果未逐一复现 |
| [Beverland等, Assessing requirements to scale to practical quantum advantage, v1](https://arxiv.org/abs/2211.07629v1) | 摘要、Fig.2与§III任务/ISA资源/执行精度 | 物理与逻辑分层、质量要求影响资源；没有直接套用其设备数字 |
| [Babbush等, Focus Beyond Quadratic Speedups for Error-Corrected Quantum Advantage, v1](https://arxiv.org/abs/2011.04149v1) | 摘要及§II开销模型Eq.(1)–(2) | 理论二次提升的常数开销可能重要；限定其容错假设，不当作所有QPU的否定定理 |

本报告first证明分解和Q1串行成本论证由协调者针对本例推导，不冒称这些论文的结论。
没有从查询复杂度直接推出硬件时间，没有把“未找到正收益”当作普适不可能性证明。
