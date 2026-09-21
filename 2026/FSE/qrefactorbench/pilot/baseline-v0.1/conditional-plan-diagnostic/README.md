# Conditional-plan elicitation diagnostic

This is a controlled diagnostic rerun testing conditional-plan elicitation. It is not an independent model baseline and must not be counted as a separate model in benchmark comparisons.

It uses the existing ChatGPT-authenticated Codex CLI session, not a raw model API. The question is whether explicitly requiring a conditional HOW plan changes plan emission while leaving practical adoption judgments separate. No reference-annotation accuracy scoring is performed.

Completed: ten successful, schema-valid first attempts; no repair, retry or observed
tool use. Eight structural-YES responses now provide conditional plans while
retaining their original practical/final judgments; the two structural-NO controls
remain null. Descriptive review codes eight plans SUBSTANTIVE, with unresolved
semantic/resource obligations. See the paired results and content review below.

## Protocol and sole scientific change

Ten original frozen model-facing pilot-v0.1 prompts are retained byte-for-byte as prefixes. Each receives two newline bytes and exactly the approved instruction in [prompt/conditional_plan_instruction.txt](prompt/conditional_plan_instruction.txt). [PROMPT_DIFF.md](PROMPT_DIFF.md) contains all ten exact textual diffs; [metadata/input_manifest.json](metadata/input_manifest.json) records original/diagnostic hashes. No other task wording, schema, public input, source algorithm, scientific label or evaluator is changed.

The actual isolated run directory is `/home/audrey/qrefactor_conditional_plan_diagnostic/`. Its runner is copied byte-for-byte from the original experiment. [runner_snapshot.txt](runner_snapshot.txt) preserves it; execute only the external copy. The overwrite guard prevents replacing first attempts.

| Control | Configuration |
|---|---|
| CLI | codex-cli 0.154.0; same resolved binary path as original |
| Model argument | gpt-5.6-sol |
| Reasoning | high |
| Authentication | Existing ChatGPT login, read-only authentication mount; no API key |
| Calls | One fresh invocation per case, ten cases, single turn; one separate non-scientific smoke call |
| Sandbox/session | Bubblewrap isolation; Codex read-only, ephemeral; ignore user config/rules; strict config |
| Wrapper | Same developer instruction as original; no tools, delegation, browsing, execution, clarification, or interim messages |
| Input | Explicit stdin bytes; only the current prompt mounted at `/work/prompt.md` |
| Output format | Existing prompt and schema; no constrained decoding, repair or normalization |
| Retry/feedback | Preserve first scientific attempt; no response-quality retry, feedback, or prompt tuning |
| Model snapshot/seed | Effective server snapshot and sampling seed not exposed; no claim of exact sampling reproducibility |

Before scientific calls, authentication/configuration and a fixed-token smoke response were checked. Pilot-001 was checked only for saved response, metadata, parse state, and tool items before continuing 002–010. Scientific content review begins only after all ten calls finish. No prior outputs, diagnostic analysis, annotation proposals, adjudication records or reference answers are supplied to any prediction invocation.

## Isolation and provenance limitations

Each invocation has a new temporary input/output directory, empty isolated home, cleared environment, and fresh thread. Only system runtime, CLI binary, read-only authentication, current prompt and private output directory are mounted. The repository, other cases, previous outputs, host configuration and session history are unavailable. The operator has prior project context; it is not passed to the prediction processes.

The local preflight prompt inspection matches the original after excluding message IDs and timestamps. Built-in skill/collaboration descriptions remain in the CLI harness as before; feature disablement does not remove all descriptive text. The fixed wrapper prohibits using them. This is a local context check, not proof about server internals or training contamination. Native bounded transport retries remain an implementation limitation; operator retries and observed event anomalies are recorded separately.

Schema validity, a non-null plan, and a substantive formulation description are three different observations. None establishes semantic correctness, feasible resources, quantum advantage or a validated benchmark label. The content review is AI-assisted descriptive coding and needs human review; it is not an independent annotation or final failure taxonomy.

## Artifact guide

- [CONDITIONAL_PLAN_DIAGNOSTIC_RESULTS.md](CONDITIONAL_PLAN_DIAGNOSTIC_RESULTS.md): paired observations and Q1–Q5.
- [PLAN_CONTENT_REVIEW.md](PLAN_CONTENT_REVIEW.md): per-plan evidence and unresolved requirements, without reference-label comparison.
- [raw/](raw/), [parsed/](parsed/): unmodified final responses and byte-identical copies of JSON-object responses. Schema errors, if any, are recorded separately rather than repaired.
- [metadata/](metadata/), [logs/](logs/): exact commands, timestamps, hashes, exit/parse/retry records and original CLI events/stderr.
- [metadata/protocol-lock.json](metadata/protocol-lock.json): pre-run configuration and runner/binary hashes.
- [metadata/run-audit.json](metadata/run-audit.json): call/thread/tool/output and configuration comparisons.
- [validation/commands.json](validation/commands.json): exact post-run commands, exit codes and captured output paths. Collector/tests are mechanical checks, not reference scoring.
- [validation/preservation.json](validation/preservation.json): comparison with pre-run fingerprints, including original baseline and frozen packets.

The original `restricted-codex/` remains unchanged. This diagnostic does not authorize additional model runs or a research-system implementation.
