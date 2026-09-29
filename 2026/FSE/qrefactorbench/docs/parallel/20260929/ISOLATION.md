# 三窗口隔离运行与固定版本交接

2026-09-29建立。原FSE作为集成来源保留；三个窗口使用独立worktree，研究任务尚未启动。
原仓库Git根目录是`/home/audrey/code_and_papers`，其`.git`在本轮可写范围外。
因此在FSE内创建无硬链接的本地bare副本，移除其origin，再从副本创建三个分支/worktree。
未改原仓库索引/分支/提交，未创建新提交、合并或推送；不是重新初始化FSE研究项目。

## Agent内部执行目录（用户无需切换）

用户在原FSE开始所有对话；下表供Agent执行任务时使用，不是用户的启动步骤。
以`/home/audrey/code_and_papers/2026/FSE`为原FSE：

| 窗口 | Agent每次命令指定的工作目录 | 独立分支 |
|---|---|---|
| A | `/home/audrey/code_and_papers/2026/FSE/.parallel/20260929/A/2026/FSE` | `parallel/A` |
| B | `/home/audrey/code_and_papers/2026/FSE/.parallel/20260929/B/2026/FSE` | `parallel/B` |
| C | `/home/audrey/code_and_papers/2026/FSE/.parallel/20260929/C/2026/FSE` | `parallel/C` |

Agent读取窗口根目录`WINDOW.md`和本地AGENTS确定角色；用户用自然语言指定任务即可。
A负责文献/案例，B负责代码开发，C负责实验设计/论文；按固定起点独立交付后再集成。
每次执行明确设置工具的workdir，编辑使用对应绝对路径；一次shell的cd不视为后续调用已切换。
不能在原FSE共享源码上运行任务后仅声称属于A/B/C，也不要求用户更换对话目录。
本次是入口文档约定，不是CLI自动切换或自动分配窗口的功能；原FSE入口优先于旧启动文字。
三个worktree共享副本的Git对象库，但源文件各有独立副本；没有开发目录软链接或硬链接。

起点为源HEAD `0815b2f3f888f11c66c7bc28eff1dfa612b9b646`，仅稀疏检出FSE路径。
另将当前FSE中的研究目录、根入口和根pilot资料复制进各窗口，包括未提交/未跟踪工作。
**论文仅保留原FSE的paper入口，沿用用户的Overleaf Git流程。**
最初建立的论文worktree、bare副本及A/B/C论文阅读副本已撤掉；删除前核对28个论文文件均与原目录一致。
代码窗口的入口直接链接原paper，不创建同名软链接或镜像。C提供论文内容，A/B只提供资料。
原paper的文件、Git配置、索引和提交保持不变；本次未连接或同步Overleaf。
Git元数据、认证目录、环境和派生缓存不复制；完整选择/排除及哈希记录在
原FSE的`.parallel/20260929/bootstrap-manifest.json`。`HEAD`相同不代表工作文件等于HEAD，必须同时引用快照哈希。

`.parallel/`已在原FSE的`.gitignore`中排除，避免递归纳入研究仓库。
它是本机运行区，不会随普通git pull传到另一台机器；跨机器接续需显式迁移或重建并核对manifest。

## 开发检查与环境

在各自FSE目录执行：

```bash
bash qrefactorbench/scripts/parallel_run.sh -- python -B -c 'import qrefactorbench; print(qrefactorbench.__file__)'
```

launcher读取本窗口`window-env.sh`，使用已安装palqo Python，强制本地代码优先，检查
`qrefactorbench`和`schemas`确实从所选代码目录导入。不要使用指向原目录的editable安装/CLI入口，
不要把其他窗口活动目录放入PYTHONPATH或sys.path。外部脚本的绝对路径依赖也须在运行协议中核对。
当前只验证已有环境和本项目入口导入，不声称所有历史脚本都已适配；历史runner不应自动重跑。

每次运行有独立`FSE_RUN_DIR`、TMPDIR和缓存，保存`environment.json`；默认BLAS/OpenMP各1线程。
自定义结果文件写入`FSE_RUN_DIR`，或任务自有的新版本输出目录，不能写入输入快照。
共享Conda环境只读使用，不执行pip/conda更新。需要不同依赖时先按既有安装授权规则处理独立环境。
Python进程内部需要启动子进程时使用`sys.executable`并继承本窗口环境。

## 正式实验先冻结代码

即使worktree独立，也不能一边跑一批实验一边修改它读取的源码。先冻结完整代码及已接收的依赖：

```bash
source ./window-env.sh
"$FSE_PYTHON" -B qrefactorbench/scripts/parallel_snapshot.py create qrefactorbench "$FSE_RUNTIME/snapshots/run-001"
bash qrefactorbench/scripts/parallel_run.sh --snapshot "$FSE_RUNTIME/snapshots/run-001" -- python -B -c 'import qrefactorbench; print(qrefactorbench.__file__)'
```

上面是导入演示，不启动模型。真实命令替换`--`后面的部分，必须使用快照内相对脚本路径，
不要传回worktree活动脚本的绝对路径。运行记录保存代码目录、Python/依赖版本及manifest SHA256。
输入数据和私有参考也须固定版本；不在代码树内的输入快照哈希写入实际实验协议。
协议绑定的manifest哈希须与运行记录一致，`verify`检查文件内容/集合和执行位，不能代替协议绑定。

快照为普通文件复制：无软/硬链接，拒绝逃逸链接和同名覆盖，复制前后核对源文件，默认只读。
可以继续修改worktree准备下一轮；正在运行的进程只读取旧快照。升级依赖或输入另建新版本。
只读权限防止意外修改，不是对同一Unix账户的安全沙箱；任何窗口仍不得主动改他人目录或chmod旧快照。

## 跨窗口交接

例如A发布其任务目录的v1（先实际完成该目录及验证）：

```bash
source ./window-env.sh
"$FSE_PYTHON" -B qrefactorbench/scripts/parallel_snapshot.py create qrefactorbench/pilot/parallel-20260929/cases "$FSE_HANDOFFS/A/cases-v1"
```

B接收时，核对A交接中声明的manifest SHA256，验证发布包，再建立自己的副本：

```bash
source ./window-env.sh
"$FSE_PYTHON" -B qrefactorbench/scripts/parallel_snapshot.py verify "$FSE_HANDOFFS/A/cases-v1"
"$FSE_PYTHON" -B qrefactorbench/scripts/parallel_snapshot.py create "$FSE_HANDOFFS/A/cases-v1/files" "$FSE_IMPORTS/A-cases-v1"
```

`FSE_IMPORTS`在接收者自己的qrefactorbench目录中，后续完整代码快照会包含它。
二次复制生成自己的manifest，记录生产者manifest哈希和自身manifest哈希；文件内容哈希应相同。
消费者只读取自己的副本。A发布v2不会自动影响B；B明确接收并验证后，才在下一批实验使用。
代码补丁也先以固定版本交付、由接收者审查应用和测试，不自动同步活动文件。

## 运行锁和集成

仅B用`parallel_run.sh --snapshot ... --model-lock -- COMMAND ...`启动模型实验。
同机重CPU/内存工作使用`--compute-lock`；锁忙时立即返回，不启动第二个任务。
需要两类锁时可同时提供。锁、缓存和运行记录在`.parallel/20260929/`下独立存放。
锁是本机协作约定，绕过launcher或跨机器执行不受它管理；QPU/新付费渠道授权不因锁存在而改变。

A更新文献/案例包，B维护实现及集成状态，C维护实验协议并按原paper/Overleaf Git流程处理论文。
需要将最终产物回写原FSE时，先核对基线manifest与原目录新增改动，审查重叠文件，再按版本集成。
论文没有跨worktree回写步骤；编辑前单独检查原paper状态，不能用研究仓库的diff代替。代码三方验证后再做集成，
不自动合并/提交/推送，也不把三份HEAD相同当成没有文件冲突的证明。

本次实际验收见[ISOLATION_VALIDATION.json](ISOLATION_VALIDATION.json)。
