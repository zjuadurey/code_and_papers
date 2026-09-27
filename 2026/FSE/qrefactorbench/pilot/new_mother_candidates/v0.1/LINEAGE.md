# 谱系与候选筛选记录

2026-09-27。人工/AI协调者来源核对，不是盲审或独立性统计检验。
来源分组与任务分组分开：不同仓库不必然独立；相同家族也不必然同题。
本轮没有系统穷尽公开仓库，以下只是有证据的定向准备记录，不报告筛选召回率。

## 旧十例的对照基线

路径取自当前PROJECT_STATUS所指版本；相关原核/改编记录都在3555项保护哈希中。
“不重复”仅指尚未发现复用原核或相同业务计算，不是确认可随机拆分。

| 旧例/来源 | 原计算及合同证据 | C01/C02/C03的关系 |
|---|---|---|
| 001 C2Q | [MaxCut核](../../source_adaptations/v0.1/cases/lit-001/kernel.py)：二分、加权cut、递增mask首次最大值 | C01非图；C02所有城市闭合排列而非二分；C03路径枚举而非cut |
| 002 C2Q | [最小顶点覆盖核](../../source_adaptations/v0.1/cases/lit-002/kernel.py)：按基数和组合顺序首个覆盖 | C01文本；C02固定全节点排列；C03所有路径输出而非覆盖子集 |
| 003 C2Q 97/98 | [agenda.complete](../../source_adaptations/v0.2-where/cases/lit-003/agenda.py)：依次试槽并回溯，preview另有语义；[谱系](../../source_adaptations/v0.2-where/cases/lit-003/ADAPTATION.md) | C02位置one-hot形式有编码相似，但约束/目标/源递推不同；C03也遍历但不解着色；C01无槽分配 |
| 004 C2Q 88/93 | [程序内选群](../../source_adaptations/v0.2-where/cases/lit-004/program.py)：最大团、mask tie、历史关系与preview；[谱系](../../source_adaptations/v0.2-where/cases/lit-004/ADAPTATION.md) | C02每节点恰一次且只计邻位边，不是两两兼容子集；C03要求邻接链不要求团；C01无图 |
| 005 QuanBench03/QuanBench+03，同一母题 | [SAT核](../../reference_completion/v0.1.1/cases/lit-005/kernel.py)及[改编](../../reference_completion/v0.1.1/cases/lit-005/ADAPTATION.md)：有锁、首个布尔见证 | 三者都可抽象为约束不代表同源；C01相等块、C02最优闭环、C03全路径；不能仅凭都是Grover/SAT归约判断独立 |
| 006 QuanBench05 | [容量DP核](../../reference_completion/v0.1.1/cases/lit-006/kernel.py)及[改编](../../reference_completion/v0.1.1/cases/lit-006/ADAPTATION.md)：容量表选择子集、numeric-mask tie | C02虽也DP，其状态为当前城市/剩余集合，输出所有城市次序，原核不同；C01双序列索引DP，C03无容量目标 |
| 007 SupermarQ signed SK | [signed score核](../../reference_completion/v0.1.1/cases/lit-007/kernel.py)及[改编](../../reference_completion/v0.1.1/cases/lit-007/ADAPTATION.md)：signed cut/Ising，与001任务结构相关 | C02可编码QUBO但原计算非二值两组偏好；其余非该目标；001/007不得机械计为独立任务族 |
| 008 Qiskit HumanEval53 | [XOR核](../../reference_completion/v0.1.1/cases/lit-008/kernel.py)：八位XOR/回执 | 三者不是固定按位编码任务；不据此推断008负类标签 |
| 009 HPL文档改编 | [高斯消元/pivot核](../../reference_completion/v0.1.1/cases/lit-009/kernel.py)：浮点行状态与按序max | C01同有max/tie义务，但域、比较对象、缓存/过滤及来源不同；C02排列DP，C03惰性枚举；本轮没有拿新浮点状态冒充母题 |
| 010 HPCG改编 | [预算CG核](../../reference_completion/v0.1.1/cases/lit-010/kernel.py)：稀疏乘法、残差、停机/轨迹 | 三者不复用CG递推；cache/cutoff资源参数不使其变成010变体 |

## 暂定新组与不单列选项

| 选项 | 处理 | 证据/理由 |
|---|---|---|
| C01 `find_longest_match` | 保留档案，建议来源/合同评审 | [C01](C01_TEXT.md)，源CPython，无旧例的直接代码谱系；条件搜索，不认定全API可替换 |
| C02 `solve_tsp_dynamic_programming` | 保留档案，建议来源/合同评审 | [C02](C02_TSP.md)，源python-tsp，闭合全排列；保留包环境和tie缺口 |
| C03 `all_simple_paths` | 保留边界档案，正例资格未定 | [C03](C03_PATHS.md)，源NetworkX，全部惰性输出使单见证映射不足；不以负标签凑平衡 |
| python-tsp `solve_tsp_brute_force` | 不另建第四份/不增加N | [同commit原代码](sources/python-tsp/python_tsp/exact/brute_force.py)，仍为相同距离矩阵闭合TSP；算法实现不同也记录同母题组，未执行 |
| difflib `get_matching_blocks` / `ratio` | 不另建第四份/不增加N | [同文件](sources/cpython/Lib/difflib.py)421/597行起，直接消费最长块；可作上下文，不能作为本批独立母题 |

最终准备三份而非四份，因为本批可核查的另外两个选项是已选原核的另一实现/调用链。
这是范围内主动停止，不声称不存在其他独立问题。没有根据模型难易、输出质量、正例比例或
量子收益预期排除任何已建档来源。新三组没有被分配train/dev/test，也不直接增加正式N。

## 暴露与分组约束

- 固定commit及SHA只保证引用版本，不保证未被预训练或无人见过。
- 协调者已看三个来源并写检查；本包所有测试均已用于本地开发，不是未来隔离验证集。
- 若评审通过，同一母题的来源、改编、A/B/C视图、参数实例及替代算法保持同组；
  先决定分组单位和角色隔离，再做split。不能将n=3的64张图算64个独立程序。
- 现有001/007的cut谱系、005两个来源的同公式谱系是需要延续的旧分组事实，不在本轮重标旧案例。
