# Transfer semantics (written before implementation)

Initial state is K0 on every logical qubit. K0/K1 means a factorized computational basis state. Q is an overapproximation of quantum/unknown, not a claim of entanglement. No inverse-gate cancellation or reset-based dematerialization is performed.

| Operation | Transfer |
|---|---|
| X, Y | Toggle K0/K1; retain Q (phase irrelevant) |
| Z,S,Sdg,T,Tdg,P,RZ, CZ,CP,CRZ,RZZ and proven diagonal operations | Retain all labels. A computational-basis diagonal unitary cannot change any known bit or entangle it with the rest. |
| H,SX,SXdg | Mark operand Q |
| RX,RY | Bound finite angles within absolute 1e-10 of 0 mod 2pi retain; pi mod 2pi toggle; otherwise Q. Symbolic/nonfinite angles are Q. |
| CX | K0 control: identity; K1 control: X target; Q control: target Q |
| CCX/MCX | A mismatching known control short-circuits (including open controls); all controls known and matching: X target; otherwise conservatively mark all operands Q. |
| SWAP | Exchange labels exactly; no new dimension |
| Unknown primitive | All operands Q; log name/count/workload |

Only trusted Qiskit standard gate **types**, not arbitrary user-defined names, receive named rules. Small (<=3-qubit) bound gates may additionally be proven diagonal or monomial by their unitary matrix. For a monomial unitary acting on all-known inputs, the output basis bits are computed directly. This admits U(pi,...) basis permutations without classifying general U gates as known. The numerical zero tolerance for matrix structure is 1e-14. Symbolic gates never use this proof.

Custom composite definitions are recursively expanded only where no proven rule exists, preserving recognized high-level reversible gates. No matrix is constructed for >3 qubits. Definitions with classical control, mid-circuit measurement, reset, or unsupported nonunitary behavior are excluded from primary results. Terminal measurements/barriers are removed as a readout suffix; barriers elsewhere affect layer scheduling but do not count as gates. State preparation/initialize are conservatively Q on involved operands (and never statevector simulated at workload scale).

## Absorption and SWAP

Q is absorbing under non-permutation transfer rules. SWAP moves a Q label to a different logical wire; that wire's historical first-Q timestamp remains recorded. Total q(t) is nondecreasing. A wire may receive K after SWAP without removal of any quantum dimension. Therefore `never_quantum_count` is historical and can differ from n-q_final. `q_peak` determines peak volume.

## Time and layer definitions

Gate traces include an initial gate_index=0 row; metrics sum only post-gate rows 1..G. Semantic time counts gates after transparent expansion of unsupported composite wrappers; raw input instruction count is separately recorded. ASAP dependency depth ignores terminal readout and uses barriers as synchronization fences. Layer opportunity is computed by replaying gates in ASAP layer order and sampling at each layer end, not by taking a serial prefix maximum. The latter incorrectly pulls independent future gates into earlier layers.

Floating tolerance is an explicit numerical approximation: exact validation requires each claimed K single-qubit reduced density matrix to be within 1e-10 of its basis projector at **every prefix**. The state also carries an accumulated operator-norm approximation budget of 5e-11. Near-special rotations charge residual/2 plus a floating angle-reduction allowance; small-matrix proofs charge distance to the nearest diagonal/monomial unitary. Unitary errors add, and marginal density-entry error is bounded by twice the state-vector error. Once a proof would exhaust the budget, its operands are conservatively Q. This prevents individually near-special gates from silently accumulating a false-known state. Regressions cover repeated RX(9e-11), 6,000 nearly diagonal unitary gates, and unreliable reduction of huge numeric angles. Plain list inputs without budget metadata receive only zero-error numerical proofs.

Generic ControlledGate rules require exactly one target as well as a single-qubit base gate. MCMTGate can report XGate as its base even with several targets; it must be expanded or conservatively marked Q, never passed through the single-target CX/MCX rule.
