"""One-off static documentation audit; no model calls or benchmark execution."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def anchors(path: Path) -> set[str]:
    content = path.read_text()
    result = set(re.findall(r'<a\s+id="([^"]+)"', content))
    counts: dict[str, int] = {}
    for heading in re.findall(r'^#{1,6}\s+(.+)$', content, re.M):
        slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        index = counts.get(slug, 0)
        counts[slug] = index + 1
        result.add(slug if index == 0 else f'{slug}-{index}')
    return result


def main() -> None:
    protected = json.loads((HERE / 'protected_before.json').read_text())
    changed = [name for name, expected in protected.items()
               if not (ROOT / name).is_file() or sha(ROOT / name) != expected]
    before = json.loads((HERE / 'before.json').read_text())
    archive_errors = [name for name, row in before.items() if sha(ROOT / row['archive']) != row['sha256']]
    files = [ROOT.parent / 'AGENTS.md'] + [ROOT / name for name in (
        'AGENTS.md', 'PROJECT_STATUS.md', 'NEXT_ACTIONS.md', 'README.md',
        'docs/RESEARCH_CHARTER.md', 'docs/CODEX_WORKFLOW.md', 'DECISIONS.md',
        'TODO.md', 'CHANGELOG.md')] + [HERE / 'README.md']
    missing, checked, checked_anchors = [], 0, 0
    for doc in files:
        for target in re.findall(r'\[[^\]\n]+\]\(([^)\n]+)\)', doc.read_text()):
            if target.startswith(('https:', 'http:', 'mailto:')):
                continue
            location, _, fragment = target.strip('<>').partition('#')
            path = doc.parent / unquote(location) if location else doc
            checked += 1
            if not path.exists():
                missing.append([str(doc.relative_to(ROOT.parent)), target, 'path'])
            elif fragment and path.suffix == '.md':
                checked_anchors += 1
                if unquote(fragment) not in anchors(path):
                    missing.append([str(doc.relative_to(ROOT.parent)), target, 'anchor'])
    entry = (ROOT / 'AGENTS.md').read_text()
    state = (ROOT / 'PROJECT_STATUS.md').read_text()
    queue = (ROOT / 'NEXT_ACTIONS.md').read_text()
    charter = (ROOT / 'docs/RESEARCH_CHARTER.md').read_text()
    old_charter = (ROOT / before['docs/RESEARCH_CHARTER.md']['archive']).read_text()
    checks = {
        'parent_entry_routes_to_project': 'qrefactorbench/AGENTS.md' in (ROOT.parent / 'AGENTS.md').read_text(),
        'read_command_explicit': '读取当前目录' in entry and '不自动执行下一任务' in entry,
        'continue_separate': '最高优先安全工作' in entry,
        'intent_for_non_experts': '非量子专家' in charter and '端到端收益' in charter,
        'original_charter_scientific_body_preserved': charter.split('## The Software Engineering problem', 1)[1] == old_charter.split('## The Software Engineering problem', 1)[1],
        'current_vs_historical_inputs': 'reference_completion/v0.1.1' in state and 'pilot/packets-v0.1' in state,
        'status_short': len(state.splitlines()) <= 100,
        'queue_short': len(queue.splitlines()) <= 40,
        'no_false_run_claim': '尚未进行这组模型实验' in state,
    }
    result = dict(command='python -B artifacts/session_entry_20260921/check_docs.py',
                  protected_files=len(protected), protected_changed=changed,
                  original_archives=len(before), archive_errors=archive_errors,
                  local_paths_checked=checked, local_anchors_checked=checked_anchors,
                  broken_links=missing, startup_static_checks=checks,
                  current_line_counts={n: len((ROOT / n).read_text().splitlines())
                                       for n in ('AGENTS.md', 'PROJECT_STATUS.md', 'NEXT_ACTIONS.md', 'README.md')},
                  model_calls=0, runtime_tests_rerun=False,
                  limits='Static paths/anchors and reading-contract checks only; no fresh model session or automatic semantic consistency proof.')
    (HERE / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    assert not (changed or archive_errors or missing) and all(checks.values())


if __name__ == '__main__':
    main()
