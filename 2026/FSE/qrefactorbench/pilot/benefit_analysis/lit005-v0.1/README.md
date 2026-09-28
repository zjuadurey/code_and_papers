# N-061：首份行为合同与端到端成本分析

入口：[报告](REPORT.md)、[验证](VALIDATION.md)、[原始结果](results.json)、
[事前诊断范围](protocol.json)、[输入hash](input-binding.json)。

分析现有lit-005 v0.1.1；保留first/absence义务，实际构造CNF相位oracle和经典诊断，
证明特定“量子提议＋经典前缀枚举修复”架构没有加速区间；其他方案与实际硬件收益保持未知。
完整系统目标不变，合同与成本是决策依据。此包是开发暴露的协调者分析，不计Agent成绩。

在本目录、既有palqo环境执行（输出文件必须不存在）：

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -B -m pytest -q -p no:cacheprovider test_analysis.py
/home/audrey/miniconda3/envs/palqo/bin/python -B check_wrapper.py
/home/audrey/miniconda3/envs/palqo/bin/python -B run.py --output /tmp/lit005-new-replay.json
```

不可重写results/replay；要扩展协议使用新版本。来源见[SOURCES.md](SOURCES.md)，
五份PDF已下载，fetch_sources.py仅保存公开来源，既有manifest存在时拒绝覆盖。
