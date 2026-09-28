# 评测方法：实现、结果与不能推断的结论

这些是**隔离的描述性工具和构造测试**，不是新的正式 benchmark 指标政策。
实现 [methods.py](methods.py)，实际运行 [run_method_checks.py](run_method_checks.py)，
数值 [METHOD_RESULTS.json](METHOD_RESULTS.json)，断言 [test_methods](test_methods.py) /
[test_quantum_methods](test_quantum_methods.py)。主 evaluator 和旧结果不变。

| 方法 | 实际检查结果 | 适用范围与限制 |
|---|---|---|
| HumanEval/QuanBench Pass@k | 手工夹具 n=4,c=2,k=2 得 5/6；k>n 等非法分母拒绝 | 需要同一任务的真实独立采样尝试和已有判定；不能用十个不同案例冒充 n=10。这里模型样本数是零 |
| QuanBench 酉过程重合度 | I 与 Z 在初态 0 的分布一样，但过程重合度 0；global phase 对照重合度 1 | 只接收无经典位、纯 gate 的小型酉线路；含 measurement/reset 直接拒绝，不擅自删掉测量 |
| QuanBench+ KL | 直接执行源函数，观测 [1,0] / 参考 [.5,.5] 得约 ln2，源阈值判 false | 源方向是 observed→expected，clip eps=1e-12 且不重新归一化。我们额外报告明确的 reference→observed、零平滑版本，此例为无穷（JSON null＋标志）。0.05 不被采纳 |
| PQID count-map | H(0);CX(0,1) 与 H(0);CX(1,0) 通过源 structural_result 所有检查，过程重合度约 .0625、TV=.5 | 结构签名没检查所有操作数/顺序语义；是一个具体反例，不是对整套数据/模型的结论 |
| MQT 多表示层资源 | 四比特源线路：逻辑 RZZ/RX/H 层 depth=4、门10、两比特门2；分解后 depth=14、门38、两比特门4；过程重合度约1 | 同一线路不同表示，基门 rz/sx/x/cx、level0、seed10；参数全 .31，未优化，无布局/硬件/shot 假设；复用已有资源提取器 |
| SupermarQ 任务质量 | 两个不同分布可有同一期望值（gap=0，TV=1）；参考期望0也能报告绝对 gap | 不直接使用源 score 的 `2*ideal_value` 分母。源代码与类说明的指标差异明确记录；绝对 gap 本身不证明可行性、精确解或合同保持 |
| HPL 残差 | 2×2 系统正确向量 residual=0；零向量 residual∞=2，scaled≈2.2518e15 | 按公开 n·eps·(||A||∞||x||∞+||b||∞) 定义计算，无默认通过线；还需完整 API 检查；不是 HPL 性能结果 |
| HPCG 对称性 | 对称矩阵 raw defect=0；改动单个非对称项后 defect=1 | 借鉴 xᵀAy=yᵀAx，当前是未缩放 defect，不冒充源 TestSymmetry 全部实现或其阈值 |

## 我们现在能区分的检查层次

代码运行 → 有声明的结构 → 指定输入上的分布 → 酉变换行为 → 任务目标/可行性
→ 原软件全合同。它们不是可以互相替代的证据，也不是所有任务都适用的线性等级：
经典算法输出正确并不要求与某一量子参考线路完全相同；不同实现可以保持同一任务。
过程保真度仅在实验明确需要同一个酉操作时有意义，不能作为一切量子重构的通用门槛。

未引入 probabilistic pass 阈值、统计置信要求、近似容差或速度分数。分布支持、位序、
采样数量与判定政策仍需按任务确定。本轮无模型基线、QPU 或量子优化器执行；只运行
小型确定性线路/数学夹具。量子测试先暴露 NumPy scalar 适配错误，修复日志保留。

## WHERE 的具体作用

新案例的测试不只比较一个目标值：保留当前分支、锁定约束、活跃项过滤、转移偏移、
有符号关系、逐条端序、数值检查分支、迭代轨迹都有反例。这让错误边界具有可检验
的行为后果。模型是否因此更难定位仍未测量；不能把上述代码测试解释为 WHERE 成绩。
