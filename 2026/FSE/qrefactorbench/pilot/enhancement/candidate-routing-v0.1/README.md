# N-055：保留原始提名的候选分析入口

本版本落实N-049已诊断的入口问题，零模型调用；不改既有分析器、响应schema或科学标签。
31项入口测试和49项既有回归通过，五份初稿的分析包已生成，3298个旧文件保持原样。
输入为明确允许的公开源码字符串和模型原始candidate_regions；提名里的路径从不用于
读磁盘。生成的目录只含公开源码已有信息，按给定文件和源码顺序排列，不排名、不选候选。

| 输入情况 | 新行为 | 不代表什么 |
|---|---|---|
| 空候选 | no_nomination，给公开函数/语句目录 | 不是已分析后确认没有机会 |
| 整函数提名 | 保留原跨度，给function_outline | 不悄悄换成某一行，不证明整个函数可迁移 |
| 跨语句或部分复合语句 | region_outline，明确相交/包含边界，seed为空 | 不把12–16自动扩大到12–20 |
| 唯一完整语句 | 保留span，标明seed和所在函数，调用已有词法清单 | 不是可靠切片、可达性或语义正确性证明 |
| 多条同线、无效区间、未知文件/函数 | 明确保留未支持状态和原提名 | 不丢弃、不猜测位置、不访问额外文件 |

每条记录独立保留declared_region、analysis_scope、seed_statement；边界条目附行列和
原文起始行。目录包含所有顶层函数及其各层语句，但嵌套函数/类的body不混入外层作用域。
当前不支持类方法范围和跨过程语义分析；源码语法错误直接报告，不能返回伪“无候选”。

## 本地验证

```sh
python -m pytest -q pilot/enhancement/candidate-routing-v0.1/test_routing.py
python -m pytest -q pilot/enhancement/state-workflow-v0.1/test_workflow.py pilot/enhancement/state-workflow-v0.2/test_claims.py
python pilot/enhancement/candidate-routing-v0.1/build.py --output /tmp/n055-new-audit
```

输出目录必须尚不存在。保存[五份历史初稿入口审核](audit/summary.json)及每份分析包，
并核对三份源码逐行出现在原公开任务中；不从私有标签、测试或已知反例生成提示。
初稿1→region_outline，2/5→statement_inventory，3→no_nomination，4→function_outline。

## 后续对照设计（未执行）

建议仍用全部五份原始初稿，每份做S普通自检、C仅公开目录、R目录加范围路由/词法清单，
各一次共15次，使用当轮新S；同包装、同schema、同模型，无反馈或补问混入。
C和R共享同一完整目录，R另给原提名与分析边界及精确语句的旧清单，因而R−C比较
整个路由/清单信息包，不宣称隔离了单个字段。S−C用于诊断目录重组的作用。
空候选和整函数是否新增更具体提名需原文审查；提名增加不能自动计成正确或有收益。
这不是新程序泛化或稳定因果效应证据。实施前另冻结准确输入、运行顺序、上限和验收，
同范围订阅预算依据D-035，不在任何旧campaign追加调用。
