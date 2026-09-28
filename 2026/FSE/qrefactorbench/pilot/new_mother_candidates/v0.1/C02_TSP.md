# C02：闭合旅行商动态规划

状态：候选档案；建议DRAFT来源/合同评审；完整tie/dtype合同、包环境和正式纳入未决。

## 来源、许可与独立性

[python-tsp固定原模块](https://github.com/fillipe-gsm/python-tsp/blob/b38179d06861e48a46c20c90a3d8162eb739795e/python_tsp/exact/dynamic_programming.py)，
tag `v0.5.0`，commit `b38179d06861e48a46c20c90a3d8162eb739795e`。
本地[dynamic_programming.py](sources/python-tsp/python_tsp/exact/dynamic_programming.py)未修改；
[MIT许可证](sources/python-tsp/LICENSE)含Fillipe Goulart版权声明，复制/改编均保留该声明和许可。
本轮仅外部加载模块、另写核查及QUBO提案；不是上游提供的量子代码。

来源差异必须保留：[pyproject.toml](sources/python-tsp/pyproject.toml)内部版本为`0.4.2`，
NumPy要求`^2.0.0`，与所解析tag及本机NumPy1.26.4不同。因此用commit标识，
只报告该单文件在既有环境的行为复现，**没有声称安装或复现完整受支持包环境**。
同commit的[brute_force.py](sources/python-tsp/python_tsp/exact/brute_force.py)只作同谱系证据，未执行；
正式完整包复现目前有环境缺口，未安装新依赖。

暂定组`PYTHON_TSP_CLOSED_TOUR`：全节点排列、位置相邻代价、闭环；不是旧006的容量下子集选择，
也不是旧004的最大两两兼容子集。DP与穷举版本以及不同矩阵全部按一个母问题组记录。
理论上可归约到SAT/QUBO不等于来源相同；也不证明其作为统计样本与旧题完全独立。

## 原始软件合同与候选边界

| 项目 | 固定模块证据与合同 |
|---|---|
| 输入 | 7–10行接口；有`.shape`和二维索引的NumPy距离矩阵，注释要求n×n，允许不对称；`maxsize`传入`lru_cache`。代码不统一验证形状/dtype |
| 输出 | 112–125行：以0开头的节点排列列表、不重复附加末尾0，以及闭合路线总代价。实际代价标量类型依输入dtype，返回注解float不保证运行时Python float |
| 核心 | 92–112行：剩余节点frozenset上的递归`dist`，空集代价为返回0的边，min选下一节点，memo保存重建选择 |
| 次序 | 等成本时Python `min`取`costs`中首项，而`costs`来自frozenset迭代；不能杜撰跨实现的字典序承诺。固定环境的原选路可观测，是否作为评测义务待审 |
| 状态 | 95/98/110行局部memo/cache，112–125行回溯；不写矩阵。缓存大小影响资源，未承诺不同进程/实现的迭代顺序 |
| 空/异常 | n=1返回`[0]`及矩阵对角值；n=0在`[0,0]`访问抛IndexError。部分非方阵抛IndexError，但不宣称所有非方阵必抛同错；没有外加校验 |
| 数值域 | 任意dtype接口较广，固定宽整数可能溢出、浮点非结合/NaN/Inf会影响min或代价；本轮只验证object数组中的Python整数，不能将数学整数QUBO当全dtype替换 |

候选是整段状态递推及解重建，不仅是一个`min`语句；矩阵解释、闭环边、排列输出、
缓存和异常路径要区分。若以后加业务报告/校验，那是新合成上下文，须另外记录，当前未创建。

## QUBO提案与义务

仅对n≥2、有限**非负整数**矩阵，令`M=max(D)`，`x[i,t]`表示城市i处于位置t，t按模n循环。
协调者提出以下二次多项式（没有第三算法家族）：

```text
E(x) = sum_(t,i,j) D[i,j] x[i,t] x[j,(t+1) mod n]
     + P [sum_i (1-sum_t x[i,t])² + sum_t (1-sum_i x[i,t])² + (1-x[0,0])²]
P = n*M + 1
```

人工论证：可行闭环代价在[0,nM]；不可行二进制赋值至少一项整数平方惩罚≥1，且代价项非负，
故能量≥P>nM。全局最小赋值因此可行并最小化闭环代价。这是局部数学提案和有限核对，
没有机械证明/量子求解或全软件等价结论。负距离虽通过经典检查，但不在该惩罚证明域内。

待审：相同最优成本的原frozenset顺序、dtype和异常、QUBO系数汇总/Ising变换及编码成本、
精确全局最优认证、经典回退与停止、QPU资源和端到端成本。
QAOA低能样本不是全局最优证明；最低成本相等也不能自动代表返回排列完全一致。
不改成近似旅行商、不任意把tie自由化。结构和实际适用标签尚未认可。

## 实际经典证据与剩余验证

[脚本](reproduce.py)的`check_tsp`：1个单节点矩阵、n=2/3所有非对角取值{-1,0,2}的9+729矩阵，
以及固定seed5802的40个n=4矩阵，共779；对三个cache设置调用2337次。
独立排列枚举核对最优成本、闭环、合法排列及输入未变；同矩阵不同cache的选路在本环境一致。
没有把穷举首次排列当原实现的普遍tie真值。

四个非负小矩阵的QUBO共1552赋值，所有最低能量解均解码成以0开头的最优闭环，
见[validation.json](validation.json)的`tsp`字段。错误对照：漏返回边会在给定三城例选错路线；
P=0时全零非法赋值优于正距离有效路线。空矩阵/一种非方阵异常也已验证。

下一审核应先决定完整源码观察等价还是明确受限profile；有条件批准后再补supported环境、
更多dtype/异常/tie及混合实现检查。这里是新经典来源，不是干净保留集或已验证量子机会。
