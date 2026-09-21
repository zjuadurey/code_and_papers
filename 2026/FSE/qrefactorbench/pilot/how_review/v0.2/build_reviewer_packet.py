"""Create a fresh allowlisted reference-review packet without model judgments."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
CHECKLISTS = {
 'lit-001': ['聚合重复/反向权重；区分 conflict 与 separated。', '全局最小冲突，window0 的最小 numeric mask；current/movement 不是目标。', '空设备、零权重、输入序、冲突序和完整 changes。'],
 'lit-002': ['每条连接至少一个选中端点；全局最少站点。', '同基数按已选位置 tuple 字典序；不要默认为 numeric mask。', 'current 可不覆盖；earliest owner、空 checklist、reassignment 和整体验证。'],
 'lit-003': ['每 session 一个 slot，参与者冲突禁止同 slot；不额外加入容量。', '最小 slot 向量字典序；失败预览/部分 current 不固定解。', 'complete 的激活路径、精确无解、空 sessions/slots、moves 与原返回/异常。'],
 'lit-004': ['latest check 和 eligibility 定义兼容矩阵；failed/unverified 都不可选为兼容对。', '最大基数后最小 numeric mask；current 不提供偏好。', 'inspect/preview 保留；select 触发、解码 best、名字序及 add/remove。'],
 'lit-005': ['锁定等式与每条恰三文字规则；重复/矛盾文字合法。', 'False-before-True 首解；空规则集与非法空单条规则区别。', '先验证；current 合格则保留；无解 None；failed/locked/changes 顺序。'],
 'lit-006': ['正整数 weight、非负 value/capacity，DP 的最大 value 目标。', '并列最优取最小 numeric mask；容量等式/slack 条件若提出需核对。', 'active 过滤、每窗口独立、select 激活、空输入/零容量/零价值和 transfer offset。'],
 'lit-007': ['完整唯一 together/apart 偏好；signed score 正负号及常数。', '全局最大 score 后最小 numeric mask；无容量/平衡限制。', 'propose 激活、False/True 组序、violated pairs 序、gain/moves 和空组。'],
 'lit-008': ['给定字节 XOR、固定八位表示；全量有序回执，而非选一个记录。', 'prefix checksum 状态、counts 的 repetitions 是确定计数字段。', '验证先行、非 bool 整数/边界、全量输出；提名后可拒绝，勿凭家族名作普遍排除。'],
 'lit-009': ['区分完整 solve 与可提名子区域；候选依赖当前 rows/col。', '最大绝对值 pivot 首索引 tie；浮点中间状态与精确零异常。', 'solve/inspect、无输入修改、残差先行、后续算术序/overflow/deltas；不私自放宽精确性。'],
 'lit-010': ['按预算运行给定 recurrence，不是返回任意精确解。', 'x/r/p 状态、停止条件、逐步 trace 与最终直接 residual 的区别。', 'advance/inspect、空/零初残差/零预算、归一化/重复/对称性/对角占优和异常序。'],
}
GUIDE = '''# 合同义务参考评审包

用途：在不看模型回答、协调者编码或私有标签的前提下，依据原公开程序建立参考义务。
这是给人类评审者的准备包，不是模型输入包，不要求现在调用任何模型或服务。

每例原公开 C 输入见 inputs/；软件合同原文及关注点见 obligations.json。
关注点是协调者编制的检查提纲，不是经过独立认可的答案或结构标签，允许修正/拒绝。
先读合同和源码，在 blank_reviews.json 中自行填写证据、可接受替代路线及未知项。
研究者身份和所有判断目前均为空。请先独立记录，再讨论分歧；不可填虚构第二评审者。

采用条件计划任务，分别看主张正确性和义务完成度；不要求模型已经提交可执行实现。
关注核心对应、编码条件、原合同、候选依赖。具体公式被反例否定，与明确未解决义务
分开记录。允许多种家族/边界；不存在性和任意输入正确性均需要相应论证。
支持/反驳必须写清命题及适用域；不能从缺乏收益证据推出结构不可行。

此包只用于先建立参考。后续匿名回答评审需另行准备；本次没有提供模型回答，
也没有声称已开展盲审。已看过协调者结论者应注明此前接触，不能冒充未暴露评审者。
MANIFEST.json 列出允许的全部载荷文件及哈希。除此之外不要引入项目私有资料。
'''


def build(destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    (destination/'inputs').mkdir()
    obligations, blank = [], []
    for case, checklist in CHECKLISTS.items():
        source = ROOT/'pilot/reference_completion/v0.1.1/review_inputs'/f'{case}-C.txt'
        data = source.read_bytes()
        text = data.decode()
        task, _ = json.JSONDecoder().raw_decode(text.split('PUBLIC TASK', 1)[1].lstrip())
        relative = f'inputs/{case}-C.txt'
        (destination/relative).write_bytes(data)
        sha = hashlib.sha256(data).hexdigest()
        obligations.append({'mother_case': case, 'input': relative, 'input_sha256': sha,
                            'software_contract_verbatim': task['software_contract'],
                            'coordinator_checklist_pending_review': checklist})
        blank.append({'mother_case': case, 'input_sha256': sha, 'reviewer': None,
                      'prior_exposure': None, 'candidate_and_scope_evidence': None,
                      'mapping_and_encoding_evidence': None, 'contract_obligations': None,
                      'admissible_alternatives': None, 'unresolved': None, 'review_status': 'UNFILLED'})
    (destination/'GUIDE.md').write_text(GUIDE)
    (destination/'obligations.json').write_text(json.dumps(obligations, ensure_ascii=False, indent=2)+'\n')
    (destination/'blank_reviews.json').write_text(json.dumps(blank, ensure_ascii=False, indent=2)+'\n')
    manifest = {str(p.relative_to(destination)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(destination.rglob('*')) if p.is_file()}
    (destination/'MANIFEST.json').write_text(json.dumps({'purpose': 'REFERENCE_REVIEW_PREPARATION_ONLY',
        'human_reviews_completed': 0, 'payload_files': manifest}, indent=2)+'\n')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: build_reviewer_packet.py NEW_DIRECTORY')
    build(Path(sys.argv[1]))
