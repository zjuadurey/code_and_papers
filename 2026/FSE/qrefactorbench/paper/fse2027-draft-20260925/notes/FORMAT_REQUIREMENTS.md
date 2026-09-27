# FSE 2027 格式核验

核验日期：2026-09-25。
一手来源：[FSE 2027 Research Papers CFP](https://conf.researchr.org/track/fse-2027/fse-2027-papers)。

| 要求 | 本稿处理 |
|---|---|
| 首次投稿正文及图表最多 18 页，参考文献最多 4 页 | 保留标准排版；最终字体环境需再次验收 |
| major revision 正文上限 20 页 | 不把修订上限当首次投稿上限 |
| acmsmall 单栏；建议 screen/review/anonymous | `\documentclass[acmsmall,screen,review,anonymous]{acmart}` |
| numeric 或 author-year 引用均可 | 使用 ACM-Reference-Format 数字引用 |
| 双匿名 | 匿名作者，无身份、机构、致谢或个人仓库链接 |
| Conclusion 后有 Data Availability，该节不计页数 | 独立成页以清晰检查；公开/匿名存储尚未建立，如实说明 |
| replication package 提供位置或解释，说明接受后发布意向 | 本稿未伪造 artifact URL；发布意向待作者补充 |
| 研究过程使用 AI 需在方法中详细交代 | 说明研究中的 AI 角色；最终版本需补具体版本与监督记录 |
| 可核验文献 | 13 条有真实一手来源的参考记录，不填猜测 DOI/venue |

官网链接的 `acmart-primary.zip` 和 ACM 模板页在本次网页工具访问中返回 403。
本机已存在官方 `acmart` v2.16 (2025-08-27)，据官网明确的 class 选项编写；不声称本机模板是最新发行版。
未修改官方类文件；完整 ACM 字体依赖在本机缺失。不要将替代字体预览的页数当成正式排版的确证。

Data Availability 单独分页仅用于当前草稿核验，不缩减正文计数。
没有利用附录绕过正文页数上限。扩展实验说明为独立工作笔记，不作为被省略的论文方法依据。
