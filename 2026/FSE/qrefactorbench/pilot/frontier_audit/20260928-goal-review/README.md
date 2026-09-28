# N-060：保持完整目标的调研补充与交付

当前结论：[docs/frontier/v2](../../../docs/frontier/v2/README.md)。
本轮在N-059证据之上补充源码自动卸载和真实软件迁移路线，并落实用户“不放弃idea”的纠正。
N-059文档/归档原字节保留，当前研究建议以v2和PROJECT_STATUS为准。

- `protected-before.json`：本轮开始时3653份旧案例、实现、实验、论文及N-059材料的哈希。
- `fetch.py`、`source-manifest.json`：第一批4个获取尝试，Road/Yamato成功，CORK403、QuaST超时。
- `source-manifest-2.json`：5份补充官方/作者来源。下载只读，无安装或上游执行。
- `sources/road.txt`、`sources/yamato.txt`：`pdftotext -layout`生成的阅读文本。
- `validation.json`：旧文件、来源哈希、新文档链接与版本指针检查。
- `completion-audit.json`：按任务要求的证据映射与审读结论，不是科学新颖性认证。
- `artifact-manifest.json`：本轮新产物与v2报告的字节清单，不覆盖N-059manifest。

核查命令（工作区根目录，现有环境）：

```sh
/home/audrey/miniconda3/envs/palqo/bin/python qrefactorbench/pilot/frontier_audit/20260928-goal-review/verify.py
```

本次不修改代码、正式案例、旧实验或论文正文；未执行模型/QPU、安装、提交、推送或发布。
保存原始论文供本地阅读，不表示已获得整包公开再分发许可。
