# Documentation consolidation audit — 2026-09-20

This is a documentation/control audit, not a scientific experiment or another
current-status file. [PROJECT_STATUS.md](../PROJECT_STATUS.md) remains the handoff.

## Canonical ownership

| Role | Canonical location | Treatment of overlapping material |
|---|---|---|
| Session entry | [AGENTS.md](../AGENTS.md) | Concise reading order and boundaries; deeper procedure in workflow |
| Stable research intent | [RESEARCH_CHARTER.md](RESEARCH_CHARTER.md) | Existing task_definition retains operational fields/protocol scope |
| Current phase/handoff | [PROJECT_STATUS.md](../PROJECT_STATUS.md) | Historical preparation/validation detail stays in its original records |
| Immediate action queue | [NEXT_ACTIONS.md](../NEXT_ACTIONS.md) | TODO remains the larger backlog, not competing execution instructions |
| Decision history | [DECISIONS.md](../DECISIONS.md) | D-001–D-012 preserved; status conventions/evidence index and administrative D-013 added |
| Codex operating manual | [CODEX_WORKFLOW.md](CODEX_WORKFLOW.md) | No new runner, hooks, automation framework or agent |
| Research history | [research_log.md](research_log.md) | Existing lowercase filename retained; no duplicate RESEARCH_LOG.md |
| Engineering history | [CHANGELOG.md](../CHANGELOG.md) | Append documentation work; no historical rewriting |
| Experiment evidence | Experiment-local README/results/raw/metadata | Original baseline and diagnostic directories untouched |

## Conflicts addressed without changing science

1. Entry documents mixed infrastructure/preparation with completed experiment state.
   README/PROJECT_STATUS now describe Phase-1 task validation. Historical preparation
   handoffs and provider-neutral protocol gain explicit time/context banners, keeping
   their original contents. No frozen experiment report is edited.
2. Historical T1/T2/T3 and the research-intent T1–T6 decomposition differ. The charter
   maps historical T2 to conceptual T2/T3 and historical T3 planning to conceptual
   T4. This does not rename fields, metrics, prompts or scored tasks.
3. Conceptual researcher/expert maturity does not equal schema metadata. Charter and
   annotation guidelines retain DRAFT/REVIEWED/ADJUDICATED/FROZEN and state that expert
   validation needs evidence; no new enum or automatic promotion is introduced.
4. Long TODOs and completed run recipes could imply unlimited work/rerun authority.
   A finite NOW item and explicit consumed one-off authorization avoid that. Routine
   engineering proceeds without repeated confirmation; scientific changes do not.
5. D-007/D-010 record initial versions/preparation facts. The ledger index points to
   D-009 and current results rather than rewriting those decisions retroactively.

Q1/Q6/Q9/Q14/Q19, scientific correctness, formal metric choices and release policy
remain unresolved. Resolving a documentation inconsistency is not adjudication.

## Startup walkthrough

A fresh “继续” follows AGENTS → charter → current status → queue → decisions →
workflow/latest results. It identifies Phase-1 task validation, one baseline plus
one paired diagnostic (not two independent baselines), no active run, and N-001 as
the next safe task. That task creates one coordinator-only blank review record from
existing evidence, not another analysis or an independent annotator's answer sheet.
Afterward, without human responses, the workflow stops for a concise scientific
decision rather than generating more infrastructure. This walkthrough is a static
documentation check; no fresh model session or experiment was launched.

## Validation scope

Local Markdown targets and anchors in changed/new documentation are checked without
network access or new dependencies. Protected-file hashes are compared with a
pre-edit snapshot. Original decision bodies and research-log/changelog prefixes
are checked for preservation; both experiment artifact manifests are verified.
Machine-readable evidence: [documentation control checks](../artifacts/documentation_control/validation.json).

Only documentation and this audit's evidence are changed. No code, schema, case,
packet, prompt, prediction, evaluator, test hook or dependency is changed. No model
or QPU call, test-suite execution, scientific scoring or artifact regeneration was
needed. Existing runtime test results are explicitly attributed to the prior
diagnostic validation, not reported as newly executed here.
