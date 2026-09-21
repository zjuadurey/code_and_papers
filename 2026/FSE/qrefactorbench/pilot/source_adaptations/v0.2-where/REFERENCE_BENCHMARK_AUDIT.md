# Reference benchmarks: inspect artifacts, then decide what is transferable

2026-09-21. This audit separates importing a classical source program, adapting a
quantum problem specification into a newly written classical program, and borrowing
an evaluation method. They are not interchangeable provenance claims. No upstream
model results were used to select answers or label our cases.

| Reference | Concrete material examined | Appropriate use / decision |
|---|---|---|
| **C2\|Q>** | [Pinned CSV/card](https://huggingface.co/datasets/boshuai1/c2q-dataset/tree/c5b457cf425c31e91bae829503ece6e92646dd0a), ten source records listed in [SOURCES](SOURCES.md) | Supplies actual classical Python. Four reviewed functions imported into two workflows. Upstream family labels are not ground truth for eligibility, practical suitability or exact behavior. |
| **QuanBench** | [ASE 2025 paper](https://arxiv.org/abs/2510.16779), [44-task file at e6cbd58](https://github.com/GuoXiaoYu1125/Quanbench/blob/e6cbd58628366c7538cc5a27e9dbf9ebdfc38e1f/QuanBench44.jsonl); fields `task_id`, `entry_point`, canonical solution/test; selected search-related records | Task 01 explicitly asks for a measured Grover circuit with a fixed marked state; task 03 specifies a fixed 3-SAT formula and a quantum implementation. These can inform later conditional-HOW tests, but do not supply a classical application with an undisclosed candidate. No code imported here. |
| **QuanBench+** | [Authors' paper](https://arxiv.org/abs/2604.08570), which identifies the ICLR 2026 **Workshop** on I Can't Believe It's Not Better; advertised GitHub `JawadKotaich/quanbench-plus` returned 404 in this check | Executable multi-framework and probabilistic evaluation are relevant. Dataset/code licensing and exact records were not verified here, so no case/code import and no claim of ICLR main-track publication. Repair is not added to our single-shot protocol. |
| **Qiskit HumanEval** | [151-task file at c98ba53](https://github.com/qiskit-community/qiskit-human-eval/blob/c98ba538239fcfd554aa89627ee8026f4b5de450/dataset/dataset_qiskit_test_human_eval.json); representative tasks 0/1 construct a circuit or run a Bell example | Reuse entry-point/function-test organization and isolated checks. Its quantum API tasks do not directly supply a new classical search/optimization application. Do not claim every task was individually reviewed. |
| **PQID-Bench** | [Project README](https://github.com/Elias-Abebe-Gasparini/PQID-Bench) describes quantum-program generation and a limited reference-structure predicate | Keep execution and structural evidence separate. Structure-signature agreement is not our full software contract. Documentation-level check only; no dataset/task import or upstream scores reproduced. Publication venue not asserted. |
| **MQT Bench** | [Grover](https://github.com/munich-quantum-toolkit/bench/blob/c05b1966274d8a8488bf777d3cc78a39ea9d7857/src/mqt/bench/benchmarks/grover.py) and [QAOA](https://github.com/munich-quantum-toolkit/bench/blob/c05b1966274d8a8488bf777d3cc78a39ea9d7857/src/mqt/bench/benchmarks/qaoa.py) circuit generators | Appropriate future circuit/resource comparators. Inspected QAOA code constructs a parameterized MaxCut circuit, not an optimized, decoded classical replacement. No new classical program is imported by copying it. |
| **SupermarQ** | [Versioned QAOA proxy API](https://superstaq.readthedocs.io/en/v0.5.37/autoapi/supermarq/benchmarks/qaoa_vanilla_proxy/index.html), [application-oriented paper](https://arxiv.org/abs/2202.11045) | Distinguish task-level quality from quantum resources. Not a source of these two application workflows; no proxy score is adopted as semantic success. |
| **LINPACK / HPL** | [Project description](https://www.netlib.org/benchmark/hpl/) | Canonical core and stable correctness checks are useful design references. Linear-system workloads would expand current positive families; no case imported. |
| **HPCG** | [Official description](https://www.hpcg-benchmark.org/) | Connected computational stages motivate context in which dependencies matter. Not authorization to copy sparse linear-algebra workloads into the current family scope; no code imported. |

Pinned raw-file checksums, lengths and inspected task IDs for QuanBench/QHE/MQT:
[checked_files.json](reference_audit/checked_files.json). These downloaded files
were read/parsed, not executed; only hashes/locations are retained for this audit.
The previously recorded dataset/code license distinctions remain in force. GitHub
metadata reported MIT for QuanBench/MQT and Apache-2.0 for QHE, but we copied none of
their code and do not infer a license for our new application material.

## Evaluation ideas actually applied now

- **HumanEval-style:** public callable contracts, standalone entry points, independent
  executable tests, invalid-input checks and source/context matching.
- **Multiple criteria rather than execution-only:** feasibility, prescribed selection,
  preview behavior, control-path status, history interpretation and complete report
  equality are tested separately through counterexamples. This is classical software
  validation, not a substitute for process fidelity or quantum validation.
- **Core/context comparison:** original functions remain in core views; context adds
  dependent stages and multiple semantically different operations. No random filler.
- **Reproducibility:** pinned source records and transformation diffs, immutable earlier
  artifacts, allowlisted inputs and raw test logs. Hashes do not validate science.

Not applied: process-fidelity scoring, KL thresholds, Pass@k, formal model runs,
feedback repair, hardware metrics or a new localization score. Thresholds from
another task are not imported as approved semantic tolerances here.

## Implication for WHERE

The inspected circuit-generation references usually state the target computation
in their prompts. They can support HOW/VALIDATE but do not, by themselves, supply
difficult WHERE discovery. Here the added challenge is selecting a behaviorally
appropriate region and recovering its dependencies in a meaningful synthetic
workflow. This is a construction hypothesis. A later reviewed experiment must test
whether localization is actually harder; file count or fewer algorithm names cannot
establish that result.
