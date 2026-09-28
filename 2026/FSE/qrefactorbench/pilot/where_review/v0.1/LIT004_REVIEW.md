# lit-004：兼容版本组合的 WHERE 审阅

**PRIVATE · AI-ASSISTED PROPOSAL — NOT GROUND TRUTH。不得进入盲测输入。**

[原始适配说明](../../source_adaptations/v0.2-where/cases/lit-004/ADAPTATION.md)。
对象是可共同选择的不同构件，不是同一个软件包的互斥版本。两两成功是这个合成
工作流的完整兼容模型；没有证明它代表真实软件部署兼容性。

## 一、核心—依赖—外围

| 层次 | 源码锚点 | 应当理解的行为 | 审阅证据 |
|---|---|---|---|
| 核心提案 | [program.py](../../source_adaptations/v0.2-where/cases/lit-004/program.py) 25–29 | 子集枚举、可行性判断、最大大小更新 | 变量是 eligible 索引的选择，目标是成员数，不是最大版本号或贪心前缀 |
| 谓词 | [reports.py](../../source_adaptations/v0.2-where/cases/lit-004/reports.py) 11–12 | 所选构件之间每一对都需要成功记录 | `len(subset)` 不是完整问题；未知检查不能当作通过 |
| 输入关系 | reports.py 6–8；[catalog.py](../../source_adaptations/v0.2-where/cases/lit-004/catalog.py) 41–49 | 无向对的最新记录优先；仅 active 且属于 members，按目录顺序 | 历史覆盖、过滤与索引顺序决定真实问题及解码 |
| 控制边界 | program.py 17–24 | 每条请求独立；inspect 仍有 preview，但无完整选择 | 不能凭一条 inspect 输入否认整个程序存在候选 |
| 外围义务 | program.py 30–37；reports.py 23–33；catalog.py 6–38 | current/preview/proposed 独立报告；变化清单；全批验证与统计 | 结果集合大小正确仍可能改变 preview、异常或报告 |

## 二、候选边界提案

- **默认审阅提案：** `program.py:25–29`，含初始 incumbent 和更新。
- **较窄提案：** `26–29` 循环，明确说明 `best=[]` 的初始化以及跨文件谓词、
  relation/names 输入。不能仅因漏圈初始化但已说明它就自动判错。
- **较宽提案：** `24–34` select 分支；需区分枚举与解码/changes。
  提名整个 `review_releases` 也应先审说明，不能把整函数都当成一个量子内核。
- **谓词单独/预览提名：** 属于进一步分析提案，不能仅按作者 intended span
  自动定为负例。遗漏目标或把预览改成最大集合，是具体的理解/替换问题。

文字样例（非模型输出）：
> select 分支中的子集枚举是候选；它在 filtered names 上求最大两两兼容子集，
> reports.compatible 读取由最新记录形成的关系。preview 是另一个按顺序加入的
> 结果，不能随最终方案一起改写。还要保留 catalog 顺序、并列选择与变化报告。

## 三、实际证据

[六个运行记录](prepared/evidence/lit-004.json)，既有独立 oracle 测试见
[test_program.py](../../source_adaptations/v0.2-where/cases/lit-004/test_program.py)。

- **混合请求：** 两次 preview，16 次枚举谓词；inspect 和 select 的 preview 都为
  `[legacy]`，只有 select 得到 proposed=`[a,b,c]`。这是四个 eligible 构件的具体输入，
  不是性能测量。原始批次中 retired 已被过滤。
- **仅 inspect：** preview 一次，完整枚举谓词零次；**仅 select：** preview 一次，
  枚举谓词 16 次。说明调用条件不等于静态候选标签。
- **错误替换 preview：** 两个请求的 preview.selected/size 改变，但 select 的
  proposed 不变。更大且合法的集合不保留顺序预览合同。
- **反转历史优先级：** 当前组的兼容描述和两个 preview 改变，即使最大 proposed
  仍相同也有完整报告错误。不能只检查最终目标值来判断依赖是否正确。
- **并列见证：** 只通过 a–d、b–c 时，选 `[b,c]`（mask 6），不选 `[a,d]`
  （mask 9）。最大大小相同不满足完整选择规则；按字符串/元组字典序会改变合同。

上述错误替换仅在测试进程作用于现有函数绑定，未改写任何案例源文件。

## 四、避免过度解释

最大组合可被描述成带互斥约束的选择问题，但本次没有核验 QUBO penalty、量子
最优性、并列规则的保持或资源收益。本例没有自动获得 structural YES 标签。
枚举很显眼，模型可能轻松定位；更有信息量的观察可能是它是否恢复了历史与过滤
依赖。不能为了证明创新而将正确定位但条件 HOW 有缺陷的回答改判为 WHERE 错误。

**本例的人审问题：** 是否允许上述不同 span＋依赖表述？预览与最大组合并存是否
有可信的业务需求，数值 mask 并列规则是否要继续作为正式案例合同？本轮保持现有
规定；任何将来调整都另建版本，不能为迁就某个模型的答案事后改合同。
