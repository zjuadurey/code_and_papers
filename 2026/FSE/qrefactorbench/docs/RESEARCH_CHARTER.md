# QRefactorBench research charter

Stable intent; current progress belongs in [PROJECT_STATUS.md](../PROJECT_STATUS.md),
not here. Target: **FSE 2027 / a top-tier Software Engineering research paper**.
This is a research target, not a submission or contribution claim.

## 先读：原始研究意图与长期愿景

这段是根据研究者已表达意图整理的中文摘要，不是逐字聊天存档，也不替代下方科学约定。
我们最终想做的软件，要**高效帮助非量子专家，在已有经典软件中找出有意义的量子化
机会，并在有充分收益证据时选择性转化**，保留周边程序及对外软件合同。
问题是 WHERE、WHETHER、HOW；不是要求把所有经典语句翻译成量子门。

量子计算被看作异构加速器，类似 CPU 软件中的 GPU/SIMD offloading：理解程序、
识别候选、判断合法性/适用性、重构、验证语义，再分析资源与收益。允许不转化。
终极目标包括可靠验证端到端收益，但每阶段可以先解决一个可检验的软件工程问题；
不要求第一步同时解决全部难题，也不能用模拟器耗时替代量子优势证据。

**QRefactorBench 是支撑这条研究路线的 benchmark，不是最终软件本身。**
先从有出处的典型计算及有真实功能依赖的合成上下文入手，借鉴参考 benchmark 的
案例与评测方法；不是往核心外面堆无关代码。核对来源和功能合同后，用基线及受控
实验发现瓶颈，再设计技术。上下文是否增加 WHERE 难度是实验问题，不是建案例的前置条件。
长期研究可以走向更大程序、工具辅助方案与硬件验证；当前不因此启用新家族或新实验。

当前刻意限于 Python → Python/Qiskit 的 Search 和 Optimization；原始构想中的
Estimation、可逆计算、C/C++ 与大仓库迁移只是候选未来方向，不是当前已支持能力。
以下章节是稳定的概念和已接受边界；最新进度、输入路径只查 PROJECT_STATUS。

## The Software Engineering problem

QRefactorBench studies **Automatic / Selective Quantumization of Existing Classical
Software**. The problem is to discover candidate computations inside existing
software, decide whether migration is justified, describe admissible reformulations,
and eventually preserve software semantics through hybrid refactoring. Translating
individual classical statements into quantum gates does not capture this task.

The analogy is heterogeneous acceleration: classical software → profiling/candidate
discovery → legality and suitability analysis → accelerator mapping → refactoring
or offloading → correctness validation. CPU-to-GPU/SIMD/parallel migration motivates
the workflow; the target here is classical CPU software with a hybrid classical/QPU
component. The analogy does not establish quantum feasibility or performance.

The benchmark defines the task and collects interpretable evidence. A future
technique must address demonstrated limitations, not precede their investigation.
Software interfaces, dependencies, exceptions, side effects, exactness, output
representation, and reproducibility are central SE concerns.

## Scope and conceptual decomposition

Current source: classical Python. Direction: hybrid Python plus a Qiskit-style
quantum component. Supported positive families remain exactly:

- `unstructured_search`: predicate/finite-domain search with a Grover-style formulation.
- `combinatorial_optimization`: QUBO/Ising formulation, potentially QAOA-style execution.

Contexts progress from kernel to function with distractors to small program.
Abstention and multiple admissible migrations are first-class outcomes. Unsupported
computations must not be forced into one of the two families.

Prospective policy [D-016](../DECISIONS.md#d-016-reviewed-uncertainty-broad-candidates-and-staged-evidence):
WHERE may nominate regions for analysis that WHETHER later rejects; a candidate
is not yet an eligibility judgment. Review may retain uncertainty, and practical
assessment remains evidence-based under explicit assumptions, without a composite
profitability score or simulator-based speedup claim. Coordinator review comes
before independent/domain-expert validation for important formal-evaluation cases.
These decisions do not change frozen pilot annotations or implemented formats.
The researcher subsequently resolved the conceptual Q2 boundary in
[D-017](../DECISIONS.md#d-017-structural-mapping-is-distinct-from-contract-preservation):
structural YES requires an established concrete mapping of the computational core
to a supported formulation, not an already complete contract-preserving migration.
Record domain/predicate or variables/objective/constraints, their correspondence,
conditions and evidence. If essential mapping evidence is missing, use UNCERTAIN;
a family name or unsupported assumptions do not establish YES. Full original-contract
preservation and practical suitability require separate evidence. Case labels and
operational scoring remain subject to review; no old annotation is changed here.

| Conceptual stage | Question | Evidence, not an automatic correctness claim |
|---|---|---|
| T1 — WHERE | Where is a potential candidate, if any? | Source region(s), dependencies, or no candidate |
| T2 — WHETHER | Is it structurally eligible and practically suitable? | Separate labels, assumptions, abstention/recommendation |
| T3 — WHAT / HOW | What intent and migration family fit? | Intent, formulation family and contract applicability |
| T4 — PLAN | What would a conditional reformulation entail? | Encoding, quantum procedure, decoding, obligations and uncertainty |
| T5 — REFACTOR | How is the surrounding program preserved? | Hybrid transformation with interface/behavior preservation |
| T6 — VALIDATE | Does the migration satisfy its contracts? | Semantic, quantum-specific and resource evidence |

**Historical numbering crosswalk:** frozen Phase-1 materials use T1 WHERE,
T2 WHETHER + WHAT (including intent/family), and T3 HOW (structured planning).
Thus historical T2 spans conceptual T2/T3 above, and historical T3 corresponds
to conceptual T4. This table separates research questions; it does **not** rename
serialized fields, alter formal scoring, rewrite frozen prompts or adopt a new
benchmark protocol. Cite the protocol/version when using task numbers. The current
implementation contract remains in [task_definition.md](task_definition.md) and
[evaluation_protocol.md](evaluation_protocol.md).

## Distinctions that must survive every implementation

`quantumizable != worth_quantumizing`

`computational_hotspot != quantumization_opportunity`

`executable_quantum_code != semantically_correct_migration`

| Concept | Meaning | What it does not establish |
|---|---|---|
| Structural eligibility | A meaningful formulation within supported families under stated conditions | Practical adoption or advantage |
| Conditional HOW | How a formulation could work under explicit assumptions | A deployment recommendation or correct implementation |
| Practical suitability | Whether adoption is reasonable under stated scale/cost/hardware assumptions | Measured quantum advantage |
| Final recommendation | QUANTUMIZE or REMAIN_CLASSICAL | Whether the model can describe a conditional plan |
| Benchmark support | A defined applicable migration contract/evaluation protocol in this release | Hardware performance or measured benefit |
| Actual quantum advantage | A separately evidenced comparison under defensible assumptions | A consequence of naming Grover or QAOA |

Structural YES + practical NO/UNCERTAIN + REMAIN_CLASSICAL + a conditional plan
is conceptually coherent and representable in the existing prediction schema.
The completed diagnostic examined elicitation of that combination. Subsequently,
the researcher accepted [D-014](../DECISIONS.md#d-014-conditional-planning-independent-of-adoption):
future protocols require a conditional plan when the response reports structural
YES, independently of practical adoption. Frozen pilot-v0.1 artifacts remain intact.
A detailed plan is not necessarily correct; planning coverage and verified quality
must be distinguished, including eligible cases the model fails to recognize.

Practical evidence may require problem size/search-space cardinality, encoding and
reversible oracle costs, qubits/depth, state preparation, shots, classical/QPU
communication and hardware assumptions. Missing evidence stays UNKNOWN/UNCERTAIN
(`null` where the schema permits it). Do not treat absent evidence as a proof of
failure or invent favorable costs. Exact classical outputs cannot silently become
approximate quantum outputs. An approved semantic relation is required.

## Original software contract

**Default: preserve the original software contract (原程序的行为约定).**
[D-015](../DECISIONS.md#d-015-preserve-the-original-software-contract-by-default)
records the researcher's approval. The contract specifies permitted inputs,
observable outputs and their meaning, interfaces, exceptions, side effects and
required ordering. It is not merely a function signature. A quantum migration
contract instead specifies how a reformulation could satisfy those requirements.

Exact outputs must remain exact. An approximate or probabilistic guarantee is
acceptable under this default only when allowed by the original contract, with its
actual bounds retained. Internal quantum randomness is not itself forbidden;
silently weakening externally required guarantees is. Missing tolerances or
conflicting code/specification/tests require review, not invented permissions.

Examples: a failed search attempt is not a proof of no solution; a good objective
value is not a certified global optimum; skipping later input validation after an
early match can change required exceptions. Conditional plans may document these
unresolved obligations, but plan presence/content is not verified preservation.

Any future explicit relaxation must be versioned and evaluated as a changed
contract, not credited as preserving the old one. No existing case is relaxed by
this decision; quantum advantage and practical suitability remain separate questions.

Subsequent explicit case-specific permission is recorded in
[D-018](../DECISIONS.md#d-018-context-001-approximate-quality-profile): a separate
context-001 approximate-contract draft reports satisfied-weight quality and gaps.
Its acceptance threshold remains open; the original exact case and D-015 default
are unchanged. Algorithm characteristics inform contract design, not automatic relaxation.

## Evidence and annotation maturity

The coordinator is not assumed to be an expert in every quantum algorithm.
Prefer AI-assisted proposal + concrete source evidence + authoritative literature
where necessary + researcher review + independent/expert validation of important
subsets. AI proposals are **NOT GROUND TRUTH**. Keep provenance, disagreements,
uncertainty and actual reviewer identities; never invent agreement or review.

Conceptual maturity (draft → researcher-reviewed → independently/expert-validated
→ frozen release) is not a replacement schema. Existing serialized states remain
`DRAFT`, `REVIEWED`, `ADJUDICATED`, `FROZEN`, under provisional D-005 and
[annotation_guidelines.md](annotation_guidelines.md). A coordinator's informal
review alone does not satisfy REVIEWED's required records. Expert validation is
evidence, not a new enum; FROZEN is not proof of expert correctness. Do not insert
`RESEARCHER-REVIEWED` or `EXPERT-VALIDATED` into manifests. The current schema checks
records, not expertise, independence, or truth.

D-016 prospectively separates review maturity from certainty and authorizes the
staged review process above. The old schema has not yet been revised: it still
requires known labels for non-DRAFT cases and independent records for REVIEWED.
Record coordinator review separately until a compatible version is available;
never fabricate certainty or independent annotation to pass the old validator.

Uncertain/disputed cases may remain uncertain. Humans decide any later exclusion
from final evaluation; Codex must not quietly change the population or labels.

## Research progression and stopping boundary

Task Definition → Pilot Benchmark → Direct-LLM / Code-Model Baseline → Failure
Characterization → Technique Design → Agentic / Tool-Augmented Solution → Evaluation
→ FSE Paper. Current results and phase are recorded in the status file. A diagnostic
prompt condition is not an independent model baseline.

Technique possibilities must follow evidence: localization failures may motivate
program analysis; suitability failures may motivate explicit applicability/cost
reasoning; formulation failures may motivate contracts; implementation errors may
motivate semantic validation. These are hypotheses, not an architecture backlog.
Single-agent tools and structured state may suffice; multi-agent design is not a
default. No solution architecture is authorized by this charter.

Prioritize scientific question > interpretable experiment > evidence > technique >
engineering polish. Build the smallest credible artifact, run only approved work,
inspect evidence, then refine. Do not manufacture infrastructure to stay busy.

Non-goals now: arbitrary C/C++ translation, full-repository migration, additional
quantum families, hundreds of generated cases, autonomous ground-truth creation,
QPU execution/performance claims, final dataset splits, and premature agent design.
Broader scope or paper-level claims require a recorded human decision. See
[CODEX_WORKFLOW.md](CODEX_WORKFLOW.md) for operating rules and
[open_questions.md](open_questions.md) for unresolved science.
