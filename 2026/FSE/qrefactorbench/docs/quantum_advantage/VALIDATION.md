# 文档验证记录

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
