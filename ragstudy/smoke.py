"""An offline fixture exercises logging and replay, never a model benchmark."""
from .common import write_json
from .replay import replay

rows = [{'query_id': 'fixture', 'relevant': ['A', 'B'],
         'baseline': {'docs': ['X', 'A', 'Y', 'Z', 'W'], 'latency_ms': 2.0},
         'reranked': {'docs': ['B', 'A', 'X', 'Y', 'Z'], 'latency_ms': 12.0}}]
for run in range(5):
    write_json(f'results/smoke/run-{run + 1:02d}.json', {'fixture_only': True, 'queries': rows})
result = replay('results/smoke')
assert result['runs'][0]['baseline']['mrr_at_5'] == .5
assert result['runs'][0]['reranked']['recall_at_5'] == 1
print('PASS: synthetic logging/replay fixture. These are not scientific results.')
