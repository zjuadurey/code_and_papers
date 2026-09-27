# 一个 benchmark case 的完整构建示例：最小顶点覆盖 → 连接检查与工作清单

日期：2026-09-22  
母案例：`lit-002`；完整上下文案例：`context-002`；状态：DRAFT

本文展示一个案例从上游算法片段到本项目评测输入的全过程：原始代码、选择与改编思路、改编后的完整程序、输入输出，以及模型需要回答什么。

**这里的“修改后”指构建 benchmark 时加入软件上下文后的经典程序。** 模型目前针对这个程序进行分析、定位和条件迁移规划；本例没有在这里展示已经完成的量子迁移实现。

## 1. 原始 case 从哪里来

| 项目 | 本例的具体信息 |
|---|---|
| 来源 | C2\|Q> 数据集的公开 cleaned mirror：`boshuai1/c2q-dataset` |
| 固定版本 | `c5b457cf425c31e91bae829503ece6e92646dd0a` |
| 来源文件与记录 | `python_programs.csv`，表头后的第 427 条数据记录 |
| 原始计算 | `min_vertex_cover_bruteforce(edges, n)` |
| 本地留存 | 原记录、解码后的完整程序、提取函数、来源及哈希记录 |
| 原始程序性质 | 合成 Python 算法程序 |
| 新增情境性质 | 本项目由 Codex 辅助编写的合成“连接检查与站点工作清单”需求 |

第 427 条是 CSV 的数据记录编号，不是文件的物理行号。原记录中的字面换行转成实际换行后，得到下面的完整程序；提取函数时移除了顶层演示代码，函数正文保持不变。

来源依据见[本地来源说明](../pilot/source_adaptations/v0.1/SOURCES.md)和[改编溯源记录](../pilot/reference_cases/v0.1/provenance.json)。上游片段标注 CC-BY-4.0；新增应用需求、代码和测试属于本项目改编，整个改编包的许可仍记为 NOASSERTION。

## 2. 原始程序完整长什么样

以下是[原始记录解码后的完整代码](../pilot/source_adaptations/v0.1/sources/lit-002.decoded.py)，包含它自带的演示输入：

```python
import itertools

# Brute-force minimum vertex cover for a small graph

def min_vertex_cover_bruteforce(edges, n):
    nodes = list(range(n))
    best_cover = None
    for r in range(n + 1):
        for subset in itertools.combinations(nodes, r):
            cover = set(subset)
            ok = True
            for u, v in edges:
                if u not in cover and v not in cover:
                    ok = False
                    break
            if ok:
                best_cover = cover
                return best_cover
    return best_cover

edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
cover = min_vertex_cover_bruteforce(edges, 4)
print(sorted(cover))
```

它的演示图是一个四点环：

```text
0 —— 1
|    |
3 —— 2
```

程序依次枚举大小为 0、1、2……的顶点子集，找到第一个能覆盖全部边的集合就返回。这里“覆盖”指每条边至少有一个端点被选中。

原程序的打印结果为：

```text
[0, 2]
```

两个最小覆盖是 `{0, 2}` 和 `{1, 3}`。因为组合按升序索引生成，程序先返回 `{0, 2}`。这个确定性的选择顺序也是后续需要保留的行为。

## 3. 为什么选它，准备怎么改

本例适合作为候选材料的可检查理由是：计算目标清楚、代码短、可以在小输入上精确枚举核验，而且存在“多个最优集合如何选”的行为细节。它为检查模型是否真正保留程序语义提供了具体抓手。

本例记录的是针对性选例与改编，尚不能据此声称已完成整个来源数据集的系统筛选，也不能声称这个案例已经具备经验证的模型区分度或量子收益。

改编围绕一个明确的软件需求展开：

> 用户提交站点、站点之间需要检查的连接，以及当前承担检查任务的站点。程序先评估当前方案，再提出覆盖全部连接所需站点数最少的方案，并为每个选中站点生成工作清单，报告站点增减和连接责任转移。

| 原始内容 | 改编后的内容 | 改动目的 |
|---|---|---|
| 整数顶点 `0…n-1` | 有名称的站点，按输入顺序映射到整数索引 | 引入外部输入与内部表示之间的对应关系 |
| 固定四点环边列表 | 用户提交连接；校验端点、规范方向、去除重复 | 让求解依赖真实的数据准备步骤 |
| 最小顶点覆盖枚举函数 | 原函数完整保留 | 保持计算目标与原有枚举行为可追溯 |
| 单次 `print(sorted(cover))` | 返回结构化 JSON 报告 | 让选择结果影响程序的多个输出字段 |
| 无现有方案 | 新增 `current_stations` 与当前覆盖评估 | 区分“评估现状”和“寻找新方案” |
| 无任务分配 | 每条已覆盖连接分配给一个选中的端点 | 让输出依赖具体集合，而不只依赖最优数量 |
| 无变更报告 | 新增站点增减、覆盖变化、责任转移 | 检查迁移后上下游结果是否一致 |

新增情境没有加入行程、容量、工时或不同站点成本。每个站点的选择成本都是 1，选中站点可以检查任意多条关联连接，所以内部问题仍然是原来的最小顶点覆盖。

`current_stations` 用来评估现状和生成变化报告，**不进入优化目标**。程序没有“尽量少调整现有站点”的要求。

## 4. 修改后必须保持什么行为

案例把外部可观察行为写成公开合同。主要要求如下：

1. **完整校验输入**：输入恰好包含三个字段；站点名称唯一且非空；连接两端是不同的已知站点；当前站点不能重复。不合法时抛出 `ValueError`，不能修改输入。
2. **规范化连接**：按站点输入位置排列两个端点，合并重复及反向重复连接，再按索引对排序。
3. **选择方案**：覆盖每条连接；先最小化站点数，再选择“已选站点索引升序元组”中字典序最小的那个。
4. **生成工作清单**：每条已覆盖连接恰好交给一个选中的端点；两端都选中时，交给输入位置较早的一端。选中但没有任务的站点也保留空清单。
5. **如实报告现状与变化**：当前方案可以漏检；所有计数、清单和责任变化都必须与实际返回的集合一致。
6. **处理边界情况**：空连接的新方案为空集；空站点要求其他输入也为空；当前版本不允许近似站点数、漏覆盖或改变 tie-break。

例如 `(0, 3)` 比 `(1, 2)` 的 tuple 字典序小。迁移方案即使找到了相同数量的站点，仍须遵守这个排序要求。

以下是[公开任务文件](../pilot/reference_cases/v0.1/cases/context-002/public_task.json)的完整内容，便于直接核查实际合同，而不是只依赖上述中文概述：

```json
{
  "case_id": "context-002",
  "title": "Connection inspection review and station worklists",
  "software_contract": "review_inspections(request) validates the whole request or raises ValueError, without modifying it. Error text is not fixed. Return station_count (all declared stations), connection_count (unique undirected connections), current, proposed and changes. Proposed selects the fewest stations such that every connection has a selected endpoint; ties choose the lexicographically smallest tuple of station input positions. There is no requirement to minimize changes from current_stations. Current selection may leave connections uncovered and must be assessed honestly. Each plan contains selected_stations in station input order, selected_count, covered_connection_count, uncovered_connections, and checklists. Normalize each connection's endpoints by their input positions i<j, remove duplicate/reversed declarations, and order connections by increasing (i,j). Assign every covered connection to exactly one selected endpoint: the earliest endpoint in station input order. Checklists contains one object per selected station, in station input order, with station and connections; retain empty checklists. Uncovered connections are listed separately, never allocated to an unselected station. Changes contains add_stations and remove_stations in input order, selected_count_delta (proposed minus current), newly_covered_connections (uncovered before, covered after), and reassigned_connections for every connection whose assigned station changes. Reassigned records contain connection, from_station and to_station, using null for an unassigned connection; retain normalized connection order. All scores and worklists describe the actual returned selections. Empty stations require empty connections and current_stations, producing empty lists and zero counts. Empty connections propose no stations. Valid CLI input produces one JSON report; invalid requests produce no successful report and a nonzero exit. No uncovered proposed connection, approximate station count, or altered tie rule is permitted in this version.",
  "input_domain": "JSON object with exactly stations, connections, current_stations. stations is a list of 0–16 unique nonempty strings. connections is a list of two-element lists of distinct known station names. current_stations is a list of distinct known station names; arbitrary order and empty selection are allowed. Every station is available at unit selection cost. A selected station can inspect any number of its incident connections. Inspection from either endpoint is sufficient. No travel, staff capacity, duration, geographical or activation-cost rules are modeled. The 16-station bound is a local enumeration limit, not a measured workload.",
  "execution_assumptions": [
    "Input is ordinary classical JSON. The report is a proposal for human review, not execution of inspections or deployment.",
    "No hardware, latency target, workload frequency or deployment cost evidence is supplied.",
    "Connection responsibility follows input ordering; station-count optimality and report correctness are separate requirements."
  ]
}
```

## 5. 修改后的完整程序

当前案例由两个 Python 文件组成，另有示例输入与预期报告：

```text
context-002/
├── program.py
├── inspection.py
├── public_task.json
├── example_request.json
└── example_report.json
```

主流程为：

```text
JSON 输入
  → prepare_request：校验、索引映射、连接去重
  → describe_plan：评估 current_stations
  → min_vertex_cover_bruteforce：求 proposed 的站点集合
  → describe_plan：为 proposed 生成覆盖情况与工作清单
  → compare_plans：计算站点变化与连接责任转移
  → JSON 报告
```

### 5.1 program.py：组织完整业务流程

以下完整复制自[当前入口文件](../pilot/reference_cases/v0.1/cases/context-002/program.py)：

```python
"""Review an existing inspection arrangement and produce station worklists."""

import json
import sys
from typing import Any

from inspection import compare_plans, describe_plan, min_vertex_cover_bruteforce, prepare_request


def review_inspections(request: Any) -> dict[str, Any]:
    """Validate, assess current coverage, propose stations, and explain work transfers."""
    names, edges, selected = prepare_request(request)
    current = describe_plan(names, edges, selected)
    proposed = describe_plan(names, edges, min_vertex_cover_bruteforce(edges, len(names)))
    return {"station_count": len(names), "connection_count": len(edges),
            "current": current, "proposed": proposed,
            "changes": compare_plans(names, edges, current, proposed)}


if __name__ == "__main__":
    print(json.dumps(review_inspections(json.load(sys.stdin)), indent=2))
```

### 5.2 inspection.py：校验、工作清单、变更报告与原始求解函数

以下完整复制自[当前实现文件](../pilot/reference_cases/v0.1/cases/context-002/inspection.py)。最后的 `min_vertex_cover_bruteforce` 就是保留的上游函数。

```python
"""Validation, coverage assessment, worklists and changes for endpoint inspections."""

import itertools
from typing import Any


def prepare_request(request: Any) -> tuple[list[str], list[tuple[int, int]], set[int]]:
    """Read all fields; an incomplete current coverage is legal and must be reported."""
    if not isinstance(request, dict) or set(request) != {"stations", "connections", "current_stations"}:
        raise ValueError("Expected stations, connections and current_stations")
    names = request["stations"]
    if not isinstance(names, list) or len(names) > 16:
        raise ValueError("stations must be a list of at most 16 names")
    if any(not isinstance(name, str) or not name for name in names) or len(set(names)) != len(names):
        raise ValueError("Station names must be unique nonempty strings")
    index = {name: i for i, name in enumerate(names)}
    connections = request["connections"]
    if not isinstance(connections, list):
        raise ValueError("connections must be a list")
    edges = set()
    for pair in connections:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("Connections require two endpoints")
        first, second = pair
        if not isinstance(first, str) or not isinstance(second, str):
            raise ValueError("Endpoints must be names")
        if first not in index or second not in index or first == second:
            raise ValueError("Endpoints must be distinct known stations")
        edges.add(tuple(sorted((index[first], index[second]))))
    current = request["current_stations"]
    if not isinstance(current, list):
        raise ValueError("current_stations must be a list")
    selected = set()
    for name in current:
        if not isinstance(name, str) or name not in index or index[name] in selected:
            raise ValueError("Current stations must be distinct known names")
        selected.add(index[name])
    return list(names), sorted(edges), selected


def describe_plan(names: list[str], edges: list[tuple[int, int]], selected: set[int]) -> dict[str, Any]:
    """Assign each covered connection once to its earliest selected endpoint."""
    assigned = {i: [] for i in sorted(selected)}
    uncovered = []
    for u, v in edges:
        pair = [names[u], names[v]]
        if u in selected:
            assigned[u].append(pair)
        elif v in selected:
            assigned[v].append(pair)
        else:
            uncovered.append(pair)
    return {"selected_stations": [names[i] for i in sorted(selected)],
            "selected_count": len(selected), "covered_connection_count": len(edges) - len(uncovered),
            "uncovered_connections": uncovered,
            "checklists": [{"station": names[i], "connections": pairs} for i, pairs in assigned.items()]}


def compare_plans(names: list[str], edges: list[tuple[int, int]], current: dict, proposed: dict) -> dict:
    """Describe station activation and connection responsibility changes independently."""
    old_set, new_set = set(current["selected_stations"]), set(proposed["selected_stations"])

    def owners(plan: dict) -> dict:
        return {tuple(pair): row["station"] for row in plan["checklists"] for pair in row["connections"]}

    old, new = owners(current), owners(proposed)
    pairs = [(names[u], names[v]) for u, v in edges]
    return {"add_stations": [name for name in names if name in new_set - old_set],
            "remove_stations": [name for name in names if name in old_set - new_set],
            "selected_count_delta": len(new_set) - len(old_set),
            "newly_covered_connections": [list(pair) for pair in pairs if pair not in old and pair in new],
            "reassigned_connections": [{"connection": list(pair), "from_station": old.get(pair),
                                        "to_station": new.get(pair)}
                                       for pair in pairs if old.get(pair) != new.get(pair)]}


def min_vertex_cover_bruteforce(edges, n):
    nodes = list(range(n))
    best_cover = None
    for r in range(n + 1):
        for subset in itertools.combinations(nodes, r):
            cover = set(subset)
            ok = True
            for u, v in edges:
                if u not in cover and v not in cover:
                    ok = False
                    break
            if ok:
                best_cover = cover
                return best_cover
    return best_cover
```

## 6. 实际输入与完整输出

下面使用仓库已有的示例。注意，这个应用示例是三条连接组成的链，和原始程序自带的四点环是两个不同输入。

### 6.1 输入

```json
{
  "stations": ["north", "south", "west", "east"],
  "connections": [["north", "south"], ["south", "west"], ["west", "east"], ["south", "north"]],
  "current_stations": ["east", "west", "south", "north"]
}
```

站点输入位置是 `north=0, south=1, west=2, east=3`。第四条连接是第一条的反向重复声明，规范化后只有三条连接：

```text
north(0) —— south(1) —— west(2) —— east(3)
```

当前四个站点都被选中。最小覆盖大小为 2，候选包括 `(0,2)`、`(1,2)` 和 `(1,3)`；按合同返回 `(0,2)`，即 `north` 与 `west`。

### 6.2 完整输出

以下为仓库保存的[示例报告](../pilot/reference_cases/v0.1/cases/context-002/example_report.json)：

```json
{
  "station_count": 4,
  "connection_count": 3,
  "current": {
    "selected_stations": [
      "north",
      "south",
      "west",
      "east"
    ],
    "selected_count": 4,
    "covered_connection_count": 3,
    "uncovered_connections": [],
    "checklists": [
      {
        "station": "north",
        "connections": [
          [
            "north",
            "south"
          ]
        ]
      },
      {
        "station": "south",
        "connections": [
          [
            "south",
            "west"
          ]
        ]
      },
      {
        "station": "west",
        "connections": [
          [
            "west",
            "east"
          ]
        ]
      },
      {
        "station": "east",
        "connections": []
      }
    ]
  },
  "proposed": {
    "selected_stations": [
      "north",
      "west"
    ],
    "selected_count": 2,
    "covered_connection_count": 3,
    "uncovered_connections": [],
    "checklists": [
      {
        "station": "north",
        "connections": [
          [
            "north",
            "south"
          ]
        ]
      },
      {
        "station": "west",
        "connections": [
          [
            "south",
            "west"
          ],
          [
            "west",
            "east"
          ]
        ]
      }
    ]
  },
  "changes": {
    "add_stations": [],
    "remove_stations": [
      "south",
      "east"
    ],
    "selected_count_delta": -2,
    "newly_covered_connections": [],
    "reassigned_connections": [
      {
        "connection": [
          "south",
          "west"
        ],
        "from_station": "south",
        "to_station": "west"
      }
    ]
  }
}
```

这个输出同时体现了多项要求：反向重复连接被合并；当前站点按声明顺序输出；当前 `east` 的空清单保留；新方案站点数从 4 降到 2；`south—west` 的检查责任从 `south` 转给 `west`。

因此，只返回“最少需要 2 个站点”不足以完成这个软件任务。返回另一个大小为 2 的覆盖集合也可能改变工作清单和责任报告。

### 6.3 本地运行方式

在项目根目录执行，使用现有 Python 环境即可：

```bash
python -B pilot/reference_cases/v0.1/cases/context-002/program.py \
  < pilot/reference_cases/v0.1/cases/context-002/example_request.json
```

## 7. 最终给模型的 case 是什么

评测中的一个 case 是“公开任务合同 + 源代码 + 统一分析指令和输出 schema”。上面的 JSON 请求是用于说明、验证程序行为的一次输入实例。

当前为同一个母案例准备了三个输入条件：

| 条件 | 给模型的材料 | 希望研究的问题 |
|---|---|---|
| A | 原始核心函数视图及对应合同 | 在核心已被抽出的情况下能否理解和规划 |
| B | 完整程序和合同，加明确的位置提示 | 获得定位帮助后能否解释依赖并规划 |
| C | 与 B 相同的完整程序和合同，去掉位置提示 | 能否从完整程序中自行发现候选区域 |

这三个条件属于同一个母案例。B/C 用于控制位置提示；A 与完整上下文还同时存在接口、长度等差异，不能把 A/C 差异完全归因于定位能力。

现有四模型试跑使用的是 C 条件。完整原始模型输入保存在 [lit-002-C.txt](../pilot/reference_completion/v0.1.1/review_inputs/lit-002-C.txt)，包括带行号的两个源文件、公开合同、共享合同菜单与 JSON schema。

模型被要求识别候选代码区域、解释输入与上下游依赖、分别判断结构适配性和实际适用性；若判断结构适配，则给出条件迁移计划，并说明编码、精确性、可行性和资源方面的义务。模型可以选择保留经典实现。当前这项分析任务不要求生成或执行补丁，也不向模型提供私有参考标签和已有评审结论。

## 8. 这个改编为能力评估提供了什么

该案例提供了几类具体可核查的回答内容：

| 回答内容 | 可以检查的实际问题 |
|---|---|
| 候选区域与依赖 | 是否定位到求解计算；是否认识到它依赖校验后的索引图 |
| 目标与约束 | 是否保持覆盖约束、最小站点数和 tuple tie-break |
| 迁移边界 | 是否保留输入校验、当前方案评估、工作清单和变化报告 |
| 编码或求解计划 | 所写目标函数是否真的产生合同要求的选择集合 |
| 检查与回退 | 是否核查完整合同；如何处理不可行、非最优和 tie-break 错误 |
| 实际建议 | 是否把结构上可构造与有证据值得迁移分别判断 |

这些维度可以用于分析粗标签相同的回答，但本例和少量试跑不足以建立稳定的模型排名。具体公式可以通过小实例穷举寻找反例；公式错误、整个条件计划错误和最终程序运行失败仍然需要分别判断。

目前的限制是：新增业务情境为合成，函数名仍直接暴露算法信息，难度与代表性尚需实验和专家审查，参考标签仍为 DRAFT/PENDING。文档展示的构建过程与代码行为，不等于已经完成独立金标认证或证明量子优势。

