# 讨论中的搜索与来源记录

检索/核对日期：2026-09-28。用途：支持 [证据框架](EVIDENCE_FRAMEWORK.md)，不是系统综述或最新硬件调查。

N-061后续阅读：三篇均已下载固定版本PDF并核查与lit-005有关章节，另补BBHT及量子minimum finding。
准确范围与hash见[新来源记录](../../pilot/benefit_analysis/lit005-v0.1/SOURCES.md)；
后文“仅摘要/未全文”的表述描述最初D-037轮次，不代表后续没有继续核查。

## 检索过程与阅读深度

首次讨论检索式：`site.arxiv.org quantum advantage end to end input output overhead practical quantum advantage`。
搜索结果包括资源估算、端到端算法综述、纠错成本分析，也混有聚合站、论坛、具体应用与硬件新闻。
本次文档化打开下面三项的原始 arXiv 页面或作者机构页面，核对标题、作者、版本/出版信息及摘要。
**没有全文精读、复现论文实验或核验其全部推导。** 搜索引擎的相对日期不作为发表日期；采用原站记录。
此处保存查询、选择理由和阅读结论，不声称逐字归档了全部搜索响应或 PDF。

## S1：端到端算法分析

Alexander M. Dalzell et al., *Quantum algorithms: A survey of applications and end-to-end complexities*。
[arXiv:2310.03011v2](https://arxiv.org/abs/2310.03011v2)；初稿 2023-10-04，v2 2025-08-05。
原页面记录 Cambridge University Press 2025 年出版；[出版 DOI](https://doi.org/10.1017/9781009639651)。

- 核对位置：arXiv 摘要与 Comments/版本记录。
- 支持：评估需明确问题和输入输出模型、具体化 oracle、计入隐藏成本，并与先进经典方法比较。
- 项目用途：检查 oracle/准备/读出成本是否缺失，为 E1→E4 的证据衔接提供方法依据。
- 不支持：本项目任何案例已经有优势；不能据摘要给出某个 Grover/QUBO 实例的具体复杂度。
- 后续精读：选定候选后再核对相关算法章节、访问模型与完整复杂度前提。

## S2：跨层资源估算

Michael E. Beverland et al., *Assessing requirements to scale to practical quantum advantage*。
[arXiv:2211.07629v1](https://arxiv.org/abs/2211.07629v1)，2022-11-14；
[arXiv DOI](https://doi.org/10.48550/arXiv.2211.07629)。

- 核对位置：arXiv 作者、提交记录和摘要。
- 支持：资源估算需连接算法到硬件的多层选择；qubit 数量之外，速度和可控性也重要。
- 项目用途：要求资源 profile 可追溯，区分抽象、逻辑和物理层。
- 不支持：把该文三个应用的资源规模当作所有算法的门槛，或直接给本项目设 qubit 数量。
- 后续精读：估算模型、错误预算、硬件假设及其适用范围；本次未安装或运行其工具。

## S3：渐近加速与实际纠错开销

Ryan Babbush, Jarrod R. McClean, Michael Newman, Craig Gidney, Sergio Boixo, Hartmut Neven,
*Focus Beyond Quadratic Speedups for Error-Corrected Quantum Advantage*。
PRX Quantum **2**, 010103 (2021)。
[作者机构页面](https://research.google/pubs/focus-beyond-quadratic-speedups-for-error-corrected-quantum-advantage/)；
[出版 DOI](https://doi.org/10.1103/PRXQuantum.2.010103)。

- 核对位置：Google Research 的作者、出版信息与摘要；本次未读取出版全文。
- 支持：该文的容错设备/表面码情景分析指出，小多项式加速可能不足以抵消纠错常数开销。
- 项目用途：提醒 Grover 类理论查询收益不能直接转换为实用时间优势；需成本与敏感性分析。
- 不支持：证明 Grover 在所有硬件/任务上无用，或确定 2026 年所有设备的实际性能。
- 后续精读：具体成本表达、设备假设与对本项目候选的可迁移性。

## 保留为线索、不作为本次证据

首次结果还包含 *A Pathway to Practical Quantum Advantage in Solving Navier-Stokes Equations*
（[arXiv:2509.08807](https://arxiv.org/abs/2509.08807)）、
*Quantum advantage in learning from experiments*（[arXiv:2112.00778](https://arxiv.org/abs/2112.00778)）
等具体应用。仅见搜索摘要，未进一步核验，且不直接对应本项目当前两类映射，不用于制定要求。
聚合转载、论坛和新闻类结果未作为技术论据；不据其标题作最新性或优势成立判断。

## 从文献到项目的推论

“分层证据表”“逐候选证据卡”和论文措辞映射是本项目根据讨论整理的工作方案，
不是上述论文原有分类或自动认可的 benchmark 标准。具体硬件参数、算法公式与优势阈值仍须另行核验。

## S4：Microsoft资源估算器官方介绍（D-041讨论补充）

研究者提供[介绍页面](https://learn.microsoft.com/en-us/azure/quantum/intro-to-resource-estimation)，
2026-09-28读取正文，页面标注更新2026-06-17。此前讨论也引用其
[overview入口](https://learn.microsoft.com/en-us/azure/quantum/overview-resources-estimator)。

- 输入为量子应用模型、硬件架构、纠错/蒸馏工厂模型及错误预算。
- 分层转换、配置搜索和Pareto筛选估计物理qubit、运行时间和累计错误；可使用假设架构。
- 支持Q#、Cirq、OpenQASM、QIR、logical counts和自定义应用。
- 项目判断：可考虑复用为量子资源估算后端；该页没有提供任意经典源码自动迁移、
  原行为验证或强经典端到端收益比较的实现。尚未安装、执行或验证项目适配。
