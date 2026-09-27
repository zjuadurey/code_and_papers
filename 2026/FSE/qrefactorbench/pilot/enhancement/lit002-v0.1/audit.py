"""Final offline handoff audit; no inference, credentials or file rewrites."""
import argparse
import json
from pathlib import Path
import re
from collect import audit, summarize, HERE, ROOT
from build import save, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit()
    old = json.loads((HERE / 'SUMMARY.json').read_text())
    new = summarize(HERE)
    old.pop('created_utc')
    new.pop('created_utc')
    assert old == new, 'Summary does not replay'
    assert new['actual_requests'] <= 15
    completed = json.loads((HERE / 'run.completed.json').read_text())
    assert new['actual_requests'] == completed['attempted']
    for path in HERE.glob('runs/*/*/metadata.json'):
        meta = json.loads(path.read_text())
        assert meta['operator_retries'] == 0
        assert all(flag in meta['command'] for flag in ('--ignore-user-config', '--ignore-rules', '--ephemeral'))
        assert not any(str(ROOT) in arg for arg in meta['command'])
    docs = [ROOT / name for name in ('PROJECT_STATUS.md', 'NEXT_ACTIONS.md', 'TODO.md',
                                     'DECISIONS.md', 'CHANGELOG.md', 'docs/research_log.md')]
    docs += list(HERE.glob('*.md'))
    count = 0
    for path in docs:
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if '://' in target or target.startswith('#') or '<' in target:
                continue
            target = target.split('#')[0]
            linked = (path.parent / target).resolve()
            if args.output and linked == args.output.resolve():
                continue
            assert linked.exists(), (path, target)
            count += 1
    result.update(local_markdown_paths_checked=count, summary_replayed=True,
                  actual_requests=new['actual_requests'],
                  engineering_validation=json.loads((HERE / 'engineering-validation.json').read_text()),
                  analysis_source_sha256={p.name: digest(p) for p in HERE.glob('*.py')})
    assert result['passed'], result['errors']
    if args.output:
        save(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
