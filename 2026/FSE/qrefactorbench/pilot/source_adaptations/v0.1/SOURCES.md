# 来源与授权边界

核查日期：2026-09-21。两例均源于 **C2|Q> 数据集公开镜像中的合成 Python
程序**，不是从已部署业务系统挖掘的代码。新应用情境由 Codex 辅助编写。

## 可定位的原始材料

- 论文：Ye et al., *C2|Q>: A Robust Framework for Bridging Classical and Quantum
  Software Development*, [TOSEM DOI](https://doi.org/10.1145/3803018)，
  [arXiv 2510.02854](https://arxiv.org/abs/2510.02854)。作者、题名、场合以原站为准；
  这里不声称重新复现其论文结果。
- 数据集维护者：Hugging Face `boshuai1/c2q-dataset`。
  [固定版本](https://huggingface.co/datasets/boshuai1/c2q-dataset/tree/c5b457cf425c31e91bae829503ece6e92646dd0a)。
  版本 `c5b457cf425c31e91bae829503ece6e92646dd0a`，文件 `python_programs.csv`。
- 该镜像有 434 个数据行；**只保留两条选中记录**。行号从 CSV 表头后第一条记录记作 1。
  不是物理文本行号，不是原作者提供的稳定 case ID。
- 原数据卡指定 **CC-BY-4.0**；保留原卡
  [DATASET_CARD.md](sources/DATASET_CARD.md)、原记录、转换说明和哈希。
  [许可说明](https://creativecommons.org/licenses/by/4.0/)；保留作者/来源、许可及改编说明，
  不暗示原作者认可我们的案例。GitHub 项目代码的 Apache 许可不能替代此数据集许可。
- 数据卡说明 HF 是 cleaned public mirror，Zenodo 是归档来源；本次只固定 HF 版本，
  不冒称与整个 Zenodo archive 完全一致。

| 新 ID | CSV 数据行 | 原函数 | 保留内容 |
|---|---:|---|---|
| lit-001 | 164 | `maxcut_bruteforce(adj)` | 非负整数加权图的逐分配枚举、完整函数及并列解顺序 |
| lit-002 | 427 | `min_vertex_cover_bruteforce(edges, n)` | 按集合大小/组合次序枚举、覆盖约束、完整函数 |

逐条原记录（含原 labels）只在 `sources/` 中供策展审查；不进入公共输入。
完整 CSV 的 SHA-256、原字段/解码文本/函数 SHA-256 见
[manifest.json](sources/manifest.json)。`fetch_sources.py` 按固定版本重新读取，
只把这两条记录的字面 `\n` 转为换行；AST 提取函数，移除顶层示例运行，保留所需
`itertools` 导入。函数正文没有修复、改名或重写。下载脚本不执行源代码。
经人工式源码检查后，本地测试才执行这两个无外部依赖的计算函数。

## 新增部分与未解决事项

`program.py`、public specification、测试、评测说明、情境均为本项目新增，
**不是原作者提供的业务需求、测试或量子化标注**。每例 ADAPTATION.md 逐项列出变化。
新文件没有借此获得项目统一许可证；case `license=NOASSERTION` 表示整个改编包的
再发布许可尚待决定，不否认上游片段已有 CC-BY-4.0 声明。不在此任务中发布/冻结数据集。

上游片段的算法名称仍出现在程序中。这是原始代码的已有信息；没有为制造定位难度改名。
公共 prose 不额外指定候选行、量子家族或正负类别，但不能宣称输入完全不含任务线索。
独立模型/标注者只接收 `review_inputs/<case-id>/` 中对应材料；不要给 sources、
ADAPTATION、case.json 或整个仓库。公共输入现在仅用于本地准备，外部分发时还需保留
合适的署名/许可材料，并记录这类材料可能产生的额外线索。
