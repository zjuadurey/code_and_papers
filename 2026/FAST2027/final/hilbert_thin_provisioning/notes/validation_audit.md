# Correctness audit history

The development validation intentionally stops on any false-known claim. An early run found an actual false-known error in a generated 6-qubit modular-adder input: at gate 5, `mcmt` left a target labeled K0 while its exact marginal was diag(0.5,0.5).

Cause: Qiskit's MCMTGate is a ControlledGate and reports base_gate=XGate even with multiple target qubits. The generic controlled-X rule had assumed a single target from base_gate alone.

Fix: the specialized controlled rule now requires both `op.num_qubits == op.num_ctrl_qubits + 1` and `op.base_gate.num_qubits == 1`. Other composite gates are transparently expanded or receive conservative unknown semantics. The `test_multitarget_is_not_single_target_x` regression checks direct, semantic-expanded, and lowered versions by exact prefix validation. Characterization and validation were rerun after the correction.

Only the run identified by `results/manifests/latest_run.json`, with a matching PASS `results/verification.json`, is evidence. Earlier timestamped raw directories are development history, not validated result sets. Final zero false-known violations refers to the final run, not to an assertion that development never exposed bugs.

Additional integration issues fixed before final delivery: unknown QiskitError fallback; duplicate metadata keys in batch output; RAM-derived Aer compiler width limit; QPY serialization of arithmetic OrGate wrappers. QPY control masks above uint32 remain a documented limit for the optional generated Grover series, which stops at 32 qubits.
