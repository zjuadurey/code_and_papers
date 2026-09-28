# Mac 接续交接 — 2026-09-28

本页是跨机器操作说明；研究当前状态仍以[PROJECT_STATUS](../PROJECT_STATUS.md)为准。
用户要求保存当前进度，在Mac继续。无需重新解释idea；在同步后的FSE/或qrefactorbench/
打开会话说“读取当前目录”即可恢复，说“继续”才推进已授权工作。

## 1. 当前目标与已经完成的工作

研究目标：从经典程序推导保持原行为时，哪些量子方案在什么规模、资源与成本条件下
具有潜在端到端优势。行为合同和强经典对照仍是核心。D-043已明确：没有大规模量子机
也要通过小规模验证、算法/结构公式及跨层资源估算推进，不能用小实例没有加速替代规模分析。

| 材料 | 实际完成 | 证据边界 |
|---|---|---|
| [公式与潜在优势](../pilot/benefit_analysis/maxcut-formulas-v0.1/REPORT.md) | 45组小规模状态核验，8项测试，11次100/200/500逻辑位QDK估算，2376条件点 | 已有条件预测，实际大规模成功率和证书成本仍未知 |
| [数学推导](../pilot/benefit_analysis/maxcut-formulas-v0.1/DERIVATION.md) | 门数/显式调度深度、获证概率及精确回退的成本反解 | 结构恒等式、概率假设、物理模型分别记录 |
| [8–64节点规模诊断](../pilot/benefit_analysis/maxcut-scaling-v0.1/REPORT.md) | 18经典实例14完成/4超时，18次QDK估算成功 | 必要时间预算；超时不是完成耗时 |
| [lit-001实际模型闭环](../pilot/llm_workflow/lit001-v0.1/README.md) | 4次模型调用，生成电路/验证/资源估算/结论 | 给定四节点及QAOA家族的闭环，不是一般程序自动迁移 |

公式工作包的具体例子：100逻辑qubit、p=1，在指定假设模型下为13310物理qubit、1.6ms/shot。
若经典同任务T=1s、固定成本A=10ms、逐shot验证/解码v=0.1ms、S=64、失败回退F=T，
则单shot可靠获证率s>0.197415%时预测期望收益；s=1%时为0.644396s，约1.552倍。
T/A/v/s是条件，不是已测100位实例表现；不能写成已实现量子优势。

原lit-001 wrapper最大16节点，旧电路解析器固定4位；100/200/500位是独立kernel分析。
旧all-edges证书对含正权三角形的图必拒绝，不能直接当一般图最优性/tie证书。
正式case/gold/split、论文数值和旧原始实验均未修改。

## 2. 新提供的真机资源：LogicalQubit

用户说“我现在有100bit的真机云平台，可以用来做小规模实验”，并提供：
<https://cloud.logicalqubit.com/landing/>。

2026-09-28公开资料核查（本次未登录、未读取凭据、未查用户账户、未提交任务）：

- [厂商2026-07-09介绍](https://logicalqubit.com/news/140.html)明确AGate-100采用物理超导qubit，
  不是100个纠错逻辑qubit。“逻辑比特”也用于公司名称，不能仅按名称推断硬件级别。
- 厂商公布并行双比特门保真度中位数99.5%、并行读出98.6%；这些是公开指标，
  不能替代实际后端、具体物理位、执行日期的校准数据。
- [lqcloud 0.5.0发布说明](https://pypi.org/project/lqcloud/0.5.0/)支持原生CZ、RX/CX等复合门分解、
  指定initial_layout、counts/memory结果、批量提交；声明最多64条线路、每次1..50000 shots。
  具体账户权限、价格、可用后端和校准时间尚未核实；示例后端名不可当成用户实际可用后端。
- SDK支持读出矫正/DD；实验需要固定开关并保存实际生效信息，原始与处理后数据分开。
- 公共控制台HTML中的零余额/空后端列表是未登录页面占位，不能当作用户账户情况。

拟议用途：同一批4/6/8/10/12位小案例比较理想模拟和真机结果，记录目标输出概率、
深度/路由开销、验证/回退频率；根据平台实际暴露字段区分排队、网络墙钟、QPU执行时间。
重复批次/日期用于观察漂移，有限小图实测不直接证明100位成功率规律。
真机NISQ数据和未来纠错资源估算是两层证据，不能把二者的qubit、错误率、时间直接互换。

当前只完成公开资料核查；SDK适配、后端查询及实验协议尚未实现。本次“保存文档”
不新增安装/真机/付费授权。后续先完成可审核的本地方案和任务用量，再按实际授权提交。
凭据在Mac本机配置，不发送到聊天，不写入仓库或转移包。

## 3. 从当前机器带走什么

**必须同步整个当前FSE工作目录，包含未提交和未跟踪文件。仅git pull/clone不能保证包含本轮成果。**
当前没有为交接提交、推送或执行跨机器传输；同步仍需用户完成。

至少保留：

- FSE工作区入口AGENTS.md及完整qrefactorbench/（源码、tests、schemas、docs、pilot、artifacts）。
- 上表三个pilot工作包内的原始run/、JSON、QASM、manifest、图片及脚本，不能只带REPORT。
- [当前论文目录paper/](../../paper/HANDOFF.md)：这是独立Git工作树，主文件paper/main.tex。
  qrefactorbench/paper下旧草稿和latex.zip为快照，不是当前编辑入口。

不要把Linux的Conda环境目录当作Mac环境复制；在Mac重建。用户目录中的认证文件不属于项目同步。
FSE可能处于更大的Git工作树中，不重新git init，也不清理已有未跟踪文件。

## 4. Mac环境方案

Linux已验证环境：Python3.10.21；numpy1.26.4、scipy1.14.1、matplotlib3.9.4、
pytest9.1.1、qdk1.32.3。Mac未实际运行验证。

**Mac建议独立Python3.11环境**，兼顾本项目与lqcloud0.5.0所需`>=3.11,<3.13`。
已查[QDK1.32.3发行文件](https://pypi.org/project/qdk/1.32.3/#files)及
[pyqir0.12.5发行文件](https://pypi.org/project/pyqir/0.12.5/#files)：均有macOS arm64/x86_64 wheel。
发行文件存在不等于本项目已经在Apple Silicon/Intel Mac验收。

在Mac已有Conda、用户决定安装依赖时，从qrefactorbench/根目录执行以下参考命令：

```bash
conda create -n qrefactor-mac -c conda-forge python=3.11 pip
conda activate qrefactor-mac
python -m pip install -e '.[test,resources]' 'numpy==1.26.4' 'scipy==1.14.1' 'matplotlib==3.9.4' 'pandas==2.2.3' 'pyqir==0.12.5'
python -m pip check
```

这是重建方案，不是完整传递依赖锁文件。不要升级现有模型/SDK并回写旧实验结果。
真正开始云适配、获安装授权后才另装`lqcloud==0.5.0`；本地公式测试不需要它。
其本机认证支持LQCLOUD_API_KEY等方式；配置细节见官方SDK说明，不在此放任何真实凭据。

## 5. Mac先做的本地验证

以下均在qrefactorbench/根目录，复用已建环境；不调用模型、不提交QPU：

```bash
python -B -m pytest -q -p no:cacheprovider pilot/benefit_analysis/maxcut-formulas-v0.1/test_formulas.py
python -B -m pytest -q -p no:cacheprovider tests/test_resource_workflow.py
```

第一条Linux已有8通过；第二条历史Linux为30通过，包含本地QDK联调。
Mac实际结果必须另记，不能复制Linux数字作为Mac验收。

如需要重放45小实例与11次大规模本地资源估算，使用新目录：

```bash
mac_check_dir=$(mktemp -d)
python -B pilot/benefit_analysis/maxcut-formulas-v0.1/run.py --output "$mac_check_dir/formula-run"
```

完成后保留这个目录并记录Mac型号/架构、Python及包版本。源文件和协议一致时比较逻辑计数、
小规模数值容差与QDK资源点；估算器自身墙钟不要求相同。不要覆盖归档run/。
不要直接再跑本包report.py：目前它固定读取归档run/且用排他写入，已有报告会拒绝覆盖；
如需为Mac新结果作图，先增加新输入/输出参数，不改历史报告。

保存模型产物的lit-001 replay也可作后续本地验证，见[环境说明](quantum_advantage/ENVIRONMENT.md)。
**真实模型runner使用Linux/WSL的bwrap隔离，在原生Mac上不能照搬执行。**
Mac原生适配尚未实现，不为连通而绕过私有资料隔离；当前公式/QDK路线不依赖该runner。

## 6. 接续优先级与边界

1. 确认同步包含本页和最新公式工作包，做最小Mac本地验证并保存真实结果。
2. 在现有范围内准备LogicalQubit本地适配和离线预检：门分解、物理位映射、位序、
   测量barrier、原始counts、任务配置/hash和不提交的dry-run。
3. 明确用户可用后端、拓扑/校准、任务数量/shots/费用后形成具体真机协议；
   保留失败/重试/实际成本，不因提供平台链接就假定已经授权任意真机用量。
4. 实测概率/成本校准对应的小规模物理模型；一般图精确证书与大规模潜在收益条件继续分开取证。

不重做已经完成的四节点LLM闭环、公式推导或历史模型队列；不改正式case/gold/近似许可。
没有真机也不阻塞公式研究，有真机则增加校准证据。无需用户重新解释这些原则。
