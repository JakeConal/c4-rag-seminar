"""Secondary vector-only quality comparison. Reuse the main run's corpus and test queries."""
import argparse
import json
import statistics
from pathlib import Path

from .common import digest, metrics, query_change_counts, read_json, write_json
from .replay import finite_number, require


def pool_quality(candidates, chunk_map, relevant):
    parents = list(dict.fromkeys(chunk_map[c] for c in candidates))
    quality = metrics(parents[:5], relevant)
    quality['pool_recall'] = len(relevant.intersection(parents)) / len(relevant)
    return quality


def read_baseline(directory):
    environment = read_json(directory / 'environment.json')
    require(not environment['pilot'], 'The chunk comparison requires the complete SciFact test set')
    config = environment['config']
    require(config['output_k'] == 5, 'The quality analysis uses the top five parents')
    rows = read_json(directory / 'run-01.json')['queries']
    require(len(rows) == environment['query_count'] == environment['data']['queries'],
            'Expected one complete primary run')
    require(len({r['query_id'] for r in rows}) == len(rows), 'Duplicate primary query ID')
    return environment, rows


def replay_ablation(directory):
    environment, rows = read_baseline(directory)
    config = environment['config']
    ablation = directory / 'chunk-ablation'
    raw = read_json(ablation / 'observations.json')
    base_map = read_json(directory / 'chunk-map.json')
    alt_map = read_json(ablation / 'chunk-map.json')
    require(raw['baseline_run_sha256'] == digest(directory / 'run-01.json'), 'Primary run identity differs')
    require(set(base_map.values()) == set(alt_map.values()), 'Chunk conditions do not cover the same parents')
    require(len(alt_map) == raw['chunks'] and raw['overlap'] == config['chunk_overlap'],
            'Alternate chunk manifest mismatch')
    require(raw['size'] != config['chunk_tokens'] and 0 <= raw['overlap'] < raw['size'],
            'Invalid size comparison')
    alternatives = raw['queries']
    require(set(alternatives) == {r['query_id'] for r in rows}, 'Alternate and primary query IDs differ')
    base_scores, alt_scores = [], []
    for row in rows:
        alt = alternatives[row['query_id']]
        candidates, scores = alt['candidates'], alt['vector_scores']
        require(len(candidates) == len(set(candidates)) == min(config['candidate_k'], len(alt_map))
                and all(c in alt_map for c in candidates), 'Invalid alternate candidates')
        require(len(scores) == len(candidates) and all(finite_number(v) for v in scores)
                and scores == sorted(scores, reverse=True), 'Invalid alternate vector scores')
        relevant = set(row['relevant'])
        base_scores.append(pool_quality(row['baseline']['candidates'], base_map, relevant))
        alt_scores.append(pool_quality(candidates, alt_map, relevant))
    summary = {'query_count': len(rows), 'overlap_tokens': config['chunk_overlap'],
               'baseline': {'window_tokens': config['chunk_tokens'], 'chunks': len(base_map),
                            'index_bytes': environment['index_bytes']},
               'alternative': {'window_tokens': raw['size'], 'chunks': len(alt_map),
                               'index_bytes': raw['index_bytes']}, 'paired_changes': {}}
    for key in base_scores[0]:
        deltas = [a[key] - b[key] for a, b in zip(alt_scores, base_scores)]
        summary['baseline'][key] = statistics.mean(b[key] for b in base_scores)
        summary['alternative'][key] = statistics.mean(a[key] for a in alt_scores)
        summary['paired_changes'][key] = {'mean': statistics.mean(deltas), **query_change_counts(deltas)}
    write_json(ablation / 'summary.json', summary)
    print(json.dumps(summary, indent=2))
    return summary


def measure_ablation(directory, size):
    from .measure import configure_cpu, encode_index, load_encoder, vector_pool
    from .prepare import build_chunks

    environment, rows = read_baseline(directory)
    config = environment['config']
    require(size != config['chunk_tokens'] and config['chunk_overlap'] < size <= 254,
            'Alternate window must differ, exceed the overlap, and fit the encoder limit with special tokens')
    ablation = directory / 'chunk-ablation'
    require(not (ablation / 'observations.json').exists(), 'A chunk comparison already exists in this directory')
    configure_cpu(config)
    from huggingface_hub import hf_hub_download
    import pyarrow.parquet as pq

    dataset = config['dataset']
    filename = 'corpus/corpus-00000-of-00001.parquet'
    path = hf_hub_download(dataset['id'], filename, repo_type='dataset', revision=dataset['revision'],
                           local_files_only=True)
    require(digest(path) == environment['data']['source_sha256'][filename], 'Primary corpus digest differs')
    encoder = load_encoder(config)
    chunks = build_chunks(pq.read_table(path).to_pylist(), encoder.tokenizer, size, config['chunk_overlap'])
    embeddings = encode_index(encoder, chunks, config)
    observations = {}
    for row in rows:
        candidates, scores, indices = vector_pool(encoder, embeddings, chunks, row['query'], config['candidate_k'])
        observations[row['query_id']] = {'candidates': [c['id'] for c in candidates],
                                         'vector_scores': [float(scores[i]) for i in indices]}
    write_json(ablation / 'chunk-map.json', {c['id']: c['doc_id'] for c in chunks})
    write_json(ablation / 'observations.json', {'baseline_run_sha256': digest(directory / 'run-01.json'),
               'size': size, 'overlap': config['chunk_overlap'], 'chunks': len(chunks),
               'index_bytes': embeddings.nbytes, 'queries': observations})
    return replay_ablation(directory)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, help='Primary results directory')
    parser.add_argument('--size', default=96, type=int, help='Alternate tokenizer window; same absolute overlap')
    parser.add_argument('--replay', action='store_true', help='Validate and summarize saved ranks with standard Python')
    args = parser.parse_args()
    if args.replay:
        replay_ablation(args.directory)
    else:
        measure_ablation(args.directory, args.size)
