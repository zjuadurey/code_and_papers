# Reference completion v0.1.1 — 三项审核修复

这是 [v0.1](../v0.1/README.md) 的修订版，**不是新增案例或新实验**。
十组母案例、两类正向量子家族、科学标签和公共软件合同保持原样；全部仍为 DRAFT。
旧版源码、输入和结果没有覆盖。下一次准备实验应使用本版
[30 份 A/B/C 输入](review_inputs/manifest.json)，只向模型提供单份 txt。

## 修复内容

| 案例 | 原问题 | 本版修复 |
|---|---|---|
| lit-005 | locked 的插入顺序改变冲突列表，违反按 features 排序的合同 | [program.py](cases/lit-005/program.py) 按 features 遍历；六种锁定顺序、inspect/complete 两种模式验证 |
| lit-009 | 有限解减去有限 current 仍可能溢出为 Infinity | [program.py](cases/lit-009/program.py) 复用 finite 检查每个 delta；溢出抛 ValueError，CLI 非零退出且不输出成功报告 |
| lit-007 | 模型可见的类名和来源文件 URL 直接提示 QAOA | [kernel.py](cases/lit-007/kernel.py) 和 [NOTICE](cases/lit-007/NOTICE.txt) 使用项目级归属；保留版权、改编说明及完整许可文本 |

lit-007 的原始类名、固定版本文件 URL 和算法背景仍在私有
[改编记录](cases/lit-007/ADAPTATION.md)、[case.json](cases/lit-007/case.json) 及旧版中。
不要把这些私有材料提供给模型。公共部分仍保留 SupermarQ 项目名，因此这次仅修复
已确认的显式算法提示，不声称完全匿名或消除所有来源识别可能。所有案例共用的
任务说明和合同菜单仍正常列出支持的量子家族，未被改写。

## 版本与差异

- [CHANGES.diff](CHANGES.diff) 保存六个新版案例目录相对 v0.1 的文本差异。
- 六份目录是旧案例的版本化工作集，不增加独立案例数；只有 005/007/009 的
  case version 改为 0.1.1，其余字段逐项不变。复制的改编文档链接指回旧来源快照。
- 005 和 009 的 B/C、007 的 A/B/C 共 **7 份输入改变**；其他 **23 份字节一致**。
  每组 B 仍严格等于 C 加一个原有位置提示。公共合同、候选范围、四份 schema 和
  共用 prompt 均不变。原始量子源文件、目标函数、求解算法和正式 evaluator 未修改。
- [build_package.py](build_package.py) 复用旧导出器，只切换案例目录；生成前核对
  旧输入哈希，输出目录必须不存在。来源快照和方法夹具继续复用 v0.1，不重复下载。
- 新版 B/C 仍共享 prediction case_id，按条件分别收集，不混成独立案例。

## 实际验证

先运行新回归测试，旧实现出现 **4 个预期失败**（005 两个模式、009 两个溢出方向），
记录保留在 [validation.json](validation.json)。随后修复，未放宽合同或断言。

- 六个案例套件：**61 passed**（11/9/8/9/11/13）。
- 版本、许可、标签、输入差异、重生和示例检查：**12 passed**。
- 原仓库：**97 passed / 15 skipped**；跳过来自 palqo 环境缺少可选 Qiskit/PyYAML。
- 既有 htp-static 环境的可选套件：**5 passed**。
- 新版六案例与原 cases/ 十四案例均 validate/summarize 成功，仅有预期 DRAFT 警告。
- [完整性记录](validation/integrity.json)：**1189 个旧文件未变**，prompt hash 相同。

```bash
# 在仓库根目录，使用既有环境；六个 case 套件因同名模块须分别运行。
/home/audrey/miniconda3/envs/palqo/bin/python -B -m pytest -q pilot/reference_completion/v0.1.1/test_corrections.py
/home/audrey/miniconda3/envs/palqo/bin/python -B -m pytest -q pilot/reference_completion/v0.1.1/cases/lit-005/test_program.py
/home/audrey/miniconda3/envs/palqo/bin/python -B -m pytest -q pilot/reference_completion/v0.1.1/cases/lit-009/test_program.py
/home/audrey/miniconda3/envs/palqo/bin/python -B -m qrefactorbench validate pilot/reference_completion/v0.1.1/cases/
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/reference_completion/v0.1.1/build_package.py --prepare /tmp/reference-v011-new
```

没有新模型/agent、QPU 或量子优化器实验，没有安装依赖或变更科学标签。
WHERE 是否更难留给实验检验，不是继续案例建设的前置门槛。
