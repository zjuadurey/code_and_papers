# 两个 WHERE 母案例：边界审阅与 A/B/C 设计

**DRAFT / AI-ASSISTED PROPOSAL — NOT GROUND TRUTH。没有运行模型实验。**

本轮依据研究者“打磨！”及“每个母案例设置三个实验条件很有道理”，将两个
已有程序整理成可审阅的定位任务。不扩充案例、不改变源程序、公示合同、标签、
schema 或 evaluator；原 [来源包](../../source_adaptations/v0.2-where/README.md) 保持不变。
接受三个条件的方向不等于接受具体提示位置、评分标准或批准实验执行。

| 母案例 | 建议先看的实际区别 | 定位审阅重点 |
|---|---|---|
| [lit-003 议程安排](LIT003_REVIEW.md) | 快速预览失败，完整求解成功；替换预览后最终安排不变但状态改变 | 递归搜索与谓词/回退状态，参与者关系来源，保留现有安排的分支 |
| [lit-004 兼容组合](LIT004_REVIEW.md) | 预览是 legacy，完整方案是 a,b,c；最大组合不能直接充当预览 | 内联枚举与跨文件谓词，最新记录、启用过滤、索引解码与并列规则 |

## 已完成的打磨

1. 每例都有“核心区域—必要依赖—外围义务”，以及较窄/较宽候选的审阅条件。
   **这是候选答案提案，不是唯一 gold span。**
2. [13 个经典执行记录](prepared/evidence/)保存输入、完整输出、指定函数绑定的调用
   次数和受控错误替换产生的字段差异。只是软件行为证据，不是模型错误或量子证明。
3. [六份待审阅输入](prepared/inputs/)：每个母案例 A 核心、B 全程序＋位置提示、
   C 同一全程序无提示。B 删除末尾 `LOCATION CUE` 后与 C 字节相同。
4. 复用现有 prediction schema、两个 DRAFT contract 和候选字段。边界说明存入
   `rationale` 后供人审，不新建评分系统、不凭关键词自动判分。
5. [实验设计](PROTOCOL.md)区分定位发现、边界理解和条件 HOW，明确比较限制、
   控制缺口与运行前必须完成的人审。

## 先审这三件事

- 两个工作流的预览、保留/检查分支和输出义务是否是有意义的功能需求？
- 对完整程序，下面“核心＋依赖”的两种边界表述是否均应允许？提示区域是否合理？
- 人审记录能否稳定地区分：没找到候选、找到了但漏依赖、知道边界但 HOW 不充分？

表述中允许科学不确定性。暂不决定 IoU 阈值、综合权重、通过分数、负例金标或
统计显著性。两个案例可以校准协议，不能代表全部正负任务或已经困难的 WHERE。

## 复现已授权的本地准备

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -B pilot/where_review/v0.1/prepare.py --output /tmp/where-review-new
/home/audrey/miniconda3/envs/palqo/bin/python -B -m pytest -q -p no:cacheprovider pilot/where_review/v0.1/test_preparation.py
```

`--output` 必须不存在。脚本没有网络、LLM/QPU 调用或模型执行器；只复制明确白名单、
生成文本并在独立子进程执行已审阅的经典程序。每个条件的模型输入只对应一份 txt，
**不要提供整个目录**：旁边有私有人审材料、提示清单和预期输出。

已有源码本身含算法/功能名称，公共功能说明也可能使定位较容易；归因时保留这个
限制，不通过偷偷改名或删许可声明制造难度。新任务提示 [TASK.md](TASK.md) 是本轮
草案，所有条件共享；不是旧 baseline 的原提示，不能把未来结果混入旧分数。

输入/脚本/schema 哈希在 [manifest](prepared/manifest.json)。检查与保护结果见
[validation.json](validation.json)。边界提示尚未人工确认，模型调用数为零。
