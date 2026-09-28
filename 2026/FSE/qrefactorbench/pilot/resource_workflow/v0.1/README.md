# N-063资源工具实际联调

2026-09-28。当前[工具说明](../../../docs/quantum_advantage/RESOURCE_WORKFLOW.md)。
这是软件工程验证，不是模型增强实验或量子优势证据。

- [smoke-result.json](smoke-result.json)：真实QDK1.32.3调用；两qubit电路、假设硬件模型。
  输出177物理qubit、9000 ns和估计错误上界0.000791000035；成本/行为证据未知，
  工作流正确输出insufficient_evidence，不给出采用建议。
- [execution.json](execution.json)：实际命令、Python/依赖版本、平台和输入hash。
- [smoke-stderr.txt](smoke-stderr.txt)：原始标准错误，首次归档为空。
- [validation.json](validation.json)：测试、旧artifact完整性和本地链接核验。
- manifest.json保存本包及本次实现/测试/示例/接口文档hash，标明各路径基准。

实际运行：

```bash
/home/audrey/miniconda3/envs/palqo/bin/python -B -m pytest -q -p no:cacheprovider tests/test_resource_workflow.py
# 30 passed，包含真实SDK与无site-packages时缺依赖回传
/home/audrey/miniconda3/envs/palqo/bin/python -B -m pytest -q -p no:cacheprovider
# 253 passed，15 skipped：14项Qiskit、1项YAML可选依赖缺失
```

此前41项聚焦回归通过；添加真实SDK检查后执行上述30专项与全套。
本轮最初各Conda环境均未见QDK；后续既有palqo环境已出现QDK1.32.3，直接复用。
助手没有执行安装命令；先前安装确认已撤回需要，无法确定其他环境变更来源。
遥测关闭，没有账号认证、云任务、QPU、模型推理、benchmark分数或论文变化。
输入为工程电路，不将此数值套用lit-005或任何实际迁移程序。
