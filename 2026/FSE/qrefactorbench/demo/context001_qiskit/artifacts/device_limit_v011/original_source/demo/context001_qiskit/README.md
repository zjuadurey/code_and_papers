# context-001：实际运行转换后的 Qiskit 程序

2026-09-21。研究者要求直接运行从源程序改编的 Qiskit 版本，本次已完成一次本地检查。
**这是 AI 辅助实现的单案例转换原型，不是自动转译器或新的模型基线。**
没有外部模型调用、QPU 任务、标签升级或量子优势实验。

## 先看结果

| 输入 | 实际 Qiskit 执行 | 原目标值一致 | 完整报告一致 | 参数优化 |
|---|---|---|---|---|
| 原三设备示例 | 3 qubits / 256 shots | 是，冲突权重 1 | 是 | 达 80 次评估上限，未收敛 |
| 当前已最优但时段互换 | 2 qubits / 256 shots | 是，冲突权重 0 | 是 | 达 80 次评估上限，未收敛 |
| 反向重复权重 | 3 qubits / 256 shots | 是，冲突权重 0 | 是 | 达 80 次评估上限，未收敛 |
| 全零权重 | 3 qubits / 256 shots | 是，冲突权重 0 | 是 | 报告收敛，目标恒为 0 |
| 空设备 | 否，直接返回空报告 | 是 | 是 | 不适用 |

五个输入均只执行一个演示尝试。**没有经典最优解兜底，也没有基于结果调参重跑。**
经典参考程序在每次量子分支完成后才运行，只用于比较，没有将最优值反馈给参数优化。
原始输出、抽样 counts、优化 trace、版本/源码 hash 和未收敛信息见
[first_run.json](artifacts/first_run.json) 与 [终端记录](artifacts/first_run.stdout.txt)。
`optimizer_success=false` 与抽样找到目标答案是不同事实，两个都保留。

三设备输入的 256 个样本中，68 个是 mask 2、70 个是 mask 5，两者冲突权重均为 1；
按“已抽到样本中的最佳成本，再选最小 mask”返回 mask 2，因此本次报告与原程序一致。
其理想状态向量中最优解的总概率约 0.530218；这是此组参数的事后模拟诊断，
不是一般成功率保证，不是对预先设定统计阈值的通过声明。

## 看代码和转换位置

- [hybrid_program.py](hybrid_program.py)：真正的 Qiskit 线路、参数优化、抽样和混合入口。
- [maintenance.py](maintenance.py)：原模块的逐字副本，校验、评分和比较逻辑保留。
  其中原穷举函数仍在副本中供审查，但混合入口不调用它；只有外部比较器调用经典参考。
- [run_comparison.py](run_comparison.py)：固定五个输入，先运行混合版，再比较原程序；
  保留逐例错误和不匹配，拒绝覆盖已有结果。
- [protocol.json](protocol.json)：在首次执行前写定的参数和预算，不根据观察结果修改。

原 [program.py](../../pilot/context_adaptations/v0.1/cases/context-001/program.py) 的调用：

```python
_, (first, second) = maxcut_bruteforce(matrix)
proposed = evaluate_windows(names, matrix, [first, second])
```

混合版替换为：

```python
windows, trace = solve(matrix)  # Qiskit QAOA, then select among sampled results
proposed = evaluate_windows(names, matrix, windows)
```

前处理、current/proposed 评分、报告字段和差异计算保留。`review_schedule(request)`
返回同样结构；`review_schedule_with_trace` 另给执行证据，避免把调试字段混入业务报告。

## 实际量子计算做了什么

1. 从输入矩阵直接构造 `H/W = 1/2 I + Σ w_ij/(2W) Z_i Z_j`；W 为总权重。
2. H 门制备均匀态；`rzz(gamma*w_ij/W)` 实现成本层（忽略全局相位）；
   `rx(2*beta)` 实现混合层。本次固定一层。
3. COBYLA 从 `[0.37, 0.21]` 开始，最多 80 次评估，最小化 Qiskit Statevector 的
   **精确期望值**。这是理想模拟器能力，未实现硬件上的有限 shots 梯度/期望估计。
4. 最终状态按 seed=7、256 shots 抽样。Qiskit counts 的最低位映射设备位置 0。
5. 只在观测到的样本中用整数成本选最小 `(冲突权重, mask)`，再接原后处理。
   未观测到的原合同最优分组不会被偷偷补上。

零权重目标为 0，示例仍执行均匀态线路以检查该分支；不认为这有量子计算必要性。
空输入不建线路。资源计数复用既有 `extract_resources`，对象是逻辑 h/rzz/rx 电路加
等价终端测量；不含物理编译、容错、数据准备或全部优化轮次的执行成本。
优化次数单独记录。Statevector 抽样使用与终端测量等价的模拟分布，并非真机读取。

实现说明参照 [Qiskit Statevector API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/quantum_info.Statevector)
和 [官方 MaxCut/Ising 教程](https://qiskit-community.github.io/qiskit-optimization/tutorials/06_examples_max_cut_and_tsp.html)。
本项目已有的 [逐项数学对应](../../artifacts/context001_mapping_audit/README.md) 提供具体目标。

## 复现命令

在仓库根目录，用已有环境（Qiskit 2.5.2 / SciPy 1.17.1 / NumPy 2.4.6 / Python 3.11.16）：

```bash
/home/audrey/miniconda3/envs/htp-static/bin/python -m demo.context001_qiskit.hybrid_program \
  < pilot/context_adaptations/v0.1/cases/context-001/example_request.json
```

完整对照需新输出路径，不覆盖首次记录：

```bash
/home/audrey/miniconda3/envs/htp-static/bin/python -m demo.context001_qiskit.run_comparison \
  --output /tmp/context001-qiskit-comparison-new.json
```

代码会真的执行模拟器，不是回放。历史命令不代表未来自动重新运行的授权。
例程限制最多 6 设备、总权重不超过 2**40；超出明确抛出 NotImplementedError。
原 case 允许 16 设备和任意精度权重，因此**本原型并未覆盖原始整个输入域**。

## 现在可以说什么

可以说：**这个经典程序已经有一个实际运行的 Qiskit 混合原型，在选定的五个小输入上
返回了相同的完整报告，其中四例真正执行了模拟量子线路。**

仍不能说它对所有允许输入保持合同：有限采样可能错过全局最优或指定并列结果，
并且原型域更小。没有因为样例通过就修改 benchmark 的科学标注或放宽原要求。
也不能将模拟耗时解读为真实 QPU 收益，或仅与原穷举比较就宣称胜过强经典方法。
这份运行回答的是“转换程序能否具体运行并在这些输入上保持输出”，不是回避实现问题。

## 验证与来源

[test_conversion.py](test_conversion.py) 检查逐基态成本层相位、Hamiltonian 数值、
位序和仅在已测样本中选解；特意注入非最优样本，确认没有隐形经典兜底；
检查非法输入在量子执行前拒绝、空输入、原型域界限和首次结果的资源/抽样记账。
没有用概率阈值掩盖未收敛或失败。实际命令与结果见 [validation.json](artifacts/validation.json)。

本次量子转换及已有可选功能测试 **20 passed**；原 context-001 测试 **43 passed**；
核心测试 **97 passed, 15 skipped**（核心环境缺可选 Qiskit/PyYAML，另一个已有环境完成
上述可选检查）。原 14 案例和独立 context-001 均验证通过，JSON 汇总成功。
529 个原有受保护文件及首次执行代码 hash 均未变化，没有安装依赖。

源函数署名/许可沿用 [context-001 来源](../../pilot/context_adaptations/v0.1/README.md)：
C2|Q> 数据镜像固定记录 164 的核函数为 CC-BY-4.0；新增 Qiskit 和报告代码是 Codex
辅助编写，整体项目发布许可仍未决定。没有发布、原 benchmark 修改或用户身份补造。
