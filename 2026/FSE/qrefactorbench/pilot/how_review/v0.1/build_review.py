"""Bind manual AI review codings to frozen responses; NOT an automatic grader."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODELS = {
    'gpt-5.6-sol': '20260922-c-v0.1',
    'gpt-6-astra': '20260922-c-v0.1',
    'deepseek-v4-pro': '20260922-deepseek-c-v0.1',
    'deepseek-flash': '20260922-deepseek-c-v0.1',
}
FOCUS = {'lit-002', 'lit-003', 'lit-004', 'lit-006', 'lit-009'}

# Each tuple is an explicitly authored judgment, not inferred from word matches.
# M = core correspondence; E = encoding conditions; C = contract; W = scope.
MANUAL = {
 ('gpt-5.6-sol', 'lit-002'): [
  ('M', 'supported', '选站变量、覆盖约束与最小基数对应原核。'),
  ('E', 'supported', 'A 与 P 的充分界成立；审核者实例化后有限枚举通过。'),
  ('C', 'supported', '反向未选位权在固定基数下给出所需 tuple 顺序；只支持目标函数，非量子/报告实现。'),
  ('W', 'supported', '完整原核；验证、当前方案和报告保留经典，范围解释对应源码。')],
 ('gpt-6-astra', 'lit-002'): [
  ('M', 'supported', '核心覆盖与最小基数映射成立。'),
  ('E', 'supported', 'A=n+1 保证基数最优；有限枚举包含全部并列最优。'),
  ('C', 'unresolved', '明确声明能量不编码 tie；提出经典 canonicalization 义务，不能当错误 tie 公式。'),
  ('W', 'supported', '完整原核和经典报告边界有明确依赖解释。')],
 ('deepseek-v4-pro', 'lit-002'): [
  ('M', 'supported', '变量及覆盖/基数核心对应；不包含其错误的次级排序主张。'),
  ('E', 'unresolved', 'P 仅要求支配目标；C<A/2^n 保住基数但不保证 tuple 顺序。'),
  ('C', 'contradicted', '正 numeric-mask 次级目标选择 (1,2)，合同选择 (0,3)；仅反驳此公式。'),
  ('W', 'supported', '完整核及周边报告义务已说明；回退尚未实现。')],
 ('deepseek-flash', 'lit-002'): [
  ('M', 'supported', '核心覆盖约束和基数目标对应。'),
  ('E', 'unresolved', '承认支配系数及 tie 构造需验证；另一层级方案仍待构造。'),
  ('C', 'contradicted', '加在选择位上的正递减超递增权重方向相反；反例只否定该分支，不否定两阶段替代方案。'),
  ('W', 'supported', '完整核、激活及报告依赖与源码对应。')],
 ('gpt-5.6-sol', 'lit-003'): [
  ('M', 'supported', 'one-hot 图着色是可辩护替代家族；不因偏离 Search 参考而判错。'),
  ('E', 'unresolved', 'one-hot/冲突惩罚及位置权重只给条件，尚无具体充分界。'),
  ('C', 'unresolved', '明确 lex 最优、无解及回退义务；无完整认证实现。'),
  ('W', 'supported', '完整 complete 边界、预览失败触发和不继承部分选择均说明。')],
 ('gpt-6-astra', 'lit-003'): [
  ('M', 'supported', '有限完整赋值域及邻接不等谓词对应图着色。'),
  ('E', 'unresolved', '前缀存在性构造有逻辑依据；可逆实现与精确否定判定尚未完成。'),
  ('C', 'unresolved', '按最小可延伸前缀可保 lex；回答明确负判定须认证，不把没采到当无解。'),
  ('W', 'supported', '完整 complete 及经典验证/预览/报告边界有源码依据。')],
 ('deepseek-v4-pro', 'lit-003'): [
  ('M', 'supported', '具体公式是每 session 一个 slot，加冲突约束；按公式审，不用另一处含糊概述替代。'),
  ('E', 'unresolved', '位置权重排序成立；lambda/mu 的充分界明确未解决。'),
  ('C', 'unresolved', '可行态 lex 顺序有有限检查；全局 ground state、无解和回退实现仍需证据。'),
  ('W', 'supported', '完整函数、complete 激活与失败报告均说明。')],
 ('deepseek-flash', 'lit-003'): [
  ('M', 'supported', 'one-hot 与冲突约束对应；允许同 slot 的不冲突 sessions。'),
  ('E', 'unresolved', 'B>=k 的可行态 lex 权重有依据；约束惩罚充分界未给出。'),
  ('C', 'unresolved', '区分无解与采样失败，认证未完成；排序检查不等于完整 QUBO 检查。'),
  ('W', 'unresolved', '28–56 未含 return 57；可能保留经典返回，需明确替换接口，不能按一行差异定错。')],
 ('gpt-5.6-sol', 'lit-004'): [
  ('M', 'supported', '最大兼容子集与最小 numeric mask 对应。'),
  ('E', 'unresolved', '两阶段思路有效，单阶段支配界明确留待推导。'),
  ('C', 'unresolved', '目标层级说明正确；精确最优认证未实现。'),
  ('W', 'supported', '25–29 保留后续解码，解释了 best 到报告的接口；不同锚点可辩护。')],
 ('gpt-6-astra', 'lit-004'): [
  ('M', 'supported', '选位与不兼容对对应。'),
  ('E', 'supported', 'B=2^n,A=nB+1 的可行性及目标支配证明成立，有限核对通过。'),
  ('C', 'supported', '仅能量全局最小的 cardinality/mask 合同成立；认证及量子执行仍是义务。'),
  ('W', 'supported', '25–29 保留解码/报告，接口已说明；非唯一合法坐标。')],
 ('deepseek-v4-pro', 'lit-004'): [
  ('M', 'supported', '最大团/非边惩罚和 mask 目标对应。'),
  ('E', 'supported', 'P>A 可通过删除冲突顶点说明；正 epsilon 的实例支配条件及有限检查见证据。'),
  ('C', 'supported', '仅所述充分 epsilon 条件下的 ground-state 顺序；量子认证尚未实现。'),
  ('W', 'supported', '24–30 包含触发与解码，较大边界本身不构成错误。')],
 ('deepseek-flash', 'lit-004'): [
  ('M', 'supported', '选择位、最新兼容矩阵与 cardinality/mask 对应。'),
  ('E', 'supported', '给出的 M/P 充分条件可实例化并通过有限检查。'),
  ('C', 'supported', '支持 ground-state 合同；未提供量子最优保证，回答已说明此义务。'),
  ('W', 'supported', '25–29 核、经典 preview 和报告边界有解释。')],
 ('gpt-5.6-sol', 'lit-006'): [
  ('M', 'supported', '识别 DP 实现后的背包目标/容量/位序。'),
  ('E', 'unresolved', 'slack、惩罚界及精确系数明确留待推导。'),
  ('C', 'unresolved', '明确 value 主、numeric mask 次及回退义务；构造未完成。'),
  ('W', 'supported', 'choose 核与每窗口独立、select 激活、catalogue 顺序对应。')],
 ('gpt-6-astra', 'lit-006'): [
  ('M', 'supported', '变量、容量等式和 value/mask 层级对应。'),
  ('E', 'supported', 'A>B*sum(v) 对非负整数值充分；标准非负二进制 slack 实例化的有限检查通过。'),
  ('C', 'supported', '只支持精确整数 ground-state 返回 mask 的合同，未证明硬件或认证实现。'),
  ('W', 'supported', '原 choose 返回 mask；独立窗口和 select 激活均保留。')],
 ('deepseek-v4-pro', 'lit-006'): [
  ('M', 'supported', '核心背包目标与容量对应；tie 不在写出的标量式里。'),
  ('E', 'unresolved', 'slack/P 未构造；缺全局输入上限不阻止用逐实例 sum(v) 推导，不能用此理由证明不可构造。'),
  ('C', 'unresolved', 'tie 依赖与原 DP 完全核对；不是已完成的 tie 编码，也未实现核对流程。'),
  ('W', 'supported', 'choose、过滤和窗口独立义务均说明。')],
 ('deepseek-flash', 'lit-006'): [
  ('M', 'supported', '容量、价值、catalogue 位序的数学核心对应。'),
  ('E', 'unresolved', '回答明确是 sketch，系数和 slack 构造未完成。'),
  ('C', 'unresolved', '明确精确 value/mask 与验证义务；未完成不自动判错。'),
  ('W', 'supported', '独立窗口、select 激活、返回 mask 到报告的接口已说明。')],
 ('gpt-5.6-sol', 'lit-009'): [
  ('M', 'unresolved', '有限有序数列可标记首个最大值；对全部 Python 中间浮点状态的等价性未证明。'),
  ('E', 'unresolved', '需比较所有行的谓词及可逆 binary64 行为未实现，可能消除收益。'),
  ('C', 'unresolved', '提出原 max 验证/回退；未完成浮点、异常和完整程序证明。'),
  ('W', 'supported', 'line 13 子区域依赖当前 rows/col 而非仅原矩阵，触发路径有明确说明。')],
 ('gpt-6-astra', 'lit-009'): [
  ('M', 'supported', '有限列上的 incumbent 改进谓词不需预知最大值；只支持条件子计算，不冻结整题标签。'),
  ('E', 'unresolved', '有限列经典谓词检查通过；可逆访问、精确终止和量子实现仍未完成。'),
  ('C', 'unresolved', '说明非有限中间状态走原实现、不提前拒绝；认证/回退尚未实现。'),
  ('W', 'supported', 'line 13 及可变 rows、col、残差先行和模式触发均说明。')],
 ('deepseek-v4-pro', 'lit-009'): [
  ('M', 'contradicted', '“必须有全局 argmax 谓词或预计算 target”的必要性主张过强；incumbent 谓词提供替代。非整题 NO 判错。'),
  ('E', 'not_applicable', '无条件计划；不凭空要求该 NO 回答给 QUBO 系数。'),
  ('C', 'unresolved', '保留浮点、异常和残差的要求合理，尚不足以否定所有条件子区域映射。'),
  ('W', 'unresolved', '整个 solve 可被提名后拒绝；内部 pivot 需要单独审核，当前记录没有可靠排除它。')],
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    rows = []
    for model, experiment in MODELS.items():
        for number in range(1, 11):
            case = f'lit-{number:03}'
            path = ROOT / 'pilot/model_comparison' / experiment / 'runs' / model / case / 'response.txt'
            raw = path.read_text()
            response = json.loads(raw) if raw.strip() else None
            input_path = ROOT / 'pilot/reference_completion/v0.1.1/review_inputs' / f'{case}-C.txt'
            selected_for_review = case in FOCUS
            item = {'model': model, 'mother_case': case, 'condition': 'C',
                    'response_path': str(path.relative_to(ROOT)), 'response_sha256': digest(path),
                    'input_path': str(input_path.relative_to(ROOT)), 'input_sha256': digest(input_path),
                    'selected_for_trial_review': selected_for_review,
                    'response_status': 'final_json_present' if response else 'budget_exhausted_no_final',
                    'review_status': 'AI_PENDING' if selected_for_review and response else 'NOT_REVIEWED',
                    'human_reviews': [], 'task_pass': None, 'assessments': [], 'excerpts': {}}
            if not response:
                assert model == 'deepseek-flash' and case == 'lit-009'
                metadata = json.loads(path.with_name('metadata.json').read_text())
                assert metadata['finish_reason'] == 'length' and metadata['usage']['completion_tokens'] == 16384
                item['failure_evidence'] = {'metadata_path': str(path.with_name('metadata.json').relative_to(ROOT)),
                                            'metadata_sha256': digest(path.with_name('metadata.json')),
                                            'finish_reason': 'length', 'completion_tokens': 16384}
            elif selected_for_review:
                plan = response.get('plan') or {}
                for field in ('formulation', 'input_encoding', 'output_decoding', 'assumptions', 'risks'):
                    if field in plan:
                        item['excerpts'][f'/plan/{field}'] = plan[field]
                for field in ('candidate_regions', 'rationale', 'structural_eligibility'):
                    item['excerpts'][f'/{field}'] = response[field]
                for dimension, state, reason in MANUAL[(model, case)]:
                    wanted = {'M': ['/plan/formulation', '/rationale'],
                              'E': ['/plan/formulation', '/plan/assumptions'],
                              'C': ['/plan/formulation', '/plan/output_decoding', '/plan/risks'],
                              'W': ['/candidate_regions', '/rationale']}[dimension]
                    pointers = [p for p in wanted if p in item['excerpts']] or ['/rationale']
                    item['assessments'].append({'dimension': dimension, 'evidence_state': state,
                        'reason': reason, 'evidence_kind': 'AI source/formula review; see linked scope and finite checks',
                        'evidence': ['EVIDENCE.md', 'checks.json'],
                        'response_pointers': pointers,
                        'obligation_status': {
                            'supported': 'scoped_argument_supplied',
                            'contradicted': 'supplied_claim_refuted',
                            'unresolved': 'open_obligation_or_interpretation',
                            'not_applicable': 'no_plan_obligation_for_this_response',
                        }[state],
                        'complete_migration_verified': False})
            rows.append(item)
    assert len(MANUAL) == 19
    return {'version': '0.1', 'status': 'PRIVATE_DRAFT_PENDING',
            'reviewer': 'Codex coordinator, AI post-hoc review, not independent/blinded annotation',
            'selection': 'Purposeful five-case calibration; not a random sample or full HOW evaluation',
            'rules': 'RUBRIC.md', 'model_calls': 0, 'human_reviews': [], 'rows': rows}


if __name__ == '__main__':
    print(json.dumps(build(), ensure_ascii=False, indent=2))
