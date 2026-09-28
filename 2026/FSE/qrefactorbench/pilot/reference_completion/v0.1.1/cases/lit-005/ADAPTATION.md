# lit-005 — QuanBench / QuanBench+ task 03 → feature requirements

**PRIVATE · DRAFT / AI-ASSISTED PROPOSAL — NOT GROUND TRUTH.**

Source records: [QuanBench44](../../../v0.1/sources/quanbench.jsonl) task `03` and
[QuanBench+ Qiskit](../../../v0.1/sources/quanplus_qiskit.jsonl) task `03`, pinned in
[manifest](../../../v0.1/sources/manifest.json). These share the same six-clause formula;
they are one source problem, not two independent cases. MIT notices retained.

The upstream task requests a measured Grover circuit. **It does not provide this
classical application.** We authored classical predicate enumeration, named rule
validation, locked choices, current inspection/retention and change reporting.
The example preserves all six signed clauses. Our lexicographic first witness,
named interface, arbitrary valid clause inputs, locks and reporting are new DRAFT
requirements, not claims about the source authors' application. Original files remain
read-only; no upstream quantum solution or distribution threshold is taken as gold.

WHERE review: the `kernel.complete` loop needs `conforms`, the named-to-index clause
compilation and lock map. `program.review` must validate all rules first; inspect or
valid-current paths must not enumerate. Retaining a valid current can yield a different
witness than recomputing the first assignment. Nominating only the predicate is
incomplete unless the search domain/state is supplied; wider spans may be defensible
with explicit classical boundaries. No unique boundary is adjudicated.

Executable evidence: [test_program](test_program.py) enumerates the source formula's
eight assignments: feature-order witnesses are 010 and 011, corresponding to Qiskit
q2q1q0 strings 010 and 110. All 64 source-clause subsets × 27 lock patterns are checked
against an independent enumeration. API tests cover validation, no-solution, current
retention, dropped locks and changed status. This tests the new classical contract,
not Grover's reliability, quantum absence certification or practical benefit.

Conditional HOW is a review hypothesis under the existing predicate-search family;
first-witness behavior, negative-result certification, oracle construction and cost
remain open. Practical and structural fields remain null/DRAFT. This shares SAT
structure with older pilots and must not be counted as an unrelated problem family.
