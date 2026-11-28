import unittest

from ragstudy.common import metrics, percentile, token_windows, unique_docs
from ragstudy.replay import summarize


class MetricsTest(unittest.TestCase):
    def test_recall_denominator_is_all_relevant_docs(self):
        self.assertEqual(metrics(['x', 'a', 'a'], {'a', 'b'}), {'recall_at_5': .5, 'mrr_at_5': .5})

    def test_rank_cutoff_and_missing_hits(self):
        self.assertEqual(metrics(['a', 'b', 'c', 'd', 'e', 'f'], {'f'})['mrr_at_5'], 0)
        with self.assertRaises(ValueError):
            metrics([], set())

    def test_collapse_parent_before_metric(self):
        self.assertEqual(unique_docs([{'doc_id': 'a'}, {'doc_id': 'a'}, {'doc_id': 'b'}]), ['a', 'b'])

    def test_chunk_coverage_without_redundant_tail(self):
        self.assertEqual(list(token_windows(list(range(8)), 4, 2)), [[0, 1, 2, 3], [2, 3, 4, 5], [4, 5, 6, 7]])
        with self.assertRaises(ValueError):
            list(token_windows([1], 4, 4))

    def test_paired_latency_is_not_difference_of_percentiles(self):
        rows = [{'relevant': ['a'], 'baseline': {'docs': ['a'], 'latency_ms': b},
                 'reranked': {'docs': ['a'], 'latency_ms': r}} for b, r in [(1, 101), (100, 102), (101, 103)]]
        self.assertEqual(summarize(rows)['added_latency']['p50_ms'], 2)
        self.assertEqual(percentile([0, 10], .95), 9.5)


if __name__ == '__main__':
    unittest.main()
