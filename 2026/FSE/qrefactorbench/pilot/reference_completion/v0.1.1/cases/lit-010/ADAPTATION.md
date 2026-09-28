# lit-010 — HPCG unpreconditioned recurrence → sparse iteration review

**PRIVATE · DRAFT / AI-ASSISTED PROPOSAL — NOT GROUND TRUTH.**

[CG_ref.cpp](../../../v0.1/sources/hpcg_CG.cpp), [SpMV](../../../v0.1/sources/hpcg_SPMV.cpp) and
[TestSymmetry](../../../v0.1/sources/hpcg_symmetry.cpp) are pinned official HPCG files,
BSD-3-Clause notices retained. New Python implements the unpreconditioned recurrence
with explicit sparse records and a caller's iteration budget. This is a manual
algorithm adaptation, **not** a C++ migration system, full HPCG port or valid HPCG run.
No MPI, multigrid, setup amortization or GFLOP/s rating is implemented.

New application requires whole-vector output, recurrent residual trace, actual iteration
count and directly recomputed final residual. Positive strict diagonal dominance and
symmetry restrict this DRAFT's valid domain explicitly. Validation sorts entry indices;
initially zero residual is handled without the source's ratio division. Error handling,
JSON/named interface and inspect branch are authored requirements.

WHERE is genuinely multi-stage here: sparse apply, dot products and recurrence share
state and budgets. Replacing a step with an exact linear solution can improve residual
yet violate the requested iterate/trace. Tests demonstrate that contrast, not that any
specific region is quantum-eligible. This is a retention/scope-control proposal under
the current search/optimization families; no new numerical quantum family is enabled.

[Tests](test_program.py): independently derived one-step `[0.25,0.5]` differs from
exact `[1/11,7/11]`; two steps, inspect, zero budget, tolerance stop and zero initial
residual; sparse/dense agreement; symmetry identity; invalid matrices and wrong exact
substitution. [methods.py](../../../v0.1/methods.py) additionally detects a deliberately broken
bilinear symmetry identity. Its raw defect is not the full upstream scaled TestSymmetry
score and no upstream cutoff is imported as a quantum correctness rule.
