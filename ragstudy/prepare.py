"""Download immutable inputs and build one fixed chunk corpus for both arms."""
import csv
import io
import os
from pathlib import Path

from .common import digest, read_json, token_windows, write_json


MODEL_FILES = (
    'config.json', 'model.safetensors', 'special_tokens_map.json', 'tokenizer.json',
    'tokenizer_config.json', 'vocab.txt',
)
EMBEDDING_FILES = (
    '1_Pooling/config.json', 'config_sentence_transformers.json', 'modules.json',
    'sentence_bert_config.json',
)


def build_chunks(corpus_rows, tokenizer, size, overlap):
    chunks = []
    for row in sorted(corpus_rows, key=lambda row: str(row['_id'])):
        text = (row.get('title', '') + '\n' + row['text']).strip()
        ids = tokenizer.encode(text, add_special_tokens=False, verbose=False)
        for i, window in enumerate(token_windows(ids, size, overlap)):
            chunks.append({'id': f"{row['_id']}:{i}", 'doc_id': str(row['_id']), 'text': tokenizer.decode(window)})
    return chunks


def main():
    os.environ.setdefault('HF_HOME', str(Path('.cache/huggingface').resolve()))
    from huggingface_hub import hf_hub_download, snapshot_download
    import pyarrow.parquet as pq
    from transformers import AutoTokenizer

    config = read_json('config.json')
    dataset = config['dataset']
    sources = {}
    tables = {}
    for name in ['corpus', 'queries']:
        filename = f'{name}/{name}-00000-of-00001.parquet'
        path = hf_hub_download(dataset['id'], filename, repo_type='dataset', revision=dataset['revision'])
        sources[filename] = digest(path)
        tables[name] = pq.read_table(path).to_pylist()
    qpath = hf_hub_download(dataset['qrels_id'], 'test.tsv', repo_type='dataset', revision=dataset['qrels_revision'])
    sources['test.tsv'] = digest(qpath)
    qrels = {}
    for row in csv.DictReader(io.StringIO(Path(qpath).read_text()), delimiter='\t'):
        if int(row['score']) > 0:
            qrels.setdefault(str(row['query-id']), []).append(str(row['corpus-id']))
    queries = [{'id': str(row['_id']), 'text': row['text']} for row in tables['queries'] if str(row['_id']) in qrels]
    queries.sort(key=lambda row: row['id'])
    if len(queries) != len(qrels) or not queries:
        raise ValueError('Query/judgment mismatch')
    model_sources = {}
    for key, files in [('embedding', MODEL_FILES + EMBEDDING_FILES), ('reranker', MODEL_FILES)]:
        model = config[key]
        snapshot = Path(snapshot_download(model['id'], revision=model['revision'], allow_patterns=files))
        model_sources[key] = {filename: digest(snapshot / filename) for filename in files}
    tokenizer = AutoTokenizer.from_pretrained(config['embedding']['id'], revision=config['embedding']['revision'])
    doc_ids = {str(row['_id']) for row in tables['corpus']}
    if any(doc not in doc_ids for docs in qrels.values() for doc in docs):
        raise ValueError('Qrels refer to missing documents')
    chunks = build_chunks(tables['corpus'], tokenizer, config['chunk_tokens'], config['chunk_overlap'])
    write_json('data/prepared.json', {'chunks': chunks, 'queries': queries, 'qrels': qrels})
    write_json('data/manifest.json', {'config': config, 'source_sha256': sources,
                                    'model_sha256': model_sources,
                                    'prepared_sha256': digest('data/prepared.json'),
                                    'documents': len(doc_ids), 'chunks': len(chunks), 'queries': len(queries)})
    print(f'Prepared {len(chunks)} chunks and {len(queries)} labeled test queries.')


if __name__ == '__main__':
    main()
