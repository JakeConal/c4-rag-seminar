"""CPU-only, sequential, warm query benchmark. Downloads are outside measurement."""
import argparse
import importlib.metadata
import os
import platform
import random
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .common import digest, read_json, unique_docs, write_json
from .replay import replay


def configure_cpu(config):
    """Call before importing numpy/torch so both BLAS and model thread counts apply."""
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ.setdefault('HF_HOME', str(Path('.cache/huggingface').resolve()))
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
        os.environ[key] = str(config['threads'])
    import numpy as np
    import torch

    torch.set_num_threads(config['threads'])
    torch.set_num_interop_threads(1)
    torch.manual_seed(config['seed'])
    np.random.seed(config['seed'])


def load_encoder(config):
    from sentence_transformers import SentenceTransformer

    encoder = SentenceTransformer(config['embedding']['id'], revision=config['embedding']['revision'],
                                  device='cpu', local_files_only=True)
    encoder.max_seq_length = 256
    return encoder


def encode_index(encoder, chunks, config):
    return encoder.encode([c['text'] for c in chunks], normalize_embeddings=True,
                          batch_size=config['batch_size'], show_progress_bar=True)


def vector_pool(encoder, embeddings, chunks, query, k):
    import numpy as np

    vector = encoder.encode(query, normalize_embeddings=True, show_progress_bar=False)
    scores = embeddings @ vector
    indices = np.argsort(-scores, kind='stable')[:k]
    candidates = [chunks[int(i)] for i in indices]
    return candidates, scores, indices


def cpu_model():
    path = Path('/proc/cpuinfo')
    if path.is_file():
        for line in path.read_text().splitlines():
            if line.startswith('model name'):
                return line.split(':', 1)[-1].strip()
    return platform.processor() or platform.machine()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=0, help='Seeded pilot subset; 0 uses all labeled queries')
    parser.add_argument('--pilot-runs', type=int, help='Override repetitions only with --limit')
    args = parser.parse_args()
    if args.limit < 0 or (args.pilot_runs is not None and (not args.limit or args.pilot_runs < 1)):
        parser.error('Provide a nonnegative --limit and use positive --pilot-runs only with a pilot')
    config = read_json('config.json')
    configure_cpu(config)
    import numpy as np
    from sentence_transformers import CrossEncoder

    data = read_json('data/prepared.json')
    manifest = read_json('data/manifest.json')
    if manifest['config'] != config or manifest['prepared_sha256'] != digest('data/prepared.json'):
        raise ValueError('Prepared data/config changed; rerun make prepare')
    chunks = data['chunks']
    queries = data['queries']
    if args.limit:
        queries = random.Random(config['seed']).sample(queries, min(args.limit, len(queries)))
    runs = args.pilot_runs or config['runs']
    encoder = load_encoder(config)
    reranker = CrossEncoder(config['reranker']['id'], revision=config['reranker']['revision'],
                           device='cpu', max_length=512, local_files_only=True)
    index_start = time.perf_counter()
    embeddings = encode_index(encoder, chunks, config)
    index_ms = (time.perf_counter() - index_start) * 1000

    def retrieve(query, rerank):
        start = time.perf_counter_ns()
        candidates, scores, indices = vector_pool(encoder, embeddings, chunks, query, config['candidate_k'])
        retrieved_ns = time.perf_counter_ns()
        cross_scores = None
        if rerank:
            cross_scores = reranker.predict([(query, c['text']) for c in candidates],
                                            batch_size=config['batch_size'], show_progress_bar=False)
            ordering = np.argsort(-cross_scores, kind='stable')
            ordered = [candidates[int(i)] for i in ordering]
        else:
            ordered = candidates
        docs = unique_docs(ordered, config['output_k'])
        stop = time.perf_counter_ns()
        return {'docs': docs, 'latency_ms': (stop - start) / 1e6,
                'retrieval_ms': (retrieved_ns - start) / 1e6,
                'candidates': [c['id'] for c in candidates],
                'vector_scores': [float(scores[i]) for i in indices],
                'cross_scores': None if cross_scores is None else [float(s) for s in cross_scores]}

    for query in queries[:3]:
        retrieve(query['text'], False)
        retrieve(query['text'], True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = Path('results') / (('pilot-' if args.limit else '') + stamp)
    git = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True)
    write_json(output / 'environment.json', {
        'config': config, 'data': manifest, 'platform': platform.platform(),
        'cpu': cpu_model(), 'logical_cpus': os.cpu_count(), 'python': sys.version,
        'packages': {p: importlib.metadata.version(p) for p in
                     ['numpy', 'torch', 'sentence-transformers', 'transformers', 'huggingface-hub', 'pyarrow']},
        'git_commit': git.stdout.strip() if git.returncode == 0 else None,
        'source_sha256': {f: digest(f) for f in ('ragstudy/measure.py', 'ragstudy/common.py', 'ragstudy/prepare.py')},
        'device': 'cpu', 'index_build_ms': index_ms, 'index_dtype': str(embeddings.dtype),
        'index_shape': list(embeddings.shape), 'index_bytes': embeddings.nbytes,
        'warmup_queries': min(3, len(queries)), 'pilot': bool(args.limit),
        'query_count': len(queries), 'run_count': runs})
    write_json(output / 'chunk-map.json', {c['id']: c['doc_id'] for c in chunks})
    print(f'Measuring {len(queries)} queries × {runs} passes in {output}', flush=True)
    for run in range(runs):
        order = list(queries)
        random.Random(config['seed'] + run).shuffle(order)
        rows = []
        for i, query in enumerate(order):
            arms = ['baseline', 'reranked'] if (run + i) % 2 == 0 else ['reranked', 'baseline']
            row = {'query_id': query['id'], 'query': query['text'], 'relevant': data['qrels'][query['id']], 'order': arms}
            for arm in arms:
                row[arm] = retrieve(query['text'], arm == 'reranked')
            rows.append(row)
            if (i + 1) % 25 == 0:
                print(f'Run {run + 1}/{runs}: {i + 1}/{len(order)}', flush=True)
        write_json(output / f'run-{run + 1:02d}.json', {'run': run + 1, 'queries': rows})
    replay(output)
    print(f'Raw results: {output}')


if __name__ == '__main__':
    main()
