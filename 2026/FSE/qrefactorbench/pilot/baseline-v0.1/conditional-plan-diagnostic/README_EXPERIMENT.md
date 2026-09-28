# Controlled conditional-plan diagnostic — protocol locked before runs

This is a controlled diagnostic rerun testing conditional-plan elicitation. It is not an independent model baseline and must not be counted as a separate model in benchmark comparisons.

Ten frozen pilot-v0.1 rendered model inputs are used with one appended researcher-approved instruction. No prior response, diagnosis or private annotation is supplied. The original runner is copied byte-for-byte: ChatGPT authentication, codex-cli 0.154.0, gpt-5.6-sol, high reasoning, one fresh ephemeral read-only Codex invocation per case in a Bubblewrap namespace. Only that case's prompt is mounted into /work; no repository, other inputs, host configuration/history or previous responses are mounted. CLI built-in harness descriptions remain as in the original experiment.

One non-scientific fixed-token smoke test precedes the ten sequential first-attempt calls. No scientific retries, repairs, tool use, feedback, or prompt tuning. Unmodified schemas validate outputs afterward; null/invalid responses are preserved. No reference scoring is planned. The original server snapshot and sampling seed are unexposed; matching configuration does not guarantee deterministic sampling.

The scientific task addition is prompt/conditional_plan_instruction.txt. Per-input hashes and the model-visible allowlist are in metadata/input_manifest.json; configuration lock in metadata/protocol-lock.json. Per-case metadata records commands, timestamps, hashes, exits, parse states and retries. raw/ preserves exact final-message bytes; parsed/ preserves byte-identical copies only for valid JSON objects. Logs retain events/stderr. The runner refuses overwrite. Never run it from the repository.
