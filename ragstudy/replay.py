"""Validate saved paired rankings and recompute metrics without ML dependencies."""
import argparse
import json
import math
import statistics
from pathlib import Path

from .common import metrics, percentile, query_change_counts, read_json, spread, write_json


def summarize(rows, chunk_map=None):
    if not rows:
        raise ValueError('No observations')
    summary = {}
    per_query = {}
    for arm in ('baseline', 'reranked'):
        scores = [metrics(r[arm]['docs'], set(r['relevant'])) for r in rows]
        per_query[arm] = scores
        latency = [r[arm]['latency_ms'] for r in rows]
        summary[arm] = {key: statistics.mean(s[key] for s in scores) for key in scores[0]}
        summary[arm].update({'p50_ms': percentile(latency, .5), 'p95_ms': percentile(latency, .95)})
    extra = [r['reranked']['latency_ms'] - r['baseline']['latency_ms'] for r in rows]
    summary['added_latency'] = {'p50_ms': percentile(extra, .5), 'p95_ms': percentile(extra, .95)}
    summary['quality_delta'] = {}
    for key in ('mrr_at_5', 'recall_at_5'):
        deltas = [r[key] - b[key] for b, r in zip(per_query['baseline'], per_query['reranked'])]
        summary['quality_delta'][key] = statistics.mean(deltas)
        summary[f'{key}_query_counts'] = query_change_counts(deltas)
    if chunk_map is not None:
        ceilings, distinct_parents = [], []
        for row in rows:
            relevant = set(row['relevant'])
            parents = {chunk_map[c] for c in row['baseline']['candidates']}
            ceilings.append(min(5, len(relevant & parents)) / len(relevant))
            distinct_parents.append(len(parents))
        summary['candidate_pool'] = {
            'oracle_recall_at_5': statistics.mean(ceilings), 'queries_with_no_positive': ceilings.count(0),
            'mean_distinct_parents': statistics.mean(distinct_parents),
            'queries_below_five_parents': sum(n < 5 for n in distinct_parents)}
    return summary


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate_rows(rows, chunk_map, environment, run):
    config = environment['config']
    query_count = environment['query_count']
    require(len(rows) == query_count and query_count > 0, f'Run {run}: query count mismatch')
    queries = {}
    parents = set(chunk_map.values())
    for i, row in enumerate(rows):
        qid = row['query_id']
        label = f'Run {run}, query {qid}'
        require(qid not in queries, f'{label}: duplicate query')
        expected_order = ['baseline', 'reranked'] if (run - 1 + i) % 2 == 0 else ['reranked', 'baseline']
        require(row['order'] == expected_order, f'{label}: arm order mismatch')
        relevant = set(row['relevant'])
        require(relevant and relevant <= parents, f'{label}: missing positive parent')
        queries[qid] = (row['query'], frozenset(relevant))
        for arm in expected_order:
            result = row[arm]
            candidates = result['candidates']
            require(len(candidates) == min(len(chunk_map), config['candidate_k'])
                    and len(set(candidates)) == len(candidates) and all(c in chunk_map for c in candidates),
                    f'{label}: invalid {arm} candidate pool')
            scores = result['vector_scores']
            require(len(scores) == len(candidates) and all(finite_number(v) for v in scores)
                    and scores == sorted(scores, reverse=True), f'{label}: invalid {arm} vector scores')
            latency, retrieval = result['latency_ms'], result['retrieval_ms']
            require(finite_number(latency) and finite_number(retrieval) and 0 <= retrieval <= latency,
                    f'{label}: invalid {arm} timing')
            cross = result['cross_scores']
            if arm == 'reranked':
                require(isinstance(cross, list) and len(cross) == len(candidates)
                        and all(finite_number(v) for v in cross), f'{label}: invalid cross scores')
                ranked = [c for _, c in sorted(zip(cross, candidates), key=lambda pair: -pair[0])]
            else:
                require(cross is None, f'{label}: baseline contains cross scores')
                ranked = candidates
            docs = list(dict.fromkeys(chunk_map[c] for c in ranked))[:config['output_k']]
            require(result['docs'] == docs, f'{label}: {arm} documents disagree with candidate rankings')
        require(row['baseline']['candidates'] == row['reranked']['candidates'],
                f'{label}: paired arms retrieved different candidates')
    return queries


def compute_summary(directory):
    """Read and validate all logged observations without modifying the result directory."""
    directory = Path(directory)
    files = sorted(directory.glob('run-*.json'))
    require(files, 'No run-*.json files found')
    fixture = read_json(files[0]).get('fixture_only', False)
    chunk_map = None
    if not fixture:
        environment = read_json(directory / 'environment.json')
        config = environment['config']
        require(config['output_k'] == 5, 'MRR@5 and recall@5 require five returned parent documents')
        expected = environment.get('run_count', config['runs'])
        require(expected == config['runs'] or environment['pilot'], 'Full runs must use configured repetitions')
        require(environment['pilot'] or environment['query_count'] == environment['data']['queries'],
                'Full runs require all labeled queries')
        require([p.name for p in files] == [f'run-{i:02d}.json' for i in range(1, expected + 1)],
                'Incomplete or unexpected run files')
        chunk_map = read_json(directory / 'chunk-map.json')
        require(len(chunk_map) == environment['data']['chunks'], 'Chunk count differs from manifest')
    runs = []
    reference = None
    for run, path in enumerate(files, start=1):
        raw = read_json(path)
        require(raw.get('fixture_only', False) == fixture, 'Mixed synthetic and measured runs')
        rows = raw['queries']
        if not fixture:
            require(raw['run'] == run, f'Incorrect run identifier in {path.name}')
            queries = validate_rows(rows, chunk_map, environment, run)
            require(reference is None or queries == reference, 'Query text, IDs or judgments differ across runs')
            reference = queries
        runs.append(summarize(rows, chunk_map))
    aggregate = {section: {metric: spread([run[section][metric] for run in runs])
                           for metric in runs[0][section]} for section in runs[0]}
    return {'fixture_only': fixture, 'pilot': None if fixture else environment['pilot'],
            'run_count': len(runs), 'runs': runs, 'across_runs': aggregate,
            'note': 'Timing quantiles use saved per-query latencies. Added latency is paired within each query and run.'}


def replay(directory):
    directory = Path(directory)
    result = compute_summary(directory)
    write_json(directory / 'summary.json', result)
    print(json.dumps(result['across_runs'], indent=2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    replay(parser.parse_args().directory)
