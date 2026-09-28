# lit-008 — Qiskit HumanEval 53 → deterministic masking receipts

**PRIVATE · DRAFT / AI-ASSISTED PROPOSAL — NOT GROUND TRUTH.**

[Source dataset](../../../v0.1/sources/qhe.json), `qiskitHumanEval/53`, specifies XOR of two
eight-bit integers and checks deterministic 1024-count bitstrings for `(10,20)`,
`(61,9)`, `(47,8)`. Apache-2.0 notices retained. We authored a classical implementation
of that operation and a validated batch receipt API. No Qiskit simulator, runtime
service or upstream circuit code is used by the classical program.

New context preserves every row's eight-bit string, bit count, optional exact histogram,
ordered prefix checksum and complete report. The input repetitions is explicit and
does not request quantum sampling; output can be produced classically. This is a
source-task adaptation, not an imported existing classical application.

This is a **provisional retention/scope control**, with structural/practical/support
labels still null. The existence of an upstream quantum implementation does not
establish that search or combinatorial optimization is the right reformulation.
Do not add Bernstein–Vazirani/Deutsch–Jozsa/reversible-computation positive families
to make the source fit. WHERE may nominate `encode` or the batch loop, then WHETHER
may reject with evidence; a nomination is not automatically an error.

[Tests](test_program.py) check all 65,536 byte pairs against individual bit truth
tables, all three original task examples, report order, empty data, validation and
the observable effect of wrong endian conversion. This tests exact functional
behavior, not quantum semantic equivalence or a model failure. API test organization
is a concrete HumanEval-style adoption, not just a literature mention.
