"""Check the seminar hand-in without publishing or claiming missing work."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
if not __package__:
    sys.path.insert(0, str(ROOT))

from ragstudy.common import read_json
from ragstudy.replay import compute_summary

CRITERIA = {
    'Question and baseline': 15,
    'Measurement re-runs': 30,
    'Findings and recommendation': 20,
    'Talk (recording)': 15,
    'Sources and facts': 10,
    'AI log': 10,
}
STUDENT_IDS = {'23120045', '23120124', '23120175'}
PLACEHOLDER = re.compile(r'\b(tbd|pending|unknown|placeholder|full name|your name|student name|to fill)\b', re.I)


def submitted_by(text):
    lines = text.replace('**', '').splitlines()
    names = {}
    for i, line in enumerate(lines):
        label = re.fullmatch(r'\s*(?:#+\s*)?submitted by\s*(?::\s*(.*))?', line, re.I)
        if not label:
            continue
        for entry in ([label[1]] if label[1] else lines[i + 1:]):
            if not entry.strip():
                continue
            match = re.fullmatch(r'\s*(?:[-*]\s+)?(\d{8})[\s·,:|–—-]+(.+?)\s*', entry)
            if not match:
                break
            sid, name = match.groups()
            if sid in names or PLACEHOLDER.search(name) or name.casefold() == 'name':
                return False
            if not any(ch.isalpha() for ch in name) or any(ch in '<>[]{}_?' for ch in name):
                return False
            names[sid] = name
    return set(names) == STUDENT_IDS


def has_reflection(text, title):
    lines = text.splitlines()
    heading = re.compile(r'^\s*(?:#{1,6}\s+|\*\*)(.*?)\s*(?:\*\*)?\s*:?\s*$')
    reading = False
    for line in lines:
        match = heading.fullmatch(line)
        if match:
            reading = match[1].strip(' :*').casefold() == title.casefold()
        elif reading and line.strip() and not re.fullmatch(r'(?:pending|tbd|to fill)[.! ]*', line.strip(), re.I):
            return True
    return False


def assessment_score(text):
    rows = {}
    has_header = False
    for line in text.splitlines():
        cells = [cell.strip().strip('*') for cell in line.strip().strip('|').split('|')]
        if [c.casefold() for c in cells] == ['criterion', 'max', 'i claim', 'evidence']:
            has_header = True
        name = cells[0]
        if name not in CRITERIA and name != 'Total':
            continue
        if name in rows or len(cells) < 3 or not all(re.fullmatch(r'[0-9]{1,3}', v) for v in cells[1:3]):
            return None
        maximum, claimed = map(int, cells[1:3])
        if maximum != CRITERIA.get(name, 100) or claimed > maximum:
            return None
        if name in CRITERIA and (len(cells) < 4 or not cells[3]):
            return None
        rows[name] = claimed
    if not has_header or set(rows) != set(CRITERIA) | {'Total'}:
        return None
    claimed = re.findall(r'^\s*Claimed total\s*:\s*([0-9]{1,3})\s*(?:/|out of)\s*100\.?\s*$',
                         text.replace('**', ''), flags=re.I | re.M)
    if len(claimed) != 1 or int(claimed[0]) != rows['Total']:
        return None
    return rows['Total'] if rows['Total'] == sum(rows[c] for c in CRITERIA) else None


def recording_url(text):
    fields = re.findall(r'^Recording(?: URL)?:[ \t]*(.*)$', text, flags=re.MULTILINE | re.IGNORECASE)
    if len(fields) != 1:
        return None
    url = fields[0].strip()
    if not re.fullmatch(r'https://[^\s<>()]+', url):
        return None
    try:
        return url if urlsplit(url).hostname else None
    except ValueError:
        return None


def measured_directories(root):
    valid, errors = [], []
    for env_path in sorted((root / 'results').glob('*/environment.json')):
        directory = env_path.parent
        name = str(directory.relative_to(root))
        try:
            if read_json(env_path)['pilot']:
                continue
            result = compute_summary(directory)
            if result['fixture_only'] or result['pilot'] is not False or result['run_count'] < 5:
                raise ValueError('Expected at least five full measured runs')
            if result != read_json(directory / 'summary.json'):
                raise ValueError('Saved summary differs from raw observations')
            valid.append(name)
        except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError) as exc:
            errors.append(f'{name}: {exc}')
    return valid, errors


def audit(root):
    checks = []

    def check(name, ok, detail):
        checks.append({'name': name, 'passed': bool(ok), 'detail': detail})

    for name in ['README.md', 'REPORT.md', 'slides.pdf', 'TALK.md', 'AI-LOG.md', 'SELF_ASSESSMENT_REPORT.md']:
        path = root / name
        check(name, path.is_file() and path.stat().st_size > 0, 'Required nonempty deliverable')
    report_path = root / 'REPORT.md'
    report = report_path.read_text() if report_path.exists() else ''
    first_line = report.splitlines()[0] if report else ''
    repository = re.fullmatch(r'https://github\.com/[\w.-]+/[\w.-]+/?', first_line.strip())
    check('report_repository', repository, 'First line must be the actual public GitHub repository URL; public access must also be checked manually')
    talk_path = root / 'TALK.md'
    talk = talk_path.read_text() if talk_path.exists() else ''
    check('recording_link', recording_url(talk), 'TALK.md needs a labeled Recording URL. Manually verify playback, duration, speakers and signed-out access.')
    pdf = root / 'slides.pdf'
    check('slides_pdf_format', pdf.exists() and pdf.read_bytes().startswith(b'%PDF-'), 'Exported slides must be a PDF')
    git = subprocess.run(['git', '-C', str(root), 'rev-parse', '--verify', 'HEAD'], capture_output=True)
    check('git_history', git.returncode == 0, 'Submission archive must include .git and actual commit history')
    result_dirs, errors = measured_directories(root)
    detail = '; '.join(result_dirs + errors) or 'Need five complete full runs and the matching saved summary'
    check('five_real_runs', result_dirs, detail)
    assessment_path = root / 'SELF_ASSESSMENT_REPORT.md'
    assessment = assessment_path.read_text() if assessment_path.exists() else ''
    score = assessment_score(assessment)
    check('self_assessment_total', score is not None,
          'Use the template table, score all six criteria with evidence, and match the explicit claimed total out of 100')
    check('self_assessment_submitters', submitted_by(assessment),
          'List each registered student ID and full name in the Submitted by section')
    for key, title in [('unfinished', 'What I did not manage'), ('reflection', 'What I would do differently')]:
        check('self_assessment_' + key, has_reflection(assessment, title), f'Include a response under {title}')
    return {'ready': all(c['passed'] for c in checks), 'checks': checks, 'claimed_score': score}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    result = audit(ROOT)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for item in result['checks']:
            print(f"{'PASS' if item['passed'] else 'TODO'} {item['name']}: {item['detail']}")
        print('Manual checks: <=3 report pages; all members speak; all numerical claims map to logs; public repo and recording access; zip filename total matches self-assessment; .git is inside archive.')
    raise SystemExit(0 if result['ready'] else 1)


if __name__ == '__main__':
    main()
