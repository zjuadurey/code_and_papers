# QRefactorBench 当前状态

**Mac接续（2026-09-28）：[跨机器交接](docs/MAC_HANDOFF.md)已保存。**
用户提供LogicalQubit云平台用于小规模实验；公开资料确认AGate-100为100物理超导qubit，
已核查lqcloud0.5.0接口/版本要求，尚未登录、安装SDK、查实际后端或提交QPU。
Mac建议Python3.11独立环境；本地公式/QDK可准备复现，原bwrap模型runner不支持原生Mac。
当前多项产物未跟踪，需同步完整工作目录而非仅git pull；本次未提交/推送/实际跨机器同步。

**最新：D-043小规模验证＋公式推导已落实，[100/200/500逻辑qubit潜在优势条件](pilot/benefit_analysis/maxcut-formulas-v0.1/REPORT.md)。**
用户要求没有大规模量子机时采用替代证据；真机或完整目标规模模拟不是研究前提。
构造推导G=n+p(3m+n)、显式调度深度，45组小规模Hamiltonian/门级核验通过；
11次QDK估算全部成功，未模拟大规模状态。100位p=1指定点13310物理比特/单shot1.6ms。
含可靠证书/精确回退的公式已反解：在T=1s、A=10ms、v=0.1ms、S=64、F=T的显式条件下，
单shot获证率s>0.197415%即有模型内期望收益；s=1%时预测0.644396s（约1.552倍）。
T/A/v/s是条件坐标，非已测100位实例表现；实际证书/成功率仍需实例证据，不能声称已实现加速。
8项专项测试通过，2376条件点保存、175旧文件未变；零新模型/QPU/安装/正式case或论文修改。
该结果承接下方规模诊断，当前工作焦点以本段和[D-043](DECISIONS.md#d-043-small-scale-validation-and-formula-derived-potential-quantum-advantage)为准。

**2026-09-28本轮纠正与实测：[MaxCut规模/资源条件诊断](pilot/benefit_analysis/maxcut-scaling-v0.1/REPORT.md)。**
用户指出四节点无收益不能回答规模增长后的收益；未执行先前提议的模型判断对照。
独立kernel诊断覆盖8–64节点：18次经典求解14完整/4超时，18次QDK估算成功。
32节点指定模型点6009物理比特/单shot0.505ms，对照经典约579.076ms；
64shots切片给其余全部开销留下546.756ms必要预算，未证明64shots够用或完整收益。
现有all-edges证书在含正权三角形的图上必拒绝，当前通用精确验证/成功率仍缺；
原wrapper上限16、解析器固定4qubit未改，超过16属于独立规模诊断而非正式case扩展。
8小图独立枚举及64图原kernel对照通过；无新模型/QPU、安装、正式标签或论文修改。

**2026-09-28侧线程补充：用户要求的 [lit-001 实际 LLM 闭环](pilot/llm_workflow/lit001-v0.1/README.md)已跑通。**
同一 Sol/medium 实际4次调用：读源码、生成QAOA电路并验证、估算资源与完整成本、读取反馈给结论。
4逻辑比特/20门/64shots，实际输出与原程序一致且无回退；21项测量结果检查通过。
QDK两假设点均279物理比特；100ns点完整场景成本约2.411–2.431ms，因此模型建议此小实例保留经典。
44项专项/资源回归通过；无模型重放的模拟和QDK估算完全一致。源码/正式案例/gold未修改。
这是给定QAOA家族和可信证书工具的单案例闭环，替代先前“只有手写联调”的状态，
不是跨案例效果实验；[原始模型终稿](pilot/llm_workflow/lit001-v0.1/run-20260928-01/conclusion.json)
及[跨机器命令](docs/quantum_advantage/ENVIRONMENT.md)已保存。N-063通用资源后端保持不变。

更新：2026-09-28（N-063资源工具及真实SDK联调完成；N-058候选纳入仍待审）。历史过程见 CHANGELOG 和研究日志。

**最新实现：[N-063资源工作流](docs/quantum_advantage/RESOURCE_WORKFLOW.md)，[联调记录](pilot/resource_workflow/v0.1/README.md)。**
D-042落实用户选择：复用Microsoft QDK开源库，我们实现接口、完整成本和工作流集成。
新增Python/CLI工具调用本地qdk.qre 1.32.3，区分模型提案与控制端行为/成本证据；
成本区间、重复调用、错误预算、未知/失败反馈已接通，未修改正式评测指标。
真实两qubit工程电路联调通过：假设模型下177物理qubit/9000 ns，因证据缺失正确返回unknown类反馈；
这些不是benchmark优势或设备测量。专项30通过；全套253通过/15可选依赖跳过。
本线程未运行模型/QPU、未执行安装命令；QDK由另行授权的环境任务安装到palqo，
授权和安装说明见[环境记录](docs/quantum_advantage/ENVIRONMENT.md)，本线程直接复用完成联调。
N-063当时的后续是给case补齐行为/成本并接LLM；现lit-001单案例闭环已完成，见页首补充。

以下N-062为已接受方向记录，最新实现指针以上文N-063为准：

**研究者已认可D-041：[输入经典程序，推导值得量子化的资源条件](docs/quantum_advantage/RESOURCE_CONDITIONS.md)。**
分析从给定设备的采用判断扩展为资源条件推导；原行为与端到端收益仍是核心依据。
输出方案、逻辑qubit等资源、速度/可靠性、规模与收益预测，不默认唯一qubit门槛。
本轮N-062仅文档同步，无实现或新实验。下一步准备首份资源条件—端到端收益分析，
N-061的first/absence证明与方案成本比较作为子任务；正式版本指针不变。

**案例分析入口：[N-061逐案例分析](pilot/benefit_analysis/lit005-v0.1/REPORT.md)与[推进说明](docs/quantum_advantage/PROGRESSION.md)。**
[D-040](DECISIONS.md#d-040-contract-and-end-to-end-benefit-as-core-decision-criteria)落实用户纠正：
行为合同与端到端收益是系统核心判定依据，不再降为候选机制。完整idea不变。
lit-005的first/absence义务已落实到oracle、经典对照、四类方案和完整成本账本；
普通Grover在源示例满足任意解概率1、所需first解概率1/2；特定串行前缀枚举修复方案无加速区间。
8项专项＋11项wrapper测试、1809实例/4633基态/6442修复检查、精确重放通过。
这不是Agent自动化或强经典硬件收益实验；物理profile和其他方案收益未知。
N-061原后续：first/absence证明义务驱动的计划与成本比较，现纳入D-041资源条件分析。
无模型/QPU、安装、正式case/gold/split/指标或论文修改；3675个受保护旧文件未变。

以下N-060为历史记录；其“不预先锁定合同/成本”和优先级已由D-040/N-061纠正：

[D-039](DECISIONS.md#d-039-preserve-the-idea-and-compare-technical-routes)落实用户纠正：
完整idea保持不变；调研确定如何向目标推进，不决定是否放弃目标，也不预先锁定合同/成本。
补充Yamato源码自动卸载、Road真实软件迁移研究及HPS验证线索，形成8项直接前沿对照、
现有技术边界和A源码候选恢复/B硬件方案选择/C可用迁移验证三条路线比较。
N-054与N-058 C01/C02三项静态诊断已完成；不是新模型结果或外部工具失败率。
建议先准备源码到候选计算的强基线适配与诊断，保留完整系统目标；具体新机制未冻结。
本轮无上游执行/模型/QPU、安装或论文编辑。证据限制、FSE差距与完成核对均已文档化。
交付与核验见[归档](pilot/frontier_audit/20260928-goal-review/README.md)。

以下N-059为历史阶段，其路线排序及“下一步三项诊断”已由N-060取代/完成：

N-059已完成：[前沿核查](docs/frontier/README.md)、[来源/代码锚点](docs/frontier/EVIDENCE.md)
及[下一步诊断](docs/frontier/NEXT_STUDY.md)。C2Q、QPipe、QuaST、Predict and Conquer、
Q-READY及早期等价卸载使“自动生成/agent修复/成本选择/语义检查”的宽泛创新主张不足。
固定C2Q/Predict/PQID源码，下载QPipe工具包并静态核查；QuaST代码获取失败保留未知。
推荐先检验“原程序行为义务如何改变替换方案及完整成本”能否超越现成工具的合理组合；
这是候选假设，未证明新颖性或效果。零新模型/QPU、零性能复现、未改论文或正式案例。
下一步仅做N-054及N-058 C01/C02的三项静态诊断，不重跑旧模型实验或扩正式数据集。
归档与完整性核验见[本次交付](pilot/frontier_audit/20260928/README.md)。

研究定位补充（2026-09-28，[D-038](DECISIONS.md#d-038-frontier-relative-research-framing)）：
“推进”须相对当前最先进工作与现有技术边界，而非仅相对本仓库增加功能。
先以文献、实现和实验核查前沿及真实缺口，再选择新技术；已有benchmark和增强原型
用于检验该判断，不预先限定贡献。N-059已完成有边界的前沿核查；具体RQ和方法仍待诊断收敛，
不是穷尽综述或已证明新颖性。

文档补充：2026-09-28，[D-037](DECISIONS.md#d-037-quantum-advantage-as-the-long-term-objective-and-layered-evidence-documentation)
确认端到端收益作为长期目标，并完成[讨论/证据/实现/文献/论文分层记录](docs/quantum_advantage/README.md)。
仅文档更新；具体优势指标、硬件profile和协议待定，无新增优势结果或运行任务。
当前资源计数和`end_to_end_quantumization_success`均不构成经典/量子收益对照。

N-058已完成：[三份新母问题候选档案](pilot/new_mother_candidates/v0.1/README.md)。
研究者回复“A”授权最多4份准备，本批形成CPython文本匹配、python-tsp闭合旅行商、
NetworkX惰性路径枚举三份；固定三个仓库commit、10份来源/许可，并对照旧十例谱系。
文本961整串对＋961区间检查、TSP779矩阵/2337调用、4个QUBO共1552赋值、
路径64图/2880多重集检查及合同错误对照通过；3555旧文件哈希未变，结果可精确重放。
前两份建议进入DRAFT来源/合同评审，第三份保留边界候选；均未正式纳入、定gold或split。
TSP仅复现原单文件，tag/包内版本及NumPy要求差异已记录；零新模型/QPU调用。
下一步见[参考评审清单](pilot/new_mother_candidates/v0.1/REFERENCE_REVIEW.md)，不按模型表现挑题。

N-057已完成：[15次目录/路由结果](pilot/enhancement/candidate-routing-control-v0.1/execution-20260927/REPORT.md)。
15/15有效、零重试。原空候选组C/R均新增局部候选而S未新增；整函数组S也改为局部，
不能归因于工具。未见R相对C明确额外正确性收益；R第1组谓词两种解释均失败16状态，
C第2组只有一种解释44通过，R第5组附加有限域谓词两解释均31通过/13排除；均保留歧义。
无无歧义有限通过结果。15行精确重放一致，3312旧文件未变。下一步已到研究数据范围决定：
[D-036具体方案](docs/NEXT_RESEARCH_SCOPE.md)已获A方案授权，先建最多4个新母问题候选档案，
不默认扩案例、认可gold或冻结split；同范围订阅额度D-035无需重问。

N-056已完成：[目录/路由运行准备](pilot/enhancement/candidate-routing-control-v0.1/README.md)。
31项入口＋32项运行器＋49项回归通过，5项离线隔离预检通过；N-057已依据D-035执行完。
原五份初稿各S自检/C仅目录/R目录加路由一次，共15次；协议已冻结，串行无工具零重试。
全部队列结束后统一引用绑定和已知回归；终止状态all_slots_terminal，不追加采样。

N-055已完成：[候选分析入口](pilot/enhancement/candidate-routing-v0.1/README.md)。
分别处理空候选、函数、局部区间及精确语句，保留declared_region并显式记录analysis_scope、
seed_statement；不把12–16行静默扩大成12–20行。31项新测试＋49项回归通过，
五份原始初稿已生成分析包，三份源码与公开任务逐行吻合，3298个旧文件未变。
该实现阶段零新模型调用；后续独立对照已由N-057完成，结果见上。

N-054已完成：[秩QUBO事后核查](pilot/enhancement/rank-qubo-audit-v0.1/REPORT.md)。
N-053第5组F的具体构造在31个已知有限状态和1704个事后合成小状态通过，13个非有限
状态保留排除；72990赋值检查、18测试、精确重放通过，3285旧文件未变，零新调用。
另给出任意精确P>0的人工数学论证；P=1/10只核对代数主张，不冒充整数系数入口实例。
秩构造已需平方级经典工作并暴露答案，不推导量子收益或正式structural标签。

N-053已完成：[信息补全结果](pilot/enhancement/claim-elicitation-v0.1/execution-20260927/REPORT.md)。
10/10有效、零重试。F第1组局部规则44通过，第2组有限值条件内31通过/13排除；
S第2组失败8状态，第5组附加Grover两种解释各失败3状态。第3/4组两支仍无计划。
第5组F补出了具体QUBO构造，超出本轮checker，未计成正确；两支仍各3份insufficient。
全部重放一致，3114旧文件未变。后续QUBO核查已另记N-054，本轮成绩保持原样。

N-052：[单次信息补全接口](pilot/enhancement/claim-elicitation-v0.1/README.md)已实现，
32项本轮测试＋49项回归通过。全部5份N-048原始初稿各做S自检/F补全一次，
共10次；同包装、同初稿、无检查结论或反例，保留未知/空计划/QUBO。
协议已冻结，5项离线预检通过后按D-035执行N-053；队列已终止，不追加采样。

N-051已完成：[16次反馈控制结果](pilot/enhancement/feedback-control-v0.1/execution-20260927/REPORT.md)。
16/16有效、零重试；唯一错误初稿中E摘要和W反例均通过44个已知回归状态，S仍失败3个，
C缺完整规则；本轮未见W相对E额外收益。12/16证据不足，另1份E只在有限值条件下通过。
不作普遍增强结论。该缺失形式信息问题由N-052/N-053继续诊断。

N-050已完成[16位置实现与验收](pilot/enhancement/feedback-control-v0.1/README.md)：
32项新测试＋49项相关回归通过，完整假传输演练及5项隔离预检通过；真实调用0次。
用户已明确“批准”，D-034独立回执已登记；N-051已执行完原16位置，队列`all_slots_terminal`。
随后D-035“限额随便用”委托同方向现有订阅额度；后续不再逐轮询问次数批准，仍先冻结
具体协议再运行。N-051保持原16位置，不因预算委托追加样本。

N-049已完成[离线设计与原文映射](pilot/enhancement/state-workflow-design-v0.1/README.md)：
25份回答/90处锚点、5份分析入口核对、16份提示词草案；零新调用。N-050已接入固定
运行配置；补问/候选改进未与反馈控制同时引入。后续信息补全执行结果为N-053。

N-048已完成：[结果报告](pilot/enhancement/state-workflow-v0.3/execution-20260926/REPORT.md)。
25/25响应有效、零重试；唯一明确错误初稿的配对中，V与AV均通过44个保留状态，S与A仍有反例。
另有未知、解释歧义、有限条件通过和新增错误主张；不据此主张普遍增强或AV优于V。
本轮调用授权已耗尽，不追加、重跑或替换样本。

当前论文编辑入口（2026-09-25）：[FSE/paper](../paper/README.md)，[新对话交接](../paper/HANDOFF.md)。
原 `paper/fse2027-draft-20260925/` 与工作区 `latex.zip` 保留为历史交付快照，不自动同步。
含详细实验设计、空白结果表及概念图占位；论文目录交接本身没有启动实验。
N-048/N-051/N-053/N-054结果尚未自动回写论文。正式字体环境的编译页数尚需复核。

N-043 / D-031已完成：[同模型映射反馈实验](pilot/enhancement/lit002-v0.1/REPORT.md)。
GPT-5.6 Sol的15次订阅调用全部完成：初稿、自检、语义反馈均5/5通过98个最终实例。
五份初稿均已正确，实际反例反馈0次；闭环跑通但无增强收益证据，授权已用完，不追加调用。

N-041 / D-029已完成：[最新四模型复跑](pilot/model_comparison/20260923-four-model-c-v0.1/REPORT.md)，
40次请求、36份有效、4份预算截断；新009谓词反例仅反驳局部主张，非整题失败。

## 研究目的与阶段

帮助非量子专家分析**已有经典软件**的 WHERE／WHETHER／HOW，最终选择性重构为
保持原软件合同、有收益证据的混合程序。当前为 **Phase 1：benchmark 案例建设与
任务验证**，已有四模型 C 比较；HOW 条件计划双维度方法已接受，逐例审核仍待审。
完整研究意图见 [研究纲领](docs/RESEARCH_CHARTER.md)。N-043开始验证局部增强原型，尚非最终Agent。

N-042 / D-030已确认技术方向：**利用程序分析与语义验证，增强LLM对经典程序的
量子机会识别与映射设计能力。** 先诊断薄弱环节，再比较同一模型原始流程与加入
方法后的流程；harness是承载框架。N-043选用精确语义反馈，提升效果以本次实际实验为准。

## 当前版本与材料位置

| 用途 | 当前指针 | 使用边界 |
|---|---|---|
| 最新候选准备 | [N-058三个档案](pilot/new_mother_candidates/v0.1/README.md) | D-036 A已接受；局部经典核对通过，正式纳入/合同/gold/split待审 |
| 最新目录/路由对照 | [N-057结果](pilot/enhancement/candidate-routing-control-v0.1/execution-20260927/REPORT.md) | 15位置终止；部分提名变化，不证实R独有收益或泛化 |
| 最新候选入口实现 | [N-055接口](pilot/enhancement/candidate-routing-v0.1/README.md) | 80测试、五份离线分析包；无候选正确性或模型效果结论 |
| 最新替代家族局部核查 | [N-054秩QUBO](pilot/enhancement/rank-qubo-audit-v0.1/REPORT.md) | 事后精确枚举与人工数学论证；不改N-053结果或gold，不证实收益 |
| 最新信息补全诊断 | [N-053结果](pilot/enhancement/claim-elicitation-v0.1/execution-20260927/REPORT.md) | 10次完成；一个局部全域回归通过、一个条件内通过，QUBO具体构造待另行核查 |
| 信息补全冻结实现 | [N-052接口](pilot/enhancement/claim-elicitation-v0.1/README.md) | S/F各5次；81项测试与5项离线预检通过；不改原schema/checker |
| 最新反馈控制结果 | [N-051执行结果](pilot/enhancement/feedback-control-v0.1/execution-20260927/REPORT.md) | 16次完成；E/W同一错误机会有限修复，12份未知，已知回归而非未见测试 |
| 反馈控制冻结实现 | [N-050准备快照](pilot/enhancement/feedback-control-v0.1/README.md) | 16位置、81测试及离线预检；历史零调用状态保留，实际执行见N-051 |
| 离线方法设计来源 | [N-049反馈信息控制](pilot/enhancement/state-workflow-design-v0.1/README.md) | 16份设计输入已由N-051执行；S/C/E各5、W仅1；旧保留状态只作已知回归 |
| 最新同模型消融结果 | [N-048执行结果](pilot/enhancement/state-workflow-v0.3/execution-20260926/REPORT.md) | 25次完成；1个明确错误初稿机会，V/AV有限修复；未知/歧义/条件与成本分列，授权耗尽 |
| 当前分析/验证工作流 | [state-workflow-v0.3](pilot/enhancement/state-workflow-v0.3/README.md) | N-047冻结实现与预检；N-048沿用0.156.1执行；上级README保留准备阶段事实；v0.1/v0.2保留 |
| 同模型失败审核与方法提案 | [lit009-review-v0.1](pilot/enhancement/lit009-review-v0.1/README.md) | N-044事后离线审核；NaN可达链、转录敏感性与回退边界；后续实现见N-045 |
| 同模型局部增强实验 | [lit002-v0.1结果](pilot/enhancement/lit002-v0.1/REPORT.md) | D-031直接QUBO新协议；A/B/C均5/5有限通过，零可观察修复机会，不改原benchmark |
| 当前十组来源案例及审核修复 | [reference_completion/v0.1.1](pilot/reference_completion/v0.1.1/README.md) | DRAFT 工作包；不是旧 pilot 的十个案例 |
| 当前 A/B/C 输入 | [30 份输入 manifest](pilot/reference_completion/v0.1.1/review_inputs/manifest.json) | 十个母案例×三个条件；本轮只跑 C，只给模型单份 txt |
| 当前暂定参考标签 | [provisional_labels/v0.1](pilot/provisional_labels/v0.1/README.md) | 私有 DRAFT/PENDING 标签与可执行诊断；不是金标，不给模型 |
| 当前包首轮模型比较 | [2026-09-22 小报告](pilot/model_comparison/20260922-c-v0.1/REPORT.md) | Sol/Astra medium，各 10 个 C；20/20 有效，暂定参考诊断 |
| 首轮四模型比较（含 DeepSeek 补测） | [首轮四模型小报告](pilot/model_comparison/20260922-deepseek-c-v0.1/REPORT.md) | Pro 10/10、Flash 9/10 有效；Flash 一题预算截断；含两份 HOW 反例 |
| 最新四模型 C 复跑 | [2026-09-23 小报告](pilot/model_comparison/20260923-four-model-c-v0.1/REPORT.md) | Sol/Astra各10/10、Pro9/10、Flash7/10有效；原输入不变；含7份目标检查与009事后反例 |
| 当前 HOW 协议及全量待审记录 | [how_review/v0.2](pilot/how_review/v0.2/README.md) | D-026接受A；39份回答/156项证据及200条完成度记录，无总分；v0.1保留 |
| 当前局部语义判定与对照验证 | [semantic_verification/v0.2](pilot/semantic_verification/v0.2/README.md) | N-040：10题均有局部验证；61输入、22正确/等价通过、30错误拒绝；非整题成绩，v0.1保留 |
| lit-002审核反馈附录 | [20260922-lit002](pilot/how_review/adjudications/20260922-lit002/README.md) | 两项公式反驳获用户转交意见支持；作者身份/独立性未登记，不升整题gold |
| 订阅连通性试跑 | [2026-09-22 smoke](artifacts/subscription_smoke_20260922/README.md) | Sol/Astra 各一次短响应成功；不是 benchmark 运行 |
| 来源与评测方法 | [覆盖表](pilot/reference_completion/v0.1/COVERAGE.md) / [方法与结果](pilot/reference_completion/v0.1/METHODS.md) | v0.1 保留来源及方法夹具；不是模型分数 |
| 原 baseline 的冻结输入 | [pilot/packets-v0.1](pilot/packets-v0.1/) | 历史实验输入，不是当前 A/B/C 包 |
| 原 baseline 结果 | [Restricted Codex CLI](pilot/baseline-v0.1/restricted-codex/BASELINE_RESULTS.md) | 已完成；非 raw API baseline；DRAFT-reference 评价 |
| 条件计划诊断 | [paired diagnostic](pilot/baseline-v0.1/conditional-plan-diagnostic/CONDITIONAL_PLAN_DIAGNOSTIC_RESULTS.md) | 已完成，不算第二个独立模型 baseline |

## 已完成与可支持的结论

- N-051 / D-034：S/C/E各5、W1，16份有效。第2组E/W显式按序严格>更新，通过44已知
  状态；S3个反例、C未知。第1组E有限值条件31通过/13排除；其余12响应未知。
  第3组S也新增候选，不能把提名增量归于提示独有作用；第4组C为整个求解器输出搜索包装。
  260561输入/36815输出token；模型746.119秒、审核墙钟315.204秒。仅1个错误初稿机会。
- N-050：复用隔离传输与主张检查器，接入16位置同稿控制；失败保留、至多一次派发、
  中断恢复、授权/预检和全量绑定门禁均经模拟测试。实际请求捕获工具为空，假认证、断网
  本地拒绝端点，无模型推理。工程可运行不等于方法有效，订阅当前可用性未验证。
- N-049：15份证据不足细分为缺规则5、无候选3、粗范围无计划4、QUBO未构造3；另有歧义2、
  明确规则8，不是新正确率。旧分析只使用起始行；第1组复合种子越过提名末行，第4组函数
  起点不支持。已生成中性AST目录及S/C/E/W控制草案，尚未实现新路由或运行模型。
- N-048 / D-033：25次调用全部完成；仅第2组初稿有明确可反驳谓词，其V/AV改为按序严格>
  更新，44/44保留状态有限通过，S/A仍有反例。两份成功修订共享一个初稿，不是两次独立机会。
  AV另两份有限条件主张各检查31状态、排除13状态；A有一份措辞歧义，一种解释通过、一种失败。
  S与V分别新增一份被反驳主张，不能把增加计划数当改善。四份初稿证据不足；未知反馈含pivot
  静态提示，候选增加有提示因素。1母案例、协调者审核，不作整体正确率或普遍提升结论。
  395819输入/53025输出token；模型耗时1164.678秒；审核墙钟605.356秒。详情与限制见报告。
- N-047：接入隔离传输，固定25槽位、同稿四支、失败保留、审核与最终评测门禁；
  26项新增＋49项回归通过。CLI 0.156.1的Sol元数据强制工具，已在本轮局部目录中
  清除三项工具元数据并关闭计划/提问工具；断网本地捕获确认请求工具为空、私有目录不可见。
  N-047当时没有真实凭据访问、模型调用或效果测量；冻结协议随后获D-033授权并由N-048执行。
- N-046：新响应经明确原文绑定可做局部检查；歧义/guard/撤回/无法表示分开记录。
  3开发请求13状态、12保留请求44状态；两个正确/等价对照通过，五个错误对照在保留集被拒。
  “总选首行”错误对照通过开发却在保留检查失败，说明有限反馈覆盖不足；不是模型新失败。
  49项新版及回归通过。仍需协调者转录，非自动文字裁判、独立母案例保留集或增强收益证据。
- N-045 / D-032：用户委托具体工作流方向与本地推进，要求解释动作、目的和效果。
  已实现词法依赖清单、已审核主张的反馈选择和四分支输入/状态记录；12项测试通过。
  分析不保证严格切片或可达性，反馈仍依赖人工绑定。零模型调用，没有增强收益结论。
- N-044：重放Sol009原响应绑定和7次历史pivot状态，新增同母案例6×6敏感性输入的6次追踪；
  旧单元素反例依赖包含自身比较，新输入两个NaN使包含/排除自身解释均失败。
  明确有限输入→溢出→NaN的真实状态链；仅局部谓词被反驳，回退与整题未判。
  009/010校验扫描已核对源码边界；Sol010缺项措辞冲突记歧义，未改标签。增强方法仍为提案。
- N-043：通用结构化公式→精确语义检查→单次反馈/自检修订→隔离最终检查已经运行。
  1母案例、5组配对、15响应；并非15个独立案例。正反对照验证检查器，真实模型结果未显示提升。
  只实现局部语义反馈，未实现生产程序的自动合同提取、完整转译或证明方法有效。
- N-041 / D-029：四模型各十题再次运行，无重试或修复。Pro002、Flash004/005/009预算截断。
  001/002的7份目标转录共38条局部检查通过；009中Sol/Pro的唯一最大值谓词被可达NaN反例否定，
  经典回退与整题仍未判。009/010校验扫描提名暴露候选边界问题，不据此擅自判错或排名。
- schema、验证/摘要 CLI、模块化评测、注释/盲输入工作流已具备；语义验证钩子不等于
  完整自动迁移正确性判定。当前正向范围仍为 Python、Qiskit、Search 与 Optimization。
- 当前 **10 组来源可追溯的合成改编**：lit-001–004 来自 C2|Q>；005/006 来自
  QuanBench/＋，007 来自 SupermarQ，008 来自 Qiskit HumanEval，009/010 来自 HPL/HPCG。
  后三个是范围/经典保留对照提案，不新增正向家族。PQID/MQT 用于评测方法借鉴。
- A 核心、B 完整程序＋位置提示、C 相同完整程序无提示。方向已接受（D-020）；
  不是 30 个独立问题。功能依赖与反例已测试，WHERE 难度留给实验检验。
- N-030 工程审核完成；N-031 修复锁定冲突顺序（005）、delta 溢出（009）、显式
  QAOA 来源提示（007）。旧版保留，仅 7/30 输入改变。未改变合同、标签或主 evaluator。
- N-033 / D-022：按研究者要求先补待审参考层。7例有结构 YES 的具体映射，3例未定；
  各例有定位锚点、意图与合同义务。可比较标签一致性、定位和计划覆盖，HOW 正确性
  仍需语义审核；没有已知结构 NO，不据此报告负类识别率或整题通过率。
- N-034 / D-023：通过现有 ChatGPT 订阅完成当前十例 C 条件两模型比较。均为结构
  参考一致 7/7、计划覆盖 7/7、定位锚点精确匹配 6/7；均保持经典 10/10。
  lit-003 有替代家族分歧；lit-009 两者均发现 pivot 搜索子步骤。support 字段解释不一。
  这些是探索性诊断，HOW 尚待人工审核，粗指标未拉开差距，不能稳定排名。
- N-035 / D-024：新增 DeepSeek Pro/Flash high/direct API，各十个 C 首次请求。
  Pro 10/10 有效，结构一致 7/7、计划覆盖 7/7、定位精确 5/7；Flash 9/10 有效，
  lit-009 达到 16384 completion-token 上限而无最终答案，不报删题后的全量分数。
  lit-002 两模型的不同 tie 编码错误均有可复现反例；HOW 内容可区分而粗标签仍饱和。
  不同 provider 脚手架/推理预算、单次采样和待审标签仍阻止稳定能力排名。
- N-036/037：D-026选择A，主张正确性与义务完成度分开。v0.2继承19份并补齐20份回答；
  40请求全部保留，39份/156项待审证据、200条完成度；1份预算失败不补造内容。
  评审准备包及保留集草案已生成；N-038收到两条lit-002公式反驳的支持意见，身份/独立性未知。
- 旧 baseline：10/10 有效响应且均保持经典，8 structural YES，所有 plan=null。
  受控诊断：8/8 structural YES 有条件计划，实际采用判断不变；支持“计划输出受
  指令耦合影响”的解释，不证明计划正确、收益或一般模型能力。
- 曾运行局部 Qiskit 原型；扩到16设备后有两个精确最优性失败，不能视为通用正确迁移。
  [保留的结果](demo/context001_qiskit/artifacts/device_limit_v011/README.md)。

## 当前计数与限制

N-040补齐剩余六题，10题均有局部判定链：61条输入、52个合成对照；不是完整方案或迁移通过。
当前集合为 **10 个母案例 / 30 个输入条件**，全部 DRAFT；最新复跑40次C请求、36份有效；
首轮40次C请求、39份有效单独保留，不能当成80个独立问题；A/B未跑。
原 `cases/` 仍有14个 DRAFT（10旧 pilot＋4 toy），不混入当前十组统计。
历史不同上下文/版本不能按文件夹数当作独立样本；v0.1.1 的六份副本不是六个新案例。
没有独立验证/冻结的科学标签，未建立端到端量子优势；具体语义/资源要求仍需逐例判断。
原 case.json 的空标签保持原样；当前暂定参考值只在版本表所指私有参考层。
实际适用性均未知，采用建议均暂定保持经典；这些常量不能单独区分模型。
SupermarQ 项目级署名仍可能提示来源，修复没有声称完全匿名。
CA6000 作业已交付文件，独立保留在 coursework/；默认不再推进，不是 FSE 证据。

## 下一步与人类决策

唯一短队列：[NEXT_ACTIONS.md](NEXT_ACTIONS.md)。不再重复修复或默认扩充案例。
A已接受并落实；[lit-002反馈已归档](pilot/how_review/adjudications/20260922-lit002/README.md)，
两条具体公式反驳获支持，不再重复询问；N-040已完成十题局部对照链。
N-044已完成009反例转录/可达链/回退边界与009/010候选源码核对，仍不升金标。
D-032已委托推进动态状态前提检查，不再等待用户先选择agent方法；N-045选定S/A/V/AV布局。
N-046已补新响应审核绑定与分开的开发/保留检查；N-047已完成runner和CLI 0.156.1重新预检。
N-048 / D-033的[25次配置](pilot/enhancement/state-workflow-v0.3/campaign/protocol.json)已执行完，
`all_slots_terminal`，不再发起调用。N-049设计已由N-050落实成16位置配置且完成预检；
N-051已完成全部16次和审核/回归，不再重做准备或在旧队列补采样。下一步落实N-049
缺失形式信息的单次补问接口，先离线验证输入边界和同预算对照，必要时在新版本澄清
“有限个检查”不等于“仅有限数值”。D-035已委托同方向订阅额度，具体新协议准备后可执行。
其余整题义务继续待审；用户学习说明按动作、目的、实际效果持续更新。
可用 [评审准备包](pilot/how_review/v0.2/reviewer_packet/GUIDE.md)建立参考；尚未开展独立盲审。
D-023/D-024/D-029/D-031/D-033/D-034各冻结队列均已执行完；D-035满足后续同方向现有订阅
额度授权，不逐轮重复询问。新付费渠道/QPU、标签或研究范围改变仍按科学/外部状态边界处理。
正式科学验收、替代边界和最终评分仍待确定；不把粗指标饱和直接作为设计 Agent 的依据。
近似合同 context-001 的质量比例定义已接受，容差仍待定（D-018），不阻塞其他精确案例。
更多债务在 [TODO.md](TODO.md)，未决科学问题在 [open_questions](docs/open_questions.md)。

## 最近验证（已有结果，不在每次读取时重跑）

N-051：[执行验收](pilot/enhancement/feedback-control-v0.1/execution-20260927/execution-validation.json)：
16行重放一致，输入/原文/绑定哈希和先调用后审核再评测时序通过；2921旧文件不变。
零工具事件/重试/QPU，论文未编辑；真实认证仅由已授权订阅CLI使用，未打印凭据。
N-050：[离线验收](pilot/enhancement/feedback-control-v0.1/validation.json)：32新版＋49回归通过，
16位置完整假传输及5项隔离预检通过；2764旧文件不变。正式attempt为0、无真实认证访问/推理/QPU。
N-049：[离线验收](pilot/enhancement/state-workflow-design-v0.1/validation.json)：
25行/90原文锚点核对，16输入差异与再生检查；2736个旧文件不变。零新模型/QPU调用，论文未编辑。
N-048：[执行验收](pilot/enhancement/state-workflow-v0.3/execution-20260926/execution-validation.json)：
25次/25份有效；输入与原文哈希、审核时序和25行评测重放全部一致；2429旧文件不变，
零工具事件/重试/QPU；论文未编辑。本轮复核实际运行产物，未重跑无改动的共享主测试套件。
N-047：[离线验证](pilot/enhancement/state-workflow-v0.3/validation.json)：26新版＋49回归通过，
五项隔离/请求预检通过；2391旧文件不变；零模型调用。共享主套件未重跑，论文未编辑。
N-046：[离线验证](pilot/enhancement/state-workflow-v0.2/validation.json)：37新版＋12前版回归通过，
57个可达pivot状态、780个抽象状态回归，evidence逐字节再生；2364旧文件不变；零模型调用。
N-045：[离线验证](pilot/enhancement/state-workflow-v0.1/validation.json)：12项针对性测试通过，
4条修订输入生成、零模型调用；2347个旧文件不变，局部链接通过；未重跑共享主套件。
N-044：[离线验证](pilot/enhancement/lit009-review-v0.1/validation.json)：7次历史pivot重放、6次敏感性追踪，
原文/源文件绑定、异常与无修改检查通过；2342个指定旧文件不变，局部链接通过。未重跑主套件或模型。
N-043：[最终审计](pilot/enhancement/lit002-v0.1/validation.json)：26项新测试通过，主套件223通过/15可选依赖跳过；
15响应重放、104定义期望核对，863个指定旧文件不变。没有QPU或完整迁移执行。
N-041：[最终核验](pilot/model_comparison/20260923-four-model-c-v0.1/validation.json)：28项离线测试通过，
40请求/36有效，7份转录与009反例重放，1654旧文件不变；无模型迁移/QPU执行，不重跑主套件。
N-040：[最终验证](artifacts/semantic_verification_v02/final/validation.json)：新增84项通过，主套件223通过/15跳过；
六组原程序及标签测试通过，1646个旧文件不变；保留着色判定器修复前失败记录，无新模型/QPU调用。
N-039：[实际验证](artifacts/semantic_verification_v01/after/validation.json)：新增42项通过；主套件139通过/15可选依赖跳过；
七组旧相关测试仍全部通过，1636个旧文件不变。无新模型/QPU调用；四题仅局部语义检查。
[N-031 实际日志](pilot/reference_completion/v0.1.1/validation.json)：新版73项通过
（61案例＋12版本/输入检查），原套件97通过/15可选依赖跳过，可选套件5通过；
六个新版案例与原十四案例验证/摘要通过，1189个受保护旧文件未变。四个修复前失败保留。
最近文档工作（N-032）仅整理入口，未开始实验、修改业务代码或重跑上述测试。
[文档校验与原文归档](artifacts/session_entry_20260921/README.md)。
N-033 新增标签/诊断的实际验证见 [validation.json](pilot/provisional_labels/v0.1/validation.json)；
当时的构造响应与小实例映射检查不是模型成绩。
N-034：[实际运行/验证](pilot/model_comparison/20260922-c-v0.1/validation.json)，
20/20 严格输出检查通过，319 个受保护参考/输入/评测文件未变；无输出修复或科学重试。
N-035：[验证](pilot/model_comparison/20260922-deepseek-c-v0.1/validation.json)：9 项离线测试通过，
20 次 HTTP/19 份有效回答、2 份公式反例及原程序核验；458 个受保护文件未变。
N-036：[验证](pilot/how_review/v0.1/validation.json)：原文绑定/复现通过，1593个旧文件未变；
历史有限检查保留；N-037 [验证](pilot/how_review/v0.2/validation.json)：1605个旧文件未变，4项记录防错测试通过；
新增001加权图761、007带符号图1100、005谓词实例6472检查；双记录/盲包复现通过，非完整迁移证明。
Git 当前含未跟踪工作；本次未暂存、提交或推送。文件持久化不等于已有 Git 历史。

历史查阅：[CHANGELOG](CHANGELOG.md) · [研究日志](docs/research_log.md) ·
[整理前完整状态和队列](artifacts/session_entry_20260921/README.md)。
