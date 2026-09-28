# lit-009：从局部主张到可执行混合程序

2026-09-28，独立侧线演示包 v0.1。用户要求“能把这三块补上吗？”后实现。
这是 Codex 编写的工程原型，不是历史被测模型的输出，不计入 Agent 成绩或正式 gold。
本包没有改变主线程队列、研究家族、原案例、历史实验、论文或待审标签。
主线程当前状态仍由 [PROJECT_STATUS](../../PROJECT_STATUS.md) 管理；本页仅交接新增侧线产物。

**实际补到的范围：可执行 Qiskit 电路＋原程序集成＋整程序有限行为检查＋本地模拟器成本对照。**
没有补齐真机性能、全域形式化证明或端到端量子优势；这几项不能由模拟器结果代替。

## 给导师的演示顺序

1. 原任务：完整输入程序求解方程并报告残差、修订量，包含 inspect、异常和输入校验。
   [原源码](../../pilot/reference_completion/v0.1.1/cases/lit-009/program.py)，
   [候选语句](../../pilot/reference_completion/v0.1.1/cases/lit-009/kernel.py) 第13行。
2. 旧模型证据：提出 pivot 搜索谓词 → 可达 NaN 反驳 → 语义反馈修订后局部44状态通过。
   见 [N-048](../../pilot/enhancement/state-workflow-v0.3/execution-20260926/REPORT.md)。
   这是历史单案例、单明确错误机会；不与本包工程实现拼成一份模型响应。
3. 新工程实现：读取当前列；有限且最多8行时构造阈值相位 oracle；1轮 Grover、4个采样；
   选择采样候选后，必做经典有序 argmax 认证，必要时回退；接着执行原消元和报告逻辑。
4. 展示 [电路文件](results-20260928/search-8.txt)、[完整结果](results-20260928/results.json)
   和 [性能表](results-20260928/REPORT.md)。2/4/8个活动元素分别需要1/2/3个地址量子比特。
5. 结论：有界混合执行可以保留这些检查中的行为，但本实现没有收益依据；完整账目显示
   经典 oracle 合成和认证已经有线性成本，且认证自身就能计算答案。

## 三块分别实现了什么

| 用户提出的缺口 | 本包实际产物 | 保留边界 |
|---|---|---|
| oracle/电路与资源 | 阈值 oracle、固定一次放大、采样、u/cx编译、OpenQASM、深度/门数/采样数 | 不是完整 Dürr–Høyer 算法；无QRAM/硬件布局/噪声/纠错 |
| 整程序行为 | 仅替换 pivot 表达式，285次完整请求差分检查，错误采样/失败回退与CLI测试 | 有限测试和手工等价性论证，不是形式化全域认证 |
| 端到端性能 | 原程序、混合模拟器、SciPy/LAPACK报告包装；原始7轮数据和分项计时 | warm-process API范围；SciPy仅质量对照；没有QPU时延/优势结论 |

Oracle 标记 `value[i] > value[t] or (value[i] == value[t] and i < t)`，t固定为最后一个位置。
以经典数据枚举谓词并合成受控相位，未把事先计算的最大值写入电路；这个枚举仍是 O(m)
经典工作，且真值表已含有比较信息，不可以视为免费数据访问。padding地址不标记。
状态制备对2的幂次空间均匀叠加，padding采样会被丢弃；不偷用成功概率直接选答案。
一轮放大没有通用最大值成功保证，全部采样失败也必须终止到经典认证/回退。
4 shots是模拟同一已制备状态的4次采样；实际模拟器只演化一次，逻辑门×4是独立执行
4次电路时的资源账，不是声称模拟器做了4次演化。

非有限值、单元素、超过8行直接调用原选择操作。构造/编译/模拟出现普通异常时回退。
正常路径也无条件计算原 `max` 作认证；因此 `certified` 仅表示采样候选与经典结果一致，
不表示整个结果由量子算法独立保证。采样候选错误会明确记录 `fallback`。

## 行为保持论证与测试

原模块在隔离命名空间加载；不改原文件、不全局 monkeypatch。AST只替换唯一 pivot
表达式，并核对它的语法树仍与固定原表达式一致。其余数值更新、检查和报告语句复用。

手工论证：对通过原输入检查的普通JSON数据，进入 solve 后的数据是原实现生成的float。
每次替换必返回原 `max` 的索引（guard原调用，或经典认证），且不修改 rows。
以循环迭代归纳，行交换、消元、回代、残差及异常所见状态保持一致；inspect不进入solve。
内部量子随机性不会改变最终索引。这个论证假设相同Python浮点语义、正常资源可用，
不涉及时间行为等价、资源耗尽、任意恶意Python对象或外部硬件故障的完全恢复。

实际检查包括81个2×2矩阵、旧正常/溢出/NaN可达请求、空输入、inspect、非法输入及
delta溢出，95个请求×3种子=285。完整报告按JSON精确比较，异常比较类型和消息，
每次核对输入未变。另有423个oracle矩阵与精确相位真值表核对，单标记放大检查，
错误索引/空采样/编译失败/模拟失败/并列/signed zero/尺寸guard及CLI成功失败测试。
源码位置/traceback内容因包装而不同；CLI仅比较退出码、stdout和末尾异常类型/消息。

## 成本与解释

7轮计时中位数：2/4/8维原程序约0.012/0.021/0.050 ms，混合模拟器约3.63/7.98/24.54 ms。
同样规模的SciPy约0.037/0.046/0.061 ms。精确值、所有样本、质量结果见原始JSON。
这些是本机小实例观测，不做统计显著性、可扩展性或最佳经典算法断言。
SciPy在4/8维完整报告与原程序不逐位相同，所以只作为数值质量对照。
逐pivot保存构造、编译、模拟+解码、认证时间；整体还计入转换/装配和完整报告。
不计进程/导入/磁盘输入输出开销；计时名称是本地warm-process完整请求，而非生产部署延迟。

当前实现的量子候选生成并未省掉经典扫描，因而没有端到端渐近加速依据。
本地慢几百倍也不能用于预测真实量子处理器的速度，更不能否定其它实现的可能性。

## 复现

使用已有 `/home/audrey/miniconda3/envs/htp-static/bin/python`；本轮未安装依赖。
从 qrefactorbench 根目录运行（输出目录必须不存在）：

```bash
/home/audrey/miniconda3/envs/htp-static/bin/python -B -m demo.lit009_end_to_end.run --output /tmp/lit009-e2e-new
/home/audrey/miniconda3/envs/htp-static/bin/python -B -m pytest -q -p no:cacheprovider demo/lit009_end_to_end/test_demo.py
/home/audrey/miniconda3/envs/htp-static/bin/python -B -m demo.lit009_end_to_end.hybrid < pilot/reference_completion/v0.1.1/cases/lit-009/example_request.json
```

[冻结配置](protocol.json)；[验证记录](validation/validation.json)；
[独立重放结果](validation/replay/REPORT.md)。计时不可逐字节复现，语义结果、种子采样路线
汇总、源哈希和示例电路可独立重放比较。原始结果保留，不覆盖。

接口参照 [IBM Grover教程](https://quantum.cloud.ibm.com/docs/en/tutorials/grovers-algorithm)
和 [Statevector API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.quantum_info.Statevector)。
实际使用安装版本Qiskit 2.5.2，未按网上latest更新环境。

## 下一步如何使用这份演示

导师可据此判断：论文以可靠机会识别/映射审查为主，还是扩展到迁移实现。
如继续追求本案例的收益，首先需要能摊销的数据访问及oracle实现、最大值搜索控制和
正确性认证成本设计；不是再堆电路或重复小规模模拟。真机评估还需要明确设备与访问授权。
主线程的跨案例参考评审继续按原队列处理，本包不替代该科学工作。

文档同步检查：本包局部README、协议、实现、测试、结果和验证齐备。侧线约束要求
最小本地修改，本次不改主线程共用STATUS/队列/决策日志；由主线程按需引用本包。
