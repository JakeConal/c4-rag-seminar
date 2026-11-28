https://github.com/JakeConal/c4-rag-seminar

# Chunking and Cross-Encoder Reranking for Retrieval-Augmented Generation

Dương Khánh Khải Hưng (23120045) · Nguyễn Minh Hiếu (23120124) · Huỳnh Thái Toàn (23120175)

CSC13114 CQ2023/3 · C4 seminar · Empirical retrieval study

**Abstract—** We compare dense retrieval with cross-encoder reranking of fifty candidate chunks, selecting five distinct documents for retrieval-augmented generation. Five paired passes over 300 SciFact claims show gains of 6.15 percentage points in mean reciprocal rank at five and 4.64 points in recall at five. On the recorded processor, total retrieval latency at the ninety-fifth percentile increases from 115.7 to 2001.0 milliseconds; paired added latency is 1928.3 milliseconds at that percentile. A separate vector-only comparison of smaller chunks yields modest quality gains at 2.18 times the embedding-matrix storage. These findings identify a quality–latency trade-off, bounded by candidate coverage, document-level judgments and a single-host evaluation.

**Keywords—** retrieval-augmented generation; chunking; dense retrieval; cross-encoder reranking; latency evaluation.

## I. Introduction

**Does reranking the vector top 50 with a cross-encoder improve MRR@5 and recall@5 over vector top five, and how many milliseconds does it add at p50 and p95?**

RAG supplies retrieved evidence to a generator [1]. Chunking determines which text is represented together; reranking determines which candidates reach the final context. A bi-encoder permits precomputed document vectors, while a cross-encoder jointly processes a query and candidate at request time [2]. We evaluate retrieval through five distinct document IDs. SciFact labels evidence that supports or refutes scientific claims [3]; relevance therefore does not imply that the claim is true.

## II. Methods

**Corpus and chunks.** All 5,183 SciFact abstracts become 12,434 chunks; evaluation uses all 300 positively judged BEIR test claims. Title and abstract are tokenized together into 192-token windows, with overlap 32 and stride 160. Overlap can preserve boundary text but repeats content, increasing index size and competition for candidate slots. The encoder input limit is 256 tokens; the cross-encoder accepts up to 512 tokens per pair. [Pinned data, judgments and model cards](docs/SOURCES.md)

**Baseline and treatment.** Both arms independently encode the query with all-MiniLM-L6-v2 and retrieve the same top 50 chunks using exact cosine similarity over normalized vectors. The baseline keeps vector order; the treatment scores all 50 query–chunk pairs using ms-marco-MiniLM-L6-v2 and sorts by score. In both arms, the highest-ranked chunk determines each parent's position; scanning returns five unique parents. This prevents overlapping chunks from earning duplicate document-level credit. All other retrieval settings remain fixed.

**Paired protocol.** Each claim runs through both arms, alternating which goes first. Five passes shuffle claims with seeds 42–46 after three warmup queries per arm. Queries execute sequentially on one host, using float32, four PyTorch/BLAS threads and batch size 16 where applicable. Timing starts at query encoding and ends at five final IDs; downloading, model loading, chunking, index construction and warmup are excluded. This yields 1,500 paired observations.

**Recorded environment.** Intel Core i5-11400H, four visible logical CPUs, WSL2 Linux x86-64 kernel 6.6.87.2; CPython 3.12.3, PyTorch 2.8.0+cpu, Sentence Transformers 5.1.2, Transformers 4.57.1, NumPy 2.2.6, PyArrow 21.0.0 and Hugging Face Hub 0.36.0. Dependencies are hash-locked; model/data revisions and input hashes are preserved in the [environment manifest](results/20261121T122915162545Z/environment.json).

**Metric definitions.** For each query, reciprocal rank@5 is 1/r, where r is the first relevant parent's rank within the top five, or zero if absent. Recall@5 is the number of retrieved relevant parents divided by all positively judged parents for that query. Both are averaged over queries with equal weight. For illustration, finding one of two relevant parents first at rank two gives reciprocal rank 0.5 and recall 0.5. Unjudged documents receive zero credit.

**Aggregation.** Calculate quality means and latency p50/p95 within each pass, then report the median [minimum–maximum] of the five pass summaries. Added latency is computed from each query's paired treatment-minus-baseline time before taking percentiles. Subtracting the two arms' aggregate p95 values does not produce paired added p95. Quality changes use unrounded values and percentage points (pp).


<!-- pagebreak -->

## III. Results

### A. Primary reranking results

All quality values were identical across five passes. Table I reports medians [minimum–maximum] across those passes; latency changes are paired as defined in Section II. [Aggregate and raw-run links](results/20261121T122915162545Z/summary.json)

**TABLE I. Retrieval quality and latency on 300 SciFact claims across five paired passes.**

| Metric | Vector top five | Reranked top five | Change |
| --- | --- | --- | --- |
| MRR@5 | 61.05% | 67.20% | +6.15 pp |
| Recall@5 | 73.07% | 77.72% | +4.64 pp |
| p50 (ms) | 27.6 [26.2–33.1] | 1554.4 [1518.9–1687.2] | +1511.0 [+1469.5–+1636.7] paired |
| p95 (ms) | 115.7 [115.4–116.0] | 2001.0 [1725.6–2109.7] | +1928.3 [+1649.7–+2049.4] paired |

**Cost.** Reranking improves both quality measures on this test set but adds substantial inference work: 50 jointly encoded pairs for every query. The approximately two-second total p95 is retrieval time alone; serving and answer generation would require additional budget. The shared float32 embedding matrix occupies 18.21 MiB and took 353.4 seconds to build outside query timing. Matrix size excludes model and runtime memory. Local inference has no API fees, while still consuming CPU time and storage.

**Variation across queries.** In the first pass, reciprocal rank improves for 67 claims, ties for 193 and worsens for 40; recall improves for 30, ties for 259 and worsens for 11. Aggregate gains therefore coexist with regressions. Claim 5's relevant parent moves from vector rank 8 to reranked rank 1. Claim 535 falls from rank 1 to outside the first five. These traces establish changes in ordering; they do not establish why the model prefers a particular passage. [Raw first pass](results/20261121T122915162545Z/run-01.json)

**Candidate bottleneck.** Fifty chunks represent only 35.3 distinct parents on average. For 32 of 300 claims, including claim 132, no judged relevant parent enters the pool. Even perfect ordering would cap recall@5 at 88.63% for these pools. All pools contain at least five distinct parents, so the baseline's output matches scanning the full vector ranking for five unique parents. Better scoring can address poor ordering among available candidates; missing evidence requires changes to first-stage retrieval. [Chunk-to-parent mapping](results/20261121T122915162545Z/chunk-map.json)

**Failure decomposition.** Of 61 claims with no judged hit in the reranked top five, 32 lack a relevant parent anywhere in the pool and 29 contain a relevant parent that finishes outside the top five. Relative to vector order, reranking newly recovers at least one relevant parent for 25 claims and loses every top-five hit for 10. These are any-hit counts, distinct from macro recall and reciprocal-rank changes. They separate a candidate-generation problem from a remaining ordering problem and provide concrete cases for subsequent investigation.

### B. Supplementary chunking results

A separate deterministic, vector-only pass compares 96-token and 192-token windows on the same 300 claims, keeping absolute overlap at 32. Stride falls from 160 to 64, and relative overlap rises from 16.7% to 33.3%. The comparison therefore concerns these two configurations, including their changed overlap ratio and candidate competition. [Observations and summary](results/20261121T122915162545Z/chunk-ablation/summary.json)

**TABLE II. Vector-only chunking comparison at fixed 32-token overlap; one deterministic pass.**

| Measure | 192-token window | 96-token window | Change |
| --- | --- | --- | --- |
| Indexed chunks | 12,434 | 27,090 | +14,656 |
| Embedding matrix | 18.21 MiB | 39.68 MiB | 2.18× |
| MRR@5 | 61.05% | 61.78% | +0.73 pp |
| Recall@5 | 73.07% | 74.47% | +1.40 pp |
| Top-50 pool recall | 88.63% | 89.70% | +1.07 pp |

Table II shows that smaller windows yield modest ranking and coverage gains at more than twice the matrix storage. Reciprocal rank improves for 39 claims and worsens for 40, showing that the average also depends on the magnitude of changes. This pass measures quality and matrix size; it provides no chunking latency or reranker-interaction result. Sentence, paragraph and semantic boundaries remain alternative designs to test [4].

## IV. Discussion

**Recommendation.** Consider reranking where the observed gains justify about two seconds of total p95 retrieval latency on this CPU. Prefer vector order for tighter budgets after reserving time for serving and generation. Diagnose candidate coverage before investing in a stronger reranker. Selective reranking is a possible deployment strategy that still needs validation; it was not measured here.

**Validity.** Five repeats characterize timing variation on one fixed test set, not uncertainty over new datasets; no significance test or confidence interval is claimed. Document judgments can credit a retrieved chunk whose parent contains evidence elsewhere. Incomplete judgments, truncation and unverified training-data overlap with SciFact constrain interpretation. Both arms pay for the same exact top-50 search and sort, rather than an optimized top-five-only baseline. Results apply to this corpus, model pair and warm sequential CPU workload; cold starts, concurrency, alternative hardware and generated-answer quality require separate evaluation.

**Next experiments.** Vary candidate depth under fixed chunking to measure coverage, quality and paired latency together. Then evaluate chunk-size/reranker combinations and passage-level evidence, followed by concurrent serving load. These experiments would test whether the current recommendation survives a different retrieval budget and more realistic use.

## V. Conclusion

At fixed candidate depth and chunking, cross-encoder reranking improves document ranking on SciFact while adding substantial query-time computation. The measured gains support evaluation under a roughly two-second retrieval budget on this host. The separate smaller-window result trades additional matrix storage for modest quality gains. Neither result establishes passage-level evidence sufficiency or generated-answer quality.

## VI. Reproducibility


Clone the repository above; run `make setup`, `make prepare`, then `make study`. To audit saved measurements without model inference, run `make replay RESULTS=results/20261121T122915162545Z`; the supplementary replay is documented in README. Public cloning and both saved-log replays passed. [Validation evidence](docs/VALIDATION.md) · [Display-value provenance](results/20261121T122915162545Z/presentation-values.json)

## References

[1] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” *Advances in Neural Information Processing Systems*, vol. 33, 2020. [Paper](https://arxiv.org/abs/2005.11401).

[2] Sentence Transformers, “Retrieve & Re-Rank,” documentation. Accessed: Nov. 21, 2026. [Online](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html).

[3] D. Wadden et al., “Fact or Fiction: Verifying Scientific Claims,” *Proceedings of EMNLP*, pp. 7534–7550, 2020. [Paper](https://aclanthology.org/2020.emnlp-main.609/).

[4] R. Qu et al., “Is Semantic Chunking Worth the Computational Cost?” *Findings of the Association for Computational Linguistics: NAACL 2025*, pp. 2155–2177, 2025. [Paper](https://aclanthology.org/2025.findings-naacl.114/).

Research sources accessed Nov. 21, 2026; bibliographic metadata rechecked Nov. 26, 2026. Pinned model/data cards, official package releases and SciFact attribution: [complete source register](docs/SOURCES.md). AI assistance and verification: [AI-LOG.md](AI-LOG.md).
