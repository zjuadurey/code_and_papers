# 四模型 C 条件复跑（2026-09-23）

**已完成：40/40首次请求，36份有效回答，4份预算截断，无重试。**
[小报告](REPORT.md)、[数字摘要](SUMMARY.json)、[内容观察](CONTENT_REVIEW.md)、
[最终验证](validation.json)。这是响应交付统计，不是36题语义通过。

用户授权：“这10个case再用deepseek flash pro gpt 5.6 sol 6 都跑一下？”
本次运行固定为 gpt-5.6-sol、gpt-6-astra、deepseek-v4-pro、deepseek-flash，
各十题 C 条件、每题一次，共最多40次首次请求。不扩题、不重试、不修复响应。

输入仍是 reference_completion/v0.1.1 的十份原始 C txt；新增 semantic_verification/v0.2
是私有评测层，不进入提示。此次是相同任务的重复采样，不是新题目或隐藏保留集。
GPT复用Restricted Codex CLI 0.155.1、medium、现有订阅登录和Bubblewrap挂载白名单；
DeepSeek复用high、thinking enabled、max_tokens=16384的直接API调用。
全局最多两请求并发，每题先GPT一对，再DeepSeek一对；无工具、反馈或科学重试。
GPT单次墙钟上限600秒；DeepSeek socket I/O timeout600秒不是总墙钟保证。
一方发生账号/传输/异常工具故障时停止该provider后续队列，另一方继续；失败保留。

新目录复用两个原运输实现，通过固定SHA256绑定，不修改历史运行或代码。
凭据只由原有读取函数从用户已指定文件读取，不进入命令参数值、提示、日志或报告。

准备记录：[protocol.json](protocol.json)、[preflight](preflight/passed.json)、
[离线测试](offline-validation.json)。离线测试14项通过，无真实网络/密钥。
初次合并pytest命令因同名test_run.py发生收集冲突；改用importlib模式后运行通过，
没有删除旧文件或把收集失败记为通过。

官方操作文档核对：[OpenAI Docs：Codex CLI](https://learn.chatgpt.com/docs/codex/cli)、
[DeepSeek Chat Completions](https://api-docs.deepseek.com/api/create-chat-completion/)。
实际型号、usage、响应及运行状态以本目录原始记录为准；动态别名不等于冻结权重。

运行入口：已有palqo环境，`run.py prepare`和`run.py preflight`离线；
`run.py run --key-file <原用户指定路径>`消耗本次授权额度，拒绝重复运行。
不要把留存命令当成未来复跑授权。

结果分层：格式/响应交付、待审参考一致性与覆盖、另外带原文出处的局部语义证据。
不自动把自然语言填入正确对照公式，不把人工缺失或预算截断计为语义通过。
局部测试并未将现有文字方案任务转换成可执行迁移任务；不会生成整题通过率或排名。
GPT与DeepSeek的脚手架、推理强度及上限不同，单次重复不足以支持稳定能力排序。

后续离线验证28项通过：[日志](review-collector-validation.json)。001/002的7份
明确目标共执行38次有限检查；另在009复现了Sol/Pro共同的NaN pivot谓词反例，
绑定原文且保留回退限定。新反例为事后诊断，不改冻结题库或旧成绩。

## 实际执行命令

均在项目根目录、既有palqo环境运行。下面的模型调用授权已经用完；不是复跑许可。

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/model_comparison/20260923-four-model-c-v0.1/run.py prepare
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/model_comparison/20260923-four-model-c-v0.1/run.py preflight
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/model_comparison/20260923-four-model-c-v0.1/run.py run --key-file /home/audrey/code_and_papers/2026/FSE/qrefactorbench/docs/deepseek.md
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/model_comparison/20260923-four-model-c-v0.1/collect.py
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/model_comparison/20260923-four-model-c-v0.1/review_formulas.py --output pilot/model_comparison/20260923-four-model-c-v0.1/semantic-review
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/model_comparison/20260923-four-model-c-v0.1/pivot_counterexample.py --output pilot/model_comparison/20260923-four-model-c-v0.1/pivot-witness
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/model_comparison/20260923-four-model-c-v0.1/bind_pro_pivot.py
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/model_comparison/20260923-four-model-c-v0.1/audit.py
```

离线测试的完整pytest命令和输出见上面的验证JSON。未运行A/B、QPU或模型生成的迁移程序；
没有重跑整个主套件（基础设施和题库代码未改）。已有输出拒绝覆盖；公式/反例离线复现
可指定新的临时输出目录，运输和收集入口不要原地重复启动。
