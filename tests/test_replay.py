import copy
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ragstudy.chunk_ablation import replay_ablation
from ragstudy.common import digest, write_json
from ragstudy.replay import replay, validate_rows


class ReplayTest(unittest.TestCase):
    def setUp(self):
        self.map = {'a:0': 'a', 'a:1': 'a', 'b:0': 'b', 'c:0': 'c'}
        self.env = {'config': {'candidate_k': 4, 'output_k': 5, 'runs': 2,
                               'chunk_tokens': 192, 'chunk_overlap': 32},
                    'pilot': False, 'query_count': 1, 'index_bytes': 16, 'data': {'queries': 1, 'chunks': 4}}
        self.row = {'query_id': 'q', 'query': 'claim', 'relevant': ['b', 'c'], 'order': ['baseline', 'reranked']}
        common = {'candidates': list(self.map), 'vector_scores': [.9, .8, .7, .6], 'retrieval_ms': 1}
        self.row['baseline'] = {**copy.deepcopy(common), 'cross_scores': None, 'docs': ['a', 'b', 'c'], 'latency_ms': 2}
        self.row['reranked'] = {**common, 'cross_scores': [0, 0, 1, 1], 'docs': ['b', 'c', 'a'], 'latency_ms': 10}
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        write_json(self.path / 'environment.json', self.env)
        write_json(self.path / 'chunk-map.json', self.map)
        self.save_run(1)
        self.save_run(2)

    def save_run(self, run, row=None):
        row = copy.deepcopy(self.row if row is None else row)
        if run % 2 == 0:
            row['order'].reverse()
        write_json(self.path / f'run-{run:02d}.json', {'run': run, 'queries': [row]})

    def test_real_log_reconstructs_stable_ties_and_parent_collapse(self):
        with redirect_stdout(io.StringIO()):
            result = replay(self.path)
        aggregate = result['across_runs']
        self.assertEqual(aggregate['mrr_at_5_query_counts']['improved']['median'], 1)
        self.assertEqual(aggregate['quality_delta']['mrr_at_5']['median'], .5)
        self.assertEqual(aggregate['candidate_pool']['oracle_recall_at_5']['median'], 1)
        self.assertEqual(aggregate['added_latency']['p95_ms']['median'], 8)

    def test_wrong_reranked_document_order_is_rejected(self):
        self.row['reranked']['docs'] = ['c', 'b', 'a']
        with self.assertRaisesRegex(ValueError, 'disagree'):
            validate_rows([self.row], self.map, self.env, 1)

    def test_pools_must_match_even_when_parent_rankings_do(self):
        self.row['reranked']['candidates'][:2] = ['a:1', 'a:0']
        with self.assertRaisesRegex(ValueError, 'different candidates'):
            validate_rows([self.row], self.map, self.env, 1)

    def test_replay_rejects_missing_run(self):
        (self.path / 'run-02.json').unlink()
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            replay(self.path)

    def test_replay_rejects_changed_judgments(self):
        self.row['relevant'] = ['c']
        self.save_run(2)
        with self.assertRaisesRegex(ValueError, 'judgments differ'):
            replay(self.path)

    def test_impossible_time_and_nonfinite_score_are_rejected(self):
        self.row['baseline']['latency_ms'] = .5
        with self.assertRaisesRegex(ValueError, 'timing'):
            validate_rows([self.row], self.map, self.env, 1)
        self.row['baseline']['latency_ms'] = 2
        self.row['reranked']['cross_scores'][0] = float('nan')
        with self.assertRaisesRegex(ValueError, 'cross scores'):
            validate_rows([self.row], self.map, self.env, 1)

    def test_chunk_comparison_uses_same_parent_labels_and_one_query_once(self):
        ablation = self.path / 'chunk-ablation'
        write_json(ablation / 'chunk-map.json', self.map)
        write_json(ablation / 'observations.json', {
            'baseline_run_sha256': digest(self.path / 'run-01.json'), 'chunks': 4, 'index_bytes': 16,
            'size': 96, 'overlap': 32,
            'queries': {'q': {'candidates': ['b:0', 'a:0', 'c:0', 'a:1'], 'vector_scores': [4, 3, 2, 1]}}})
        with redirect_stdout(io.StringIO()):
            summary = replay_ablation(self.path)
        self.assertEqual(summary['paired_changes']['mrr_at_5'], {'mean': .5, 'improved': 1, 'tied': 0, 'worsened': 0})
        self.assertEqual(summary['paired_changes']['pool_recall']['mean'], 0)
        self.row['query'] = 'modified'
        self.save_run(1)
        with self.assertRaisesRegex(ValueError, 'identity differs'):
            replay_ablation(self.path)
