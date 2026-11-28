"""Create a local review bundle, or a checked hand-in with explicit score.

Only tracked files plus .git are included; caches and credentials stay out.
"""
import argparse
import json
import subprocess
import zipfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if not __package__:
    sys.path.insert(0, str(ROOT))

from scripts.submission_check import audit

TEAM = '23120045-23120124-23120175'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--draft', action='store_true', help='Allow incomplete human/publication deliverables and mark the archive DRAFT')
    parser.add_argument('--score', type=int)
    args = parser.parse_args()
    if args.draft and args.score is not None:
        parser.error('A draft must not claim a submission score')
    if not args.draft:
        if args.score is None or not 0 <= args.score <= 100:
            parser.error('Supply --draft, or --score between 0 and 100')
        result = audit(ROOT)
        if not result['ready']:
            parser.error('Hand-in checks failed: ' + ', '.join(c['name'] for c in result['checks'] if not c['passed']))
        if result['claimed_score'] != args.score:
            parser.error('Filename score must equal the evidence-backed self-assessment total')
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    tracked = [p for p in tracked if p]
    if not tracked or not (ROOT / '.git' / 'HEAD').exists():
        parser.error('Initialize Git and add the complete intended deliverables before packaging')
    dirty = subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT).decode()
    if dirty and not args.draft:
        parser.error('Commit all changes before producing a final hand-in')
    if any(Path(p).name == '.env' or any(part in ['.cache', '.venv', 'data'] for part in Path(p).parts) for p in tracked):
        parser.error('Refusing to package tracked credentials/caches/raw downloaded data; inspect git ls-files')
    target = ROOT / 'dist' / f'{TEAM}_{"DRAFT" if args.draft else args.score}.zip'
    target.parent.mkdir(exist_ok=True)
    files = [ROOT / p for p in tracked]
    files += [p for p in (ROOT / '.git').rglob('*') if p.is_file() and 'hooks' not in p.relative_to(ROOT / '.git').parts]
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, arcname=path.relative_to(ROOT))
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise ValueError('Archive integrity check failed')
        if '.git/HEAD' not in archive.namelist():
            raise ValueError('Archive must include .git')
    print(json.dumps({'archive': str(target), 'bytes': target.stat().st_size, 'draft': args.draft}, indent=2))


if __name__ == '__main__':
    main()
