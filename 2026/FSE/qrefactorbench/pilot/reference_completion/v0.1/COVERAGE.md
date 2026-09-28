# 指定参考 benchmark 的实际落地清单

本页的“落实”必须能指向具体程序/测试/输出，不以阅读文献代替交付。所有来源固定
在 [sources/manifest.json](sources/manifest.json)，旧 C2|Q> 源版本见原来源包。
来源贡献有别于软件出处：用 quantum task 写经典程序，不能称复用原作者的经典应用。

| 指定参考 | 具体采用内容 | 案例落地 | 可执行方法落地 | 未声称完成 |
|---|---|---|---|---|
| C2\|Q> | 固定 rows 164/427、97/98、88/93 | 既有 lit-001–004，纳入十组输入 | 复用其已有逐赋值/完整报告/原函数对应测试 | 没有把旧本地 SAT/归档案例改称来自 C2Q |
| QuanBench | [03/05](sources/quanbench.jsonl) 题面、[Pass@k 实现](sources/quanbench_evaluation.py) | lit-005 六子句配置；lit-006 五物品源实例＋窗口上下文 | `methods.pass_at_k`，函数/反例测试，酉线路 `process_overlap` | 不接受 05 的可疑测试串；不复现其模型分数 |
| QuanBench+ | 固定 [Qiskit 03](sources/quanplus_qiskit.jsonl)、[get_kl_div](sources/quanplus_kl.py) | 03 关联到 lit-005，同一问题不重复计数 | 实际执行其 KL 函数，并展示方向、截断、阈值与本地描述性报告的区别 | 不新增一个“独立 SAT 案例”，不照搬 0.05 |
| Qiskit HumanEval | [task 53](sources/qhe.json) 和三个测试输入 | lit-008 新经典全量回执控制 | 三个原例逐一通过；全 65,536 字节对；边界/错误端序测试 | 没有把已知量子 XOR 实现当成迁移收益证据 |
| PQID-Bench | [structural_result](sources/pqid_worker.py)，固定 count-map predicate | 不强造不相关经典源案例 | 直接提取执行四个已审纯函数：同结构检查通过但语义不同；本地签名工具与之对应 | 不叫语义证明，不下载/运行其模型响应或 Docker |
| MQT Bench | [QAOA create_circuit](sources/mqt_qaoa.py)，固定 seed/层数 | 不把参数线路伪装成一个新经典应用 | 实际运行生成函数，仅移除注册装饰器；既有 `extract_resources` 比较表示层，并核对等价 | 不运行优化器，不做物理布局或硬件收益报告 |
| SupermarQ | [SK ±1 score](sources/supermarq.py) 和目标期望 | lit-007 新有符号偏好程序，源 energy 方法逐赋值比对 | 期望 gap 与分布差分别运行，零参考值也能描述 | 不把注释中的 Hellinger 与当前 score 实现混同，不执行五次变分优化 |
| LINPACK / HPL | [HPL 求解和 backward error](sources/hpl_algorithm.html) | lit-009 新 Python 数值范围控制 | 部分主元例、精确有理数对照、归一化残差错解见证 | 本次采用的是 HPL，不是另外复现 LINPACK；无官方性能跑分 |
| HPCG | [CG_ref](sources/hpcg_CG.cpp)、[SPMV_ref](sources/hpcg_SPMV.cpp)、[TestSymmetry](sources/hpcg_symmetry.cpp) | lit-010 新无预条件迭代流程 | 稀疏/稠密检查、bilinear symmetry defect、预算/轨迹错误替换见证 | 无 MPI/多重网格/官方评分；不新增线性求解量子家族 |

## 怎样判断这次补上了，而不是再次换说法

- 六个新程序的 `example_request.json` 能实际运行，输出可与已存报告和独立测试对照。
- 每个 ADAPTATION 区分源题面/源公式/源算法与新上下文要求；许可证和来源 SHA 留存。
- 每种采用的评测方法都有执行检查、故障见证或源函数对应，结果可重生。
- source-task 改编仍是合成软件，不声称找到六个真实部署仓库。
- 所有 10 组有具体外部出处，但 cut/Ising、SAT、背包和线性迭代有交叉，不能据此
  推断十个独立任务家族或最终独立数据划分。

## 更正先前 QuanBench+ 记录

旧 [来源审计](../../source_adaptations/v0.2-where/REFERENCE_BENCHMARK_AUDIT.md) 使用
`JawadKotaich/quanbench-plus` 得到 404。论文 v2 的实际地址是
[JawadKotaichh/quanbench-plus](https://github.com/JawadKotaichh/quanbench-plus)，
本轮确认并固定到 `2dfd1a863b13d3762a734ed96742adb39e65e34b`。这是前次查证不充分的
更正，不是刚刚出现的新资源。旧记录不重写，本页作为后续证据与状态更正。
