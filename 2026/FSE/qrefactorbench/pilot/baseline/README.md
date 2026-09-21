# Direct-LLM baseline protocol — Phase 1 (PROVISIONAL)

**Historical provider-neutral protocol (2026-09-18):** the “no model call” statement
below describes its preparation date. The completed [Restricted Codex baseline](../baseline-v0.1/restricted-codex/README.md)
and [conditional-plan diagnostic](../baseline-v0.1/conditional-plan-diagnostic/README.md)
have separate frozen protocols/results. This page does not authorize another run.
Current task numbering is cross-referenced in the [charter](../../docs/RESEARCH_CHARTER.md);
historical T1/T2/T3 meanings below remain unchanged.

**Export source:** [packet_instructions.v0.1.md](packet_instructions.v0.1.md) is
byte-identical to the frozen pilot-v0.1 baseline instructions and is the source
used by `prepare_packets`. This README is coordinator-facing project documentation
and is not exported. Keep the versioned instructions unchanged; a future approved
protocol needs a new version. The snapshot's historical wording is retained for
reproduction and does not authorize another model run.

This is a one-response T1/T2/T3 baseline. No model/provider is configured and no
model call has been made. Select a strong generic code LLM and record its exact
identifier/revision; this protocol does not assume a provider, credentials or SDK.

## Run procedure

1. The coordinator reviews public_task facts and the common DRAFT contract menu,
   then fixes the packet before annotation/baseline collection. Distribute only
   baseline/ from the prepared packet to the model operator. Do not expose
   case.json, category manifest, curator notes, reference plans, tests, annotations
   or the repository. The packet's schema documents contain formats only.
2. Copy run_metadata.template.json to a separate run directory. Record the model,
   provider, revision/date, decoding settings, token limit, actual system message,
   packet manifest hash and any provider defaults/unavailable controls. Keep
   credentials outside the repository; none are required by these local scripts.
3. Submit each prompts/pilot-NNN.md verbatim in a fresh context with the same fixed
   system message and settings. Exactly one response per case, with no tools,
   retrieval, execution feedback, repairs or cross-case conversation. A fixed low
   temperature is a possible run setting, not a reproducibility guarantee. Record
   the actual setting rather than assuming a seed is supported.
4. Preserve the raw response, request/response identifiers when available, elapsed
   time, stop reason, token usage and errors. Store one JSON object per case as
   responses/pilot-NNN.json only if the raw response is itself valid JSON. Preserve
   malformed/fenced/truncated responses unchanged as raw files; do not silently
   strip fences or re-prompt. Record failure before deciding any later analysis policy.
5. Locally collect and evaluate from the source checkout (these commands make no
   API calls):

```bash
python scripts/prepare_pilot.py collect --responses /path/to/run/responses --output /path/to/run/predictions.json
python -m qrefactorbench evaluate cases/pilot /path/to/run/predictions.json --allow-draft --json > /path/to/run/evaluation.json
```

The collector requires all ten IDs, validates schema/paths/spans, preserves every
prediction value, refuses overwrite and does not repair responses. Errors do not
generate artificial REMAIN_CLASSICAL answers or a partial-success aggregate. Keep
failed calls in run metadata. To inspect a deliberately selected valid subset,
create an array containing only those unchanged responses and pass explicit
`--case-id` options to evaluate; report selected IDs, excluded failures and coverage
as subset diagnostics, never as the full ten-case score. The final missing-response
scoring policy is an open scientific question.

Before human adjudication, --allow-draft yields demonstration diagnostics only.
For scientific analysis, prepare a separately versioned human-reviewed dataset
with the same case IDs and point evaluate to that directory, omitting --allow-draft
once annotation statuses permit it. Do not overwrite the seed drafts or silently
promote labels. Human coding of intent and contract conformity remains necessary.

## Output and interpretation

The Phase-1 prediction schema is schemas/phase1_prediction.schema.json, version
0.2.0. Its common fields and nested plan reuse the existing v0.1 schemas. Old v0.1
predictions remain accepted by the evaluator. No generated code is required.
The prompt spells out the complete output object. null retains missing scientific
evidence; REMAIN_CLASSICAL is an explicit abstention, not an unknown answer.

Report T1 exact and line-overlap diagnostics separately; no overlap threshold is
final. T2 retains independent structural/suitability/support labels, family,
free-text intent, assumptions and risks. Conditional accuracy on resolved label
pairs must be accompanied by known-reference/prediction and unresolved counts.
Private intent IDs are not a fair recognition test, so free-text intent needs
human semantic coding. For T3, selecting a shared contract ID is distinct from
demonstrating applicability/conformity. There is no combined Phase-1 pass score.
End-to-end quantumization success is outside the main pilot task and remains
unestablished by this static protocol.

Use the failure-analysis template after independent reference annotation has been
preserved. Investigate empirical patterns before designing any agent technique.
