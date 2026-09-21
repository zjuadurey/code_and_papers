"""Bind explicit AI review codings and a separate completion ledger to raw answers."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODELS = ['gpt-5.6-sol', 'gpt-6-astra', 'deepseek-v4-pro', 'deepseek-flash']

# Explicitly authored additional judgments, one scoped record per MECW dimension.
ADDITIONAL = {
 ('gpt-5.6-sol', 'lit-001'): [
  ('supported', '二元 MaxCut 与原非负整数邻接矩阵对应。'),
  ('supported', '-2^n*cut+mask 的支配界成立；有限原核核对通过。'),
  ('supported', '仅 ground-state 的最小 window0 mask 合同有支持；精确认证/完整报告尚未验证。'),
  ('supported', '完整核依赖聚合矩阵，验证/当前评估/报告保留，触发及空输入说明对应源码。')],
 ('gpt-6-astra', 'lit-001'): [
  ('supported', 'C=W-S 的 min-conflict 对应原 MaxCut。'),
  ('supported', '2^n*C+mask 与所写 Ising 常数/符号一致；有限整数核对通过。'),
  ('supported', 'ground-state 目标保 tie，明确认证尚需独立证据。'),
  ('supported', '原核、无 movement 目标、验证与报告依赖完整说明；没有实现迁移。')],
 ('deepseek-v4-pro', 'lit-001'): [
  ('supported', 'x=0 表示 window0 是一致的变量翻转；核心多项式解码后对应。'),
  ('supported', '1-xu-xv+2*xu*xv 等于同窗指示；有限核对通过。'),
  ('unresolved', '所写能量不编码 tie；声明测量后强制最优/tie，但未给认证及 canonicalization 构造。'),
  ('supported', '完整核和调用前验证/当前评估、后续报告边界可辩护。')],
 ('deepseek-flash', 'lit-001'): [
  ('supported', '同窗冲突/异窗 cut 与原核对应；所有位串均可行。'),
  ('supported', 'M>2^n-1 对整数冲突分数足够；Ising 同窗项符号正确。'),
  ('supported', '给出的 scalar 能量保全局 tie；仅对 observed candidates 排序仍不构成完整认证。'),
  ('supported', '完整核、window0 位序和经典报告义务说明对应。')],
 ('gpt-5.6-sol', 'lit-005'): [
  ('supported', '有限 Boolean 向量、locks 和三文字子句谓词对应。'),
  ('unresolved', '提出 certified prefix search，未完成可逆 oracle 或精确否定实现。'),
  ('unresolved', '有序前缀逻辑可保首解；全局无解/负前缀认证明确待解决。'),
  ('supported', '10–14 全核、conforms 依赖、complete 且 current 不合格触发正确。')],
 ('gpt-6-astra', 'lit-005'): [
  ('supported', '给出锁定等式和各三文字析取的合取，核心谓词对应。'),
  ('unresolved', '前缀构造明确，但 oracle 和精确负判定尚无实现。'),
  ('unresolved', '准确区分空规则集、非法空子句和无解；原枚举回退提案尚未验证。'),
  ('supported', '完整核和先验证、保留 current、锁定失败特征序都与源码对应。')],
 ('deepseek-v4-pro', 'lit-005'): [
  ('supported', '域、锁定、三文字规则与 conforms 对应。'),
  ('unresolved', '仅谓词描述与 oracle 假设；less-than wrapper 尚待构造。'),
  ('unresolved', '明确随机 marked state 不满足首解要求；排序/无解认证未完成。'),
  ('supported', '额外提名 conforms 是依赖边界选择；保留 complete 的完整失败/返回接口。')],
 ('deepseek-flash', 'lit-005'): [
  ('supported', '在公开合法域上谓词对应；“Empty clauses are true”措辞需澄清，单个空子句本来非法，不据此计合法域错误。'),
  ('unresolved', '可逆 oracle、shots/confidence 条件没有具体构造或阈值；不能替代精确语义。'),
  ('unresolved', '首解及无解明确未解决；提到 quantum counting 不是完成认证。'),
  ('unresolved', '10–13 不含 return None 14；可以保留经典返回，但替换接口需澄清。')],
 ('gpt-5.6-sol', 'lit-007'): [
  ('supported', '带符号 pair score 的二次展开逐赋值对应原 score。'),
  ('supported', '2^n*S-mask 支配 mask 范围；整数核有限检查通过。'),
  ('supported', '仅精确最优的 numeric tie 由 scalar 目标保证，采样认证/报告未验证。'),
  ('supported', 'choose 核、score 依赖、propose 触发和成对完整验证已说明。')],
 ('gpt-6-astra', 'lit-007'): [
  ('supported', 'QUBO/Ising 正负号与 score 对应；无额外平衡或容量约束。'),
  ('supported', 'E=sum w*Zi*Zj 与 -score 相等，2^n*E+mask 目标支配成立。'),
  ('supported', '仅 ground-state 的最优与 tie 合同支持；认证及回退仍是义务。'),
  ('supported', 'choose 与 classical score/report 分开；member 位序和模式依赖明确。')],
 ('deepseek-v4-pro', 'lit-007'): [
  ('supported', '线性/二次/常数三类系数与原 signed score 对应。'),
  ('supported', '无约束核心的系数可直接检查；未提供 Ising 电路或 tie 编码。'),
  ('unresolved', '必须验证 true maximum 与最小 mask 的义务已说明，具体机制未给出。'),
  ('supported', 'choose、score、成对排序和 propose 触发说明正确。')],
 ('deepseek-flash', 'lit-007'): [
  ('supported', 'pair 项和汇总系数对应所有合法带符号偏好。'),
  ('supported', '二次展开在有限逐赋值检查中相等；核心无需约束惩罚。'),
  ('unresolved', 'best observed 及 observed tie 不是全局保证；回答承认 exact fallback/verification 未解决。'),
  ('supported', 'choose 核、完整 pair 验证、False/True 报告序和 propose 模式均说明。')],
}

# Rejection explanations are reviewed without promoting controls to structural NO.
CONTROL_NOTES = {
 ('gpt-5.6-sol', 'lit-008'): '直接 XOR/全量有序回执的识别成立；不能据未见优化变量证明所有条件映射不可能。',
 ('gpt-6-astra', 'lit-008'): '区分 repetitions 计数字段与采样预算正确；没有对任意子区域/编码的排除证明。',
 ('deepseek-v4-pro', 'lit-008'): '提名 encode 后拒绝符合 D-016；one-to-one 表述不是本次接受的单射主张，拒绝仍待域审。',
 ('deepseek-flash', 'lit-008'): '识别固定 XOR 和逐行输出；“无有限域/谓词”只能作本任务缺少合理搜索的解释，不当不可能性证明。',
 ('gpt-5.6-sol', 'lit-010'): '识别预算化状态迭代和完整 trace；未充分排除所有局部候选，结构 NO 仍未定。',
 ('gpt-6-astra', 'lit-010'): '正确区分连续最优解与特定有限 recurrence；对验证扫描保留单独论证要求。',
 ('deepseek-v4-pro', 'lit-010'): '不能用 exact solve 替代预算迭代；“所有支持家族均不能保持”的普遍主张证据不足。',
 ('deepseek-flash', 'lit-010'): '描述 recurrence 正确；“No oracle can be constructed”过于绝对，未提供排除所有映射的证据。',
}

# Independent manual completion coding. Order: mapping, encoding, selection,
# certification, context. P=provided, T=partial, D=deferred, N=not_applicable.
# These codes are NOT derived from evidence_state or copied from model labels.
COMPLETION = {
 'lit-001': ['PPPTP', 'PPPTP', 'PPDDP', 'PPPTP'],
 'lit-002': ['PPPTP', 'PPDTP', 'PTPTP', 'PTPTP'],
 'lit-003': ['PTTTP', 'PTPTP', 'PTPTP', 'PTPTT'],
 'lit-004': ['PTTTP', 'PPPTP', 'PPPTP', 'PPPTP'],
 'lit-005': ['PTPTP', 'PTPTP', 'PTDTP', 'PTDTT'],
 'lit-006': ['PTTTP', 'PPPTP', 'PTDTP', 'PTTTP'],
 'lit-007': ['PPPTP', 'PPPTP', 'PPDDP', 'PPTTP'],
 'lit-008': ['PNNNP']*4,
 'lit-009': ['TTTTP', 'PTPTP', 'PNNNP', 'XXXXX'],
 'lit-010': ['PNNNP']*4,
}
OBLIGATIONS = ['mapping', 'encoding', 'selection', 'certification', 'context']
STATES = {'P': 'provided', 'T': 'partial', 'D': 'deferred', 'N': 'not_applicable', 'X': 'no_response'}
NOTES = {
 'mapping': '具体核心表达或拒绝理由的提供程度；有表达不等于理由成立。',
 'encoding': '具体能量/谓词、系数或判定构造；不要求提交可执行电路。',
 'selection': '有序解/tie 的具体构造；错误但具体的公式也记 provided，正确性另审。',
 'certification': '全局最优、否定判定或异常/无结果的精确机制；泛称验证/回退通常只到 partial。',
 'context': '候选依赖、激活、保留接口与周边行为；这是规划解释，不是已实现保真。',
}
POINTERS = {
 'mapping': ['/plan/formulation', '/rationale'],
 'encoding': ['/plan/formulation', '/plan/input_encoding', '/plan/assumptions'],
 'selection': ['/plan/formulation', '/plan/output_decoding'],
 'certification': ['/plan/output_decoding', '/plan/risks', '/plan/assumptions'],
 'context': ['/candidate_regions', '/rationale', '/plan/output_decoding'],
}


def build() -> dict:
    old = json.loads((HERE.parent/'v0.1/review.json').read_text())
    rows = old['rows']
    for row in rows:
        model, case = row['model'], row['mother_case']
        had_prior = bool(row['assessments'])
        row['inherited_v01_claim_review'] = had_prior
        row.pop('selected_for_trial_review')
        path = ROOT/row['response_path']
        response = json.loads(path.read_text()) if path.read_text().strip() else None
        if response:
            row['review_status'] = 'AI_PENDING'
            plan = response.get('plan') or {}
            for field in ('formulation', 'input_encoding', 'output_decoding', 'assumptions', 'risks'):
                if field in plan:
                    row['excerpts'][f'/plan/{field}'] = plan[field]
            for field in ('candidate_regions', 'rationale', 'structural_eligibility'):
                row['excerpts'][f'/{field}'] = response[field]
            if not had_prior:
                codings = ADDITIONAL.get((model, case))
                if codings is None:
                    codings = [('unresolved', CONTROL_NOTES[(model, case)]),
                               ('not_applicable', '无计划的范围拒绝；无需凭空构造编码，不代表结构 NO 已验证。'),
                               ('supported', '识别全量输出/预算 trace 与原合同相符；仅支持合同阅读，不证明所有迁移不可能。'),
                               ('supported', '原输入、状态、模式触发与周边报告已解释；空候选或提名后拒绝均可记录。')]
                for dimension, (state, reason) in zip('MECW', codings):
                    row['assessments'].append({'dimension': dimension, 'evidence_state': state, 'reason': reason,
                        'evidence_kind': 'AI source/formula review; scoped derivation and finite checks where available',
                        'evidence': ['EVIDENCE.md', 'checks.json'],
                        'response_pointers': [p for p in POINTERS[{'M': 'mapping', 'E': 'encoding', 'C': 'selection', 'W': 'context'}[dimension]]
                                              if p in row['excerpts']] or ['/rationale'],
                        'complete_migration_verified': False})
            for claim in row['assessments']:
                claim.pop('obligation_status', None)
                if had_prior:
                    claim['evidence'] = ['../v0.1/EVIDENCE.md', '../v0.1/checks.json']
        codes = COMPLETION[case][MODELS.index(model)]
        row['completion'] = []
        for obligation, code in zip(OBLIGATIONS, codes):
            pointers = [p for p in POINTERS[obligation] if p in row['excerpts']]
            if response and not pointers:
                pointers = ['/rationale']
            row['completion'].append({'obligation': obligation, 'completion_state': STATES[code],
                'scope_note': NOTES[obligation], 'response_pointers': pointers,
                'applicability_reason': 'No final response.' if not response else
                    'No plan required by this unresolved-reference rejection.' if code == 'N' else
                    'Reference-positive planning obligation or submitted candidate/rejection analysis.',
                'human_reviews': []})
        row['complete_migration_verified'] = False
    assert len(ADDITIONAL) == 12 and len(CONTROL_NOTES) == 8
    return {'version': '0.2', 'method_status': 'ACCEPTED_A_D026', 'case_review_status': 'AI_PENDING',
            'reviewer': 'Codex coordinator; post-hoc non-blind review', 'human_reviews': [],
            'new_model_calls': 0, 'overall_score': None, 'rows': rows,
            'previous_review_sha256': hashlib.sha256((HERE.parent/'v0.1/review.json').read_bytes()).hexdigest()}


if __name__ == '__main__':
    print(json.dumps(build(), ensure_ascii=False, indent=2))
