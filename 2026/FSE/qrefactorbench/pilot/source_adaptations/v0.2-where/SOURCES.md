# Source audit and selection: concrete records, not inherited labels

Checked 2026-09-21. The user corrected the expansion direction: find suitable
examples in the reference benchmarks, rather than mainly repackaging existing
local pilot functions. v0.3 remains historical synthetic construction material;
this package starts a separately versioned source-driven route.

## Imported source and attribution

Source: **C2|Q> Dataset**, associated with *C2|Q>: A Robust Framework for Bridging
Classical and Quantum Software Development*, [TOSEM DOI](https://doi.org/10.1145/3803018).
The [maintainer's mirror](https://huggingface.co/datasets/boshuai1/c2q-dataset/tree/c5b457cf425c31e91bae829503ece6e92646dd0a)
is pinned to `c5b457cf425c31e91bae829503ece6e92646dd0a`. Data-card metadata identifies
synthetic Python inputs and **CC-BY-4.0**, not deployed application code. See the
unchanged [downloaded card](sources/DATASET_CARD.md) and [notice](NOTICE.txt).
Source attribution is not author endorsement of these adaptations or labels.

The CSV has 434 data records. We parsed its function definitions and selected ten
records for focused inspection. We did not validate all 434 programs. Row numbers
below count records after the header, not physical CSV lines or author-issued IDs.
Original records, source labels, decoded source and functions are in `sources/`;
they are **curator-only**, not model inputs. The original labels are never copied
into our scientific fields. [Manifest](sources/manifest.json) records hashes.

| Record | Function | Actual behavior / review outcome | Use here |
|---|---|---|---|
| 87 | `clique_brute_force` | Starts subsets at size 2; on one isolated vertex returns `[]` | Excluded from desired all-size largest-group contract; counterexample retained |
| 88 | `clique_greedy` | Ordered inclusion, no backtracking; may be smaller than greatest possible group | Imported as an observable quick-preview policy in lit-004 |
| 93 | `clique_bitmask` | Enumerates masks, retains greatest size and first mask on ties | Imported as the requested largest-group computation in lit-004 |
| 94 | `clique_backtracking` | Recursive include/exclude alternative; tie policy differs from mask enumeration | Reserve alternative, not an independent benchmark problem |
| 97 | `greedy_kcolor_adj_matrix` | First available color without revisiting earlier choices; may block on a feasible instance | Imported as quick preview in lit-003 |
| 98 | `kcolor_backtracking` | Backtracks until first feasible assignment, or raises on no solution | Imported as completion fallback in lit-003 |
| 101 | `kcolor_backtrack_partial` | Dict-based complete assignment alternative; four-vertex witness checked | Reserve alternative, not a new task |
| 103 | `kcolor_with_color_sets` | Ordered greedy assignment despite multiple data structures; same witness blocks | Reserve heuristic variant, no gold infeasibility label |
| 388 | `min_vertex_cover_bruteforce` | For one vertex/no edges returns `{0}` rather than an empty minimum cover | Excluded from desired minimum-cardinality contract; evidence retained |
| 431 | `min_vertex_cover_bnb` | Starts cardinality at 1; returns `{0}` for one vertex/no edges, `None` at n=0 | Excluded from desired total-domain contract; not silently repaired |

These are **10 reviewed source records, 4 imported functions, 2 new mother problems**.
They must not be reported as ten independent benchmark cases. Exclusions concern
our intended contracts; source names/classification alone are not authoritative
specifications. We make no dataset-wide quality rate claim from this selection.

## Exact changes and reproducibility

`fetch_sources.py` downloads only the pinned CSV/card, decodes literal `\n`, extracts
functions and removes top-level demos. It never executes downloaded source. Reviewed
function excerpts contain only local computation; later tests execute them locally.
Fetch to a **new** directory; refusal to overwrite is deliberate:

```bash
python pilot/source_adaptations/v0.2-where/fetch_sources.py --output /tmp/c2q-where-source-check
```

Core views concatenate the selected source functions with attribution. Their
function bodies remain byte-identical. Context adaptations rename variables/functions
to match the new application and integrate control flow; they are **not** claimed to
be unmodified originals. Full diffs: [agenda](source_diffs/agenda.diff),
[release cohorts](source_diffs/cohort.diff). Per-case adaptation notes explain the
semantic correspondence; independent oracles and bounded source-equivalence tests
check it. Exceptions are preserved by type where applicable; new public contracts do
not require the source's exact error messages.

Attribution travels with public views as identical `NOTICE.txt` files. This reveals
generic source provenance consistently, but not selected record IDs or private region
proposals. Do not remove attribution to make a task appear harder. The old packets
remain unchanged. New code/package license is `NOASSERTION`; upstream CC-BY-4.0
does not settle rights for the whole newly authored package. No external release.

## What the other reference benchmarks supplied

The actual checks and decisions are in [REFERENCE_BENCHMARK_AUDIT.md](REFERENCE_BENCHMARK_AUDIT.md).
Only C2|Q> source functions are imported into these two programs. Other benchmarks
inform evaluation or future sourcing; do not describe these cases as copied from
QuanBench, Qiskit HumanEval, MQT Bench or SupermarQ.
