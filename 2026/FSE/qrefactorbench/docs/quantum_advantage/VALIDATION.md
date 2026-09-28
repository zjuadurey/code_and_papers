# 文档验证记录

## 2026-09-28 Mac交接增补

- 新增[Mac交接](../MAC_HANDOFF.md)，同步PROJECT_STATUS、NEXT_ACTIONS、README、ENVIRONMENT、
  本目录README、CHANGELOG和research_log；以下原记录保持历史范围。
- 编辑前后核对229个公式/规模/闭环工作包、实现、测试和schema文件SHA256，全部未变。
- 检查上述8份交接相关文档321个本地链接，全部存在；本验证页新增链接另行确认。
- 核对官方PyPI元数据：QDK1.32.3与pyqir0.12.5提供macOS arm64/x86_64 wheel，
  lqcloud0.5.0要求Python>=3.11,<3.13。实际Mac安装、运行与QPU均未执行。
- 本次仅文档工作，未重复运行测试/模型/资源估算；没有安装、凭据操作、真机任务、提交/推送或跨机器传输。

日期：2026-09-28。范围：[本次分层文档](README.md)、九份既有研究/论文入口文档。

## 实际执行

- 编辑前对 `qrefactorbench/` 与 `paper/` 的3861个普通文件计算SHA256；排除符号链接、
  `.git`、`__pycache__`、`.pytest_cache`、`.venv`。不是整个文件系统的完整性审计。
- 编辑后比较：3852个既有文件哈希不变；仅下列九份既有文档发生预期变化。
  新增内容文档五份，另有本验证记录；未改源码/schema/案例/原始结果、LaTeX正文/文献库或旧草稿。
- 首轮检查九份既有文档和五份新增内容文档的340个本地链接路径，全部存在；
  当时尚未写入的本验证页链接单独留到末轮检查。外部URL不计入本地路径数。
- 末轮全部343个本地链接路径、新增D-037锚点、六份新Markdown文件的末尾换行/行尾空白检查通过；
  再次确认3852个既有受保护文件哈希不变。
- `git -C qrefactorbench diff --check -- docs/RESEARCH_CHARTER.md DECISIONS.md PROJECT_STATUS.md NEXT_ACTIONS.md CHANGELOG.md docs/research_log.md`
  与 `git -C paper diff --check` 均退出0。
- 人工核对：已接受目标与待定协议分离；来源阅读深度明确；资源/严格成功实现与文档描述一致；
  论文正文未宣称新增结果。新文档中的E1–E5仅为工作分类，不改正式指标。

九份预期更新：研究项目的 `docs/RESEARCH_CHARTER.md`、`DECISIONS.md`、`PROJECT_STATUS.md`、
`NEXT_ACTIONS.md`、`CHANGELOG.md`、`docs/research_log.md`；论文的 `HANDOFF.md`、`README.md`、
`notes/EVIDENCE_MAP.md`。

哈希比较通过本机Python标准库 `pathlib/hashlib/json` 完成；编辑前清单暂存于
`/tmp/fse-advantage-docs-before-20260928.json`，属于本次操作记录，不是长期发布manifest。
链接检查用 `re` 提取Markdown目标并相对所在文件解析；末轮还核对新增D-037锚点和新增文档空白。
不把路径存在检查称为外链健康、全文语义或Markdown渲染验证。

## 未执行与限制

没有运行单元测试、历史实验、模型推理、QPU任务或LaTeX编译；没有安装、提交、推送或发布。
三篇来源仅核对官方摘要和元数据，没有全文复现或硬件参数验收。
本次新增的是研究记录和后续证据要求，不是量子优势实验或已实现收益判定器。

## N-062 / D-041资源条件方向记录验证（2026-09-28）

以上为D-037历史验证。本次新增RESOURCE_CONDITIONS.md并同步README、PROGRESSION、
SOURCES、研究charter/决策/状态/队列/TODO/日志；没有修改N-061已归档包。

- 编辑前清单：`/tmp/fse-resource-conditions-before-givowzxb.json`，覆盖cases、schemas、
  实现、tests、pilot、artifacts、研究历史paper、当前paper及docs/frontier的3705普通文件；
  排除符号链接和缓存，不是整个文件系统审计。编辑后3705个SHA256全部不变。
- 检查11份新/改内容文档的403个相对文件链接，全部存在；核对D-041标题存在及新增锚点拼写。
  外部网页与其他历史锚点不属于此链接路径检查；用户给定Microsoft介绍页正文已另外读取。
- 本轮内容文档的末尾换行、行尾空白检查通过；相关Git diff --check退出0。
- 本验证附录写入后再检查自身空白及相关Git diff；未重跑代码测试、模型、QPU或论文编译。

人工核对：用户已认可方向与尚未实现能力分开；资源条件与单一qubit阈值分开；
条件预测与真机实测分开；最新实现仍为N-061。本次没有新优势结果或新实验授权。
