# Information sufficiency — blinded input audit

**AI-ASSISTED PROPOSAL — NOT GROUND TRUTH** · 2026-09-19.

This is an audit of supplied information, not a request to silently repair cases.
YES means enough information for the specified limited judgment; PARTIAL means a
conditional proposal is possible but not a complete admissibility determination;
NO means the needed evidence is absent. These values are **not** the structural
or practical labels in the individual proposals. Independence limitations from
TOMORROW_REVIEW.md apply throughout.

| Case | WHERE info sufficient? | Structural info sufficient? | Practical info sufficient? | HOW info sufficient? | Missing info / source issue |
| --- | --- | --- | --- | --- | --- |
| 001 | PARTIAL: loop/helper visible, boundary policy missing | YES for finite predicate; no constructed oracle | NO | PARTIAL: conditional search plan only | n/clauses/widths/distribution, reversible helper/data costs, no-solution policy |
| 002 | YES for scoped NONE; hotspot convention pending | YES for current scope exclusion | YES only for scope-based abstention; NO for timing comparison | N/A quantum plan; retaining classical behavior is specified | Candidate versus rejected hotspot convention; callback details/timings if performance is later studied |
| 003 | YES: objective and optimization block visible | YES for explicit quadratic expression | NO | PARTIAL: QUBO/Ising outline; exact execution unresolved | n/density/weights, precision, classical comparator, optimizer/shots, exact optimum certification |
| 004 | YES: guarded membership kernel visible | YES for finite index predicate | NO: the bound 8 is known, costs/rubric are not | PARTIAL: conditional search encoding; retain guard | Integer widths, target/cost metric, setup budget, empty/padded states and exact absence |
| 005 | PARTIAL: kernel/preprocessing/interface boundary needs policy | YES for finite predicate and candidate quadratic reformulation | NO | PARTIAL: alternative-family and slack choices need review | Offer sizes/widths, preprocessing/loading costs, comparable sku types, exact feasibility policy |
| 006 | YES: minimization and energy visible | YES: direct binary quadratic form | NO | PARTIAL: algebra clear; exact solver unavailable | Variable/coefficient bounds, tuple→matrix conventions, budgets, exactness/certification |
| 007 | YES: finite subset enumeration visible | YES: predicate and squared-residual quadratic form | NO | PARTIAL: choose admissible family/encoding | Signed arithmetic width, sizes/distribution, oracle cost, correct zero/no-solution decision |
| 008 | YES for scoped NONE; hotspot convention pending | YES for current scope exclusion | YES only for scope-based abstention; NO for timing comparison | N/A quantum plan; complete classical output required | Candidate convention, detailed numeric/error-domain policy if included in future semantics |
| 009 | PARTIAL: kernel visible; wrapper/domain inconsistent | YES for kernel algebra; PARTIAL for whole-program valid domain | NO | PARTIAL: soft-cost encoding and exactness need review | name integer in public task versus str validator; costs/budgets, exactness, metadata/errors |
| 010 | YES: lookup separable from mandatory full parse | PARTIAL: finite predicate visible, representation/domain details incomplete | NO: one-use loading cost is an obligation, not a measured dominance result | PARTIAL: preserve parse order, construct/cost oracle | Batch/field widths and types, loading/lookup comparison, target, exact absence policy |

No supplied input profile justifies a positive practical-suitability conclusion for
any of the eight structurally proposed cases. Nor does missing evidence alone
prove a negative cost comparison. In particular, “at most eight” (004) and “fresh
data once” (010) are relevant constraints, but a decision policy is still needed
to turn them into categorical suitability labels.

The actual size parameters often exist in the API (n, list lengths); what is absent
is the **intended workload instance/distribution and resource regime**. This is not
the same as claiming that the search space cannot be expressed: 001 and the subset
loops explicitly define finite mask spaces.

## Repeated omissions and construct validity

- **Practical target undefined:** 001, 003–007, 009, 010 lack an approved metric,
  cost/resource regime and comparable classical reference. Query/formulation
  arguments cannot establish end-to-end software suitability.
- **Exact interface versus stochastic execution:** exact booleans in 001/004/005/007/010
  and exact extrema in 003/006/009 need a declared semantic policy. The supplied
  common menu explicitly leaves this unresolved.
- **Unbounded Python data versus finite quantum registers:** arithmetic values in
  004–007/009 and record/key representations in 010 need per-instance widths and
  preparation assumptions; concrete finite inputs do not imply free encoding.
- **Alternative formulations versus a single expected family:** the explicit
  residual constructions in 005/007 show why intent and admissible strategy should
  be evaluated separately; no alternate contract is silently added here.
- **Public prose may do part of the task:** software_contract and titles already
  describe the intent in all ten cases. In 005 the assumptions name the enumeration;
  in 002/008 they explicitly exclude a search/optimization reading. Researchers
  must decide whether this is intended specification assistance or a confound.
- **Concrete inconsistent public domain:** 009 calls name an integer field, while
  support.py:2 rejects non-strings. This can be resolved only by choosing the intended
  source/task contract, not by pretending the packet is already unambiguous.

T3 currently asks for a structured plan, not an executed migration. Missing circuit
depth, shots or certified output need not prevent writing a conditional plan;
record them as UNKNOWN. Do not accidentally require completed quantum execution
as a prerequisite for all Phase-1 planning annotations.
