# C4 — Chunking and reranking for RAG

Team: **23120045–23120124–23120175** · CSC13114 CQ2023/3.

Question registered in Classroom: Does adding a cross-encoder reranker (vector top-50 reranked to top-5) improve MRR and recall@5 over plain vector top-5, and how many ms (p50, p95) does it add per query?

Start with the [Vietnamese study guide](docs/STUDY-GUIDE.vi.md) for lessons from first principles, worked examples, exercises, and a map to the report and slides. The [topic guide](docs/TOPIC-GUIDE.md) covers chunking choices, both model stages, metric formulas and questions to rehearse. [Submission requirements](docs/REQUIREMENTS.md) track every rubric item.

## Measured primary result

Five passes over all 300 SciFact test queries on the recorded CPU host gave the following medians. Quality scores were identical in every pass.

| Metric | Vector order | Reranked |
| --- | ---: | ---: |
| MRR@5 | 0.6105 | 0.6720 |
| Recall@5 | 73.07% | 77.72% |
| Total query p50 | 27.65 ms | 1554.38 ms |
| Total query p95 | 115.74 ms | 2000.97 ms |

The quality changes are **+6.15 percentage points MRR@5** and **+4.64 percentage points recall@5**, calculated before rounding. Paired added latency was **1511.02 ms p50** (run range 1469.51–1636.68) and **1928.33 ms p95** (1649.70–2049.38). Paired quantiles differ from subtracting the two methods' percentile medians. See [the five-pass summary](results/20261121T122915162545Z/summary.json), its raw run files, and [the independent audit](docs/REVIEW.md). These are retrieval results for this dataset, model pair and CPU configuration.

The separate **96/32 versus 192/32** vector-only comparison raised MRR@5 from 0.6105 to 0.6178 and recall@5 from 73.07% to 74.47%. Its float32 embedding matrix grew from 18.21 to 39.68 MiB (2.18×). It measures quality and matrix storage, not latency or the interaction with reranking. [Secondary observations and summary](results/20261121T122915162545Z/chunk-ablation/)

## Setup from a fresh clone

The reproducibility target is **Linux/WSL x86-64 with CPython 3.12**, Git, curl and make. CPU execution is explicit; no Docker, GPU, model API key, or paid service is required. Allow several GB of disk space for packages and model caches. Installation/preparation need internet; measurement and replay run offline. Keep the machine idle and use the same power profile for timing.

Clone the public repository, enter it, then run:

```bash
git clone https://github.com/JakeConal/c4-rag-seminar.git
cd c4-rag-seminar
make setup
make prepare
make study
```

`make setup` bootstraps a pinned, checksum-verified uv executable locally under `.cache/uv-bin`, creates `.venv` without requiring system pip/ensurepip, and installs the **complete hash-locked environment** from `requirements.txt`. `requirements.in` records the selected direct dependencies; the lock includes CPU PyTorch and all transitive dependencies. Setup checks consistency, imports and CPU tensor execution, and records installed versions in `results/environment/requirements.resolved.txt`. No sudo is needed. Set `PYTHON_BIN=/path/to/python3.12` if your default python3 has a different version.

`make prepare` downloads SciFact corpus/queries and **test judgments** at immutable Hugging Face commits, downloads both models at pinned commits, creates identical token chunks for both arms, and hashes the inputs/model files. The cache lives in `.cache/huggingface`; generated data lives in `data/`.

**`make study` is the one-command full measurement.** It runs the primary reranking comparison for five passes, then the separate chunk-size analysis, and writes its output path to `results/latest-study.txt`. Do not run competing model jobs during primary timing. `make measure` runs just the primary experiment. Corpus embeddings are rebuilt outside query timing on each invocation.

Quick checks and a pilot:

```bash
make doctor
make test
make smoke
.venv/bin/python -m ragstudy.measure --limit 10 --pilot-runs 1
```

The smoke command needs only standard Python. It uses **synthetic fixtures**, writes to ignored `results/smoke/`, and does not validate model inference or produce reportable measurements. Pilots write to `results/pilot-*`; use the full study for reportable results.

## Outputs and replay

Every measurement creates a new `results/<UTC timestamp>/` directory containing `environment.json`, `chunk-map.json`, five `run-*.json` logs, and `summary.json`. Every run includes query IDs/text, positive judgments, both arms' final parent-document rankings, top-50 chunk candidates and vector scores, reranker scores, execution order and latency in ms. Track the full directory for the study you report.

```bash
study_dir=$(cat results/latest-study.txt)
make replay RESULTS="$study_dir"
python3 -m ragstudy.chunk_ablation "$study_dir" --replay
```

Replay reconstructs parent rankings from raw scores and checks paired candidate pools, query/judgment identities, finite timings and complete passes. It recomputes summaries with standard Python; it does not rerun inference or remeasure latency. Measurement reports per-run mean recall@5 and MRR@5 and per-query p50/p95 latency. Across-run summaries include median, min, max, Q25 and Q75. Added latency is the percentile of **paired per-query differences**. This is distinct from subtracting two latency percentiles.

The supplementary `chunk-ablation/` directory stores a vector-only 96-token/32-overlap comparison against the main 192/32 baseline for the same test queries. It reports quality, pool recall and index size. This is a deterministic quality analysis, not a five-pass latency study or a claim about chunk-size/reranker interactions. Keeping absolute overlap fixed changes relative overlap and stride as a consequence of changing window size.

## What is controlled

- SciFact test queries and document judgments; the full corpus is retained.
- Token chunks of 192 embedding-tokenizer tokens, overlap 32; title is included before splitting. Chunk text is decoded without special tokens. Encoder input limit 256; cross-encoder pair limit 512. Long inputs can be truncated at the model limits.
- Normalized MiniLM embeddings, exact cosine search, CPU float32, four PyTorch threads, batch size 16, sequential queries, three warmup queries per arm, deterministic query-order seeds.
- Both arms retrieve the same top-50 chunk pool. Baseline returns the first five **distinct parent documents** in vector order; treatment scores the same 50 chunks with the cross-encoder then returns the first five distinct parents. A parent counts once even if several chunks match. Candidate recall is limited by the 50-chunk pool. Check the summary's count of pools with fewer than five parents before claiming equivalence to unconstrained vector top-five parent retrieval. Baseline latency includes the controlled common top-50 search/sort work, not an optimized top-five-only index.
- Both arms independently time query embedding, search, sorting and parent collapse; treatment additionally times reranking. Invocation order alternates. Model loading, downloads, chunk construction, corpus embedding and warmup are outside query latency. No query/result cache is used.

MRR is explicitly **MRR@5**, matching the five returned documents. Recall@5 divides retrieved relevant parents by all positively judged parents for that query. Unjudged documents count as nonrelevant; judgment incompleteness is a limitation. This is retrieval evaluation, not generated-answer quality. Chunking is held fixed for the registered question and varied only in the separately labeled secondary analysis.

The pinned BEIR distribution lists CC BY-SA 4.0. Logs contain claim text and judgment identifiers; retain the attribution in [docs/SOURCES.md](docs/SOURCES.md), which also records the original SciFact terms. The dataset is downloaded into an ignored directory rather than bundled with the repository.

## Status

The full fresh-clone study completed successfully: [official results](results/20261121T122915162545Z/), [setup and study transcript](results/verification/fresh-clone.log), and [latest-study pointer](results/latest-study.txt). See [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md) for installation evidence, [docs/VALIDATION.md](docs/VALIDATION.md) for checks, and [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) for the assignment review. Local artifacts do not establish public repository access or recording completion.

The public repository is [https://github.com/JakeConal/c4-rag-seminar](https://github.com/JakeConal/c4-rag-seminar). An all-member recording and its accessible URL remain pending. English and Vietnamese speaking scripts are in [TALK.md](TALK.md) and [TALK.vi.md](TALK.vi.md). Check readiness with `python3 scripts/submission_check.py`. After review, `python3 scripts/package_submission.py --draft` creates a clearly labeled review archive including `.git`. The final command `python3 scripts/package_submission.py --score <total>` requires completed deliverables and the same evidence-backed self-assessment total as the filename. Keep environments/caches out of the zip.
