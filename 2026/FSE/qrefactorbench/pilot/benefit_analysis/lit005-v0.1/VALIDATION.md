# N-061验证记录

日期2026-09-28。既有环境`/home/audrey/miniconda3/envs/palqo/bin/python`，全部用`-B`，
pytest关闭cacheprovider。没有安装、模型/QPU调用或修改旧输入。

| 检查 | 实际结果 |
|---|---|
| `python -B -m pytest -q -p no:cacheprovider test_analysis.py` | 最终8 passed |
| `python -B check_wrapper.py` | 11 passed，原wrapper测试中注入本地lex-DPLL，未改原文件 |
| `python -B run.py --output results.json` | 1809实例、1809 DPLL对照、4633基态、6442修复全部通过 |
| 新输出`replay.json`与results逐字节比较 | 一致 |
| 输入绑定6文件 | SHA256逐一匹配 |
| 受保护旧文件 | 3675文件SHA256全部匹配 |
| 新/改Markdown相对文件链接 | 交付前检查，结果见verification.json |
| 交付包完整性 | manifest.json记录除自身以外全部包内文件SHA256 |

第一次专项测试7通过/1失败：手算期望漏4个X；实际有9个positive literals，
compute/uncompute各两次X包裹给36 X，加6个flag双向12 X，总48 X。
修正测试期望，oracle未改；最终8通过。见[validation-history.json](validation-history.json)。
本次没有重复运行整个历史模型campaign或全项目测试，因为基础设施和正式案例代码未改。

有限诊断范围在运行前写入[protocol.json](protocol.json)：64个源子句子集×27种锁定，
加n=1..3所有单条三literal多重集（4+20+56），以及n=0空实例，共1809。
多重集包含重复literal、重言式；锁定涵盖矛盾/常量分支。额外测试覆盖更长合取辅助位链。
这些是开发诊断状态，不能换算独立软件数、泛化成功率或硬件可靠性。

范围核对：已读取量子优势材料并纠正当前入口；完成具体合同、候选算法、经典对照、
oracle逻辑资源、完整成本账本、条件结论和下一技术任务；纸面正收益区域和物理可行性
因参数不足保留未知。没有把条件分析冒充实际优势、自动化系统或前沿超越证明。
