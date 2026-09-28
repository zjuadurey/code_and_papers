# Eight reference groups / sixteen core–context views

**DRAFT / AI-ASSISTED MATERIAL — NOT GROUND TRUTH.**

2026-09-21: the researcher authorized expanding the four prepared exemplar groups.
This bounded expansion adds four mother problems and their paired views, using
the existing construction standards. It does not certify any quantumization label,
approve a model run, or freeze a benchmark. Earlier review remains pending; user
authorization to expand is not an independent annotation.

Start with [tomorrow's review table](TOMORROW_REVIEW.md). This package contains
**8 problem groups × 2 views = 16 public inputs**, not 16 independent problems.
The two views share a computation and lineage; several groups also share old pilot
parents or mathematical structure. No train/test split or independence claim is made.

| Group | Core / context IDs | Functional need | Source and review status |
|---|---|---|---|
| 1 | core-001 / context-001 | Assess and change two-window maintenance arrangements | Pinned C2\|Q> MaxCut kernel; synthetic context; prior exact contract preserved |
| 2 | core-002 / context-002 | Assess connection coverage and transfer inspection work | Pinned C2\|Q> vertex-cover kernel; synthetic context |
| 3 | core-003 / context-003 | Decide whether fixed feature settings permit a completion | Existing synthetic pilot-001; context from v0.2 |
| 4 | core-004 / context-004 | Seal an ordered batch with required per-event audit callbacks | Existing synthetic pilot-002; context from v0.2 |
| 5 | core-005 / context-005 | Assess exact capacity requests using eligible indivisible lots | Existing synthetic pilot-007 function, unchanged; new context |
| 6 | core-006 / context-006 | Assess current component charges and attainable charge floor | Existing synthetic pilot-006 function, unchanged; new context |
| 7 | core-007 / context-007 | Select archive items within hard capacity and prepare transfers | New synthetic kernel and context; no external-source attribution |
| 8 | core-008 / context-008 | Export all labelled normalized row copies without mutable aliasing | Existing synthetic pilot-008 function, unchanged; new context |

Design coverage is two search-oriented proposals, two unconstrained-objective
proposals, two constrained-objective proposals and two retention controls. These
are **curation intentions**, not reviewed scientific labels. Search vs optimization
can overlap mathematically; this balance is not a final task taxonomy. Only the
existing two positive quantum families are in scope.

## What is new and what stays fixed

New implementation/test files live in [cases/](cases/), with a standalone newly
authored [core-007](cores/core-007.py). Existing functions are preserved verbatim
inside the other three new helper modules. [provenance.json](provenance.json) records
origin, parent source hashes, source rights, synthetic/Codex assistance and the
core/context domain relation. New code/package rights are `NOASSERTION`; absence
of a verified license is not permission to redistribute. The earlier two C2\|Q>
source attributions do not grant provenance or licensing to these new programs.

[PAIR_INDEX.json](PAIR_INDEX.json) retains the previous four groups and adds four;
the inherited `independent_problem_count: 1` means “count this mother problem once,”
not statistical independence. The index's counting note makes this explicit.

The earlier eight public views are byte-identical. The original `cases/` collection
still contains fourteen DRAFT cases. New review manifests stay outside that frozen
population, rather than silently changing a baseline denominator. New manifest
scientific labels, expected decisions, intent/family and reference plans are null.
Their required `case_type` and candidate nominations are private provisional design
proposals under the existing schema. They must not be used as scored gold labels.

Each new case includes source, public software contract, private DRAFT manifest,
independent tests, an executable request/report example, and [case-specific review
notes](cases/context-005/REVIEW.md). Reports are generated classical examples checked
by independent test oracles; they are not migration outputs or model responses.

## Two layers and contracts

Core views expose the computational function and its valid-domain contract.
Context views additionally require input validation, eligibility or coefficient
preparation, meaningful reports and interface behavior. Every new context step
affects a specified observable outcome; none is an unrelated line-count distractor.
These views support **kernel and small-program** study. They do not add a separate
third `function_with_distractors` tier or establish that localization is difficult.

The context may intentionally use a business subdomain of the source core:
positive inventory units vs signed integer totals; distinct component adjustments
vs possible self-couplings; rectangular tables vs ragged rows. Both domains and
relations are public and tested. No source function is narrowed or silently altered.
No artificial simulator-sized domain cap is imposed. Exhaustive classical functions
can be expensive; bounded tests are not a claim that large inputs are practical.

Original-contract preservation remains the default. New contexts require exact
decisions/values and their stated output, tie, error and alias semantics. No sampling
success, exactness relaxation or approximation threshold has been silently added.
Context-001's separately authorized approximate profile remains in its existing
[draft](../../context_adaptations/v0.2-draft/CONTRACT_CONTEXT_001.md); its threshold
is pending and it is **not** substituted for the old exact public input here.

## Public/private boundary and commands

[review_inputs/](review_inputs/) contains only source files and five-key public
specifications: `case_id`, `title`, `software_contract`, `input_domain`,
`execution_assumptions`, plus a global hash manifest. It contains **40 files across
16 views + one manifest**. Never give a model this parent directory, review notes,
tests/examples, manifests, source lineage index, or previous model results.
There is no model invocation in this package.

The allowlist and reproducible exporter follow the existing pattern. From repository
root, using the already installed environment (no installation needed):

```bash
PY=/home/audrey/miniconda3/envs/palqo/bin/python
# Use a fresh destination; refuses overwrite.
$PY pilot/reference_cases/v0.3/prepare_inputs.py --output /tmp/qrefactor-review-v03
# Run each context in its own process, avoiding local module-name collisions.
for id in 005 006 007 008; do
  $PY -m pytest -q pilot/reference_cases/v0.3/cases/context-$id/test_program.py
done
$PY -m pytest -q pilot/reference_cases/v0.3/test_views.py
$PY -m qrefactorbench validate pilot/reference_cases/v0.3/cases/
$PY -m qrefactorbench summarize pilot/reference_cases/v0.3/cases/ --json
$PY pilot/reference_cases/v0.3/cases/context-007/program.py \
  < pilot/reference_cases/v0.3/cases/context-007/example_request.json
```

Allowlisting and obvious-cue checks exclude reference fields and explicit expected
quantum-family/category prose. Functional names/objectives and visible source
structure remain; this is not proof of zero task cueing or independently hard WHERE.

## Validation and interpretation

Exact commands, exit codes and raw logs are in [validation.json](validation.json)
and [validation/](validation/). Focused new context tests: 25 + 25 + 25 + 24 passes;
pair/domain/export tests: 10 passes. Bounded oracle checks cover 259 inventories,
231 component catalogues / 1,781 current-selection comparisons, 85 item lists with
all tested capacities/current selections, and 321 table/copy configurations.
These are engineering input checks, not new benchmark cases or statistical samples.

Core regression: **97 passed, 15 skipped in 3.45s** in existing `palqo`; skips are
optional Qiskit/PyYAML features unavailable there. New four and original fourteen
manifests validate and summarize successfully. **926 pre-existing protected files
remain unchanged.** No quantum code changed, so no optional quantum suite was rerun.

Tests use separate subset enumeration/named functional definitions, fractional value
references, and deliberate wrong substitutes: including held stock, substituting
total capacity for exact existence, dropping pair charges, infeasible/suboptimal
selection, wrong ties, corrupt manifests, reordered labels and aliased copies.
Source identity, broader core domains, whole-input validation, standalone execution,
old-view identity, deterministic export and overwrite refusal are also checked.

The suite does not validate quantum algorithms, reversible oracles, penalty choices,
approximate acceptance, practical suitability, actual advantage or reviewer agreement.
No model/QPU/quantum-solver run, schema/evaluator change, dependency installation,
scientific-label promotion, or large generated population occurred.
