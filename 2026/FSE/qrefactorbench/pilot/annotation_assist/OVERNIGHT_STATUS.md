# Overnight handoff — 2026-09-19

**AI-ASSISTED PROPOSAL — NOT GROUND TRUTH.** Phase 1 remains task-validation
preparation. No independent annotation, adjudication or frozen release occurred.
Start with [TOMORROW_REVIEW.md](TOMORROW_REVIEW.md), which contains the ten-row
review table and the nine proposed human decisions.

## Completed and limits

- Ten source-grounded proposals, pilot-001 through pilot-010, with candidate
  boundaries, separate structural/practical judgments, intent, conditional approach,
  applicability evidence, missing information, alternatives and separate confidence.
- Cross-case review order, information-sufficiency matrix, repository-only provenance
  audit, reproducible mechanical workflow check and saved validation logs.
- Updated project-state/backlog/research/validation handoff documentation.
- Proposal evidence was restricted to annotator_a's blinded source, public task and
  common menu. Proposals were hashed before workflow/provenance inspection; none
  was revised from reference annotations. However, prior preparation context and
  mandatory startup summaries were available. **These cannot be counted as truly
  independent blind annotations.** No formal model baseline or model/API call occurred.

The analyzed cases are 001 clause satisfaction, 002 ordered digest/audit,
003 weighted cut, 004 bounded lookup, 005 contextual bundle feasibility,
006 binary quadratic minimum, 007 subset-sum existence, 008 full normalization,
009 contextual placement cost and 010 fresh JSON lookup. All original scientific
annotations remain DRAFT; proposals do not overwrite them.

## Findings for tomorrow

- **Apparently straightforward:** 002/008 support scoped rejection under the two
  supported families; the candidate-versus-rejected-hotspot convention still needs review.
- **Careful review:** 001/003/005/006/007/009 admit source-derived conditional mappings;
  exact outputs, boundaries, alternative families and wrapper obligations matter.
- **Insufficient suitability evidence:** all eight structurally proposed cases,
  especially 004/010, lack an approved practical decision rubric/cost regime. Their
  execution facts do not alone prove a categorical profitability result.
- **Concrete specification conflict:** 009's public task describes name as integer,
  while support.py requires str. A researcher must choose the intended domain.
- **Possible benchmark-definition problems:** public descriptions may reveal WHERE/
  intent; one family label may reject a valid alternate plan (005/007); binary final
  decisions and non-null candidate arrays do not fully distinguish ignorance from
  rejection; exact classical interfaces lack reviewed probabilistic contracts.
- **Licensing:** repository metadata identifies synthetic/Codex-assisted origin;
  source_url remains null and license remains NOASSERTION. No rights were inferred.

The [nine decisions](TOMORROW_REVIEW.md#scientific-decisions-requiring-human-review)
cover input-domain consistency, candidate meaning, structural evidence, exact
semantics, suitability, alternative families, observable behavior, public cues and
uncertainty/independence. No accepted or provisional scientific decision was changed.

## Workflow readiness

The blind input → structured JSON → collector/schema → evaluator path **passes
mechanical checks**. Fresh packets reproduce byte for byte, A/B forms are blank,
all ten IDs survive collection/evaluation, null labels and abstention are supported,
malformed responses are rejected and DRAFT evaluation requires an explicit flag.
See [WORKFLOW_AUDIT.md](WORKFLOW_AUDIT.md) for commands, actual checks and caveats.

No populated case-specific reference fields were found in prompts. This does not
resolve public-prose cueing or the 009 inconsistency. Evaluation results against
DRAFT labels are demonstrations, not approved research scores. Temporary dummy
fixtures tested plumbing only; neither dummy predictions nor scores were retained.

## Exact validation executed

All commands ran from the repository root with existing environments; no packages
were installed. Raw logs are linked below. All successful commands exited 0.

| Command | Actual result | Evidence |
| --- | --- | --- |
| /home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q | 84 passed, 3 skipped in 3.22s; missing Qiskit/PyYAML in that environment | [core](validation/pytest-core.txt) |
| /home/audrey/miniconda3/envs/htp-static/bin/python -m pytest -q tests/test_optional.py | 5 passed in 1.26s, covering optional features | [optional](validation/pytest-optional.txt) |
| /home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench validate cases/ | VALID: 14; 14 expected DRAFT warnings | [validation](validation/dataset-validation.txt) |
| /home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench summarize cases/ --json | valid=true; 14 DRAFT, 8 positive, 5 hard_negative, 1 negative (existing draft metadata, not new proposal counts) | [summary](validation/dataset-summary.json) |
| /home/audrey/miniconda3/envs/palqo/bin/python pilot/annotation_assist/verify_workflow.py | All checks PASS; fresh exports, ten-ID dummy flow, null/abstention, default DRAFT exclusion, malformed-input rejection, blank-form comparison | [workflow](validation/workflow.json) |
| PYTHONPATH=. /home/audrey/miniconda3/envs/qrefactor-v1-py312/bin/python tests/test_packaging_integration.py | integration=passed; 14 cases, 4 schemas, actual Qiskit circuit and YAML roundtrip | [integration](validation/runtime-integration.json) |

The audit deliberately expects exit 2 for evaluation without --allow-draft and for
malformed collection; both were observed. These are successful rejection checks,
not hidden failures. No wheel rebuild was necessary; production code is unchanged.

[Protected-file verification](validation/protected-files-check.json) found all
225 snapshotted pre-existing data/code/configuration files unchanged. The
[before manifest](validation/protected-files-before.json) persists their hashes.
[Evidence manifest](evidence_manifest.json) identifies blinded analysis inputs
and the ten proposal hashes established before the reference-dependent workflow
audit. Hashes support artifact identity, not cognitive independence or scientific validity.

A final [package check](validation/package-check.json) confirmed all ten proposal
markers/required sections, unchanged blinded input/proposal hashes, unchanged
protected files and no broken local links across 19 checked Markdown files.

## Exact next human actions

1. The coordinator reviews the table and 009 contradiction before distributing any
   new snapshot. Record choices or uncertainty for the nine decisions; preserve originals.
2. Decide which public facts/cues are intended and what evidence can justify
   suitability. If specifications change, prepare a separate versioned packet after review.
3. Give fresh A/B researchers only their approved role packet, excluding this assist
   directory and all private labels; collect independent records before sharing proposals.
4. Compare completed records and have a human adjudicate disagreements; do not
   promote labels just because a program/test/schema passes.
5. Once the protocol is interpretable, obtain direct-LLM responses externally using
   the existing prompt/run metadata; collect/evaluate with the documented CLI and
   open-code failures using the existing observation template. Retain unresolved evidence.

Deliberately unchanged: source programs, reference/draft annotations, public inputs,
distributed packets, schemas, evaluator semantics, contract library, scientific
decisions, licenses and release splits. No new families, agent architecture, QPU
jobs, dependency installations, quantum-advantage claim or formal baseline were added.
