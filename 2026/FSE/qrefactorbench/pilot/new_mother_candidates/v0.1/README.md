# N-058：三个新母问题候选档案

2026-09-27。D-036的A方案已获研究者回复“A”授权。本包完成三份档案，未占满四份上限。
**仅候选准备 / AI_REVIEW_PENDING；不是新增benchmark案例、gold或split。**
候选先按真实来源、不同计算与软件合同选择，未用模型输出筛题；零预测模型/QPU调用。

| 档案ID（不是case ID） | 来源与计算 | 准备建议及关键边界 |
|---|---|---|
| [C01](C01_TEXT.md) | CPython `SequenceMatcher.find_longest_match`：文本连续块匹配 | 建议进入DRAFT来源/合同评审；字符串、无junk且关闭autojunk的条件子域有明确搜索义务，全API未验证 |
| [C02](C02_TSP.md) | python-tsp：闭合旅行商的子集动态规划 | 建议进入DRAFT来源/合同评审；非负整数QUBO有局部证据，完整tie/dtype合同与包环境未解决 |
| [C03](C03_PATHS.md) | NetworkX `all_simple_paths`：惰性简单路径枚举 | 保留为边界候选；单解搜索不能自动替换完整生成器，暂不建议作为已确立正例 |

三者来源库、原代码与业务计算不同，暂列三个母问题组；不是已确证的三个独立统计样本。
与旧十例逐项关系和本轮不单列的选项见[谱系/排除记录](LINEAGE.md)。
没有为了第四份而把同题的另一个算法或新输入当作新母问题。

## 实际交付与复现

- [固定来源清单](sources/manifest.json)：三个仓库的10份原始代码/文档/许可证，commit与SHA256齐全。
- [复现脚本](reproduce.py)：直接加载未改动的difflib与TSP模块；NetworkX安装模块与固定源码逐字节一致。
- [实际结果](validation.json)：文本961整串对＋961区间检查；TSP779矩阵×3缓存设置=2337调用；
  4个小QUBO共1552二进制赋值；路径64有向图、2880多重集比较，以及顺序/重复/异常等定向检查。
- 错误方案对照：忽略junk/autojunk或tie、忘记闭环边、零惩罚、排序/只返回一个路径/去重均有具体见证。
  这些是协调者构造的检查，不是测到的新模型失败，也不是独立测试案例数。
- [参考评审清单](REFERENCE_REVIEW.md)：逐项证据、待决范围、评审角色与信息隔离要求。
- [旧材料保护](protected-before.json)：3555个旧文件内容哈希（含历史pilot、基础设施及两处paper树）。
  检查不覆盖旧文档的新状态更新，也不声称全文件系统完整性；排除缓存和Git元数据。

从项目根目录运行已有环境，无安装：

```bash
/home/audrey/miniconda3/envs/palqo/bin/python pilot/new_mother_candidates/v0.1/reproduce.py --check
/home/audrey/miniconda3/envs/palqo/bin/python pilot/new_mother_candidates/v0.1/audit_package.py --check
```

`--check`仅核对来源/旧文件并精确重放结果，不覆写结果。首次生成命令不带`--check`，遇不同旧结果拒绝覆盖。
第二条命令核对[本包文件哈希](artifact-manifest.json)与[文档链接审计](audit.json)；二者不自包含哈希。
下载脚本只从commit固定的公开URL取证，不是运行所需；默认复现无需网络。
环境为Python3.10.21、NumPy1.26.4、NetworkX3.4.2；这里只加载CPython3.10.14的difflib模块，
没有复现完整CPython3.10.14运行时。TSP来源tag与包内版本/NumPy要求存在差异，详见C02，未安装修补。

## 本次学习点与停止边界

一个工具增强工作流至少需要分清三样东西：给模型的程序、模型应保留的合同、判断回答的依据。
先把合同和局部检查做成可审核材料，可以避免工具只把回答改得更像答案，却改变了任务。
本轮产出的是未来评测的候选依据；没有证明agent变强、完整量子迁移正确或有实际收益。

本工作包已完成。下一步先由研究者/实际参考评审者确定纳入范围、合同与评测角色，再准备正式案例
及后续冻结协议；不得直接把本包的AI映射提案当gold或自动启动模型试题。公开来源可能已在预训练中，
新母问题、新源码版本和未调用预测模型都不等于无污染保留集。本包也已被协调者阅读和用于本地开发。
