# QRefactorBench

面向 **FSE 2027** 的研究基础设施：帮助非量子专家分析已有经典软件的
**WHERE → WHETHER → HOW → REFACTOR → VALIDATE**。
把量子计算看作异构加速器，默认保持原软件合同，并允许保持经典。
长期目标是有证据支持的收益；当前范围是 Python/Qiskit、Search 与 Optimization。

## 新对话从这里开始

在 FSE/ 或 qrefactorbench/ 打开新对话，只需说：

> 读取当前目录

Codex 应按 [AGENTS.md](AGENTS.md) → [研究意图](docs/RESEARCH_CHARTER.md) →
[当前进度与版本表](PROJECT_STATUS.md) → [下一步](NEXT_ACTIONS.md) 阅读，简短汇报。
此指令只读；说“继续”才推进已授权安全任务。无需重新粘贴研究 idea。
改动前还须核对 [决策](DECISIONS.md)、[工作规程](docs/CODEX_WORKFLOW.md) 和相关源码/测试。

## 现在做到哪里

Phase 1：案例建设与任务验证。当前十组来源案例及30份 A/B/C 输入已准备，
最近修复了两处合同实现问题和一处显式算法提示。**当前包、验证日志及历史 baseline
输入的唯一路径表在 PROJECT_STATUS**，避免与旧 pilot 的十个案例混淆。
所有案例仍为 DRAFT；未运行当前十组的新模型实验。难度由实验检验，不是构建前置门槛。

已完成一次 Restricted Codex CLI baseline 和一次条件计划受控诊断；
诊断不算独立 baseline，计划非空不等于技术正确或量子优势。
[研究方法](docs/benchmark_design.md) · [注释指南](docs/annotation_guidelines.md) ·
[评测协议](docs/evaluation_protocol.md) · [未决问题](docs/open_questions.md)。

工程历史见 [CHANGELOG](CHANGELOG.md)，科学观察见 [研究日志](docs/research_log.md)；
[TODO](TODO.md) 是长 backlog，不替代短队列。旧 [Phase-1 handoff](PHASE1_PILOT_STATUS.md)
和 [pilot-v0.1 修改记录](PILOT_V01_CHANGELOG.md) 都是历史记录，不是当前实验入口。

[终端 demo](demo/README.md) 与 [局部 Qiskit 原型](demo/context001_qiskit/README.md)
保留，均不代表通用正确迁移；已知原型精确性失败见当前状态。
[CA6000 作业](coursework/sat_case_study/README.md) 独立保留，默认不再推进。

## Commands

Python >=3.10 is required. Installation below is an option for an environment where
dependency installation has been authorized; initialization reused existing Conda
environments instead. Optional extras provide YAML and Qiskit:

```bash
python -m pip install -e '.[test,yaml,quantum]'
python -m pytest -q
qrefactorbench validate cases/
qrefactorbench summarize cases/ --json
qrefactorbench summarize cases/pilot --json
```

From a source checkout in an existing environment with jsonschema/referencing,
use `python -m qrefactorbench` in place of `qrefactorbench`; no install is needed.
The scripts/ wrappers provide the same operations. Validation never executes code.
Exit codes: 0 valid/completed, 1 invalid dataset, 2 input/coverage/dependency errors.
Draft warnings do not fail structural validation. For externally collected **historical pilot**
responses, use the provider-neutral workflow below; it is not an evaluation command
for the new A/B/C collection. No model call is made; responses must be obtained separately:

```bash
python scripts/prepare_pilot.py collect --responses /path/to/run/responses --output /path/to/run/predictions.json
python -m qrefactorbench evaluate cases/pilot /path/to/run/predictions.json --allow-draft --json
```

Historical pilot A/B/adjudication/model packets remain under pilot/packets-v0.1/. The coordinator
distributes only the appropriate role directory, never the full repository or
common parent. See [pilot/README.md](pilot/README.md) for blinding and regeneration.

Legacy predictions use schemas/prediction.schema.json (v0.1.0). The Phase-1 profile
is schemas/phase1_prediction.schema.json (v0.2.0), adding separate predicted labels,
free-text intent and applicability evidence. Both are accepted as JSON arrays.
REMAIN_CLASSICAL permits an empty candidate list. QUANTUMIZE requires a candidate
and structured plan. Evaluation is static, deterministic and produces JSON with
component results and input/implementation hashes. It never applies patches or
runs generated code. Trusted execution, semantic and contract interfaces are
documented in the evaluation protocol; their existence is not a completed
end-to-end migration evaluator.

## Repository map

| Path | Purpose |
| --- | --- |
| schemas/ | case, legacy prediction, migration-plan and Phase-1 prediction schemas |
| cases/ | four original DRAFT toys plus ten DRAFT pilot programs and classical tests |
| pilot/ | private sampling plan, shared contract menu, blind packets, baseline and failure-analysis forms |
| templates/ | positive, hard-negative and negative human annotation scaffolds |
| qrefactorbench/ | loader, validator, CLI, fingerprints and modular evaluators |
| tests/ | validation, scoring, execution-hook and optional Qiskit/YAML tests |
| examples/ | deliberately incomplete predictions for CLI demonstrations |
| scripts/ | source-checkout command wrappers |
| docs/ | research protocol, questions, notebook and actual validation record |

Tests under tests/ run classical toy tests in separate processes to avoid module
name collisions. `pytest` in a toy directory can also run that case's classical
test. Quantum-specific optional tests skip cleanly if Qiskit is unavailable.

Review preparation N-001 is complete. [D-014](DECISIONS.md#d-014-conditional-planning-independent-of-adoption)
records researcher choice A: future protocols require conditional plans for structural
YES independently of adoption. NEXT_ACTIONS now waits for actual human plan review;
do not ask the policy question again, regenerate forms or launch another run.
Scientific progression requires human plan review and independent case
annotation/adjudication. Licensing is pending; see
[LICENSE](LICENSE) before redistribution. Real-world provenance remains future work.
