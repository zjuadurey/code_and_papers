# lit-007 — SupermarQ signed SK objective → pair-preference review

**PRIVATE · DRAFT / AI-ASSISTED PROPOSAL — NOT GROUND TRUTH.**

[Pinned QAOAVanillaProxy](../../sources/supermarq.py) supplies a complete signed ±1
pair Hamiltonian and `_get_energy_for_bitstring`: equal bits contribute `-weight`,
different bits `+weight`. `_get_opt_angles` minimizes the negative expectation, so
the intended objective here is **maximize**, not minimize. Apache-2.0 attribution retained.

We adapted that exact score formula and authored deterministic enumeration, named
together/apart preferences, inspection and movement reports. Source random generation,
Cirq/QAOA optimizer, five restarts and hardware execution are not imported or run.
The example's pair signs are our explicit fixture, not an upstream published instance.
Smallest-mask ties and full report are new synthetic application obligations.

WHERE: distinguish the scalar score used by both current/proposed reports from the
enumeration/selection that produces a proposal. Input complete-pair validation and
relation-sign conversion affect the objective; removing negative signs changes the
problem. Group emptiness and equal-score moves are legal in this contract; do not
silently impose balance or minimum movement.

[Tests](test_program.py) execute only the reviewed source energy method (no class
initialization or quantum optimizer) and compare every assignment for all ±1 complete
graphs through four vertices. Independent mask optima match the authored solver;
full-report tests expose substituting an unsigned cut. This is source-to-objective
correspondence, not a verified quantum mapping or demonstrated usefulness.

Evaluation caution: upstream class prose describes Hellinger fidelity, while this
pinned `score()` actually uses an expectation-based expression dividing by the ideal
expectation. Zero/signed denominators require care. Our method fixtures report absolute
expectation gap and distribution distances separately, without importing a pass threshold.
This shares cut/Ising structure with lit-001, not a new independent algorithm family.
