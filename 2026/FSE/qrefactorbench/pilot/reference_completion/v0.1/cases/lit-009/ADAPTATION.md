# lit-009 — HPL problem/validation specification → balance review

**PRIVATE · DRAFT / AI-ASSISTED PROPOSAL — NOT GROUND TRUTH.**

[HPL algorithm page snapshot](../../sources/hpl_algorithm.html) describes dense
linear solving with row partial pivoting and a normalized infinity-norm backward
error. URL/hash in [manifest](../../sources/manifest.json); page redistribution license
not established here. No HPL C code was copied into this new Python implementation.

The adaptation implements a small serial numerical workflow with named variables,
current inspection, solve/inspect branches, deltas and a caller-supplied residual limit.
It does not reproduce MPI/panel algorithms, benchmark timing, random matrix generator,
official HPL compliance or a particular implementation's bitwise output. Numerical
test tolerances are test tolerances, not adopted quantum-semantic thresholds.

The same normalized residual formula is now an executable diagnostic in
[methods.py](../../methods.py). Passing it does not prove full software behavior;
inspection need not solve a singular system, and original inputs remain unchanged.
The supplied limit affects this new application's reported boolean only; no cutoff
is adopted in the main benchmark evaluator.

This is a provisional scope-control proposal. An expensive solve loop may be nominated
for WHERE and later rejected or left uncertain under the current two families.
Continuous linear algebra is not automatically combinatorial optimization; changing
the input/output to a discretized problem would need a different contract. No HHL or
linear-systems positive family is introduced and no universal impossibility is claimed.

[Tests](test_program.py): pivot-required example; every nonsingular 2×2 matrix with
entries -2..2 versus exact rational formulas; singular/empty/inspect paths; wrong-vector
residual witness and invalid data. No performance or quantum experiment ran.
