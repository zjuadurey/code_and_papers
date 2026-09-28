# C03：NetworkX惰性简单路径枚举

状态：完整候选档案，**保留边界/待审，不建议直接作为已确立正例**。不是负类gold。

## 来源、许可与独立性

[NetworkX固定原源码](https://github.com/networkx/networkx/blob/2acf1590f82757c01a57b81b8c5dfb79e60aa416/networkx/algorithms/simple_paths.py)，
tag `networkx-3.4.2`，commit `2acf1590f82757c01a57b81b8c5dfb79e60aa416`。
本地[模块](sources/networkx/networkx/algorithms/simple_paths.py)、[上游测试](sources/networkx/networkx/algorithms/tests/test_simple_paths.py)
及[BSD三条款许可证](sources/networkx/LICENSE.txt)原样保留，完整版权与免责声明随包保留；不暗示上游背书。
既有NetworkX3.4.2的该模块与快照逐字节一致；复现调用实际安装的公开API，无AST提取或装饰器替换。
上游测试仅归档参考，本次未执行整个上游suite，也未冻结整个安装包依赖树。

暂定组`NETWORKX_SIMPLE_PATH_ENUMERATION`。与001–004/007都涉及图，但本题输出所有不重复节点的
有向/无向路径并带生成器行为，不是cut、cover、coloring、clique或Ising选解。
源到目标、多个target、MultiGraph都是该母题变体，不能各增独立N。
区别于005 SAT首见证：这里要求完整输出，并非找到任何一个满足谓词的解即完成。

## 原始软件合同与候选边界

| 项目 | 固定源码证据与合同 |
|---|---|
| API | `all_simple_paths` 95–257行，输入G、source、单节点或可迭代target及cutoff；返回yield节点列表的生成器 |
| 数学输出 | 路径不重复节点，长度按边数，默认cutoff=len(G)-1；source也是target时可输出`[source]`零边路径；不可达时无输出，不抛NetworkXNoPath |
| 多重性 | 255–257行将edge path投影为node path；平行边的每种组合各产生一次，相同节点列表会重复。不能擅自set去重 |
| 核心 | 362–402行`_all_simple_edge_paths`：显式栈、当前路径字典和边迭代器；节点成员检查避免重复，达到target时yield，还可能继续到其他target |
| 次序 | 固定版本按图边迭代顺序做DFS，dict保留插入次序。公开接口未在这里承诺统一全局排序；原代码的流次序可观察，不能自动改为按长度或字典序 |
| 异常 | 345–356行：不存在source抛NodeNotFound；不存在且不可迭代的单target也抛；含不存在节点的target iterable可仅产生空结果。验证发生在生成器推进时 |
| 状态 | 373–402行保存搜索栈/current_path和未消费边迭代器，图按引用读取；调用到首次next之间的图改动可能改变结果，中途修改不提供统一稳定性保证 |
| 周边 | `all_simple_paths`消费edge generator并解码；source/target/cutoff处理和lazy异常时机属于整体API。没有新增JSON包装或业务上下文 |

本地完整枚举验证域：静态n=3整数节点DiGraph，单source/target和cutoff∈{-1,0,1,2,None}；
另有MultiDiGraph、target iterable、边插入顺序与首次推进前改图的定向见证。
不能将这些有限检查推广到所有可hash节点、自定义图backend、并发修改或全部生成器协议。

## Search映射候选及主要缺口

可构造有限**边标识序列**域：长度≤cutoff，首点source、终点属于targets、相邻端点连接、
节点不重复，MultiGraph保留边key；空路径另处理。这是协调者提出的候选谓词，尚未实现可逆oracle。
只用节点序列会丢多重性；只搜一个解会丢其余输出；把cutoff数值当节点数会改边界。

完整替换还需：覆盖全部解而无额外重复、证明枚举结束、维持原顺序与分步消费/异常时机、
维护图状态及回退，以及输出和预处理成本。一般Grover成功一次不能满足这些义务；
穷尽输出的成本也不能被一次搜索复杂度替代。结构子谓词可讨论，完整API的映射仍UNKNOWN。
这不证明所有量子方案不可能，也不构成REMAIN_CLASSICAL金标签。

## 实际经典证据与剩余验证

[reproduce.py](reproduce.py)的`check_paths`对64个三节点有向图，在9种source/target和5种cutoff下，
共2880次与独立节点排列枚举作Counter比较；该检查验证内容/多重集，不等于全次序验证。
额外构造固定插入顺序图，其输出`[0,2,3]`先于`[0,1,3]`，揭示排序或只保留一个解的变化；
2×3条平行边产生6份相同`[0,1,2]`，揭示去重错误。多target、零边路径、两类缺失target、
缺失source延迟异常及首次next前改图均通过定向核对。详细记录见[validation.json](validation.json)。

建议保留供参考评审选择：若纳入，重点是原生成器合同与不确定性，而不是换成“找一条路径”的新题。
后续需评审公开规范和可观察实现之间的次序要求，再决定静态profile、图backend与异常覆盖。
没有调用模型来决定保留/排除，也没有把检查构造当未来独立保留测试。
