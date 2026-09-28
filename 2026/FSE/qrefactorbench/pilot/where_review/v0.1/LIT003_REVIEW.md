# lit-003：议程安排的 WHERE 审阅

**PRIVATE · AI-ASSISTED PROPOSAL — NOT GROUND TRUTH。不得进入盲测输入。**

母案例来源及合同见 [ADAPTATION](../../source_adaptations/v0.2-where/cases/lit-003/ADAPTATION.md)。
功能是检查/补全议程：共享参与者不能同时出席；已有合法安排保持原样。
只有需要重新安排且顺序预览失败时，才进入完整求解。部分 current 不构成固定约束。

## 一、核心—依赖—外围

| 层次 | 具体源码锚点 | 应当理解的行为 | 审阅时寻找的证据 |
|---|---|---|---|
| 核心提案 | [agenda.py](../../source_adaptations/v0.2-where/cases/lit-003/agenda.py) 28–57 `complete` | 尝试完整时段向量；递归、回退；返回首个合法向量或抛出失败 | 不能只说“这里有递归”；说明搜索对象、冲突条件、完整性要求 |
| 内部依赖 | 同文件 29–30、32–40 `available`、42–53 `place` | `assigned` 是试探状态，`neighbors` 决定约束；失败后撤销当前选择 | 谓词与状态不能被误认成彼此独立、无上下文函数 |
| 外部依赖 | [catalog.py](../../source_adaptations/v0.2-where/cases/lit-003/catalog.py) 32–38 `relations` | 参与者交集编译为图；列表索引对应 session 顺序 | 承认关系来源及索引对应，不要求关系构建一并量子化 |
| 控制边界 | [program.py](../../source_adaptations/v0.2-where/cases/lit-003/program.py) 11–33 | inspect、有效 current、成功 preview 都绕过 complete | 说明调用条件；某次输入不调用，不代表程序静态候选不存在 |
| 外围义务 | program.py 34–38；catalog.py 6–29、41–52 | 名字解码、moves、全部输入验证、冲突/状态报告 | 一个合法索引向量不等于保持完整 API 行为 |

## 二、候选边界提案，等待研究者审阅

- **完整函数提案：** `agenda.py:28–57`。合理的初始候选，但仍需说明上游关系与
  下游命名输出、调用条件。提示 B 只给这个 span，不给算法或依赖答案。
- **较窄提案：** `agenda.py:42–53` 的递归，并明确列出谓词 32–40、状态初始化
  29–30，以及 55–57 的失败/返回责任。不能仅因少圈几行自动判错。
- **较宽提案：** 整个 `review_agenda` 被提名进一步分析，可保留这个提名；
  但必须区分其中的核心与应保留的分支/报告。大框本身不是更完整的正确证据。
- **只提名 available 或 preview：** 暂不定为负例。先看是否恢复了完整计算意图、
  是否提出支持性映射，以及是否把不同合同混同。WHERE 提名和 WHETHER 拒绝分开。

供人讨论的文字样例（不是模型输出）：
> 候选是 complete 的赋值递归；判定依赖 neighbors 与 assigned。图来自参与者
> 交集，结果索引按 slots 解码。只在重新安排且 preview 失败时需要它；保留当前
> 安排和 preview 状态的规则继续由外层负责。量子方案仍需交代首解与无解保证。

## 三、实际运行的路径与反例

[完整记录](prepared/evidence/lit-003.json)，既有独立 oracle 测试见
[test_program.py](../../source_adaptations/v0.2-where/cases/lit-003/test_program.py)。

| 记录 ID | preview / complete 调用数（原程序路径） | 输出/意义 |
|---|---|---|
| completion_after_blocked_preview | 1 / 1 | 两时段预览 blocked；完整安排为 morning, afternoon, afternoon, morning |
| inspection | 0 / 0 | 只检查；无 proposed |
| retain_valid_current | 0 / 0 | 保留另一份同样合法的 current，不强制回到首个解 |
| ready_preview | 1 / 0 | 预览成功；无需完整求解 |
| no_arrangement | 1 / 1 | 单时段有冲突；status=unavailable |

两个人为错误替换（不是模型产生）：

1. **把 preview 换成 complete：** 最终 proposed 完全相同，但 `preview.assignment`、
   `preview.status`、顶层 `status` 改变。证明这两种计算职责不可直接互换。
2. **去掉参与者关系：** 返回同一时段给所有人，原始关系的报告出现冲突。
   证明缺少依赖会改变求解的问题，而非单纯边界写法不同。

trace 只统计 program 模块被包装的函数绑定。第一个错误替换内部用保存的函数
引用调用 complete，绕过该绑定；不要把替换记录中的 complete=0 解释为没有执行
完整求解，也不把这些计数当作复杂度或耗时。

## 四、哪些结论仍不能下

这说明边界/依赖有行为后果，没有证明模型难以发现它们。函数名仍提供线索。
可行安排不自动满足首解/无解合同；找到量子映射也不证明量子求解可靠或有收益。
没有根据本页赋予 structural YES 或 practical NO；科学判断仍为 null/DRAFT。

**本例的人审问题：** 接受完整函数与“较窄递归＋完整依赖说明”作为不同有效表述吗？
是否保留当前例子的 preview/status 和首解要求？未收到答案前按原合同展示，
不替研究者填写结论，不将本页提案用作准确率分母。
