# Codex operating workflow

**READ → ORIENT → SELECT → EXECUTE → VALIDATE → DOCUMENT → HANDOFF.**
Use the repository as memory; never require the user to reconstruct past chats.
The user works primarily inside Codex and prefers concise Chinese communication,
with existing identifiers, commands and research terms unchanged.

## Startup: “读取当前目录” versus “继续”

从父目录 FSE/ 开始时，先遵循其 AGENTS.md 跳转至 qrefactorbench/；从项目根目录
开始时直接读项目 AGENTS.md。不要将父工作区误当成空项目。

**“读取当前目录”／“了解项目”是只读指令。** 阅读入口、charter、当前状态、短队列和
当前交付 README 后，用中文汇报五项：研究目的、当前阶段、已经做到什么、当前版本
与历史实验的区别、下一步及人类决策点。不要只列目录，不自动修改、跑测试或启动实验。
不要为回答已有材料能说明的问题要求用户重述 idea。

**“继续”／“推进”／“proceed”是执行指令。** 读同一阅读链，再按下面流程选择已授权
安全任务；若下一步是科学决定，给一个简短问题。下面步骤针对执行任务；只读读取
完成汇报后停止，不执行第5/6步的工作或写文档。不重跑旧实验，不编造新任务。

1. Read [AGENTS.md](../AGENTS.md).
2. In its order, read [RESEARCH_CHARTER.md](RESEARCH_CHARTER.md),
   [PROJECT_STATUS.md](../PROJECT_STATUS.md), [NEXT_ACTIONS.md](../NEXT_ACTIONS.md),
   [DECISIONS.md](../DECISIONS.md), then this manual and the current status-linked
   handoff/results. Consult [README.md](../README.md) for layout/commands and
   [TODO.md](../TODO.md) only for the relevant backlog detail.
3. Inspect relevant Git status/diff, files and tests before edits. This checkout
   may be nested in a larger Git repository: scope inspection to this project;
   untracked files also count as existing user work. Do not clean or overwrite them.
4. Identify current phase/question, last completed action, accepted/provisional
   constraints, next safe action, and any human blocker. Briefly state the intended
   work and any real documentation/implementation discrepancy. Investigate a conflict
   rather than silently declaring either version correct.
5. If a useful authorized action is unblocked, do it. If blocked, complete any
   independent safe portion, then ask one concise scientific question below.
6. Validate, update status/queue, record meaningful evidence and leave a handoff.
   Do not ask the user to repeat information already present in the repository.

This is an operator workflow. A scientific prediction process must **not** receive
the repository or this reading stack; it receives only its approved blinded input.

## Selecting work without expanding the project

Choose the first applicable NOW item in NEXT_ACTIONS, checking that it is not
already completed. Prefer a concrete artifact that enables the next scientific
decision. Reuse existing tables/forms/results instead of re-summarizing them.
Finish the bounded item and advance the queue; do not regenerate it next session.
Use TODO as a backlog, not an instruction to implement every unchecked item.

If NOW is complete, choose an unblocked AFTER THAT item within existing scope.
If only scientific decisions remain, stop with one decision request. Do not invent
new infrastructure, experiments, cases or agents to avoid stopping. There is no
standing authorization to repeat an experiment whose approved run has completed.

## Autonomy and human decisions

Proceed without routine confirmation for reading, existing tests, schema checks,
consistency/leakage/provenance audits under existing rules, evidence extraction,
review preparation, post-hoc comparisons within an approved analysis scope,
metadata documentation, temporary regeneration from accepted inputs, and obvious
implementation fixes that preserve scientific semantics. Use existing environments;
no dependency installation is required for documentation work.

Document assumptions. Unknown scientific evidence remains unknown; the engineering
convenience of filling a field is not a scientific justification. Reversible does
not mean scientifically neutral: changing a threshold/label can alter conclusions.

Stop for changes to formal task meaning, supported families, disputed ground truth,
scientific assumptions, main metric semantics, case inclusion/exclusion, practical
advantage claims, competing research interpretations, paper contributions, final
release/split decisions, or materially different methodological alternatives.
Routine reformatting and versioned artifact generation need no extra approval
when their inputs and purpose are already approved.

New model experiments need an explicit approved scope/configuration; an example
command or historical README is not a fresh run authorization. Preserve prior
authorization for unfinished approved work, but respect one-shot limits. Do not
install, publish, push, purchase access, execute QPU jobs or change external state
without applicable authorization. Never request or print credentials unnecessarily.
Default to the main thread; do not introduce subagents or agent frameworks.

When genuinely blocked, use this small format (normally in Chinese):

```text
Decision needed: <one concise question>
Why it matters: <2–5 sentences tied to the current evidence>
Options:
A. <meaningful option>
B. <meaningful option>
C. <only if needed>
Recommended default: <evidence-supported option, otherwise “no clear default”>
Files/evidence: <specific paths>
```

Ask one unresolved question, not a questionnaire or a generic request to continue.
Do not ask already answered questions again. Record a human answer in the decision
ledger, queue and status so the next session can apply it.

## Experiment and frozen-artifact hygiene

- Never modify observed/distributed input snapshots, raw responses, metadata or
  historical reports in place. Hash manifests identify bytes, not scientific truth.
  Put corrections/new analyses in a new version or a separately linked addendum.
- A new prompt condition is not a new model. Preserve the distinction between
  original baseline, retrospective diagnosis, and paired controlled diagnostic.
- Record actual model/CLI/configuration, prompt/input/output hashes, timestamps,
  isolation, retries, repairs, tool use and parse failures. Unknown server snapshot,
  seed or sampling details stay unknown. Do not claim deterministic model sampling.
- Preserve first attempts and raw outputs under the approved protocol. Do not
  repair malformed outputs, retry weak answers or use execution feedback unless
  a separate approved experiment explicitly permits it.
- Audit input allowlists and prose task cues; exclude references, proposals, prior
  responses and diagnostic conclusions from blinded prediction input. Coordinator
  review of outputs is not independent A/B annotation. Never give an output-review
  worksheet to annotators who must remain blind.
- Version benchmark/input changes after observing model behavior. Do not retroactively
  adjust labels or metrics to improve an experiment. DRAFT scores remain provisional.
- Execution success, detailed plans, and schema validity do not establish semantic
  preservation. Resource analysis remains distinct from semantic validation.

Use experiment-local READMEs for exact historical execution commands. Do not launch
the stored runners merely to verify documentation. The conditional-plan run's
authorization is complete; future invocation needs a new explicit experiment scope.

## Validation proportional to the work

For documentation-only work: verify local links/paths, reconcile claims with saved
results, compare before/after hashes of protected cases/code/schemas/predictions,
and record the audit. Do not rerun models or install Markdown tooling. Existing
tests need not be rerun for prose alone; say which checks actually ran.

For implementation changes: inspect relevant tests, run focused checks, then required
integration checks in existing environments. Use [validation.md](validation.md) and
the latest experiment validation record linked from PROJECT_STATUS. Preserve failures
and distinguish skips from passes. Do not execute generated code through trusted
helpers without review; the trusted execution API is not a sandbox.

Regenerate derived data only in a fresh temporary/versioned directory; compare it
with frozen artifacts rather than overwriting them. Do not fabricate a reviewed
label simply to make validation pass.

## End-of-session handoff and documentation ownership

<a id="documentation-sync"></a>

### Documentation sync — 交付前同步表

| 发生的变化 | 必须检查/更新 | 不应做的事 |
|---|---|---|
| 代码或案例修复、版本替换 | 局部 README/验证日志、CHANGELOG；影响当前进度时更新 STATUS/短队列 | 把旧测试结果冒充新验证、覆盖旧实验 |
| 当前优先级或完成状态 | PROJECT_STATUS、NEXT_ACTIONS，TODO 对应任务 | 向短队列反复追加历史全文 |
| 新的研究者决策 | DECISIONS 追加证据/状态，必要时更新 charter/未决问题 | 默默把 PROVISIONAL 改成 ACCEPTED |
| 新实验或重要研究观察 | 实验局部记录、research_log、状态及真实限制 | 在研究日志里堆每次常规测试 |
| 文档整理 | 入口/链接、归档、CHANGELOG；规则变化记决策 | 重跑模型或改科学材料来“验证文档” |
| 只读读取/解释/审核 | 回答中说明证据和限制；无需为普通问答改文件 | 声称进行了未执行的修复 |

每次交付先核对实际 diff/产物：受影响文档是否更新、完成与待定是否区分、当前路径
是否唯一、历史结果是否保留、验证是否真实。STATUS 控制在约100行内、短队列约40行内；
详细历史归日志或归档。没有实质变化不为打勾而修改全部文件。
这是 Codex 操作完成条件；当前没有能自动判断文字语义一致性的 CI，不宣称绝对保证。

- Update PROJECT_STATUS for current phase, actual result, blockers and latest evidence.
- Update NEXT_ACTIONS with a short finite next task and completion condition. Move
  completed work out of NOW; keep detailed future work in TODO.
- Append CHANGELOG for meaningful engineering/documentation work. Append
  [research_log.md](research_log.md) only for significant research observations,
  results, hypotheses or methodology events; do not rewrite old entries.
- Add decision IDs for meaningful choices with status/date/rationale/consequences
  and evidence. Preserve prior states; supersede explicitly rather than silently
  rewriting accepted/provisional decisions. OPEN science stays in open_questions.
- Use PROJECT_STATUS as the current handoff, with links to experiment-local evidence;
  do not create a competing “latest status” file every session.

End with: completed work; actual validation; remaining uncertainty; next safe action;
and one decision question only if blocked. Keep routine narration brief and update
the user during long tasks. The charter changes rarely; status and queue change
when work changes. A fresh session should need only “继续”.
