"""Update recorded upstream skills without forcing local changes or syncing targets."""
import json
import os
from pathlib import Path
import subprocess


def candidates(root, metadata):
    return [
        key for key, entry in sorted(metadata['entries'].items())
        if not entry.get('tracked')
        and entry.get('repo_url', '').startswith('https://github.com/')
        and not key.startswith('_local-variants/')
        and key != 'utils/template-skill'
        and (root / key / 'SKILL.md').is_file()
    ]


def main():
    root = Path(__file__).resolve().parents[1]
    metadata = json.loads((root / '.metadata.json').read_text())
    names = candidates(root, metadata)
    if not names:
        raise SystemExit('No verified upstream skills found')
    report = [
        '# Weekly upstream skill updates', '',
        'Only recorded GitHub sources are updated. Local edits and security audit blocks are respected; no force, pruning, or target sync is used.', '',
        'After merging, run `skillshare pull` and `skillshare sync` on your machine.', '',
    ]
    # A separate invocation isolates a failed upstream without losing other updates.
    for name in names:
        try:
            result = subprocess.run(
                ['skillshare', 'update', name, '--json'], cwd=root,
                capture_output=True, text=True, timeout=180,
            )
            try:
                payload = json.loads(result.stdout)
                summary = json.dumps(payload, ensure_ascii=False)
            except json.JSONDecodeError:
                summary = 'No structured result. See the workflow log.'
            report.extend([f'## {name}', '', f'Exit code: {result.returncode}', '', '```json', summary, '```', ''])
            print(name, 'exit', result.returncode, flush=True)
        except subprocess.TimeoutExpired:
            # A timed-out update cannot safely be included in an automated PR.
            report.extend([f'## {name}', '', 'Update timed out; job stopped without publishing a PR.', ''])
            write_report(report)
            raise
    write_report(report)


def write_report(lines):
    text = '\n'.join(lines)
    (Path(os.environ.get('RUNNER_TEMP', '/tmp')) / 'skillshare-update-report.md').write_text(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary:
            summary.write(text)


if __name__ == '__main__':
    main()
