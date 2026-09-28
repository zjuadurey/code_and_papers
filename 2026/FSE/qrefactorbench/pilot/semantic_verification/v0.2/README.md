# 全部十题的局部验证链 v0.2（N-040）

继续用户“另外6个case不改吗”的要求。本版补齐 001/003/006/007/009/010 的
配套契约、独立 oracle、正确/等价/错误对照和实际运行；原四题从 v0.1 兼容继承。
**10/10 题现在都有经过对照检验的局部判定链，不代表十题完整方案或迁移通过。**
原程序、公开输入、标签、模型回答、历史分数与 v0.1 材料均未改写。

## 新补的六题

| 案例 | 检查什么 | 能区分的错误例子 | 输入数 | 正确/等价通过 | 错误拒绝 |
|---|---|---|---:|---:|---:|
| 001 加权最大割 | 加权目标、优化方向、规范化 mask | 忽略权重；最大化写成最小化；大整数转浮点丢排序 | 5 | 2/2 | 3/3 |
| 003 图着色 | 二进制搜索谓词或 one-hot QUBO 的合法解对应、极值界、首解/无解 | 漏边；接受非法颜色码；漏 one-hot；把贪心失败当无解；负惩罚 | 6 | 4/4 | 5/5 |
| 006 背包 | 价值、容量、整数选择、mask tie、slack 解码 | 忽略容量/价值；tie反向；容量等式漏slack | 7 | 2/2 | 4/4 |
| 007 带符号偏好 | 正负权重含义、目标方向、规范化解码 | 丢弃负号；优化方向反转 | 5 | 2/2 | 2/2 |
| 009 线性求解 | active-suffix pivot 的绝对值/首索引规则；小系统解及残差 | 按带符号值选pivot；选择最后并列者；忽略rhs | 8 | 2/2 | 3/3 |
| 010 有预算迭代 | 初值、停止条件、零/一步结果和轨迹 | 用精确解替代一步结果；忽略预算；遗漏轨迹 | 7 | 2/2 | 3/3 |

合并原四题后共 **61 条测试输入、52 个合成对照**，22 个正确/等价对照通过，
30 个错误对照被拒绝。样卷都是用于检查评测器的工程材料，不是模型的新成绩。
003 的 4 个正确对照包括搜索原表示/重编码，以及 one-hot 原表示/重编码与能量平移。
009/010 的等价对照只变更对象键顺序，不冒充不同数值求解算法。

材料：[契约与输入](contracts.json) · [判定器](verification.py) ·
[独立依据](oracle_extensions.py) · [对照构造](control_extensions.py) ·
[回归测试](../../../tests/test_semantic_verification_v02.py) ·
[实际逐项结果](../../../artifacts/semantic_verification_v02/final/evidence/results.json)。

## 本轮确实抓住并修复了一个判定器漏洞

开发 003 时，最初只验证“合法着色 iff 能量为 0”。将正确惩罚整体取负后，零点不变，
这个初版判定器仍给通过；但最小化会奖励非法状态。这是新判定器开发过程中发现的问题，
不是对旧版模型分数的追溯改写。

已保存[失败测试输出](../../../artifacts/semantic_verification_v02/coloring-before-fix.stdout.txt)
与[执行命令](../../../artifacts/semantic_verification_v02/coloring-before-fix.json)。
修复后额外检查合法状态能量是全域下界（最大化形式则为上界），不只检查零点集合。
指定 `feasible_energy` 后也接受常数平移；不能强迫正确答案的能量恰好写成 0。
负惩罚被拒绝，重编码并作 `3E+7` 变换的正确对照通过同一检查。

另一条容易理解的测试是 010：输入 A=[[4,1],[1,3]]、b=[1,2]、初值[0,0]，要求一步。
独立公式得到 alpha=1/4，必须返回 [0.25,0.5] 和那一步的轨迹。直接给出精确解虽然
残差更小，仍违反“返回规定迭代过程结果”的合同。这条测试检查行为，不评价量子收益。

## 判定依据和有限范围

- 001/007：独立枚举原定义的加权割/带符号分数，再按 numeric mask 决胜。正确控制
  使用二次多项式与 A=2^n 的主次目标分离；任意整数目标差优先于 0..A-1 的 mask。
  007 的 signed score 与二倍加权 cut 相差常数，不据此推导硬件收益。
- 006：独立枚举容量内所有子集。正确控制使用
  `-A*value + mask + B*(weight+slack-capacity)^2`，A=2^n，B=A*(sum(values)+1)。
  slack 覆盖 0..capacity，不足容量允许留空；非法约束残差至少1，惩罚超过可能价值收益。
  检查全部编码 ground states，经双射解码后只取逻辑 item 位，不把辅助位当物品。
- 003：独立枚举颜色赋值，与每个编码的标记或能量关系比较；非法二进制码和 one-hot
  约束必须保留。最优颜色选择与“是否找到任意合法解”分开检查，两种家族都能被接受。
  原上下文的 greedy preview、保留有效 current 等行为仍不由这些核心测试全面覆盖。
- 009：pivot 直接按定义求值；小系统用独立行列式公式对照可信原消元程序；残差和
  scaled backward error 用有理数定义计算。只使用本文列出的精确可表示小实例，
  不引入通用浮点容差，不要求与某个 HPL 实现逐位一致。
- 010：oracle 独立推导零/一步闭式结果，对照原可信经典递推内核；所选实例中除
  sqrt 以外的中间量均为二进制可精确表示数。测试不证明任意多步 binary64 数值等价。

原公共前提、任务 A/B/C 区分、输出要求和来源哈希均保留在 contracts.json。
数值行为测试**不会**将009/010的结构机会 null 改成 NO/YES；所有科学标签仍待审。
识别候选位置、完整上下文、量子电路与资源/稳定性也未因此自动通过。

## 执行与兼容性

仍接受私有审核者的结构化主张转录，原模型仍提交 Phase-1 条件计划。不是自动理解
任意文字答案的裁判，也没有把文字任务换成代码任务。模型主张的引用、参数来源和
范围绑定规则继承 v0.1；代码只执行可信仓库内核作为对照，不执行模型代码。

复用旧判定器的独立模块实例，未修改旧源文件。状态分类、固定十题分母、未运行/证据
不足保持未知等政策继承；四题原契约逐项保持相同。所有 task_pass 仍为 null。
公开包没有收到这些私有材料。未来工具型 agent 的 OS 隔离仍未建立；本轮不声称靠
文件名或哈希能阻止拥有仓库写权限的 agent 篡改评测器。

仓库根目录复现（输出目录必须不存在）：

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -B -m pytest -q -p no:cacheprovider tests/test_semantic_verification_v02.py
/home/audrey/miniconda3/envs/palqo/bin/python -B -m pytest -q -p no:cacheprovider tests
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/semantic_verification/v0.2/run_verification.py --output /tmp/qrefactorbench-verification-v02-new
```

[最终执行记录](../../../artifacts/semantic_verification_v02/final/validation.json)
保存实际命令、stdout/stderr、退出码及旧文件完整性。本轮最终输出位于
`artifacts/semantic_verification_v02/final/evidence`；`after/` 是发现着色漏洞之前的
中间检查，不能当作最终版本结果。

实际结果：新增回归测试 **84 passed**；主套件 **223 passed / 15 skipped**。
修改前[基线](../../../artifacts/semantic_verification_v02/baseline.json)为主套件139 passed/15 skipped；
六个相关原程序测试组分别17、9、8、11、13、43 passed，最终仍全部通过；暂定标签测试24 passed。
15项跳过源于palqo缺少Qiskit/PyYAML，本轮未安装或运行这些可选功能。
1646个受保护旧文件哈希不变，包括v0.1验证层及已有模型材料。

没有新模型/QPU调用、依赖安装、Git提交/推送或新benchmark题目。当前十个母案例仍是
开发材料；没有把这些暴露过的测试包装成独立保留集或完整语义证明。
