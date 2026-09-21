# 补齐参考 benchmark：10 组有出处案例与可执行评测检查

**DRAFT；未运行新模型实验，未变更科学标签或正式评分。**

本包补的是原要求的两项欠账：从指定 benchmark 的**具体任务/算法**构建案例，
以及把参考评测方法落实为**实际运行的代码与结果**。此前 6 组本地合成扩展不计入
这里的外部来源完成数，也没有被删除或改称有出处。

现有 4 组 C2|Q> 来源案例，加上本次 **6 个新程序**，形成 **10 组来源可追溯的
任务改编**。它们不是 10 个独立量子算法，也不是 10 份原作者的经典应用软件：
量子任务来源改编出的经典实现和业务上下文均明确注明是我们新写的。

## 案例清单

| 母案例 | 具体来源 | 经典软件功能 / WHERE 重点 | 本次状态 |
|---|---|---|---|
| lit-001 | C2\|Q> row 164 | 维护安排、当前/拟议冲突与变更报告 | 复用既有核心＋context-001 |
| lit-002 | C2\|Q> row 427 | 检查覆盖、工作清单与责任转移 | 复用既有核心＋context-002 |
| lit-003 | C2\|Q> rows 97/98 | 议程预览与完整补全的不同职责 | 复用已有两视图 |
| lit-004 | C2\|Q> rows 88/93 | 最新兼容记录、过滤、预览与最大组合 | 复用已有两视图 |
| [lit-005](cases/lit-005/ADAPTATION.md) | QuanBench **03**；QuanBench+ **03** 同一公式 | 命名功能约束、锁定选择、保留合法当前状态 | 新经典实现＋9 项测试 |
| [lit-006](cases/lit-006/ADAPTATION.md) | QuanBench **05** 背包问题 | 活跃物品过滤、独立传输窗口、DP 与传输偏移 | 新经典实现＋9 项测试 |
| [lit-007](cases/lit-007/ADAPTATION.md) | SupermarQ **QAOAVanillaProxy** signed SK objective | together/apart 偏好、当前分数、最大分数、移动报告 | 适配评分公式＋新选择流程；8 项测试 |
| [lit-008](cases/lit-008/ADAPTATION.md) | Qiskit HumanEval **53** | 8 位异或的全量有序回执、直方图与前缀校验 | 新经典实现；待审范围控制；9 项测试 |
| [lit-009](cases/lit-009/ADAPTATION.md) | HPL **Algorithm / Checking the Solution** | 稠密平衡系统的检查/求解、残差、命名增量 | 新 Python 实现；待审范围控制；8 项测试 |
| [lit-010](cases/lit-010/ADAPTATION.md) | HPCG **CG_ref / SPMV_ref** | 稀疏迭代、多内核依赖、预算、残差轨迹 | 手工算法适配；待审范围控制；13 项测试 |

管线只支持原来的 search/optimization 正向家族。后三个控制的标签仍是 null，
`hard_negative` 仅为 DRAFT 抽样提案；没有宣布它们绝不可能量子化，也没有加入
HHL、线性系统、可逆布尔等新正向家族。WHERE 可提名后由 WHETHER 排除或保留不确定。

每个新程序都有 `program.py`、`kernel.py`、严格输入校验、公共合同、输入/完整输出
示例、独立/反例测试、来源与改变说明；不只是一个案例标题。数值问题没有被包装成
HPL/HPCG 正式跑分，案例没有从旧模型表现中挑选或标注。

## 每组 A/B/C，实际准备了 30 份输入

[review_inputs/manifest.json](review_inputs/manifest.json)记录十组，每组 A 核心、B 全程序＋
文件/行范围提示、C 同一全程序无提示。**B 去掉唯一 cue 后和 C 完全一致。**
旧 4 组源文件保持原样；新增许可证说明不回写旧包。提示仍需人审，不能当作金标。
负向控制的 B 也只是待审关注区域，不证明适用性；评估提示是否诱导过量提名是
协议审阅事项。30 份不是 30 个独立问题。未来结果须按母案例与条件分开保存；
B/C 的 prediction case_id 相同，不能混装进要求 case_id 唯一的同一次收集。

允许列表检查只证明未打包私有注释、答案或测试，**不证明完全没有任务提示**。
NOTICE 保留了来源项目、任务编号及许可；源代码也保留有意义的命名。这些可能帮助
识别已有任务，须在正式运行前审查并固定来源信息展示政策，不能称为匿名/完全盲测。

只给模型单个 txt，不能提供包含本页、测试、来源参考答案和方法结果的父目录。
全部条件共用 [既有 WHERE 草案任务](../../where_review/v0.1/TASK.md)，不混入旧 baseline。
这不是授权运行：没有新增模型 runner、API 配置或代理系统。

## 评测已经落地在哪里

完整对照见 [COVERAGE.md](COVERAGE.md)，方法定义与限度见 [METHODS.md](METHODS.md)。
实际原始数值：[METHOD_RESULTS.json](METHOD_RESULTS.json)。

- HumanEval/QuanBench：函数入口测试＋有实际采样分母才可用的 Pass@k 计算器。
- QuanBench/QuanBench+：单独的分布偏差与小型酉线路过程重合度；不照搬阈值。
- PQID：实际调用其固定版计数签名函数，构造同签名、不同语义的线路见证。
- MQT：实际执行固定版生成函数，用既有资源提取器报告逻辑门与基础门两个表示层。
- SupermarQ：源评分公式逐赋值核对；期望目标差与分布差分开。
- HPL/HPCG：实际残差、稀疏/稠密一致性与对称性检查，保留调用者预算和输出轨迹。

没有把这些检查自动接入主 evaluator 或定义新科学通过线。工程反例不是模型成绩，
能运行、结构相同、分布相同、目标值相同，各自能支持的结论不同。

## 来源审查发现的实质问题

1. **先前 QuanBench+ URL 写错了。** 正确用户名是 `JawadKotaichh`（两个 h），
   已取得固定版任务、KL 函数和 MIT 许可。此前“404，未落地”只在旧记录中保留，
   不能继续当作阻塞理由。
2. QuanBench 05 的测试字符串长度与五个物品不一致，canonical 顶层函数没有 return；
   原样保存。新经典例子根据题面数据独立验证出价值 8/物品 0、4，不复制错误答案。
3. SupermarQ 固定版的类文字与 `score()` 实现不是同一个度量；根据实际代码记录。
   不把带零/符号风险的分母直接当成我们的质量比。

## 实际验证和复现

六个案例 **56 passed**；描述性方法 **14 passed**；Qiskit 方法 **5 passed**；
来源/盲输入/重生检查 **6 passed**，当前新增共 **81 passed**。
首次 Qiskit 检查为 2 failed/3 passed，原因是新归一化函数拒绝 NumPy scalar；
已修复为接受有限实数并转换为 Python 数值，原失败日志保留，没有放宽断言或阈值。
其余检查、旧文件保护和原仓库回归见 [validation.json](validation.json)。
原仓库为 **97 passed / 15 optional skips**，既有可选套件 **5 passed**；
六个新案例和十四个原案例均校验通过。最终核对 **1170 个旧文件未变**、
22 份来源文件和 30 份输入哈希一致、222 个本地 Markdown 路径均存在；
见 [完整性记录](validation/final_integrity.json)。未检查远程链接或 Markdown 锚点。

```bash
# 在仓库根目录，使用既有环境；不安装依赖。
PY=/home/audrey/miniconda3/envs/palqo/bin/python
$PY -B pilot/reference_completion/v0.1/cases/lit-006/program.py < pilot/reference_completion/v0.1/cases/lit-006/example_request.json
$PY -m qrefactorbench validate pilot/reference_completion/v0.1/cases/
$PY -B -m pytest -q pilot/reference_completion/v0.1/test_methods.py pilot/reference_completion/v0.1/test_package.py
# 各案例有同名模块，分别运行 pytest，不把六个目录一次收集进同一个解释器。
$PY -B -m pytest -q pilot/reference_completion/v0.1/cases/lit-006/test_program.py
PYTHONPATH=. /home/audrey/miniconda3/envs/htp-static/bin/python -B pilot/reference_completion/v0.1/run_method_checks.py --output /tmp/reference-methods-new.json
$PY -B pilot/reference_completion/v0.1/build_package.py --prepare /tmp/reference-inputs-new
```

输出路径必须不存在。`--materialize` 是初次生成元数据用，已有记录拒绝覆盖。
源代码/题面归属逐文件保留；新实现包许可证仍 NOASSERTION，HPL 页面许可仍未知。
研究者需要审功能要求、候选边界和方法适用范围；通过测试不替代独立注释。
