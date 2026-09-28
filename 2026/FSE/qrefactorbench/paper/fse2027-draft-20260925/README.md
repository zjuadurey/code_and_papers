# FSE 2027 LaTeX 论文草稿

英文研究论文草稿，生成于 2026-09-25。正式入口为 `main.tex`，目标是 FSE 2027 Research Papers。
研究主线：用程序分析与语义验证增强同一个 LLM 的量子机会识别和映射设计。

## 使用

将 `latex.zip` 作为新项目导入 Overleaf，主文件选择 **main.tex**，编译器选择 **pdfLaTeX**，使用完整且较新的 TeX Live 环境。
本地完整环境可运行：

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error main.tex
```

也可按 `pdflatex main`、`bibtex main`、`pdflatex main`、`pdflatex main` 编译。
依赖是标准 ACM `acmart` / `ACM-Reference-Format` 及其字体包，不包含自制类文件，不改边距、字号或行距。
源码按章节拆分；参考文献在 `references.bib`；所有占位宏在 `macros.tex`。

本机缺少 `libertine.sty`、`zi4.sty`、`newtxmath.sty`，未安装依赖。
`local-preview.pdf` 是用本机已有 Latin Modern 字体生成的阅读副本，第一页有明确标识，**不是投稿 PDF**。
正式入口没有静默字体替换；只有显式编译 `local-preview.tex` 才启用替代字体。
因此本地预览验证不能代替正式字体环境下的最终页数验收。实际检查见 `validation.json`。

## 已写内容与留空规则

- 完整摘要、引言、问题定义、案例构建、方法设计、评估设计、结果结构、威胁、相关工作、结论和 Data Availability。
- 6 个研究问题、8 组实验；D/S/A/V/AV 同模型对照、配对修订、消融、预算敏感性、谱系分组、统计与失败处理。
- 数值结果表的单元格使用 `\blank`，真正留空；待定运行配置使用 `\field`。不填零、不编造趋势或显著性。
- 3 个非实验图占位框：流程、合同示例、证据隔离。包含图注、标签、内容提示与无障碍描述。
- 实验图不画伪数据曲线；待有真实数据后再生成配对效果、质量/成本及扩展性图。
- 公式中的数学常数、案例 ID、RQ/E 编号和文献年份不是实验数据，正常保留。
- 即便仓库已有实验数值，本稿也依用户要求留空；不能把现有天花板结果改写成增强有效。

正文中的集成方法是 **proposed**，已实现的局部原型与未来方法明确区分。
本稿不是实验运行授权，不会改现有 benchmark、标签、指标、split 或研究队列。
新增研究问题、描述性指标、消融及主张均是论文设计草案，未被自动提升为正式科学决策。

## 包内说明

- `notes/EXPERIMENT_MATRIX.md`：逐实验的输入、对照、输出、有效性与执行前待定项。
- `notes/EVIDENCE_MAP.md`：论文叙述与本地证据的对应，区分已有/提案/未建立。
- `notes/FORMAT_REQUIREMENTS.md`：官网格式核验与页数边界。
- `notes/SOURCES.md`：参考文献的一手来源，便于复核。
- `data/results-template.csv`：空的长期格式数据入口；没有伪造样本行。
- `data/protocol-draft.json`：未确定的配置为 null，不可作为可执行实验配置。
- `validation.json`：编译、静态检查、篇幅、旧文件保护的实际记录。

尚待完成：实施与审核拟议方法，确定并授权实验、完善独立参考和保留集、填入真实结果、替换图占位，提供匿名 artifact 地址与发布意向，并在完整 ACM 字体环境复核排版。
压缩包是作者编辑材料；包内工作说明不是要提交的论文附件。投稿时遵循正式入口生成的 PDF 和会议要求。
