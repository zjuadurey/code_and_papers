# C01：CPython连续文本块匹配

状态：候选档案；建议DRAFT来源/合同评审，正式纳入和科学标签未决。

## 来源、许可与独立性

主来源：[CPython固定源码](https://github.com/python/cpython/blob/976ea78599d71f22e9c0fefc2dc37c1d9fc835a4/Lib/difflib.py)，
tag `v3.10.14`，commit `976ea78599d71f22e9c0fefc2dc37c1d9fc835a4`。
本地[原模块](sources/cpython/Lib/difflib.py)与[原文档](sources/cpython/Doc/library/difflib.rst)
均未修改，哈希见[manifest](sources/manifest.json)。不是最新版本声明。
[完整LICENSE](sources/cpython/LICENSE)保留PSF Version2及历史条款；代码/文档复制保留原声明，
若未来改编须另写变更说明。当前只加本项目的外部核查脚本，没有改造为应用程序或重新许可来源。

暂定谱系组`CPYTHON_SEQUENCE_MATCH`。核心为双序列相等块及索引动态规划，区别于旧SAT、图选择、
背包及数值pivot；与009共享“最大值/次序”义务不代表同一原核。不能将`ratio`、
`get_matching_blocks`或本模块的新视图再算新母问题。见[逐旧例对照](LINEAGE.md)。

## 原始软件合同与候选边界

| 项目 | 固定源码证据与合同 |
|---|---|
| 输入 | `SequenceMatcher.__init__` 120–182行；两个可索引、元素可hash的序列，`isjunk`回调可选、`autojunk=True`为默认。不是仅字符串API |
| 查找接口 | `find_longest_match` 305–419行；`alo/ahi/blo/bhi`及None上界；输出`Match(a,b,size)` namedtuple |
| 排序与空结果 | 无过滤条件下最大长度，等长时先最小a起点、再最小b起点；无匹配返回`(alo,blo,0)`。实际autojunk会改变候选，不能无条件应用最长公共子串解释 |
| 核心与依赖 | 363–389行按a位置扫描，借`b2j`与`j2len`更新匹配长度；390–417行扩展被过滤元素。266–303行建立索引并过滤junk/popular，属于语义依赖 |
| 状态 | 184–248行setter更新/清缓存，同对象身份会提前返回；输入序列按引用持有，不能假定对可变对象做了快照。`find_longest_match`主要局部状态，`get_matching_blocks`另有缓存 |
| 异常 | b含不可hash元素可在构造/索引阶段抛TypeError；越界上界可在查找阶段抛IndexError。回调或自定义hash/equality异常照原流程传播。没有统一输入校验器 |
| 周边行为 | `get_matching_blocks` 421行起多次调用候选函数并排序/加尾哨兵；`get_opcodes`/`ratio`消费结果。保持单个最长块并不验证这些API的全合同 |

**局部验证域**：Python字符串，合法非负区间，`isjunk=None, autojunk=False`，不改变输入。
这是未获正式纳入的条件profile，原API更广；在其他状态保留原经典执行是待设计的完整方案，
不是本轮已实现的混合系统。不静默关闭用户默认autojunk或吞掉回调副作用。

## 搜索映射提案与待证明项

协调者提案，不是上游量子算法或gold：有限域为合法三元组`(i,j,k)`，条件为区间内、
`a[i:i+k]==b[j:j+k]`。在上述无过滤字符串域，目标次序为`(-k,i,j)`。
可考虑阈值存在性搜索确定k，再用前缀约束确定最早i/j；非法二进制编码须拒绝，
`k=0`空结果另有确定规则。这只陈述域、谓词和次序义务，没有实现Grover或认证过程。

必须另审：字符存储/访问和可逆相等比较、长度/起点编码、垃圾位反计算、阈值推进、
找到最大值的认证、没有更好解时的精确终止，以及与索引预处理和经典DP相比的完整成本。
有限次Grover未命中不能证明无匹配；随机找到任意等长块也不满足原次序。
全API的junk/autojunk、对象回调和缓存语义仍UNKNOWN；不据此给全函数structural YES/NO或实用标签。

## 实际经典证据与剩余验证

[reproduce.py](reproduce.py)的`check_text`直接加载固定原模块，独立穷举子串比对：
长度0–4的二元字符串961整串对；长度≤2各合法区间组合961次。计数有输入重叠，不是1922个独立程序。
setter更新、TypeError和IndexError定向检查通过，见[原始结果text字段](validation.json)。

三项错误方案见证：`ab`对`ba`须取`(0,1,1)`而非另一个等长块；
空格junk例从`(0,4,5)`变为`(1,0,4)`；`x+a*200`对`y+a*200`默认autojunk输出零长度，
关闭后输出`(1,1,200)`。因此“直接替换成最长公共子串”不能覆盖原默认合同。

后续参考评审需确定是否接受受限profile，还是保留全默认行为作为边界案例。
需补多字符/Unicode、自定义元素、同对象可变缓存及调用链验证；没有声称这些已覆盖。
该源码是公开标准库材料，预训练污染未知；条件profile须先审再冻结，不按模型成绩调整。
