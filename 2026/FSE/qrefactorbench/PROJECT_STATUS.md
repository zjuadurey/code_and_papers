# QRefactorBench 当前状态

更新：2026-09-22。本页是当前状态；历史过程见 CHANGELOG 和研究日志。

## 研究目的与阶段

帮助非量子专家分析**已有经典软件**的 WHERE／WHETHER／HOW，最终选择性重构为
保持原软件合同、有收益证据的混合程序。当前为 **Phase 1：benchmark 案例建设与
任务验证**，已有四模型 C 条件比较及 HOW 待审规则试审；尚无验证/冻结的 benchmark。
完整研究意图见 [研究纲领](docs/RESEARCH_CHARTER.md)。不在设计最终 Agent。

## 当前版本与材料位置

| 用途 | 当前指针 | 使用边界 |
|---|---|---|
| 当前十组来源案例及审核修复 | [reference_completion/v0.1.1](pilot/reference_completion/v0.1.1/README.md) | DRAFT 工作包；不是旧 pilot 的十个案例 |
| 当前 A/B/C 输入 | [30 份输入 manifest](pilot/reference_completion/v0.1.1/review_inputs/manifest.json) | 十个母案例×三个条件；本轮只跑 C，只给模型单份 txt |
| 当前暂定参考标签 | [provisional_labels/v0.1](pilot/provisional_labels/v0.1/README.md) | 私有 DRAFT/PENDING 标签与可执行诊断；不是金标，不给模型 |
| 当前包首轮模型比较 | [2026-09-22 小报告](pilot/model_comparison/20260922-c-v0.1/REPORT.md) | Sol/Astra medium，各 10 个 C；20/20 有效，暂定参考诊断 |
| 当前四模型比较（含 DeepSeek 补测） | [四模型小报告](pilot/model_comparison/20260922-deepseek-c-v0.1/REPORT.md) | Pro 10/10、Flash 9/10 有效；Flash 一题预算截断；含两份 HOW 反例 |
| 当前 HOW 审核提案与试审 | [how_review/v0.1](pilot/how_review/v0.1/README.md) | 五例×四模型；19份回答试审、1份预算失败；AI/PENDING，无新总分 |
| 订阅连通性试跑 | [2026-09-22 smoke](artifacts/subscription_smoke_20260922/README.md) | Sol/Astra 各一次短响应成功；不是 benchmark 运行 |
| 来源与评测方法 | [覆盖表](pilot/reference_completion/v0.1/COVERAGE.md) / [方法与结果](pilot/reference_completion/v0.1/METHODS.md) | v0.1 保留来源及方法夹具；不是模型分数 |
| 原 baseline 的冻结输入 | [pilot/packets-v0.1](pilot/packets-v0.1/) | 历史实验输入，不是当前 A/B/C 包 |
| 原 baseline 结果 | [Restricted Codex CLI](pilot/baseline-v0.1/restricted-codex/BASELINE_RESULTS.md) | 已完成；非 raw API baseline；DRAFT-reference 评价 |
| 条件计划诊断 | [paired diagnostic](pilot/baseline-v0.1/conditional-plan-diagnostic/CONDITIONAL_PLAN_DIAGNOSTIC_RESULTS.md) | 已完成，不算第二个独立模型 baseline |

## 已完成与可支持的结论

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
- N-036：HOW 四项证据规则及五例试审已准备；区分公式反例、狭义支持与未完成义务。
  40请求全部列清单，19回答/76项试审，其余20回答未做本轮内容审核；正式口径待研究者确认。
- 旧 baseline：10/10 有效响应且均保持经典，8 structural YES，所有 plan=null。
  受控诊断：8/8 structural YES 有条件计划，实际采用判断不变；支持“计划输出受
  指令耦合影响”的解释，不证明计划正确、收益或一般模型能力。
- 曾运行局部 Qiskit 原型；扩到16设备后有两个精确最优性失败，不能视为通用正确迁移。
  [保留的结果](demo/context001_qiskit/artifacts/device_limit_v011/README.md)。

## 当前计数与限制

当前集合为 **10 个母案例 / 30 个输入条件**，全部 DRAFT；四模型共 40 次 C 请求、39 份有效回答，A/B 未跑。
原 `cases/` 仍有14个 DRAFT（10旧 pilot＋4 toy），不混入当前十组统计。
历史不同上下文/版本不能按文件夹数当作独立样本；v0.1.1 的六份副本不是六个新案例。
没有独立验证/冻结的科学标签，未建立端到端量子优势；具体语义/资源要求仍需逐例判断。
原 case.json 的空标签保持原样；当前暂定参考值只在版本表所指私有参考层。
实际适用性均未知，采用建议均暂定保持经典；这些常量不能单独区分模型。
SupermarQ 项目级署名仍可能提示来源，修复没有声称完全匿名。
CA6000 作业已交付文件，独立保留在 coursework/；默认不再推进，不是 FSE 证据。

## 下一步与人类决策

唯一短队列：[NEXT_ACTIONS.md](NEXT_ACTIONS.md)。不再重复修复或默认扩充案例。
HOW 提案、反例复现和五例试审已完成；下一步确认 [HOW 正式口径](pilot/how_review/v0.1/DECISION_REQUEST.md)：
建议条件计划的主张正确性与义务完成度分开记录；另一选择是新增可执行编码任务。
这是操作口径/任务选择，不是批准全部案例标签；所有试审仍非独立注释或 gold。
D-023/D-024 均已完成；Flash 增预算补测、重复采样或 A/B 运行需新授权。
正式科学验收、替代边界和最终评分仍待确定；不把粗指标饱和直接作为设计 Agent 的依据。
近似合同 context-001 的质量比例定义已接受，容差仍待定（D-018），不阻塞其他精确案例。
更多债务在 [TODO.md](TODO.md)，未决科学问题在 [open_questions](docs/open_questions.md)。

## 最近验证（已有结果，不在每次读取时重跑）

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
覆盖/团各1100图、背包4100实例、着色排序499向量、pivot3905有限列检查；非完整迁移证明。
Git 当前含未跟踪工作；本次未暂存、提交或推送。文件持久化不等于已有 Git 历史。

历史查阅：[CHANGELOG](CHANGELOG.md) · [研究日志](docs/research_log.md) ·
[整理前完整状态和队列](artifacts/session_entry_20260921/README.md)。
