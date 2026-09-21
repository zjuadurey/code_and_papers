# 今晚可运行的终端 demo

在仓库根目录运行：

```bash
bash scripts/run_demo.sh
```

脚本复用本机已有 `htp-static` 环境（Qiskit 2.5.2），不安装依赖、不调用模型、
不访问 QPU。其他机器可指定 `QREFACTOR_DEMO_PYTHON=/path/to/python`。
保存新报告时使用一个不存在的路径，已有报告不会被覆盖：

```bash
bash scripts/run_demo.sh --output /tmp/qrefactor-demo-review.json
```

## 现场按这个顺序看

1. **原程序与 WHERE**：打印 pilot-001 的代码、行号以及已有模型识别的区域。
2. **WHETHER 和条件 HOW 分开**：历史回答是结构 YES、实际 NO、REMAIN_CLASSICAL，
   但仍有 Grover 条件计划。打印编码、解码和精确无解认证的义务。
3. **真实执行一个演示实现**：从 CNF 子句构造可逆 oracle，计算子句真值、相位标记、
   反计算辅助位，执行一次 Grover 迭代，使用 Qiskit Statevector 固定种子抽样。
   这不是预录的成功输出，也没有枚举真值表来构造 oracle。
4. **保护原软件行为**：原函数返回精确 bool。测得的候选由原谓词验证；没有有效候选时，
   调用原穷举程序认证结果。有解、无解、空合取、空子句、重复文字/重言式五组检查，
   逐项打印实际量子执行、经典兜底和资源数据。
5. **可以拒绝量子化**：pilot-002 回放 NONE / 结构 NO / null 计划，实际运行保留的
   经典程序，检查最终 digest 和每次回调的内容、顺序。异常传播由测试另外覆盖。

## 哪些是回放，哪些是本次实现

| 部分 | 来源与边界 |
|---|---|
| 经典源码 | 原 `cases/pilot/pilot-001` / `pilot-002`，只读加载 |
| WHERE / WHETHER / HOW | 已完成 conditional-plan-diagnostic 的两份 parsed 回答，明确标注回放；不是新预测或 ground truth |
| 混合搜索实现 | [hybrid_search.py](hybrid_search.py)，本次 AI 辅助编写的独立演示代码；不是运行时从计划自动生成 |
| 执行与验证 | 本地实际运行，复用现有 SemanticOracles 和 extract_resources；不改 benchmark evaluator |
| 保留经典 | 原 pilot-002 实现，无变换 |

本 demo 展示的是一条接通的演示流程，**尚不是接受任意程序的自动分析/转译系统**。
量子执行是在明确选择的条件方案下演示，不覆盖或推翻历史 REMAIN_CLASSICAL 建议。
没有新科学标签、独立基线、模型调用或优势结论。

## 实现边界

- 量子分支仅处理正常类型、域内输入，最多 6 个变量、14 个总量子位；其他输入
  委托原函数，保留原行为。该限制是本机 statevector 内存预算，不是科学适用性阈值。
- 固定一次 Grover 迭代、16 shots、seed=7 是演示预算；不假设已知解数量，
  不宣称最优搜索调度或固定成功概率。漏测到解也必须经过原程序兜底。
- 经典兜底可能消除潜在收益，不能省略其成本。无解不会仅凭抽样宣布。
- 资源数据来自 `u/cx`、optimization_level=0 的分解电路及等价末端测量；
  Statevector 实际抽样数据位，资源表示计入所有量子位的末端测量。
  这些不是物理硬件成本，也未计完整数据加载/容错成本。
- 测试覆盖有限域，不是所有输入的形式证明；DRAFT 案例和计划仍待人审。

## 已执行的验证（2026-09-20）

- demo 成功运行；[首次 JSON 报告](artifacts/first_run.json) 保留源码/回放 hash、版本、
  输入、抽样、输出、兜底与资源数据；[终端记录](artifacts/terminal.txt) 可直接预览。
- 新增 demo 测试 **13 passed**：36 种小公式 × 4 个赋值的 oracle 相位/辅助位检查，
  正常/边界输入、测量失败但有解的兜底、异常传播等。
- `palqo` 全套 **91 passed, 14 skipped**；该环境缺 Qiskit/PyYAML。
  `htp-static` 的 demo + optional 套件 **18 passed**，覆盖上述跳过项。
- 14 个案例 validate 通过；JSON summarize 通过，全部仍是 DRAFT。
- 首次尝试直接用 `htp-static` 跑全套测试出现 **4 个 collection errors**，原因是
  该环境缺 jsonschema；同环境 validate 也因它失败。没有安装依赖，改用项目原有
  两环境分工完成验证。失败日志保留在 [初次检查](artifacts/pytest_htp_full_attempt.txt)。
- [保护文件检查](artifacts/preservation.json) 比较本次修改前后冻结输入、案例、
  schemas、评估实现和两个实验目录的文件 hash。

实际命令：

```bash
bash scripts/run_demo.sh --output demo/artifacts/first_run.json
PYTHONDONTWRITEBYTECODE=1 /home/audrey/miniconda3/envs/palqo/bin/python -m pytest -q -p no:cacheprovider
PYTHONDONTWRITEBYTECODE=1 /home/audrey/miniconda3/envs/htp-static/bin/python -m pytest -q -p no:cacheprovider tests/test_demo.py tests/test_optional.py
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench validate cases/
/home/audrey/miniconda3/envs/palqo/bin/python -m qrefactorbench summarize cases/ --json
```

现在先看这条演示是否把研究问题讲清楚；不要为了今晚的展示扩展 schema、
添加 Agent 或自动启动新模型实验。
