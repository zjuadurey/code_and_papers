"""Regenerate the scale report/plot from retained observations only."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import run as r


def main() -> None:
    results = json.loads((r.HERE/'run/results.json').read_text())['rows']
    audit = json.loads((r.HERE/'audit/validation.json').read_text())
    gray = {x['n']: x['best_seconds'] for x in audit['gray_timings'] if x['seed'] == r.SEEDS[0]}
    rows, table = [], []
    for entry in results:
        n, depth = entry['n'], entry['depth']
        classical = entry['classical_seconds']
        if classical is not None:
            classical = min(classical, gray.get(n, float('inf')))
        points = [{**p, 'overhead_budget_at_64_seconds': None if classical is None else classical-64*p['runtime_ns']*1e-9}
                  for p in entry['points']]
        rows.append({'n': n, 'depth': depth, 'classical_seconds': classical, 'points': points})
        if depth == 1 and points:
            point = min(points, key=lambda x: x['runtime_ns'])
            baseline = '未完成' if classical is None else f'{classical*1000:.3f}'
            budget = '未知' if classical is None else f'{point["overhead_budget_at_64_seconds"]*1000:.3f}'
            table.append(f'| {n} | {baseline} | {point["physical_qubits"]} | {point["runtime_ns"]/1e6:.3f} | {budget} |')
    r.save(r.HERE/'derived.json', {'rows': rows, 'comparison': 'Same first-seed graph; min(MILP, available optimized enumeration)',
        '64_shots': 'Illustrative slice of parameter S, not measured sufficient sampling budget',
        'positive_budget_is_not_benefit': True})
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for ax, n in zip(axes, (32, 48)):
        for row in rows:
            if row['n'] != n:
                continue
            fastest = min(row['points'], key=lambda x: x['runtime_ns'])
            s = np.arange(1, 1025)
            budget = (row['classical_seconds'] - s*fastest['runtime_ns']*1e-9)*1000
            ax.plot(s, budget, label=f'p={row["depth"]}, {fastest["physical_qubits"]} physical qubits')
        ax.axhline(0, color='black', linewidth=.8)
        ax.set(xlabel='Total shots S (quality requirement unknown)', ylabel='Remaining total overhead budget (ms)',
               title=f'n={n}: necessary timing budget only')
        ax.legend(fontsize=7)
        ax.grid(alpha=.2)
    fig.suptitle('Hypothetical hardware; exact certification and success rate not established', fontsize=10)
    fig.savefig(r.HERE/'resource-budget.png', dpi=180)
    fig.savefig(r.HERE/'resource-budget.pdf')
    plt.close(fig)
    report = '''# 规模增长后的资源条件：实际诊断结果

四节点的无收益结果不能回答规模增长后的交叉点。本轮实际测量经典求解、调用QDK估算
8–64节点资源，并反求完整开销能占用的预算。**在32/48节点已出现正的必要时间预算，
但当前实现尚不能把它转成满足原精确行为的收益区域。**

## 结果

每行同一个固定种子的非二分图；一层QAOA、100ns门/500ns测量、物理错误率1e-4，
单shot资源估算错误预算1%。这些是假设硬件模型、未优化固定角度的资源模板。
经典侧为实测精确割值及最小mask恢复；8/16节点取MILP与优化枚举的较快结果。
其他规模只有MILP，不能宣称最强专用算法。时间为单机描述性观测，不是置信区间。

| 节点数 | 经典完成耗时 ms | 物理比特 | 单shot预测 ms | 假设64 shots后可留给全部其余成本的预算 ms |
|---|---:|---:|---:|---:|
'''+'\n'.join(table)+'''

64 shots只是参数切片，**未证明够用**。正预算表示仍有值得检验的空间；若所需shots、
验证/回退、参数优化和其他开销超过预算，方案仍无收益。64节点超时未完成，不能把3秒
当成经典完成耗时，也不能据此宣称量子胜出。三个种子的原始记录全部保留。

![不同深度和shots下的必要开销预算](resource-budget.png)

## 具体条件而非单一qubit门槛

32节点p=1的指定资源点为6009物理比特，单shot 0.505ms。本机该实例经典完成约579.076ms。
所以必须同时满足：足够的指定物理资源、精确行为得到保证，以及
`0.505*S + H_ms < 579.076`。
其中H包括输入/电路准备、参数搜索、编译摊销、控制通信、解码、最优性/tie证书和回退。
取S=64时，H必须小于546.756ms。这个数值是必要预算，不是已测完整量子耗时。
物理模型点也不是所有架构的最小qubit门槛；更快门/更高并行度需要重新估计，不能独立任意调参。

如果采用验证失败后回退，令q为一批候选获得可靠证书的概率，V为平均验证成本，
F为失败后的条件平均回退成本，则期望收益条件是
`S*t_shot + H_other + V + (1-q)*F < T_classical`。
若另外确有F=T_classical，才可简化成`S*t_shot + H_other + V < q*T_classical`。
q不是“得到高割值”的概率；它要求完整最优性与最小mask证书通过。
不能用理想单shot成功率代替含物理错误、验证和回退的真实q。

## 找到的实际实现缺口

现有lit-001工具只接受切开全部正权边的候选。新图包含正权三角形，任何二分都至少
留下其中一条未切边，因此该证书对所有候选都拒绝。这是结构性判断，不依赖采样是否幸运。
现有wrapper还限制n<=16，现有电路解析器固定4qubit；本轮扩展的是独立kernel资源模板，
不是已经实现任意规模的LLM迁移。原正式案例与合同未修改。

因此之前的“小规模没有收益”不能支持终止研究；真正缺少的是一般实例上可计算的
成功率与有成本的精确验证方案。单纯放大现有四节点workflow会触发回退，不能得到有效交叉点。
本轮没有假装已补齐这个机制，也未证明它不可实现。

## 验证与可复核性

- 18次经典实例求解：14次完整完成、4次预算内未完成，均保留；18次QDK资源调用全部成功。
- 冻结前实现的8个小图求解与独立枚举一致；超时分支及严格盈亏边界检查通过。
- 事后强化经典对照：64种四节点图的MILP/优化枚举与原kernel输出完全一致；
  8/16节点六个规模实例的优化枚举与MILP一致。事后审计只加强对手，不筛选量子有利实例。
- 原始协议和源码hash在[run/protocol.json](run/protocol.json)，原始输出及manifest在run/；
  [审计](audit/validation.json)、[派生数据](derived.json)与绘图代码保留。
- 超过16节点属于独立kernel规模研究；没有新正式case/gold、近似许可、模型/QPU调用或依赖安装。
- 这是资源条件的开发诊断，不是自动方法效果、跨程序泛化、统计优势或真机收益证明。

运行环境与预算见[README](README.md)。SciPy求解状态及接口解释依据
[官方文档](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html)。
'''
    (r.HERE/'REPORT.md').write_text(report)


if __name__ == '__main__':
    main()
