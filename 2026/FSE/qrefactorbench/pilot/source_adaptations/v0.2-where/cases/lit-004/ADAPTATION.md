# lit-004: release groups from a changing compatibility record

**DRAFT / AI-ASSISTED PROPOSAL — NOT GROUND TRUTH.**

Source: C2|Q> records **88 and 93**, preserved in [ordered preview](../../sources/row-88.decoded.py)
and [complete selection](../../sources/row-93.decoded.py), with [source audit](../../SOURCES.md).
Do not confuse the source dataset's synthetic algorithm snippets with a real package
manager. This application's record/history and reporting requirements are newly authored.

Versions are independently selectable artifacts, not competing versions of one package.
Active/member filtering and the **latest** result for each undirected pair determine
eligibility and compatibility. Pairwise success is explicitly the whole model; it does
not establish real multi-component compatibility. Current, ordered preview and greatest
size proposal have different report roles. Inspect requests must not run full selection.

The [example](example_request.json) has an isolated early `legacy` entry plus a compatible
group `a,b,c`. Preview gives `[legacy]`; requested proposal gives `[a,b,c]`. An old passed
legacy–a result is superseded by a reversed failed result. Ignoring history changes
the graph. [Actual report](example_report.json) preserves both outcomes and their reasons.

## Source transformation / WHERE challenge

- Row 88's ordered inclusion becomes `reports.preview` over an explicit boolean relation.
- Row 93's increasing-mask enumeration is embedded **inside the per-request select
  branch** in `program.review_releases`; it is not exposed as a standalone named
  maximum-clique function in the context view. Its predicate is factored into
  `reports.compatible`; selected indices are decoded through the filtered name list.
- Names and factoring serve the record/report API, not obfuscated identifiers.
  Challenge also comes from policy differences, branches, history and cross-file
  dependencies. [Full transformation diff](../../source_diffs/cohort.diff).
- Source and adapted preview/proposal selections agree on all 76 simple graphs through
  four vertices. An independent combinations oracle checks actual history/filter/current
  reports. These are bounded behavior checks, not scientific validation.

The provisional core nomination includes initialization, subset loop, feasibility test
and incumbent update. `compatible` and the active latest-result relation are required
dependencies. Nominating the whole `review_releases` function would also include
history interpretation, preview and output construction; a migration must explain
which parts remain classical. Nominating only `len(subset)` misses the problem.

Tests expose wrong choices: replace the preview with a larger valid group; reverse
history precedence; drop active filtering; accept every subset; or run the complete
selection during inspection. These are **constructed counterexamples**, not measured
model mistakes or automatic label adjudication.

## Scientific obligations

The core supports a candidate binary selection objective with incompatible-pair
constraints for review under the current optimization family. The benchmark has
not certified a QUBO penalty, quantum solver, precise/tie-preserving decoder or benefit.
An alternative supported formulation is not ruled out merely by the intended family.
Retain the source's smallest numeric mask on equal sizes; it differs from ordinary
lexicographic index-tuple order. Exactness is still required in this version.

WHERE region alternatives, dependency completeness, the meaning of `preview`, pairwise
model realism and workload assumptions need review. Static candidate existence does
not disappear because one request uses inspect mode; active-path suitability is a
separate observation. Scientific fields remain null/DRAFT.
