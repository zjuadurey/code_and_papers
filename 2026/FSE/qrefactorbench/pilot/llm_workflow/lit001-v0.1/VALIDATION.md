# 实际验证 — 2026-09-28

- 新 workflow 专项 14 项通过；同时运行原资源工具 30 项回归，共 **44 passed**。
- 专项包含所有 64 种四节点无向图（确定的非均匀正权），逐图核对 16 种测量输出、空样本、
  原程序结果和强经典对照；另检查输入错误、空图、QASM 范围、禁用表达式和结论绑定。
- 首次 pytest collection 因参数名 `request` 是保留名失败；改为 `payload` 后通过。
  这发生在模型调用之前，没有删除模型失败或重抽模型输出。
- `run.py --output pilot/llm_workflow/lit001-v0.1/run-20260928-01` 实际退出 0。
  模型调用 4 次，四次 exit 0 / JSON object；零控制器传输重试、零候选修订、零人工响应修复。
  运行前预检验证实际序列化模型为 gpt-5.6-sol / medium、原生 tools 为空、私有目录不可见。
- 模型生成电路实际执行 64 shots，返回准确维护窗口；未使用回退。21 种测量/异常样本检查通过。
  两个硬件假设点均由 QDK 1.32.3 实际计算，完整成本项均非空。
- 运行后核对协议绑定的源码和输入 hash 未变。原始模型响应、工具输出和 manifest 保留。
- `replay.py` 实际重放退出 0；[重放记录](replay-20260928-01/replay.json)：
  行为通过、模拟结果完全一致、QDK 原始资源估算完全一致；主机时间重新测量，没有要求相同。
- 原 lit-001 case、正式 gold、指标、已有资源工具及历史模型运行未修改。
  本次新增局部 workflow、文档入口和当前状态补充；没有安装依赖、QPU、提交或发布。

验证命令（项目根目录）：

```bash
PYTHONDONTWRITEBYTECODE=1 python -B -m pytest -q -p no:cacheprovider \
  pilot/llm_workflow/lit001-v0.1/test_workflow.py tests/test_resource_workflow.py
```

此次运行证明这个给定实例的 LLM/工具闭环实际完成。协议指定 QAOA 家族和可信恢复工具，
不声称已经验证自主家族发现、模型错误修复效果或跨案例泛化。最终自然语言是模型原文，
机器验收检查动作顺序、hash、工具结果和采用结论方向，不是对每句话的自动形式证明。
