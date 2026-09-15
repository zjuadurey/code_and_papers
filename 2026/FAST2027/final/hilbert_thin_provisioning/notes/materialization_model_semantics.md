# Materialization model — preregistered semantics and accounting

Parent study commit: `765b480e46642b5a84e61bb3db1e284f0f4f8cd6`. Existing results are immutable; their full hash inventory is under `results/materialization_model/`. No benchmark discovery or external source edits.

## Product invariant and ordering

K0/K1/P are single-qubit factors, M participates in one dense backing vector. M is absorbing except SWAP, which exchanges logical-to-physical mappings. No attempt to factor the backing vector is made. Local gates update two scalars, including P→K canonicalization. Symbolic local unitaries retain P with an unevaluated vector. Basis shadow labels replay the existing conservative analyzer; the old q_logical is an upper bound, not an entanglement measure. The dimension inequality applies to lazy policies; EAGER_FULL deliberately allocates n even when q_logical=0.

Known controlled-gate shortcuts respect open controls and single-target arity. For gates of ≤3 qubits, a stronger local proof constructs U applied to virtual product factors and every basis input of the involved M wires. A virtual output wire may stay virtual only if matricizing this isometry against that wire has rank one. Linearity then guarantees independence even when the M wires are entangled with unaddressed backing wires. This is a bounded 8-by-8 local calculation, never a workload-sized statevector. Numerical proof residuals accumulate under a 1e-12 vector-error budget, stricter than the 1e-10 validation tolerance. Unproved operands become M, except old basis-shadow proofs safely preserve known basis wires. Large composite/unknown gates conservatively materialize unproved operands; names alone do not establish semantics.

## Append-only dimension placement

Physicalization appends k address bits to the compact backing. This preserves old amplitude indices. SWAP only changes the mapping. An implicit-zero insertion installs 2^k branch descriptors, conceptually represented by one active branch plus a default ZERO rule (no exponential descriptor allocation). K1 selects the corresponding active branch. Insertion itself reads/writes zero amplitude bytes. Actual mixing/entangling output is a separate obligation.

## Four policy definitions

- EAGER_FULL: n dimensions at all times; no resize events.
- BASIS_REWRITE: follow the prior K/Q labels. For each positive Δq, explicit resize reads B_old and writes B_new. The following gate separately reads/writes its expanded operand state, represented by the traversal oracle in the composed model.
- BASIS_THIN: install the known branch and implicit ZERO branches without copying. When that same gate consumes the new dimension, conservatively produce a dense B_new output from one B_old input pass. No coefficient aliasing, unstructured amplitude sparsity, or free sub-chunk ZERO sparsity is assumed. Consequently post-gate capacity and the conservative event-byte envelope can match BASIS_REWRITE. The zero insertion itself is still copy-free. This is an intentionally honest test of whether ZERO alone solves first-H output traffic.
- PRODUCT_FUSED: keep arbitrary factorized single-qubit states in metadata until the first unproved entangling interaction. Directly write the post-gate B_new from B_old and local vectors: read B_old + write B_new, with no intermediate expanded array. Both one-qubit and multi-qubit batches are allowed. Two-scalar metadata bytes are reported separately from backing bytes.

The optional coefficient-ALIAS/COW representation of a single product qubit is algebraically identical to P metadata until a branch-dependent operation; it is not a separate implementation or policy here.

## Traversal composition and avoiding overclaims

Use unchanged QDAO greedy partition, fixed t=2, m=16 primary; 18/20/22/24 are sensitivity, never tuning. For n≤m, a single whole-circuit traversal pair is an explicit in-memory extension of the oracle (not a legal QDAO OOC run). Oversized single gates are excluded with an error, never fabricated as valid partitions. Primary aggregate uses common-valid m=16 circuits, and coverage is reported against all 90 eligible circuits.

Primary conservative additive checkpoint accounting is T = partition endpoint reads/writes + all materialization event reads/writes. For REWRITE, the event is an expansion pass; for THIN and FUSED it is the output-generation checkpoint. For these last two, part of that checkpoint may overlap the normal partition traversal. Thus this primary model can overcharge them; it does **not** credit fusion twice. A second boundary-overlap convention credits an event's compact read only at the first gate of a partition and its expanded write only at the last gate. Credits are direction-specific and each traversal endpoint is used at most once. A maximally resident convention absorbs all THIN/FUSED event passes into traversal, serving only as an optimistic bound. Results expose every component and convention.

Standalone numerical kernels separately establish the real expand-then-gate cost B_old+3B_new versus fused B_old+B_new. Those saved gate passes are not blindly added to the QDAO benefit. Report gross materialization traffic, boundary credits, total predicted bytes, and standalone fusion savings separately.

Peak backing is post-gate persistent amplitude storage, not allocator RSS or peak simultaneous input+output buffers. Working-buffer peaks and P metadata have separate fields. Gate volume samples post-gate sizes. No zero-fill filesystem charge is added. Chunk sensitivity rounds each modeled input/output buffer up to a chunk and charges dense output chunks; it does not assume fragmented ZERO holes cost nothing. Pre-consumption ZERO extents remain metadata only.

All primary conclusions are lowered, external, 20–40 qubits. All 251 external circuits have both views as secondary evidence. Previously generated/synthetic controls stay separate. Censored never-physicalized qubits retain missing physical timestamps, with a separately reported observed lower bound on their virtual lifetime.

Interpretation: PROMISING requires median EAGER/FUSED≥3 and at least two identified families with ≥3 common-valid primary circuits and median≥5, plus a materialization reduction or observed physicalization delay, and zero false_virtual. NEEDS_REFINEMENT admits concentrated benefits or strong THIN with small incremental PRODUCT gain. WEAK requires both mechanisms close to eager and negligible lifetime gains. Thresholds are descriptive phase gates, not performance claims.

**trace-driven static model — NOT measured SSD traffic.** No actual SSD layout, file I/O experiment, or QDAO runtime integration.
