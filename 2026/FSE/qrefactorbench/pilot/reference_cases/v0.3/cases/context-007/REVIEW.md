# Context-007: archive staging within capacity

**DRAFT / AI-ASSISTED PROPOSAL — NOT GROUND TRUTH.**

Functional need: given indivisible archive items and their caller-supplied priorities,
assess the current staging set, select a highest-priority feasible set and issue a
transfer manifest. No actual I/O occurs. The current set may exceed capacity and
must still be reported rather than rejected. See [request](example_request.json),
[report](example_report.json), [program](program.py) and [contract](public_task.json).

Example: current image+index uses 8 units against capacity 5. Proposed notes+index
uses 5 and attains priority 9. The report removes image, adds notes and assigns
contiguous offsets 0 and 3. Current assessment, hard capacity, priority, deltas and
offsets have distinct effects; checking only a scalar objective misses bad transfers.

This is a new Codex-assisted synthetic kernel/context, **not** a quoted paper case.
The two function bodies are identical. Priority is additive abstract importance,
not accuracy or a probability. No implicit relaxation of hard capacity is allowed.
The new exact contract chooses lexicographically smallest input-index tuples on
ties. This can add a zero-priority early item when the tuple precedes a shorter
later one; all-zero optima still choose empty. It is not minimum storage or minimum
change. This explicit engineering tie choice needs functional review before release.

Independent [tests](test_program.py) enumerate subsets as combinations, cover 85
bounded item lists with their bounded capacities and every current set, and detect
infeasible/suboptimal answers, wrong ties and corrupt manifests. Very large integer
priorities are checked without floating-point ranking. These checks do not establish
quantum solver correctness or user utility.

Conditional research direction: recover binary choices, maximize summed priorities
subject to the hard capacity inequality. For the supported optimization family,
slack representation, penalty bounds, feasible decoding and coefficient ranges need
an explicit derivation; this package supplies **no certified QUBO contract**. An
unreviewed penalty must not silently soften capacity. Exact optimality and tuple
tie preservation remain separate obligations. Classical dynamic programming and
specialized methods are important comparisons, not just this exhaustive baseline.

Researcher decisions: are additive priorities and indivisibility appropriate?
Keep the exact tie rule or version a different one before model exposure? Any
approximate profile would need separate permission/criteria; context-001's permission
does not apply here. No size distribution, hardware or practical evidence is given.
