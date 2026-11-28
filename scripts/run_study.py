"""One command runs the primary study followed by the secondary chunk analysis."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def full_results():
    return {p.parent for p in (ROOT / 'results').glob('*/environment.json')
            if not p.parent.name.startswith('pilot-')}


def main():
    before = full_results()
    subprocess.run([sys.executable, '-m', 'ragstudy.measure'], cwd=ROOT, check=True)
    created = full_results() - before
    if len(created) != 1:
        raise RuntimeError('Expected exactly one new primary result directory; avoid concurrent study commands')
    result = created.pop()
    subprocess.run([sys.executable, '-m', 'ragstudy.chunk_ablation', str(result)], cwd=ROOT, check=True)
    relative = result.relative_to(ROOT)
    (ROOT / 'results' / 'latest-study.txt').write_text(str(relative) + '\n')
    print(f'Complete study: {relative}')


if __name__ == '__main__':
    main()
