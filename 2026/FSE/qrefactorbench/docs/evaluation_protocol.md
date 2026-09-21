# Evaluation protocol (v0.1, PROVISIONAL)

The original component rules below remain provisional. The Phase-1 extension at
the end adds a v0.2.0 prediction/result profile for T1/T2/T3 without changing the
v0.1 case/plan schemas or accepting any unresolved scientific policy.

Read D-004 through D-006 before interpreting a score. DRAFT cases are excluded by
default. `--allow-draft` enables a demonstration run explicitly tagged
demonstration_only=true; its numbers are not empirical benchmark findings.

## Input and result formats

Validate the complete dataset before evaluation. Predictions are a JSON/YAML array
of objects conforming to prediction.schema.json, exactly one per included case.
Unknown IDs, duplicate IDs, missing predictions and malformed outputs produce a
nonzero exit code, rather than changing denominators silently. Excluded draft IDs
must not appear in the submitted prediction array. For an eventual baseline,
researchers must explicitly decide how model failures become scored outputs.

Predictions use decision=QUANTUMIZE or REMAIN_CLASSICAL, candidate_regions and,
for quantumization, a nested plan conforming to migration_plan.schema.json. Plans
carry intent ID, family, formulation, input encoding, quantum_algorithm_family,
decoding, assumptions, risks and expected resources. Optional rationale is never
graded. Optional generated_files contain path/content pairs; generated_patch is
recorded but not automatically applied. Do not count unapplied patches as execution.

`qrefactorbench evaluate` is static: no generated file is written, no module is
imported, and no case/quantum code runs. It emits result_schema_version, protocol,
execution_mode, excluded IDs, component results, aggregates and a reproducibility
manifest. Missing evidence is null with a reason. The result envelope is documented
here and regression-tested; a separate JSON Schema for results is future work.

## WHERE

Exact regions are sets of `(file,start_line,end_line)`. Optional function names are
validated against source but do not change coordinate identity. True positives
are set intersection; precision=TP/predicted, recall=TP/reference,
F1=2TP/(predicted+reference). Report counts and micro aggregation. No macro score
is silently substituted. Duplicate overlapping lines are not double counted.

For diagnostics, merge each file's intervals and report line precision, recall
and intersection-over-union. Different files never overlap. No approximate-match
threshold is chosen. candidate_correct uses exact set equality in v0.1. For two
empty sets it is true, while precision, recall, F1 and IoU with zero denominators
are null. Q3 must determine the final research metric.

## WHETHER

Use explicit expected_decision; null labels are unscored and counted. Let TP mean
correct QUANTUMIZE, TN correct REMAIN_CLASSICAL, FP inappropriate QUANTUMIZE and
FN missed QUANTUMIZE. Report:

- overall accuracy=(TP+TN)/(TP+TN+FP+FN)
- QUANTUMIZE precision=TP/(TP+FP)
- QUANTUMIZE recall=TP/(TP+FN)
- REMAIN_CLASSICAL accuracy=TN/(TN+FP)
- false quantumization rate=FP/(TN+FP)

Every zero denominator yields null, never a fabricated perfect score. D-006's
definition is provisional; supportedness-based abstention and unsuitable-but-
eligible computations may eventually warrant separate strata.

## HOW

Compare structured intent IDs and migration families. Test that the selected
contract ID exists and permits the proposed algorithm family. Never compare
arbitrary formulation, encoding, decoding or rationale text for exact equality.
`contract_membership` is a diagnostic only. `admissible_plan` remains null until a
trusted PlanVerifier supplies a Check for conformity. A known structured mismatch
is false. Verifier errors remain unknown and retain an error reason.

## Execution, interfaces and quantum constraints

`check_syntax` parses supplied Python files without running them. `check_imports`
and `run_trusted_python` provide subprocess helpers with argv and timeout, and
require explicit trusted=True. They execute arbitrary Python with the caller's
permissions; they are **not a sandbox** and do not isolate network/filesystem access
or child processes. They are for reviewed local research fixtures only. A hardened
runner is necessary before evaluating arbitrary model-generated programs.

`check_interface` compares named AST signatures (argument kinds, names, annotations,
defaults and sync/async). It does not prove runtime behavior, return-type or effect
preservation. Researchers must include runtime interface evidence in their trusted
evaluation harness. Static CLI execution/import/interface fields remain null.

Quantum-specific constraints (e.g. valid encoding, oracle reversibility, ancilla
cleanup, decoding and allowed circuit structure) are case-specific evidence. The
strict aggregator reserves quantum_constraints_pass. v0.1 supplies no universal
automated proof, and circuit existence alone never sets that field true.

## Semantic oracles

`SemanticOracles` supports:

| Kind | Configuration/evidence | Scope |
| --- | --- | --- |
| deterministic_equality | explicit expected value | equality for an observed output |
| property | registered trusted hook_id | researcher-defined properties |
| optimization_feasibility | registered trusted hook_id | admissible solution constraints |
| optimization_objective | direction and explicit numeric threshold | scalar objective quality only |
| probabilistic | registered trusted hook_id and human policy | extension point; no default threshold |

An oracle call checks one observation; it does not execute the input program or
establish a whole-program theorem. A case-specific harness must cover declared
inputs and compose checks. Feasible and high-quality solutions are separate
requirements. Objective quality alone cannot establish optimizer semantics.
For more complex contracts a trusted property hook may combine checks explicitly.
No approximate tolerance, confidence level, shot budget or statistical correction
is invented. Hooks are registered callables; configuration cannot dynamically
import a module path. Errors or absent hooks produce unknown results.

## Resources

`extract_resources(circuit, shots=..., representation=...)` uses local Qiskit only.
It returns qubits, depth, operation count, Gate count, two-qubit Gate count,
measurement count, shots and top-level operation types. Directives such as barriers
contribute to operation_count but not Gate counts. Depth uses Qiskit's default
filter. Shots come from the supplied execution configuration, not inferred from
the circuit. Supply a transpiled circuit explicitly if physical-basis counts are
desired, and record target/transpilation assumptions externally.

Counts describe the supplied representation: custom/composite gates are not
silently decomposed, and nested dynamic control flow cannot be interpreted as a
fixed execution count. Dynamic circuits retain qubits and top-level operation
diagnostics while cost/depth fields are null. These choices follow the API's
distinction between circuit instructions and gates and its warning about depth
for control flow. [Qiskit QuantumCircuit API](https://quantum.cloud.ibm.com/docs/en/api/qiskit/2.3/qiskit.circuit.QuantumCircuit)

`check_resource_limits` compares measured values with explicit upper bounds.
Missing measurements/limits yield unknown; an exceeded bound yields false even
if other measurements are missing. These checks do not establish loading/oracle
cost, advantage, hardware feasibility or probabilistic semantics.

## Strict end-to-end condition

For expected QUANTUMIZE, `end_to_end_quantumization_success` is the conjunction of:

1. candidate_correct and decision_correct;
2. admissible_plan from trusted conformity evaluation;
3. syntax_valid, imports_valid, execution_success and interface_preserved;
4. semantic_oracle_pass and quantum_constraints_pass;
5. resource_limits_pass.

All true gives true; any false gives false; otherwise the result is null. Missing
keys cannot produce success. D-006 deliberately requires evidence for every gate;
cases without numeric resource constraints remain unknown under this provisional
strict policy. Researchers must revisit that rule rather than marking absent
constraints as passing. Negative/abstention cases have this field null and separate
abstention_correct. Aggregates expose passed/failed/unknown/applicable counts.

The programmatic aggregator accepts results from a trusted harness; it is not an
attestation service. Prediction schemas do not accept self-reported correctness
flags. The static CLI cannot claim end-to-end success, even for a correctly named
contract and syntactically valid code. No score blends semantics and resources.

## Phase-1 T1/T2/T3 extension (D-009, D-010)

Use cases/pilot/ for the ten-case population, separate from the four original toys.
The Phase-1 schema is phase1_prediction.schema.json (schema_version=0.2.0), reusing
v0.1 common field and plan definitions by reference. `schema_errors(..., 'prediction')`
dispatches by version; old v0.1 predictions remain accepted unchanged.
New predictions require structural_eligibility, practical_suitability,
benchmark_supported, free-text computational_intent, migration_family,
contract_applicability, assumptions, risks, rationale and plan (nullable on abstention).
Generated code is outside this Phase-1 profile. A conditional plan is allowed on
REMAIN_CLASSICAL, e.g. to distinguish formulation from practical suitability.

Results now carry result_schema_version=0.2.0, the full parsed prediction and a
recognition block. For each structured label, retain reference, predicted, correct
and reason; correctness is null if either value is unknown. Aggregates report
correct/incorrect/unresolved, known reference/prediction counts, total and
accuracy_on_resolved_pairs. That conditional accuracy is not full-population
accuracy; report coverage prominently. For a null family reference, both known
absence and unresolved applicability remain unscored until human coding clarifies
them. Legacy predictions missing new fields contribute unresolved cells.

Free-text intent is retained for human semantic coding, never compared for textual
equality or against a private intent ID. A plan's self-chosen intent slug is also
unscored in the Phase-1 profile. Contract applicability descriptions remain for
human review. Shared contract-ID/algorithm membership is a diagnostic only; no
automatic plan conformity or semantic preservation is inferred. Aggregate intent
or applicability accuracy requires separately recorded human judgments.

T1 retains both exact region metrics and descriptive merged-line overlap. Existing
candidate_correct is an exact-match diagnostic, not a final scientific acceptance
criterion. Annotators may disagree on boundaries and on rejected-hotspot versus
eligible-region semantics; record those questions instead of choosing a new cutoff.
No new end-to-end or blended Phase-1 score is introduced.

`--case-id ID` may be repeated to request an explicit subset; output records both
selected_case_ids and not_selected_case_ids. This preserves the four-toy demo and
permits clearly labeled subset diagnostics after response failures. Predictions
must exactly cover the selected, status-eligible cases. Unselected/invalid/missing
responses cannot be silently dropped and presented as the full pilot population.
No final missing-response scoring policy is implemented (Q16).

The local collector requires one raw valid JSON object per pilot case and rejects
missing, malformed, fenced, duplicate-ID or wrong-span responses without repairs.
Preserve original failures in run metadata. The schema/prompt, raw response, model
settings and packet hash together identify the run; result hashes alone do not
capture provider nondeterminism. See pilot/baseline/README.md for execution steps.
