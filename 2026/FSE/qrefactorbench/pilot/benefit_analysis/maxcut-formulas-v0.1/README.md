# 小规模验证 → 公式推导 → 大规模潜在收益条件

2026-09-28。用户明确要求采用没有大规模量子机器时的替代证据路线：小规模核验规律，
用公式推导100 qubit等无法完整模拟规模的潜在量子优势。本包承接该请求与D-041/D-042。
它不要求先获得真机，不把小实例无收益当作研究终点。

范围是现有MaxCut/QAOA计算核心的参数分析，不修改原wrapper16节点上限、正式case或精确输出合同。
结构公式由电路构造推导，再用小规模模拟核验；不把几个点拟合当作证明。
物理资源由已安装QDK1.32.3估算，不进行100/200/500qubit状态模拟。

执行前固定：

- 小规模n=4,6,8,10,12，种子20260928/29/30，p=1,2,4，共45组。
  独立Hamiltonian与门级实现比较；记录最优割概率、规范最小mask及其补集概率。
- 大规模n=100,200,500，p=1,4,16，固定第一个种子与100ns门/500ns测量、物理错误率1e-4；
  每个电路单shot估算错误预算1%。100qubit另比较10ns/1000ns门模型的p=1点，共11次后端调用。
- 一层角度gamma=pi/4、beta=pi/8，逐层相同，是资源模板而非已优化算法；
  小规模成功概率不外推成大规模事实。使用greedy matching安排可交换ZZ项。
- 大规模条件网格：经典完整任务时间T=0.1/1/10/100秒，固定其他成本A=0/0.01/0.1秒，
  每shot解码/验证成本v=0/0.0001/0.001秒，S=1/4/16/64/256/1024；这些都是条件坐标，
  不是测得的大规模经典时间或证书耗时。F=T为此网格的显式回退假设。
- s表示每shot获得**可靠的原合同输出证书**的概率，含物理运行和证书覆盖；不等于高割值概率。
  iid条件下q=1-(1-s)^S，期望总成本A+S(t+v)+(1-q)F，反求s下界。
  不作iid假设时保留q为整批参数。硬件失效导致无法完成执行的风险不在本场景内。
- 返回精确结果依赖可靠证书/精确回退；本轮给出它们必须满足的成本与概率条件，不伪称实现一般图证书。

命令（palqo环境，项目根目录；输出目录必须不存在）：

```bash
python -B -m pytest -q -p no:cacheprovider pilot/benefit_analysis/maxcut-formulas-v0.1/test_formulas.py
python -B pilot/benefit_analysis/maxcut-formulas-v0.1/run.py --output pilot/benefit_analysis/maxcut-formulas-v0.1/run
python -B pilot/benefit_analysis/maxcut-formulas-v0.1/report.py
```

QAOA构造依据：[Farhi等原论文](https://arxiv.org/abs/1411.4028)。
跨层物理估算依据：[Microsoft官方说明](https://learn.microsoft.com/en-us/azure/quantum/intro-to-resource-estimation)。
本地公式推导、有限验证与外部算法文献的支持范围分别记录；无模型/QPU/安装/付费任务。
