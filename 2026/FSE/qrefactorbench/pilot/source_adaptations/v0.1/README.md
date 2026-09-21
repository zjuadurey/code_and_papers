# 两份有出处的改编样例：先跑通案例构建路线

2026-09-21 · **DRAFT / AI-assisted adaptation — NOT GROUND TRUTH**

本次按研究者要求只做 **MaxCut + 一个带约束的图问题**，不先扩到十例。
两段计算函数来自 C2|Q> 的公开合成数据，新增情境/接口/测试由本项目编写。
完整路线为：固定来源 → 审查实际行为 → 保留计算函数 → 增加有作用的应用接口
→ 明确原软件合同 → 可运行测试 → 分离公共输入与私有评审材料。

| 样例 | 原计算 | 新的功能需求 | 关键合同与上下文 |
|---|---|---|---|
| [lit-001](cases/lit-001/ADAPTATION.md) | 加权 MaxCut，C2|Q> CSV 第 164 条 | 把设备安排到两个维护时段，使被分开的偏好权重总和最大 | 重复权重累加、端点校验、名字映射、精确分数与稳定并列输出 |
| [lit-002](cases/lit-002/ADAPTATION.md) | 最小顶点覆盖，C2|Q> CSV 第 427 条 | 为所有连接选择检查端点，使用最少的站点 | 每条连接至少覆盖一次、无向去重、精确数量与稳定并列输出 |

优先阅读每例 `public_task.json` 和 `program.py`，再打开 `kernel.py`。
策展者随后查看 ADAPTATION.md；独立标注者不要看私有提案。
来源/许可/转换：[SOURCES.md](SOURCES.md)；借鉴评测及实际落地：
[EVALUATION_DESIGN.md](EVALUATION_DESIGN.md)。

## 状态与边界

- 单独放在这里；原 `cases/` 仍是 14 个 DRAFT，旧十例 pilot、冻结输入和模型结果不变。
- 新两个 `case.json` 通过现有 schema。`case_type=positive` 只是 schema 必填的
  **暂定采样意图**，不是通过审定的科学结论；regions 同样只是私有提案。
  structural/practical/support/expected_decision/intent/family 均为 null，计划为 null。
- 核心函数保留源代码，业务背景是合成需求，不冒充真实部署程序。
- 16 节点是本地有界穷举域，未声称代表真实规模或能获得量子优势。
- 没有模型调用、Qiskit/QPU 执行、量子实现、gold 标签或新评测语义。

## 本地运行

以下在仓库根目录执行，使用现有环境，不需安装包。两个 pytest 分进程运行，
因为各案例按现有约定使用自己的 `program` / `kernel` 模块名。

```bash
PY=/home/audrey/miniconda3/envs/palqo/bin/python
$PY -m pytest -q pilot/source_adaptations/v0.1/cases/lit-001/test_program.py
$PY -m pytest -q pilot/source_adaptations/v0.1/cases/lit-002/test_program.py
$PY -m qrefactorbench validate pilot/source_adaptations/v0.1/cases/
$PY -m qrefactorbench summarize pilot/source_adaptations/v0.1/cases/ --json
```

运行可见的功能示例：

```bash
echo '{"equipment":["pump","fan"],"requirements":[{"first":"pump","second":"fan","weight":3}]}' | python pilot/source_adaptations/v0.1/cases/lit-001/program.py
echo '{"stations":["north","south","west"],"connections":[["north","south"],["south","west"]]}' | python pilot/source_adaptations/v0.1/cases/lit-002/program.py
```

`review_inputs/` 是本次派生的六个公共文件与哈希清单，只有两个程序、两个 kernel、
两个 public_task；没有参考标注。重新导出到**新目录**：

```bash
python pilot/source_adaptations/v0.1/prepare_inputs.py --output /tmp/qrefactor-source-review-new
```

这不是新 baseline packet/prompt；旧 pilot exporter 固定读取 `cases/pilot/`，不应为这两例
修改它或覆盖其结果。准备正式新一轮实验时再采用新版本协议及既有预测格式。

## 下一步

研究者先按 ADAPTATION 审查两例：“功能需求自然吗？原合同清楚吗？候选与完整软件边界
合理吗？评测能区分可行/最优/完整行为吗？”审查通过后再按同一路线扩充。
不需要先决定 Agent 架构。尚待人审：上述边界、量子条件对应、实用证据与发布许可。

实际命令、输出和保护检查见 [validation/results.json](validation/results.json)。
检查来源：`fetch_sources.py` 可联网复核固定版本，常规测试无需网络。
