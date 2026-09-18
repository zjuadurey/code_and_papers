# GBSA reproduction: algorithm and execution contract

This is an independent **GBSA reproduction**, not author-provided software and
not a reproduction of the paper's absolute timings. The complete paper became
available from the user's local download on 2026-09-16; the earlier source-blocked
audit remains in `results/gbsa_comparison/source_blocked_checkpoint/` and Git.

## Primary source and artifact

Chuan-Chi Wang, Chia-Heng Tu, Shih-Hao Hung, *Toward Efficient Quantum Circuit
Simulation with Memory and I/O Reduction through Gate Block Search Algorithm*,
RACS 2025, 8 pages, [DOI](https://doi.org/10.1145/3769002.3769982).
User file: `D:\Downloads\3769002.3769982.pdf`; local source copy:
`external/gbsa-paper/racs2025-user.pdf` (not redistributed in Git).
SHA256: `dd421fc76a2c7ff2ba9bfe2bc713d574762db6f8325c83c01af63d4fad195563`.

No verified official artifact/repository was found in the earlier DOI/title,
GitHub, institutional and repository searches. The full paper contains no GBSA
repository or artifact link. This does not prove no implementation exists.
Author code license is unknown; no author code is copied. The PDF carries ACM
publication rights and is not treated as an open software license.
The paper's native simulation library uses GCC 9.4 and OpenMP 4.5, an AMD
Threadripper PRO 3995WX with 256 GB RAM and 16 TB Kingston SSD storage. The
precise source language and library implementation are not specified enough to
reproduce its kernels. Our execution uses the validated common Aer backend.

## Algorithm-to-code mapping

The basis is Sections 3.1–3.3, Algorithms 1 and 2, and Figure 4, not the abstract.

| Paper | Reproduction |
|---|---|
| Algorithm 1 initial chunk `{q0,...,qC-1}` | `search_blocks`: initial low-C set |
| `createGB`, `updateGateList` | `extract_ready`: take eligible gates while preserving each wire's order |
| `updateDependency` | `dependencies`: transitive qubit support `dep` and predecessor set `REQ` |
| Algorithm 2 maximum `REQ.size()` with union fitting C | scan every gate, choose largest predecessor count; last tie wins (`<=`) |
| fragmented gate aggregation | remove executable gates, refresh dependencies, extend chunk until no progress or C bits |
| Algorithm 1 `addSwaps` | actual layout SWAP gates and logical/physical remapping |
| block-by-block cached execution | resident 2^C Aer compute unit executes block before store |

All control and target operands participate in dependencies. Only disjoint-wire
operations can pass one another; no undocumented commutation or fusion rule is
used. Every input gate executes exactly once. Integer bit sets encode REQ; this
does not claim to match the paper's stated O(G+C) auxiliary-space bound.

### Explicit pseudocode ambiguities

Algorithm 2 initializes `changed=False` then uses `while changed`, which would
never enter. Its printed lines 19–22 reset `ptr` inside the scan, contrary to the
prose describing a full scan followed by post-processing. `chunkSet` also lacks
local initialization. We implement the Section 3.3 prose: start a new empty
candidate chunk, perform a complete scan, select maximum predecessor count,
aggregate/remove gates, then repeat while space and progress remain. Dependencies
are refreshed after removal. This interpretation is tested against Figure 4:
initial gates [1,2,9], then [3,4,5,6], then [0,7,8], exactly its three GBSA blocks.
The prose's `H7` is Figure 4's CZ7. This is not bit-identical author code.

## Execution and parameters

- C=16 is fixed to the same 2^16-complex compute-unit capacity as Phase A m=16.
  The paper gives cache-capacity guidance but not a reproducible numerical C for
  every experiment. No parameter search is performed.
- Storage t=12, complex128, one thread, fusion disabled, same normalized Aer
  state-injection bridge, buffered NPY manager and final fdatasync barrier.
  Paper parameter T (thread exponent) is **not** QDAO storage t; one thread
  corresponds to paper T=0. The paper's multiple-SSD file scheme is not copied.
- The selected chunk may contain **any** C logical qubits. The QDAO low-t
  requirement does not constrain GBSA search. Selected nonresident bits are
  physically swapped into vacant low-C positions. Existing resident selected
  bits stay in place. The common QDAO partitioner batches SWAP operations into
  valid compute units; their traversals, bytes and time are counted.
- The block then executes on low-C physical bits. Mapping persists between blocks.
  No final reorder pass is required; output includes mapping, and exact validation
  reconstructs logical order outside performance timing.
- Inputs are the exact frozen Phase A QPY files. No extra lowering/optimization,
  new workload, or P/K virtualization is introduced.
- Timing includes dependency search, swaps, initialization, execution and final
  sync. Separate search time, swap time, block count and swap-pass count are saved.

## Implemented / omitted and fairness limits

Implemented: published maximum-predecessor dependency search, gate-block reuse,
unrestricted chunk selection and executable virtual-layout swaps.
Omitted: author-specific native kernels, OpenMP scaling, exact multi-SSD layout,
hardware tuning and unrelated baseline implementations. The paper's absolute
results and block counts on its different QFT/QAOA inputs are not local data.
Figure 4 is a correctness fixture, not a new performance workload.
The paper's application QAOA is fully connected with five levels; the frozen
common suite uses its existing ring QAOA at p=3 and HEA at four layers. All common
circuits are lowered to u/cx, whereas the paper's example retains CZ. We do not
substitute paper-specific inputs for GBSA or expect Table 2's block counts.

This experiment isolates the GBSA **policy on a common execution substrate**.
It is not a comparison against the author's complete optimized SSDGBSA system.
Layout swaps on QDAO's fixed NPY storage and Python dependency search may cost
substantially more than native GBSA. We expose these costs rather than calling
them inherent GBSA lower bounds. A win over this reproduction cannot establish
a win over the author's implementation.

Phase A randomized QDAO/QThin order; Phase B runs later in a separate serial
batch. All 3 samples are retained, with min/max/std/CV. Buffered states fit RAM
at 20–24q; process reads may be cached. Request counters are exact payload traffic;
guest device counters are shared and cannot be called uniquely attributable
native SSD/NAND traffic. No large-capacity claim is supported.

## Reproduction

```bash
conda activate htp-static
python scripts/setup_qdao_integration.py
pytest -q
python scripts/validate_gbsa_reproduction.py
python scripts/run_gbsa_comparison.py
python scripts/analyze_end_to_end.py
```

The runner refuses unvalidated code and verifies frozen Phase A/older result
hashes before performance. It holds the common benchmark lock. Do not rerun old
Phase A scripts merely to regenerate the combined report.
