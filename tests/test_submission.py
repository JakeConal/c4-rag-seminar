import tempfile
import unittest
from pathlib import Path

from ragstudy.common import read_json, write_json
from ragstudy.replay import compute_summary
from scripts.submission_check import CRITERIA, assessment_score, has_reflection, measured_directories, recording_url, submitted_by


class SubmissionTest(unittest.TestCase):
    def test_requires_labeled_recording_url(self):
        misc = 'Assignment reference https://drive.google.com/file/d/brief/view'
        self.assertIsNone(recording_url(misc))
        self.assertIsNone(recording_url('Recording: pending\n' + misc))
        url = 'https://video.example.edu/seminars/c4'
        self.assertEqual(recording_url('Recording: ' + url + '\n' + misc), url)

    def test_assessment_requires_six_bounded_scores_and_matching_sum(self):
        total = '| **Total** | **100** | **100** | |'
        header = '**Claimed total:** 100/100\n\n| Criterion | Max | I claim | Evidence |'
        rows = [f'| {name} | {max_score} | {max_score} | report |' for name, max_score in CRITERIA.items()]
        table = '\n'.join([header, *rows, total])
        self.assertEqual(assessment_score(table), 100)
        self.assertIsNone(assessment_score('\n'.join([header, *rows[1:], total])))
        self.assertIsNone(assessment_score(table.replace('100/100', '95/100')))
        self.assertIsNone(assessment_score(table.replace('I claim', 'Notes')))
        self.assertIsNone(assessment_score(table.replace('| 30 | 30 |', '| 30 | TBD |')))
        self.assertIsNone(assessment_score(table.replace('| 30 | 30 |', '| 30 | 31 |')))
        self.assertIsNone(assessment_score(table.replace('| 30 | 30 |', '| 30 | 29 |')))

    def test_assessment_needs_labeled_team_and_two_written_reflections(self):
        team = '**Submitted by**\n\n- 23120045 · Person A\n- 23120124 · Person B\n- 23120175 · Person C'
        self.assertTrue(submitted_by(team))
        self.assertFalse(submitted_by(team.replace('Person B', 'Full name pending')))
        self.assertFalse(submitted_by(team.replace('23120124', '23120045')))
        self.assertFalse(submitted_by(team.replace('Submitted by', 'Team comments')))
        headings = '## What I did not manage\n\n## What I would do differently\n\nCollect cold-query timings.'
        self.assertFalse(has_reflection(headings, 'What I did not manage'))
        self.assertTrue(has_reflection(headings, 'What I would do differently'))
        self.assertFalse(has_reflection(headings.replace('Collect cold-query timings.', 'TBD'), 'What I would do differently'))

    def test_check_replays_raw_logs_and_leaves_saved_summary_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / 'results' / 'experiment'
            write_json(run_dir / 'environment.json', {'pilot': False, 'config': {'candidate_k': 1, 'output_k': 5, 'runs': 5},
                       'query_count': 1, 'data': {'queries': 1, 'chunks': 1}})
            write_json(run_dir / 'chunk-map.json', {'a:0': 'a'})
            arm = {'docs': ['a'], 'candidates': ['a:0'], 'vector_scores': [.7], 'retrieval_ms': 1,
                   'latency_ms': 2, 'cross_scores': None}
            for number in range(1, 6):
                order = ['baseline', 'reranked'] if number % 2 else ['reranked', 'baseline']
                row = {'order': order, 'query_id': 'q', 'query': 'claim', 'relevant': ['a'],
                       'baseline': arm, 'reranked': {**arm, 'cross_scores': [.5]}}
                write_json(run_dir / f'run-{number:02d}.json', {'run': number, 'queries': [row]})
            summary = run_dir / 'summary.json'
            expected = compute_summary(run_dir)
            self.assertFalse(summary.exists())
            write_json(summary, expected)
            self.assertEqual(measured_directories(root), (['results/experiment'], []))
            write_json(summary, {})
            self.assertEqual(measured_directories(root)[0], [])
            self.assertEqual(read_json(summary), {})
            write_json(summary, expected)
            write_json(run_dir / 'run-04.json', {})
            good, errors = measured_directories(root)
            self.assertEqual(good, [])
            self.assertTrue(errors)
            self.assertEqual(read_json(summary), expected)
