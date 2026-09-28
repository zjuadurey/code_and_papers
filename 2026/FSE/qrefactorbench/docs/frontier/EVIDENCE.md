# N-059：来源与主张核查

截至2026-09-28。检索问题为经典代码/需求转换、量子机会与算法选择、生成验证、
硬件/端到端成本。沿直接相关论文的引用追踪QPipe、Q-READY和早期Quantum Offloading。
这是定向核查，不是预注册系统综述；未保存完整搜索引擎排名，不声称检索穷尽或全球首创。
主要查询包括 `classical to quantum code C2Q`、`quantum algorithm selection cost prediction`、
`quantum offloading program equivalence`、`QPipe quantum application agent`、
`Q-READY predictive feasibility`。证据包内的源码**只读，未导入或运行**。

## 直接竞争者

### E01 C2|Q⟩

- [论文v3](https://arxiv.org/abs/2510.02854v3)，已存PDF并读方法、实验与局限；
  [作者RCR报告](https://arxiv.org/abs/2604.04112)不算我们独立复现。
- [代码固定版本](https://github.com/C2-Q/C2Q/tree/42e9cb642d4300662274c859e96f131a26d0a714)。
  本次存17份源码/说明/许可；`docs/CLAIMS_MAP.md`将论文主张与可运行入口分开。
- `src/parser/parser.py:116–159`：先预测问题类再提取实例；184–211寻找可转为图的值，
  找不到时实际返回随机5节点图。这是特定路径的静态观察，未执行，不推导整套系统错误率。
- `src/recommender/recommender_engine.py:950`入口接收量子电路；964–965设定
  shots=1000、iterations=50，后续按量子设备的错误/时间/价格给建议。
  在该函数中未见把原CPU实现作为竞争候选；不能扩张成“作者没有任何经典对照”。
- 论文报告434个合成Python输入及100个JSON输入，完成率93.8%/100%；约40倍
  implementation effort代理不是程序运行加速。实验中的生成与验证不足以推出完整原API等价。

### E02 QPipe

- [论文v1](https://arxiv.org/abs/2607.00939v1)，存HTML；重点读§3、§4.3–4.6。
  §4.4为无噪声本地模拟器，§4.6把QRR限定为生成formulation层面的GA相对质量。
- [工具DOI](https://doi.org/10.5281/zenodo.21094837)、
  [实验DOI](https://doi.org/10.5281/zenodo.21094908)。API分别返回文件记录21095005、21094996；
  保留原元数据和实际下载URL，不把不同编号悄悄合并。
  工具zip已下载、列目录、选择6份文件静态阅读；约105 MB实验zip未下载，未重算作者结果。
- 源码前缀 `backend/src/quantum_workflow/`：
  `pipeline/stage_verify.py:1–11`区分agent规格审查与数值核对；94–102将
  `combined.instance`交给经典求解器；`knowledge/classical/solvers.py:41`开始的
  `solve_instance`对Hamiltonian精确对角化，对不超过20变量的QUBO枚举。
- `pipeline/stage_global_review.py`的`StageGlobalReview.run`确实读取原需求及中间产物，
  不能说它“不检查需求”。但agent审查和对生成实例数值核对不等于原源码全行为证明。
- 直接冲突：多agent、工具反馈、语义审查、经典参考与消融都已有实现；
  不能用这些宽泛机制声称首次。未检查完整trace，不报告其真实错误率。

### E03 QuaST Decision Tree

- [论文v1](https://arxiv.org/abs/2605.18539v1)，存HTML；重点§VII–IX及Table V/VI。
- 输入已建模问题/JSON，可配置YAML流程；§VIII用QUBO特征与预计算拟合估计采样成本，
  含不确定性和不可行结果。训练规模3–10、外推至10–100不是对应规模的硬件优势实测。
- 其shot/call数量与穷举边界的比较，不能直接替代同质量下强经典求解器的墙钟比较。
- [官方代码地址](https://gitlab.cc-asp.fraunhofer.de/iks-quantum-computing-public/quast-decisiontree)
  在本次API请求超时、网页访问失败；未固定代码版本。论文§IX说明当时计划公开框架、
  不含§VIII自动化模块；不能据5月文稿断言9月仍未公开。
- [作者机构8月说明](https://safe-intelligence.fraunhofer.de/en/articles/quantum-computing-modular-software-brings-quantum-computers-into-industry)
  支持框架公开线索。当前模块发布状态保留未知；论文结果不得写成代码已核验。

### E04 Predict and Conquer

- [论文v1](https://arxiv.org/abs/2507.06758v1)，存HTML；读算法选择、质量/运行模型与实验。
- [代码固定版本](https://github.com/lfd/qce2025-design-automation/tree/4b4490a6abfdebfe8a8801becad343dd733fa326)，
  本次存README和4份代码。`algorithm_selection_framework.py:620`的框架从结果训练模型，
  808–841根据目标/约束选择可预测的算法；`main.py`示例使用结构化实例和CSV回放。
- `csvs/classical_approximation_benchmark.py`确有MaxCut SDP等经典近似算法计时。
  所以不能写“现有选择工作不考虑经典算法”。其可扩展框架也不能只凭示例断言禁止经典候选。
- README要求QLM等依赖，完整模拟可能数周；本次未安装、未运行。
  该工作可直接作为成本/质量选择与合理组合的参照，不只是外围相关工作。

### E05 Q-READY；E06早期Quantum Offloading

- [Q-READY v1](https://arxiv.org/abs/2606.16201v1)：已存HTML，读引言、策略模型、
  可行性部分；引言明确research vision，不是fully realized solution。
  因而需求→策略→成本链条这一“想法”已经出现，但不能将示例数值写成实测。
- [Quantum Offloading论文DOI](https://doi.org/10.1109/CCWC51732.2021.9375948)：
  作者机构摘要描述CORK与Shor局部原型的变体等价检查。机构PDF本次403，**只读到摘要**。
  足以排除“首次用程序等价做量子卸载”的宽泛说法，不足以断言其全部能力上限。

## 生成、评测及基础组件

| 证据 | 核查深度 | 能支持什么/不能支持什么 |
|---|---|---|
| [QUASAR v1](https://arxiv.org/abs/2510.00967v1) | 存PDF；读奖励、Table 1/2与消融 | 工具＋RL生成电路已有先例。Table 1 pass@1的99.31%是语法SCR；SREV22.41%、HQCR17.24%是另两项，不能当99%语义正确 |
| [Q-Bridge v1](https://arxiv.org/abs/2603.27836v1) | 存PDF；读数据/训练与§4评价；只取代码树 | CML→QML属相邻受限域；ML误差/准确率不是通用程序等价或实测加速 |
| [QuanBench+ v2](https://arxiv.org/abs/2604.08570v2) | 存PDF；读任务/反馈修复设计 | 量子任务生成、执行反馈修复已有；不是已有经典软件的完整迁移评价 |
| [PQID-Bench](https://github.com/Elias-Abebe-Gasparini/PQID-Bench/tree/f4bafb4ce96569dbffe82c2e44f142a81e4ee27e) | 存README、许可、复现合同和PQID2 prereg | 电路signature不是语义等价；prereg不是已完成语义实验，未来版本仍可能撞题 |
| [QSynth / POPL 2024](https://doi.org/10.1145/3632901) | 论文/作者仓库说明级；未运行 | 给定受限规格的验证引导量子程序合成已有；不代表自动从任意源码提规格 |
| [Qrisp/Jasp](https://qrisp.eu/reference/Jasp/Ported%20Features.html) | 官方文档 | 量子/混合语言编译；Jasp支持表中automatic uncomputation不能与普通Qrisp混同 |
| [MQT Predictor](https://doi.org/10.1145/3673241) | 论文摘要/官方说明级 | 从已有量子电路选设备与编译；不是原经典程序收益识别 |
| [Microsoft资源估计器](https://learn.microsoft.com/en-us/azure/quantum/overview-resources-estimator) | 官方文档 | 容错架构/纠错模型下的资源估计；不能直接当当前NISQ设备实测 |
| [Horizon子程序](https://www.horizonquantum.com/product/core-capabilities/subroutines) | 厂商公开文档 | C函数转可逆子程序等能力线索；闭源商业宣传不是本次独立验证 |

Q-Bridge仓库树固定于`3eaccadabbd593982d89216c08ff4c30fcd2f826`，未运行/下载模型。
QUASAR候选仓库API返回404；记录为获取失败，不能推出“作者没有公开实现”。
所有横向成功率因任务、条件和指标不同，本次不作数值排名。

## 检索对判断造成的修正

1. C2Q使“首次把经典输入接到量子程序和后端”不成立。
2. QuaST/Predict使“没人自动选择/预测成本/表达不确定性”不成立。
3. QPipe使“多agent＋修复＋验证＋消融”不能独立作为新贡献。
4. CORK/QSynth使“有语义验证就是新技术”不成立。
5. Q-READY使“需求与资源联合建模”的宽泛愿景也必须进一步具体化。

剩余假设见[NEXT_STUDY](NEXT_STUDY.md)。即使所读单篇未覆盖，也必须与合理组合比较，
不能用单篇能力缺口偷换全领域技术缺口。
