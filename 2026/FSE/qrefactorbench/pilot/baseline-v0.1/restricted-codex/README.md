# First pilot-v0.1 Restricted Codex CLI baseline

**PILOT · NON-FINAL · DRAFT-REFERENCE EVALUATION**

This is a Restricted Codex CLI single-turn pilot baseline using a ChatGPT-authenticated
Codex session. It is not a raw model API baseline and should not be represented as one.

The experiment actually ran: ten cases, ten successful CLI invocations, ten valid
structured predictions, zero failed/malformed predictions, zero operator retries.
No formal human annotation/adjudication or scientific ground-truth promotion occurred.
Start with [BASELINE_RESULTS.md](BASELINE_RESULTS.md) and
[FAILURE_NOTES.md](FAILURE_NOTES.md); machine-readable summary: [SUMMARY.json](SUMMARY.json).

## Exact configuration and procedure

| Item | Recorded configuration |
| --- | --- |
| Authentication | Existing ChatGPT login, verified by codex login status on the host and in isolation; no API key |
| CLI | codex-cli 0.154.0 |
| Model | --model gpt-5.6-sol; local bundled catalog identifies GPT-5.6 Sol and supports high |
| Reasoning | -c model_reasoning_effort="high"; accepted by strict configuration parsing |
| More specific model snapshot | Not exposed in CLI events; do not invent a server revision |
| Invocation | codex exec, stdin prompt, --ephemeral, --sandbox read-only, --skip-git-repo-check, --ignore-user-config, --ignore-rules, --strict-config, --json, --output-last-message |
| Approval | never |
| Sampling | Temperature, seed and token limit not explicitly set; CLI/provider defaults not exposed |
| Input revision | Exact frozen pilot/packets-v0.1/baseline/prompts/pilot-NNN.md bytes |
| Common wrapper | Fixed developer instruction prohibiting tools, browsing, execution, delegation, clarification and interim messages; verbatim in each metadata record |
| Output constraints | Existing prompt/schema only; no --output-schema constrained decoding or post-generation repair |
| Retry | One scientific invocation per case, no replacement; no visible transport retries |
| Timeout | 900 seconds per invocation, never reached |
| Scientific run times | 2026-09-20 07:34:31.890951–07:40:56.526744 UTC; local timestamps also retained |
| Isolated run directory | /home/audrey/qrefactor_baseline_v01/ |

The CLI help explicitly says --ignore-user-config retains CODEX_HOME authentication;
the single smoke call verified this with the actual account. Model availability
was verified by that successful fixed-token call, not inferred solely from a catalog.
It was followed by pilot-001 as a mechanical pipeline check, then 002–010 sequentially.
The operator checked only saving, parsing and tool events after 001; no answer-quality
inspection or prompt/config tuning occurred. Reference-dependent evaluation started
only after all ten scientific invocations finished.

The exact argv arrays, paths, wrapper, UTC/local times, hashes, exit codes, parse
states and usage/thread IDs are in metadata/pilot-NNN.json. For example,
[pilot-001 metadata](metadata/pilot-001.json). [runner_snapshot.txt](runner_snapshot.txt)
archives the exact runner; its SHA256 was fixed before scientific calls and verified
unchanged afterward. Run the actual runner only from the external isolated directory;
do not launch a scientific prediction process from this results checkout.

## Isolation and audit

Each call used a new Bubblewrap filesystem/PID namespace with an empty home and
cleared host environment. Only system runtime files, the CLI executable, the current
case prompt at /work, a fresh private output directory and a read-only authentication
file were mounted. The repository, other cases, previous responses, personal config,
session history, annotation-assist and private labels were unavailable to that process.
No authentication contents were copied to the experiment or results directories.

Shell/unified exec, web, apps/plugins/hooks, browser/computer use, memory and
multi-agent features were disabled; the wrapper also prohibited tool use. Logs show
one turn, one final message and no tool-call item per case. No model code or tests were
executed for solving a case. The separate post-run optional suite includes local
Qiskit checks, which are validation only, not model feedback or baseline computation.

The [input manifest](metadata/input_manifest.json) lists the ten copied prompts
and four generic schema documents; each hash matches the frozen baseline packet.
No populated reference fields or annotation-assist artifacts were found. Generic
schema label definitions and the shared contract menu are intentionally public.
The separate [source packet manifest](metadata/source_packet_manifest.json) identifies
the frozen input. Nothing from the original unfiltered packets was used.

The parent/operator had previous project context; that history was not supplied to
the prediction processes. New thread IDs, isolated paths and the inspected context
support this separation. This does not prove absence of training contamination or
control the provider's internal implementation. Necessary functional specifications
and original program identifiers still convey task information; inputs were not changed.

## Preserved outcomes and deviations

- [raw/](raw/) contains original CLI final-message bytes; [logs/](logs/) contains
  unmodified JSONL/stderr. Copies in parsed/ are byte-identical JSON-object responses.
  The collector made zero repairs; predictions.json only collects the objects.
- [run audit](metadata/run-audit.json) confirms ten unique threads, ten single turns,
  one final message each, matching raw/event bytes, no tool calls and no visible
  transport retries. The smoke response is separate and never evaluated as a case.
- Two pre-model setup failures were preserved: a WSL resolver symlink needed its
  target mounted, and this CLI rejects overriding the reserved openai provider's
  retry settings. They were fixed before the one smoke call; no scientific retry resulted.
- Native bounded transport retry defaults remain because those overrides are not
  supported; unbounded retries were disabled. Zero observed retries is an event-log
  statement, not a guarantee about every underlying HTTP request.
- Built-in skill descriptions and collaboration-role instructions remain in the
  harness despite relevant disablement/overrides. An overstrict setup assertion
  expecting no skill catalog failed and was documented. No private research content
  appears there; no skills or subagents were used. This is a CLI-specific context
  limitation and one reason this cannot be represented as a raw API baseline.
- Each CLI run recorded two fixed startup warning items: development-stage
  skip_host_skill_discovery and code mode failing closed because its host is disabled.
  They did not prevent successful final responses; no warning was erased.
- No scientific-prompt edits, repairs, model substitutions, benchmark modifications,
  API-key setup, extra quantum families or agent architecture occurred.

[README_EXPERIMENT.md](README_EXPERIMENT.md) is the copied isolated protocol record;
its inputs/schema paths refer to the external run directory, not this results copy.
The actual snapshot/profile limitations above take precedence over any expectation
that a disable flag removes all built-in descriptive text.

## Evaluation and validation

Evaluation used the unmodified collector and evaluator against the ten DRAFT cases,
with --allow-draft. [evaluation.DRAFT_REFERENCE.json](evaluation.DRAFT_REFERENCE.json)
is the unmodified result, tagged demonstration_only=true. Do not present conditional
DRAFT agreement as scientific success. Null suitability is not automatically a failure.

Exact commands and outcomes: [validation/README.md](validation/README.md).
Full tests: 87 passed, 3 skipped; separate optional suite: 5 passed. All fourteen
dataset cases validate; all ten predictions collect/evaluate successfully.
[Preservation check](validation/benchmark-preservation.json) confirms **308**
pre-existing benchmark/program/schema/evaluator/test/packet files unchanged.

Next human action: review practical NO versus uncertainty, benchmark-support
terminology, candidate boundary conventions and the absence of structured plans.
Decide whether a future independently versioned protocol should elicit conditional
plans on abstention; do not rerun or repair these ten first-attempt predictions.
