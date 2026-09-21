# Bounded objective-mapping audit — return to the FSE research track

Date: 2026-09-20. **AI-assisted post-hoc evidence, not ground truth, an independent
review, a new model baseline, or a complete migration-correctness result.**

The researcher ended the coursework diversion and requested continuation of FSE
work. The next evidence gap is whether the saved conditional plans describe
technically consistent transformations, beyond merely containing detailed text.
This audit checks all three optimization plans in the completed diagnostic, rather
than selecting successful-looking examples. Search plans are outside this audit.
No reference annotation was used to judge correctness or assign a label.

## Result

| Saved response | Direct source objective | Plan's minimized binary objective | Inputs checked | Assignments checked | Observation |
|---|---|---|---:|---:|---|
| pilot-003 | Maximum weighted crossing score | `-Σ w(x_u+x_v−2x_ux_v)` | 103 | 393 | Exact arithmetic agrees; negate minimum to recover the API's maximum |
| pilot-006 | Minimum signed binary expression | `Σ b_ix_i+Σ w_ijx_ix_j` | 851 | 3,345 | Signs, repeated terms and diagonal-to-linear folding agree |
| pilot-009 | Minimum unary placement cost plus same-side penalties | `Σ[L_i+(R_i−L_i)x_i]+Σ p(1−x_a−x_b+2x_ax_b)` | 851 | 3,345 | Constant offsets, self-links and repeated terms agree |
| Total | | | **1,805** | **7,083** | No mismatch in this bounded audit |

Each assignment was compared with a direct transcription of the source's objective,
then with exact-rational Ising substitution `x=(1−z)/2`. Each input's recovered
optimum was also compared with an actual call to the original classical function.
All source files were checked against the line-numbered frozen model-facing input.
The original functions are inspected local code; no model-generated code was run.

The binary identities make the correspondence reviewable: `x_u+x_v−2x_ux_v`
equals the crossing indicator; `1−x_a−x_b+2x_ax_b` equals the same-side indicator;
`x_i²=x_i` handles diagonal terms. Ising expansion retains the identity/constant
term, even though that term does not select the optimizing assignment: the API
returns a value, so the shift must be restored. This is an algebraic explanation,
not a verification of Hamiltonian compilation or finite-precision hardware behavior.

## What was checked, and what was not

`check_mappings.py` manually transcribes each response's `plan.formulation` and
the `x=(1−Z)/2` instruction in `plan.input_encoding`. It does not automatically
parse/verify natural-language plans. A mistaken transcription is a review risk.
The evidence supports only the specific objective correspondence represented by
this transcription, not all claims in a response or a scientific accuracy score.

Finite fixture domain (not new benchmark cases or training data):

- `n=0,1,2`; every multiset of zero, one or two ordered-index terms. Ordered indices
  include reversed pairs and self-pairs; multisets include identical repetitions.
- pilot-003/009 term weights `{0,1,3}`; pilot-006 signed weights and biases
  `{-2,0,3}`. Placement unary-cost pairs `{(0,0),(0,2),(3,−1)}`.
- One additional input per case with `n=3`, more than two terms, repeated/reversed
  pairs, zero and diagonal terms, and an integer `2**60+1` above exact binary64 range.
- Every assignment for each fixture; Python integers and `Fraction`, not float
  comparisons with an invented tolerance. All fixtures stay within the public
  domains; they are arithmetic test inputs, not a sample of realistic workloads.

Deliberately incorrect audit variants drop constants, repeated terms or relevant
self-terms, and reverse the cut optimization direction. Concrete distinguishing
assignments are retained in `results.json`. These variants test audit sensitivity;
**they are not defects observed in the saved model outputs**. Dropping cut self-loops
does not change the cut objective and is correctly not treated as a detectable fault.

No QAOA circuit, optimizer, shots, sampling distribution, hardware precision,
resource budget, runtime comparison, generated hybrid implementation, or complete
interface-preservation check is supplied. The placement report's validation and
metadata code were not replaced. Passing objective checks does not validate a
migration of those surrounding behaviors. Existing classical-case tests remain
separate from evidence about a proposed quantum implementation.

## Exactness gap: concrete witnesses, not simulated model failures

| Case | Permitted input | A feasible sampled assignment | Correctly recomputed sample value | Required original API result |
|---|---|---|---:|---:|
| pilot-003 | `n=2; edges=[(0,1,1)]` | `(0,0)` | 0 | 1 |
| pilot-006 | `biases=[−2]; couplings=[]` | `(0,)` | 0 | −2 |
| pilot-009 | One job, `left_cost=0, right_cost=2`; no links | `(1,)` | 2 | 0 |

Repeating only the displayed assignment in a sample set leaves its best observed
value unchanged. These witnesses show that feasibility and rescoring alone do not
imply exact optimality. They do not estimate QAOA failure probability or show that
any actual circuit produced those samples. No quantum circuit was run.

All three saved plans already state that a global-optimality certificate is missing.
Thus the evidence does **not** reveal an undisclosed error or support calling the
plans failed complete implementations: they were conditional proposals. Under
D-015/D-017, objective mapping and complete original-contract preservation remain
separate. Classical exhaustive certification is one possible exact fallback but
has not been selected as a technique or shown useful here.

## Implications and next action

This audit adds limited executable support beyond the earlier SUBSTANTIVE coding.
It does not establish general HOW capability or convert those codings into gold.
No practical-suitability judgment follows. A useful falsifiable next check is
whether the five search plans' predicates/decoding match the original programs
on explicit bounded inputs, including empty domains and no-solution cases.
Reversible-oracle implementation and full contracts would still require separate
evidence. Do not build an agent or run another model merely because a gap is known.

Human review should inspect the transcription, algebra and obligations in the
[existing coordinator record](../../pilot/review/CONDITIONAL_PLAN_HUMAN_REVIEW.md).
Its human fields remain blank. Researchers still decide per-case annotation,
coverage/quality criteria and final methodology. No new review worksheet is needed.

## Reproduce and inspect

From the repository root, redirect a repeat check to a **new** output path:

```bash
/home/audrey/miniconda3/envs/palqo/bin/python artifacts/plan_mapping_audit/check_mappings.py > /tmp/plan_mapping_audit_repeat.json
```

Python standard library only; no installation, credentials or network required.
[Results and source hashes](results.json) include the audit-script hash, original
raw/parsed responses, frozen prompts and original source/public specifications.
[Protected snapshot](before_hashes.json) and [validation](validation.json) record
preservation; no cases, labels, schemas, evaluators, model results, demo or coursework
files were edited. Generated Python bytecode is excluded from preservation hashes.

Actual validation:

- Audit: exit 0, the counts above, all expected deliberately incorrect variants
  distinguished. Independent repeat output is byte-identical in the same environment.
- `python -m pytest -q tests/test_pilot.py tests/test_execution_semantics.py`:
  **29 passed in 2.74s**, using the existing `palqo` Python; [log](pytest.txt).
- `python -m qrefactorbench validate cases/ --json`: **14 valid DRAFT cases**;
  [output](dataset_validation.json). Summary also succeeds: [output](dataset_summary.json).
- Full suite, optional Qiskit tests, model calls and training were not rerun:
  runtime benchmark implementation did not change; the new audit uses no Qiskit.

The script's finite audit population and deliberately incorrect variants are
engineering checks, not new benchmark inclusion criteria, metric semantics or
accepted scientific labels. Frozen experiment reports are preserved without edits.
