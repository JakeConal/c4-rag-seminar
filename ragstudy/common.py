import hashlib
import json
import math
import statistics
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def unique_docs(chunks, k=5):
    return list(dict.fromkeys(c['doc_id'] for c in chunks))[:k]


def metrics(ranked, relevant, k=5):
    if not relevant:
        raise ValueError('Queries without positive judgments must not enter evaluation')
    ranked = list(dict.fromkeys(ranked))[:k]
    hits = [i + 1 for i, doc in enumerate(ranked) if doc in relevant]
    return {'recall_at_5': len(hits) / len(relevant), 'mrr_at_5': 1 / hits[0] if hits else 0.0}


def query_change_counts(deltas):
    return {'improved': sum(d > 0 for d in deltas), 'tied': sum(d == 0 for d in deltas),
            'worsened': sum(d < 0 for d in deltas)}


def percentile(values, p):
    values = sorted(values)
    if not values:
        raise ValueError('Empty sample')
    position = (len(values) - 1) * p
    lo, hi = math.floor(position), math.ceil(position)
    return values[lo] + (values[hi] - values[lo]) * (position - lo)


def spread(values):
    return {'median': statistics.median(values), 'min': min(values), 'max': max(values),
            'q25': percentile(values, .25), 'q75': percentile(values, .75)}


def token_windows(ids, size, overlap):
    if not 0 <= overlap < size:
        raise ValueError('Require 0 <= overlap < size')
    for start in range(0, len(ids), size - overlap):
        yield ids[start:start + size]
        if start + size >= len(ids):
            break
