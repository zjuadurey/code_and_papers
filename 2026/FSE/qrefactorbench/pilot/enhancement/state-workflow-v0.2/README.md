# N-046：新回答的主张绑定与分开的开发／最终检查

2026-09-25。承接D-032委托和N-045短队列，保留v0.1及全部历史实验。
**已让任意新响应在获得明确审核绑定后进入局部检查，不再只认某条历史回答；
没有绑定、含糊、撤回、条件外未验证均保留各自状态。没有新模型调用。**

## 实现及科学范围

[claims.py](claims.py)执行的是审核者对文字主张的显式转录，原模型仍交Phase-1 JSON，
不要求它改交代码或本文件的表达式。绑定记录含响应SHA256、JSON pointer、逐字原句、
解释理由、审核者身份/状态、范围、条件和一个或多个解释。
哈希和原句保证“在检查哪份回答”，**不能自动证明“转录理解得对”**。
协调者审核仍为AI_REVIEW_PENDING，不冒充独立专家验收。

支持两种局部构造：

- `predicate`：对每个候选索引求布尔值，检查标记集合是否恰为原程序选择的唯一索引。
- `ordered_scan`：从首候选出发，按显式比较条件更新incumbent，再与原程序选择比较。

表达式是受限数据：布尔运算、比较、索引、all/any单域量词及abs/isnan/isfinite。
白名单AST解释器有长度、节点和步数上限；不使用eval，不执行模型Python，不执行任意函数。
它能表达两个不同正确构造及错误构造，**不是所有合法量子映射的通用表示**。
无法表示的方案记unsupported/insufficient_evidence；完整电路、资源、回退和程序迁移未验证。

示例转录：原Sol的最大值主张包含如下解释之一：

```python
all(values[i] >= values[k] for k in indices) and not any(values[j] == values[i] for j in indices if j < i)
```

这里values是原程序当前pivot列的绝对值，indices是实际活动行索引。
“排除自身比较”的解释独立保留，不能悄悄选一种方便判错的读法。
`guard`可注明主张只适用于哪些状态；条件外的经典回退仅记声明，没有执行认证。

| 输出状态 | 实际含义 |
|---|---|
| finite_scope_pass | 所列状态均通过；不是全域证明 |
| contradicted | 至少一个具体状态反驳该解释 |
| all_interpretations_contradicted | 保留的每种解释均有反例；不自动判整题错 |
| ambiguous_interpretation | 原文解释尚未消歧，即使某解释有限通过也不能升gold |
| finite_guarded_pass | 条件内通过，另有状态被排除；不是完整修复 |
| not_exercised | 所有状态均被guard排除，没有实际检查到主张 |
| claim_withdrawn | 撤回局部主张；不自动算成功或语义错误 |
| insufficient_evidence | 无绑定或超出表示范围；保持未知 |

绑定损坏/表达式不支持会显式报错，由协调者处理，不能转换成模型数学错误。
Phase-1 JSON schema/任务ID/候选坐标的完整校验仍由原collector负责；这个局部API不替代它。

## 开发证据和评测保留证据

[build.py](build.py)追踪未修改的原程序，复用N-044的可信追踪函数，核对原源码哈希。
没有运行模型生成代码。两个集合是：

| 集合 | 完整请求 | 实际pivot状态 | 允许作为修订反馈 |
|---|---:|---:|---|
| [development](evidence/development.json) | 3 | 13 | 是 |
| [evaluator-reserved](evidence/evaluator-reserved.json) | 12 | 44 | 否 |

开发集合复用普通2×2及已暴露的5×5/6×6。保留集合包含换行、并列、零pivot、三维系统、
不同缩放/维度的消元溢出及空系统。空系统没有pivot状态，只保留其原程序结果，不给局部
谓词凭空加一次通过。所有请求记录输入未修改及原输出/异常；两个集合没有规范化JSON完全
相同的请求，但这些变体仍属同一个已开发母案例，**不是独立程序保留集**。

此处“最终检查”表示未来修订后独立计算、不给模型反馈的角色；旧回答的重放仍是事后诊断。
本次控制测试已用这些集合检验评测器，不能宣称研究者或本对话从未见过它们。
新模型运行前还需固定协议/源hash；独立跨母案例评测仍未建立。

`development_feedback`只接受development角色且验证内容hash。返回白名单字段、首个开发
反例与范围限制，不传修复表达式或保留集结果。测试确实修改了保留集内容并确认反馈不变，
也检查把保留集改名成development但不更新hash会被拒绝。
这是接口与完整性检查，**不是能阻止有写权限程序伪造hash的安全隔离**；模型可见文件的
实际隔离要在后续runner preflight单独检查。

## 实际结果：验证器能区分什么

[control-results.json](evidence/control-results.json)保留11种合成对照结果，均非新模型响应。

| 对照 | 开发检查 | 保留检查 |
|---|---|---|
| NaN-aware谓词、等价strict ordered scan（2种） | 有限通过 | 有限通过 |
| 含自身、排除自身、漏tie、选最后tie（4种错误） | 反驳 | 反驳 |
| 总选首行（第5种错误） | 有限通过 | **反驳** |
| 有限值guard的条件构造 | 条件内通过，排除部分状态 | 同左 |
| 恒假guard | 未实际检查 | 未实际检查 |
| 无法表示、撤回（2种） | 未知／撤回 | 未知／撤回 |

“总选首行”是特别有用的检查：原3个开发请求的pivot恰好都选当前首行，这个错误对照因此
漏检；保留集合的换行输入把它拒绝。**这不是模型作弊或新模型失败，而是开发证据覆盖的限制。**
不能把有限通过反馈写成“你已经正确”。本轮没有据此把保留输入移进反馈集合来制造好结果。

还对780个抽象比较状态（长度1–4，值取NaN/inf/0/1/2）检查正确表达式与独立Python max
定义一致；它们只用于解释器回归，不声称都可由原程序到达，也不增加模型实验样本量。

真实历史Sol响应用含/不含自身两个解释重放，在开发和保留集合上均为
`all_interpretations_contradicted`，范围仍限局部谓词。
[原文绑定](evidence/historical-binding.json)、[开发反馈](evidence/historical-feedback.json)、
[历史保留检查](evidence/historical-reserved.json)分开保存。
四条修订prompt重新生成，均为awaiting_model_not_run，没有补造修订答案。

## 新回答如何接入

[review.py](review.py)提供离线入口。先提取原句生成UNREVIEWED模板；没有填写真实审核
依据前，模板不能评分。下列路径为使用示例，输出文件须不存在：

```bash
PY=/home/audrey/miniconda3/envs/palqo/bin/python
$PY -B pilot/enhancement/state-workflow-v0.2/review.py template --response /tmp/new-response.json --output /tmp/binding-draft.json
# 协调者对照完整回答填写binding：不能只看一句话忽略其它条件/回退。
$PY -B pilot/enhancement/state-workflow-v0.2/review.py feedback --response /tmp/new-response.json --binding /tmp/binding-reviewed.json --suite pilot/enhancement/state-workflow-v0.2/evidence/development.json --output /tmp/development-feedback.json
$PY -B pilot/enhancement/state-workflow-v0.2/review.py evaluate --response /tmp/new-response.json --binding /tmp/binding-reviewed.json --suite pilot/enhancement/state-workflow-v0.2/evidence/evaluator-reserved.json --output /tmp/private-evaluation.json
```

无明确pivot主张、改提名其它区域或合法但超出表示的方案保持未知；不自动填旧公式。
只声明“非NaN时适用”不能证明原程序保证它；应同时记录排除状态和条件建立/回退义务。
人类或协调者转录时间需要单独记录；当前不是端到端自动语义裁判。

## 下一阶段运行方案已具体化，但尚未启动

[protocol.proposed.json](protocol.proposed.json)列出25个固定槽位：5份新初稿，各复制为S/A/V/AV
四个一次修订分支，轮换分支顺序，同一Sol/medium/现有订阅、单并发、每次600秒、无操作员重试。
初稿不完整则保留该失败及未运行依赖，不补写初稿；语义对错不决定是否分配修订机会。
模型响应损坏和基础设施失败分开记录；工具/隔离异常停止剩余调用。

分支都依赖同一初稿及其开发审核；只有开发检查能进入反馈。所有修订结束后再进行最终
检查，避免先看到保留结果再影响转录/反馈。最终绑定须先于最终评测固定。
没有可转录主张时提供证据不足，不拿别的区域强行套pivot反例。
主表保留每支5槽位；局部修复、缩小范围、撤回、未知及退化分别报告，无整题总分。

**当前run_authorization=null**。这份文件是具体预算与依赖计划，不是模型调用器。
下一步把既有隔离传输接到这些状态/审核接口，验证只给模型对应prompt、不能看到保留集合。
本机实际读到CLI为0.156.1，历史实验为0.155.1；不能直接继承旧preflight通过结论。
完成本地适配与预检后，再请求这25次新调用的授权。不会复用D-031已经用完的15次授权。

## 验证与复现

实际执行与输出保存在 [final-tests.json](final-tests.json)、[stdout](final-tests.stdout.txt)：

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -B -m pytest -q -p no:cacheprovider pilot/enhancement/state-workflow-v0.2/test_claims.py pilot/enhancement/state-workflow-v0.1/test_workflow.py
# 49 passed：37项新版＋12项前版回归
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/enhancement/state-workflow-v0.2/build.py --output /tmp/state-workflow-v02-new
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/enhancement/state-workflow-v0.2/prepare_protocol.py --output /tmp/state-workflow-proposal-new.json
```

构建测试逐字节再生本次evidence，检查正/负/等价对照、guard、未知、撤回、歧义、原文绑定
破坏、解释器限制、集合隔离、25槽位和输出不覆盖。先前32/46项中间检查另行保留。
[validation.json](validation.json)记录本次源hash、2364个指定旧文件完整性和局部链接。
未重跑共享主套件；未改共享实现/原题/标签/论文，未安装、运行模型/QPU或提交/推送。
