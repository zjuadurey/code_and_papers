# N-043：同模型、单次语义反馈的最小实验

用户已确认 [D-031](../../../DECISIONS.md#d-031-lit002-paired-semantic-feedback-pilot)。
固定 GPT-5.6 Sol / medium / 现有订阅，5份独立初稿；每份分别进行一次自我检查、
一次开发反例反馈修订，最多15次调用，无操作员重试。调用配置沿用已验证的隔离传输。

## 任务与科学边界

这是单独的新映射设计协议：给定 lit-002 顶点覆盖核心，提交包含规范化排序的直接
QUBO；**没有修改原来的自由文字 Phase-1 benchmark**，不测机会定位、完整转译、
QAOA求解质量或量子收益。原程序最多16顶点，检验采用预先固定的小图，不能证明全域正确。
只允许n个二进制变量；可用变量重排/取反、常数偏移、有理缩放和相应优化方向。
受限表达语言不能覆盖所有合法量子映射，语言外回答记格式/表示限制，不据此否定其数学可能性。

公开 [prompt.txt](prompt.txt) 是模型看到的完整新任务。模型提交通用模板，不为每个
测试实例单独给答案。模板是数据：只解析白名单算术树，不执行Python或模型代码。
候选不能改检查器。原benchmark、参考公式、正反对照与最终测试均不挂载给模型。

## Oracle 与反馈

[engine.py](engine.py) 将模板实例化为二次多项式；复用冻结v0.1独立定义oracle枚举
覆盖集合，按 `(基数, 升序索引元组)` 取最小。再枚举所有编码位串的能量，检查**每一个**
全局最优解的解码；不只挑一个碰巧正确的最优解。全程精确有理数，无容差/采样。
失败分为覆盖、最小基数、规范化排序、格式/表示、候选预算、基础设施、未运行。
格式和解释不能抵消语义错误；解释不做关键词评分，整题/迁移通过始终未判。

开发测试复用先前6个实例。最终测试在模型运行前固定：穷举n<=4的所有简单图并排除
开发图，补充固定种子抽取的n=5/6图及n=8结构图。具体数量与输入见 [tests.json](tests.json)。
二者图实例不重复，仍属同一个已经开发使用的母案例，不是独立保留集。
反馈只给开发测试首个失败输入、oracle答案、候选最优解与违反义务；无失败则只报告
有限检查通过。它不提供修复公式。最终测试结果绝不放进修订prompt。

正确对照为 `A=2**n; P=n*A+1; E=sum((A-2**(n-1-i))*x_i)+P*U`。
选择成本非负，总和小于nA；P使不可行解差于全选。不同基数间A大于整个tie项范围；
同基数时第一个不同索引的负超递增项支配后续差异，因而得到所需tuple次序。
等价对照反转索引并取反，目标变为 `-3E/2+7`、改为最大化。
错误对照分别为numeric-mask、正超递增、漏覆盖、漏tie和反转优化方向。
[test_experiment.py](test_experiment.py) 检查每个错误在指定义务上被拒绝，并独立检查编译能量。

## 配对比较及预算

- 初稿A：每份一轮；自检B与反馈C：各共享同一份A，然后各一轮全量修订。
- 奇数rep先B后C，偶数反向；同模型、配置、格式、可用修订次数。两分支不能看到对方答案。
- B对C用于考察外部语义反馈的增量；A更便宜。记录模型token/耗时、经典检查耗时；
  不声称等token或等总计算量。模型seed/温度/服务端snapshot未知，5次不能证明稳定性。
- 统计单位是5份初稿的配对分支，不是把所有图当作独立实验样本。只报计数和变化，不做显著性或模型排名。
- 固定分母5/arm；无论初稿是否正确，都运行B/C。不按结果挑选样本或增测。
- 600秒每次，最多15次操作员调用，CLI内部网络重试可能不透明；基础设施/账号/工具异常
  停止剩余队列，保留实际已调用与未运行项。候选格式错仍有原定修订机会。

## 运行与产物

使用已有palqo环境，不安装依赖。以下prepare/build/run是**一次性命令**，不能为验证而重跑模型。

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q tests/test_semantic_verification.py tests/test_semantic_verification_v02.py
/home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q pilot/enhancement/lit002-v0.1/test_experiment.py
/home/audrey/miniconda3/envs/palqo/bin/python pilot/enhancement/lit002-v0.1/build.py
/home/audrey/miniconda3/envs/palqo/bin/python pilot/enhancement/lit002-v0.1/run.py preflight
/home/audrey/miniconda3/envs/palqo/bin/python pilot/enhancement/lit002-v0.1/run.py run
```

`protocol.json`记录预先冻结的源文件hash、预算与统计口径；`protected_before.json`保护旧材料。
`offline-validation.json`记录正反对照；`inputs/`保留每次实际prompt，`runs/`保留原始响应、
事件、配置、用量和分项评估；`feedback-*.json`绑定对应初稿。旧传输metadata中的condition=C
是历史字段，本实验真实条件必须读取experiment.json的arm，不能与旧C成绩直接合并。
源级bwrap隔离复用旧传输，网络仅为服务调用所需，非经过独立安全审计的通用恶意代码沙箱。

效果以实际运行后 [REPORT.md](REPORT.md) 为准。当前预期允许零提升：Sol此前两轮在
lit-002上均提出过正确tie方向，这轮可能只有天花板结果。不会为了得到提升而临时换模型或改题。
