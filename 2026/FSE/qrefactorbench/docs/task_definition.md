# Task definition

Operational vocabulary for the existing v0.1/Phase-1 infrastructure. Stable research
intent and the conceptual T1–T6 versus historical T1–T3 crosswalk are in
[RESEARCH_CHARTER.md](RESEARCH_CHARTER.md). That explanatory decomposition does not
change these fields, frozen prompts or the current evaluation protocol.

Prospective update: [D-016](../DECISIONS.md#d-016-reviewed-uncertainty-broad-candidates-and-staged-evidence)
allows WHERE candidates that WHETHER later excludes, reviewed uncertainty and
staged coordinator/independent review. The operational v0.1 descriptions below
remain historical implementation semantics until versioned changes are made.
D-017 now resolves structural eligibility's conceptual boundary; case evidence and
versioned implementation remain pending. Do not reinterpret historical scores.

QRefactorBench studies selective quantumization of existing classical software:
localize candidate computation, decide whether to migrate under stated assumptions,
choose an admissible formulation, refactor into a hybrid program, and validate.
The unit is a case containing a classical program and human annotations, not a
request to translate every Python statement into quantum gates.

The initial scope is Python 3 and Qiskit, with unstructured_search and
combinatorial_optimization migration families. A family names an evaluation
domain, not a uniquely correct algorithm. No complete scientific contract library
is claimed in v0.1.

| Capability | Structured evidence | Current infrastructure |
| --- | --- | --- |
| WHERE | case-relative source regions | exact metrics and descriptive line overlap |
| WHETHER | decision and three independent labels | confusion counts and abstention metrics |
| HOW | intent ID, family, selected contract and structured plan | set membership plus trusted verifier interface |
| REFACTOR | generated files or patch | syntax check and explicit trusted execution/import/interface helpers |
| VALIDATE | semantic oracle, quantum constraints, resource assumptions | extensible hooks, resource extraction, strict component aggregation |

`NO_QUANTUMIZATION` is the task-level name for a legitimate abstention. Its wire
representation is `decision: REMAIN_CLASSICAL`. Candidate regions may be empty,
or present when a recognized computation is unsuitable under the stated policy.

The glossary used by schemas and docs:

- **Original software contract (原程序的行为约定):** the declared input domain,
  output meaning/representation, interface, exception and side-effect behavior,
  including required ordering and exactness/quality guarantees. Preserve it by
  default under [D-015](../DECISIONS.md#d-015-preserve-the-original-software-contract-by-default).
  Approximation/probabilistic guarantees need original-contract permission;
  unresolved obligations are not completed migrations. This term is not a new
  serialized field or a change to the existing evaluator.
- `structural_eligibility`: an established concrete correspondence between the
  computational core and a supported formulation, with domain/predicate or variables,
  objective and constraints, mapping conditions and evidence (D-017). Missing essential
  correspondence means uncertainty. This is distinct from complete preservation of
  the original software contract and from practical suitability; no new wire field
  or implemented scoring change follows from this clarified definition.
- `practical_suitability`: reasonableness of migration under the case's explicit
  size, data, oracle, resource, effects and execution assumptions.
- `benchmark_supported`: whether this release has a defined migration contract
  and evaluation protocol for the case. It does not establish physical advantage.
- `admissible_migration_contract`: conditions, representation, formulation, allowed
  algorithm families, decoding, semantic relation, resource assumptions and limits.
- `semantic_oracle`: a case-specific check of the declared software semantics.
- `reference_plan`: optional example in the admissible set, not the sole valid plan.
- `null`: an unresolved annotation or unmeasured result, never a false label.

Labels are case-level in v0.1. Multiple regions describe the annotated migration
target collectively; per-region suitability and dependency annotations are a future
design question. A program can have no migration target and still be a valid case.

The intended workflow is task definition → infrastructure → pilot human annotation
→ pilot benchmark → direct model baseline → failure taxonomy → technique design
→ full evaluation. This repository implements infrastructure, not a migration agent.
