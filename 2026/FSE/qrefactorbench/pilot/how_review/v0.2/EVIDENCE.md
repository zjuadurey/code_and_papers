# 新增五案例审核证据与限制

既有002/003/004/006/009的76项记录继承 [v0.1推导](../v0.1/EVIDENCE.md)，
原判断不因研究者选择 A 自动升级。新增001/005/007/008/010的80项记录见 review.json。
两份记录中的双维度分类为协调者人工编码，不是文本关键字评分。

## 001：MaxCut、变量翻转与 mask

核心整数 cut 为 `sum w*(xi+xj-2*xi*xj)`，冲突为总权重减 cut。
Sol 的 `-2^n*cut+mask` 与 Astra/Flash 的 `2^n*conflict+mask` 只差常数。
一单位整数目标差支配0..2^n-1的 mask，故精确最小态保原核 tie。
Astra 的 Ising 展开保留常数，整数倍核对其系数和符号。
Pro 定义 x=0 为 window0，核心多项式与原核在补位解码后一致；没有因为位意义不同判错。
Pro 的具体能量没有 tie 项，后处理仅要求强制最优/tie，认证方法仍待补足。
Flash 在 observed candidates 中选最小 mask 不足以完成全局认证；其 scalar 能量
对应正确与采样结果已认证是不同命题。

对 n=0..4、所有边权0..2枚举 **761** 个加权图，与原 maxcut_bruteforce 核比较。
检查精确最小态和所有最优集合对应；不验证完整报告、设备精度或量子求解。

## 005：谓词、顺序与 no-solution

核心为锁定等式合取、每条三文字析取的合取。源码验证每条正好三个文字；
允许重复和相反文字；空 rules 集合为真。Flash 的“Empty clauses are true”含糊，
单条空 clause 不在合法公开输入域，不能以此构造合法域失败。
Sol/Astra 提供逐前缀优先 False 的构造：若准确知道一个前缀存在后缀解，归纳可取首解。
然而可逆 oracle、精确负判定和全局无解认证仍未完成。Pro 的 less-than wrapper
只是方向；Flash 明确首解/无解仍未解决。

对 n=0..3，零条或一条恰三文字规则、全部锁定组合，枚举 **6,472** 个核心实例，
与原 conforms/complete 比较，并用经典精确存在性检查逐前缀逻辑。
包含重复文字、矛盾文字和空规则集；不覆盖任意多条规则，不是量子存在性检查。
Flash 定位10–13不含14行 None返回，可能保留经典返回，需补充替换接口解释。
Pro 同时提名 conforms/complete 是可辩护依赖边界；不按额外行自动判错。

## 007：带符号目标与 tie 的完成度

每对贡献为 `w*(2*XOR-1)=-w+2w*xi+2w*xj-4w*xi*xj`；四模型核心展开相符。
负 score 的 Ising 表达为 `sum w*Zi*Zj`。没有容量/平衡/非空组约束。
Sol/Astra 的 `-2^n*score+mask` 有整数目标支配依据。DeepSeek 两回答未给该 tie 构造；
不把审核者能补出的公式算作模型提交内容。Flash 只给 observed tie 并明确 exact
fallback 未解决；Pro 要求与 true maximum 核对，没有交代完整认证机制。

对 n=0..5 全部完整图的±1偏好枚举 **1,100** 个实例、**33,867** 个位赋值，
检查展开、Ising恒等式、Sol/Astra scalar tie 与原 score/choose。
这里只测合法完整偏好集合的核心，不声明全程序或任意规模实现正确。

## 008/010：审核拒绝理由，不自动批准负标签

008 源码直接 XOR 并生成全部有序回执，prefix checksum 随输入顺序改变；
repetitions 只是确定 counts 的数值，不是量子 shots 或重复计算预算。
010 合同要求预算内具体 recurrence、完整 iterate/trace 与重算 residual；
求一个不同的精确线性系统解不能替代这些行为。
这些狭义合同阅读有源码依据。各模型对整个程序/所有子区域的普遍排除仍证据不足，
故 M 保持 unresolved；C/W 仅支持所述合同及依赖识别。E 因未提交条件计划不适用。
空候选与 Pro008 提名后拒绝均允许。**不产生结构 NO gold 或负类识别率。**

## 核验方式及实际限制

脚本执行人工转录算术和经过阅读的原始经典核，先核对原核与公开 C 包的源文字节内容。
首次命令误用了001源码目录，FileNotFoundError 后改为已有 context_adaptations 路径；
该次没有完成公式检查，也没有模型重试。成功结果记录在 checks.json。
其余验证未调用模型、认证、QPU 或新依赖。
完成度中的 provided 只表示具体内容已给出，不能作为正确性或整题通过的替代字段。
