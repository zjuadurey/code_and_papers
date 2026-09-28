# Restricted Codex CLI single-turn pilot baseline

This is a Restricted Codex CLI single-turn pilot baseline using a ChatGPT-authenticated
Codex session. It is not a raw model API baseline and should not be represented as one.

## Fixed protocol

- Input revision: QRefactorBench pilot-v0.1; exactly ten frozen rendered prompts.
  inputs/pilot-NNN/prompt.md is byte-identical to the baseline packet prompt. Each
  already includes the scientific instructions, case facts, common menu and source.
  prompt/baseline_prompt.txt archives their common prefix with a CASE_ID placeholder;
  that derived template is NOT submitted separately or used to rewrite prompts.
- Codex CLI 0.154.0; requested model gpt-5.6-sol (bundled catalog's GPT-5.6 Sol),
  reasoning effort high. No Ultra. Server snapshot is unknown unless exposed.
- Existing ChatGPT authentication only. The CLI receives a read-only mount of its
  existing authentication file. No API key is requested, configured or recorded.
- Exactly one fresh codex exec invocation per case, ephemeral, sandbox read-only,
  approval never, no repository discovery, input via stdin, no output-schema forced
  decoding. JSON parsing happens only after the original response is saved.
- The scientific prompt is unchanged. A fixed developer wrapper prohibits tools,
  file/web browsing, code/tests, delegation, feedback and intermediate messages.
  Its exact text and all arguments are recorded in every per-case metadata record.
- Shell/unified exec, web, apps/plugins/hooks, browser/computer use, memories,
  images, code mode and multi-agent features are disabled. Built-in Codex scaffolding
  is still part of this CLI baseline. Built-in skill descriptions and collaboration
  role instructions remain visible despite skill overrides/multi-agent disablement;
  they contain no benchmark data. This observed limitation is recorded, not hidden.
  The wrapper prohibits using them; inspect saved context and actual tool events.
- No repair, alternate prediction or scientific retry. The runner refuses existing
  first-attempt markers. Malformed JSON stays malformed. No fence stripping or
  field editing. Unspecified sampling parameters remain unknown CLI/provider defaults.
- Built-in provider retry settings cannot be overridden by this CLI; bounded native
  transport behavior remains. Unbounded connection retries are disabled. Visible
  reconnects/errors must be recorded separately from zero operator-level retries.

## Filesystem isolation

The experiment directory is outside the repository. Only frozen baseline prompts
and generic schema documents were copied; no annotator records, private case JSON,
reference plans, annotation-assist notes, tests or old packets were copied.
metadata/input_manifest.json identifies every copied input with its source hash.

Every invocation uses a fresh Bubblewrap mount/PID namespace. It mounts system
runtime files, the CLI binary, a single case prompt read-only at /work, a private
output directory and the authentication file. It does NOT mount the research
repository, other cases, prior responses, normal home directory, Codex session
history, user config, personal skills or IPC state. HOME/CODEX_HOME are temporary;
the host environment is cleared. Network transport exists for authenticated model
inference, while the model web tool is disabled. No model-generated tool operation
is authorized. Event logs are retained to check observed behavior.

The operator has earlier project context, but none is supplied to the separate
prediction processes. Required project setup summaries are not case-generation
evidence. Reports/evaluation are produced only after all case invocations finish.

## Execution and provenance

Run with the existing Python environment:

```bash
/home/audrey/miniconda3/envs/qrefactor-v1-py312/bin/python run_baseline.py smoke
/home/audrey/miniconda3/envs/qrefactor-v1-py312/bin/python run_baseline.py pilot-001
# Inspect only response existence, metadata, tool events and JSON parse status.
# If mechanically sound, invoke pilot-002 through pilot-010 once each.
```

Before the smoke call, read-only preflight checks verify auth, feature flags and
model-visible context. The initial preflight exposed a WSL resolver-mount issue,
then unsupported built-in-provider retry overrides. Both were corrected before
any model invocation; their failure logs are preserved. A later preflight attempted
to disable bundled skill descriptions, but they remain visible. An overstrict audit
assertion about their absence failed and is documented in preflight-summary.json.
These are setup checks, not scientific retries; scientific calls require smoke success.

raw/ holds the CLI's exact last-message bytes; logs/ holds stdout JSONL and stderr.
parsed/ contains byte-identical copies only when the entire raw response is a JSON
object. metadata/ retains UTC/Asia-Shanghai times, version/config, argv, hashes,
exit/parse states, thread/usage events, retries and tool evidence. Original artifacts
are never overwritten. A 900-second per-invocation timeout is an infrastructure
failure, never a reason to replace an answer.

After all ten calls, predictions may be validated/collected with the existing
repository tools and evaluated with --allow-draft. All scores must be labeled
PILOT / NON-FINAL / DRAFT-REFERENCE EVALUATION. Missing practical evidence and null
judgments are not automatically scientific failures. No benchmark changes or
publication-ready capability claims are authorized by this experiment.

CLI syntax was checked locally; supporting official documentation covers
[non-interactive execution](https://learn.chatgpt.com/docs/non-interactive-mode)
and [configuration](https://learn.chatgpt.com/docs/config-file/config-reference).
Local help/catalog/strict parsing take precedence where this installed release
differs, as happened for built-in provider overrides.
