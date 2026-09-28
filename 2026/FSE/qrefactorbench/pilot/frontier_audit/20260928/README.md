# N-059：2026-09-28前沿核查归档

入口：[研究结论](../../../docs/frontier/README.md)、[来源核查](../../../docs/frontier/EVIDENCE.md)、
[下一步诊断](../../../docs/frontier/NEXT_STUDY.md)。响应用户“做”，未执行任何上游程序。

本目录不是模型可见输入。包含公开原始文件及研究者阅读材料；保留来源版权/许可，
本地阅读存档不表示已获整包再分发许可。

## 文件说明

- `sources.json`及`fetch.py`：第一批25份公开证据的URL与下载脚本。
- `source-manifest.json`、`source-manifest-2.json`至`source-manifest-5.json`：
  分批追加的来源/哈希；失败行保留错误，不能算成功归档。
- `fetch_additional.py`：第三批7个下载尝试（含1个403），已完成；拒绝覆盖既有manifest。
- `*-tree.json`：公开GitHub树与固定commit；代码树获取不等于完整克隆或代码复现。
- `qpipe-*-record.json`、`qpipe-zip-index.json`、`qpipe-selected-members.json`：
  Zenodo元数据、工具包成员清单与6份选择性解包文件；未下载约105 MB实验数据包。
- `sources/*.txt`：本地PDF/HTML文本转换，用于阅读，不是作者额外产物。
- `protected-before.json`：修改前3580份既有案例/代码/测试/实验/论文文件哈希。
- `validation.json`、`artifact-manifest.json`：交付时的完整性核验；不验证论文科学结论。

主代码版本：C2Q `42e9cb642d4300662274c859e96f131a26d0a714`；
Predict `4b4490a6abfdebfe8a8801becad343dd733fa326`；
PQID `f4bafb4ce96569dbffe82c2e44f142a81e4ee27e`。
QPipe按下载zip字节哈希固定，未声称Git版本或实验zip复现。

获取限制：QuaST GitLab API超时/网页不可达，QUASAR候选GitHub API404，
旧Quantum Offloading机构PDF403。后两项本地分别有access记录/manifest错误；
QuaST失败仅保留本说明及会话调用记录，成功取得论文HTML。

本次只下载、静态阅读、文档同步、文件哈希和链接检查；模型/QPU调用0次，
没有依赖安装、性能实验、标签/评分变更、论文编辑或Git提交。
