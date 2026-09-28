# Source-driven additions with stronger WHERE obligations

**DRAFT / NOT GROUND TRUTH.** This package responds to the researcher's correction:
the previous local-kernel expansion did not meet the intended reference-benchmark
sourcing goal. Earlier eight groups, all public snapshots and experiments are retained;
they are not relabeled as newly sourced workloads.

This version adds **two externally sourced computational problems, each with a
core view and a multi-stage functional-context view**. Four functions come from
four newly selected C2|Q> records; the application requirements are our synthetic
adaptations, not real deployed software. We reviewed ten concrete source records,
not ten new independent cases. [Source audit](SOURCES.md),
[other reference benchmarks](REFERENCE_BENCHMARK_AUDIT.md).

| New case | Imported records | Functional program | WHERE obligations beyond old wrappers |
|---|---|---|---|
| [lit-003](cases/lit-003/ADAPTATION.md) | C2\|Q> 97/98: greedy assignment + backtracking | Participant-aware agenda inspection/completion | Preserve valid current agendas; distinguish blocked preview from infeasibility; trace nested predicate/state and participant-derived conflicts |
| [lit-004](cases/lit-004/ADAPTATION.md) | C2\|Q> 88/93: ordered group + greatest-cardinality group | Release-group review using latest compatibility checks | Distinguish preview and requested proposal, handle inspect/select per request, locate inline selection and cross-file predicate/history/filter dependencies |

## Open these examples first

- [Agenda request](cases/lit-003/example_request.json) → [report](cases/lit-003/example_report.json):
  the ordered preview blocks with two slots, but completion finds a feasible arrangement.
  Selecting the quick path and interpreting its failure as no solution gives a wrong answer.
- [Release request](cases/lit-004/example_request.json) → [report](cases/lit-004/example_report.json):
  preview contains `legacy` alone; the requested group contains `a,b,c`. The latest
  reversed failed check supersedes an old passed check. Replacing preview by a larger
  group changes required behavior; final proposal validity cannot excuse that change.

Private [WHERE review](WHERE_REVIEW.md) gives provisional regions, dependencies,
counterexamples and open scoring questions. **“Harder WHERE” is a hypothesis**, not
an empirical result. No model/quantum run occurred. This implements real selection
and dependency distinctions, not only renamed algorithms or irrelevant filler.

## Source and semantics discipline

Original dataset functions remain byte-identical in core views. Context changes
have [recorded diffs](source_diffs/) and bounded source-equivalence checks; they are
explicitly adapted, not misrepresented as unchanged source. Excluded snippets with
singleton/empty-graph mismatches remain preserved with counterexamples, not repaired
silently. Full reports are checked by independent input-domain oracles.

Existing schema/evaluators are reused unchanged. Both manifests have DRAFT status,
null structural/practical/support/intent/family/decision labels and null plans.
The schema-required positive category and regions are **private sampling proposals**.
No color-specific quantum family is added: prospective plans must stay within the
current search/optimization families, with alternatives and unmet obligations explicit.

The original software-contract default still applies. The new agenda workflow has
its own specified branch behavior; the release workflow retains the source's numeric
mask tie rule, not a new minimum-change objective. We do not grant approximate answers
or assume practical benefit. Existing schemas do not yet encode all dependency/path
review dimensions; they are retained in private documentation, not silently scored.

## Public materials and execution

Only [review_inputs/](review_inputs/) is intended for blind use: four view directories,
16 allowlisted files plus a hash manifest. Every view includes identical attribution
`NOTICE.txt`; no source row metadata, reference labels, tests, expected reports,
region proposals or previous model output is included. Public functional descriptions
still explain what the software must do. Generic source attribution is a known cue;
do not remove license notices or pretend the inputs are cue-free.

`source-core-003` / `source-core-004` each expose two related source operations.
`lit-003` / `lit-004` expose the whole application. These are related views, not four
independent observations. Do not merge this population into historical pilot scores.

From repository root, using the existing environment without installing anything:

```bash
PY=/home/audrey/miniconda3/envs/palqo/bin/python
$PY pilot/source_adaptations/v0.2-where/cases/lit-003/program.py \
  < pilot/source_adaptations/v0.2-where/cases/lit-003/example_request.json
$PY pilot/source_adaptations/v0.2-where/cases/lit-004/program.py \
  < pilot/source_adaptations/v0.2-where/cases/lit-004/example_request.json
# Separate processes avoid collisions between per-case catalog/program modules.
$PY -m pytest -q pilot/source_adaptations/v0.2-where/cases/lit-003/test_program.py
$PY -m pytest -q pilot/source_adaptations/v0.2-where/cases/lit-004/test_program.py
$PY -m pytest -q pilot/source_adaptations/v0.2-where/test_sources_and_views.py
$PY -m qrefactorbench validate pilot/source_adaptations/v0.2-where/cases/
$PY pilot/source_adaptations/v0.2-where/prepare_inputs.py --output /tmp/source-where-review-new
```

The exporter refuses an existing output directory. This is a review package, not
a new frozen baseline prompt or approved experimental runner. Source licensing is
CC-BY-4.0 for the retained/adapted source portions; new material/package license stays
NOASSERTION. No external publication or claim of independent annotation is made.

## Actual validation

- Agenda: **17 passed**; release cohorts: **15 passed**.
- Source/equivalence/export: **6 passed** after fixing a test-harness issue. Its first
  attempt had **5 passed / 1 failed** because executing a copied packet created Python
  bytecode files before a directory identity check. Subprocesses now use `-B`; the
  allowlist/hash assertions and source behavior were not weakened. First log retained.
- Full existing suite: **97 passed / 15 optional skips in 3.45s**. Skips reflect
  unavailable Qiskit/PyYAML in palqo; no quantum code changed or optional suite rerun.
- Both new DRAFT manifests and fourteen original cases validate and summarize.
- Bounded checks: all 76 simple graphs through four vertices; agenda slot counts 0–3
  give 304 graph/count combinations. Release contexts additionally test active filters,
  check history, both modes, exact masks and independent reports. These are test inputs,
  not more benchmark cases or evidence of quantum advantage.

Commands/logs and protected-artifact/link checks: [validation.json](validation.json).
Current new test total is **38 passed**. Earlier cases, schemas, evaluators, model
outputs and quantum artifacts are protected by a before/after hash audit.

## Next review

Inspect the two reports and code paths. Decide whether the synthetic functional
requirements are useful, and review provisional candidate/dependency boundaries.
Only after this construction direction is satisfactory should additional source
problems be admitted. Do not count algorithm variants as independent diversity or
translate unrelated quantum circuit tasks into supposedly existing classical software.
