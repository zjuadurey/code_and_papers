# Benchmark design

## Artifacts and scope

Each case directory contains case.json (or case.yaml/case.yml), program artifacts,
classical tests, and eventually independent annotations and review evidence. Paths
are relative to that directory, portable, and cannot escape via `..` or symlinks.
The loader discovers only case manifests, not arbitrary JSON test data. Multi-file
cases use `files`; single-file cases use `classical_program`, exclusively.

Contexts progress from a kernel to a function with distractors to a small program.
This changes software-context demands without pretending to represent large
repositories. Four original DRAFT toys cover those formats. Ten additional DRAFT
synthetic programs under cases/pilot/ are Phase-1 annotation material, not validated data.
Positive, hard-negative, and negative templates live outside cases/ and are never
included in normal dataset summaries.

JSON Schema draft 2020-12 documents live in schemas/, are packaged with the wheel,
and are resolved from a local registry. Unknown top-level fields are rejected.
Case, legacy prediction and plan formats carry schema_version=0.1.0; the separate
Phase-1 prediction profile uses 0.2.0 and references those unchanged schemas. Applicability is
enforced by the schema plus `validator.py` checks of artifacts and cross-fields.
External schema validation alone cannot verify source files or review evidence.
Nullable draft fields and strict maturity validation permit partial human work.

## Multiple migrations

A case holds zero or more admissible_migration_contracts. Each contract has a
stable contract_id, status, applicability conditions, encoding, formulation,
algorithm_families, decoding, semantic relation, resource assumptions, and known
limitations. A reference plan selects one contract. Additional alternatives are
equally representable. Matching the ID does not demonstrate conformity.

In v0.1 contract descriptions are human-authored text and algorithm families are
extensible strings; no arbitrary exact-text grading occurs. Human-supplied trusted
verifiers can interpret the structured plan under the selected contract. Contract
versions are tied to case versions/content hashes until Q5 establishes library
versioning. Draft examples carry only DRAFT contracts.

## Reproducibility

Keep case IDs stable. Increment case versions for changed programs or annotations;
never edit published frozen artifacts in place. Schema evolution requires an
explicit decision and compatibility/migration tests. Package version, schema
version, case version and future benchmark release ID are distinct.

Evaluation emits sorted JSON with no volatile timestamp: prediction hash, case
manifest/artifact hashes, schema hashes, implementation hashes, Python and observed
dependency versions. Artifacts include classical tests and review records. These
fingerprints identify inputs; they are not an immutable release service or a
complete OS/hardware reproduction guarantee. Future executable experiments must
also record backend, transpilation settings, seeds, shots, outcome evidence and
oracle code hashes. Automatic freeze and release integrity verification are TODOs.

pyproject.toml pins direct dependencies; optional extras isolate Qiskit and YAML.
The validation record documents actual existing environments. A full transitive
lock and clean installation matrix remain release tasks. No dependency was
installed during initialization.

## Data policy

There is no final train/validation/test split, no published benchmark release and
no annotator agreement statistic. Decide provenance/near-duplicate grouping,
leakage and licensing before any split. The LICENSE file explicitly records that
licensing is pending; it is not a grant. Case source licenses must be established
independently of the infrastructure license. No speedup or practicality claim is
supported by the teaching examples.

The implementation uses the documented offline JSON Schema registry interface:
[jsonschema referencing documentation](https://python-jsonschema.readthedocs.io/en/v4.18.6/referencing/).
