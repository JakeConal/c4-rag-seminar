# C4 speaking and question preparation

For a full Vietnamese learning path with worked examples, exercises and code walkthroughs, read [STUDY-GUIDE.vi.md](STUDY-GUIDE.vi.md).

This guide covers the concepts behind the measured study. It is supplementary to the three-page report. Official sources below were read on 2026-11-21.

## Where chunking and reranking fit

RAG couples retrieved external material with a generator. Retrieval quality and generated-answer quality are different evaluation targets; this seminar measures retrieval. [Lewis et al.](https://arxiv.org/abs/2005.11401)

Our path is documents → token chunks → stored embeddings → query embedding → cosine candidate search → optional cross-encoder → five distinct document IDs. A bi-encoder permits document vectors to be computed in advance. The cross-encoder scores each query and candidate jointly, so its work occurs for each query. Our reranker scores 50 pairs rather than the entire corpus. [Sentence Transformers retrieve-and-rerank documentation](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html)

## Chunking choices to explain

| Choice | What to consider in this study |
| --- | --- |
| Fixed token windows | Reproducible size in the embedding tokenizer's units; can split a sentence or separate evidence |
| Overlap | Gives boundary text another window; repeats text and increases vector count |
| Smaller window | Changes context per vector, number of vectors, stride and which chunks compete for the candidate pool |
| Larger window | Carries more surrounding text but is constrained by model input limits |
| Sentence/paragraph boundaries | Preserve a chosen structural unit; not evaluated by the fixed-window comparison |
| Semantic boundaries | Seek content-based breaks; require a separate, fully specified splitter and experiment |

These are design considerations, not evidence that one strategy always wins. The main experiment fixes window length 192 and absolute overlap 32. The secondary comparison changes length to 96 while retaining overlap 32; conclusions concern those two concrete configurations. Do not generalize it to all chunking methods. The pinned embedding model card specifies its input truncation limit. [Model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/tree/1110a243fdf4706b3f48f1d95db1a4f5529b4d41)

## Metrics to explain without mixing units

For query q, let R be its set of positively judged source documents and D its first five distinct retrieved documents.

- Recall@5 = |D ∩ R| / |R|. This asks how much of the judged evidence was recovered.
- Reciprocal rank@5 = 1 / rank of the first relevant document, or zero when none appears. MRR@5 averages that value across queries.
- Quality differences use percentage points: a rise from 0.60 to 0.65 is +5 pp, not +5% relative.
- Latency p50/p95 summarizes query times within each pass. Across five passes, report the median and spread of those pass summaries.
- Added latency pairs treatment and baseline timings for the same query within a pass before taking percentiles.
- Candidate-pool recall asks whether the first-stage 50 chunks contain the relevant parents. The reranker cannot recover a parent absent from its inputs.

Our implementations and raw logs define these formulas. Repeated chunks from one parent cannot create multiple relevant-document hits. Repeating deterministic queries five times characterizes timing variation; it does not create five independent datasets or establish generalization.

## Questions to rehearse

1. **Why no vector database?** Exact in-memory cosine search keeps the retrieval implementation fixed and removes approximate-search tuning from this question. The study makes no scaling claim about production databases.
2. **Why no LLM answer?** The registered metrics require labeled retrieval, so generated answers would add another model, cost and evaluation target.
3. **Can reranking make a query worse?** Yes; inspect measured per-query wins and losses. Its score is a ranking signal, not proof that a document supports the claim.
4. **Why document-level scoring with chunk retrieval?** SciFact labels source documents. We map chunks back to parent IDs and collapse duplicates before evaluating five results.
5. **What could change the recommendation?** A different domain, model, chunk strategy, candidate depth, device, concurrency or latency budget. This experiment does not vary those together.
6. **What if quality does not improve?** Report that result and its measured cost. The rubric accepts a supported negative finding.

A retrieved chunk can inherit a relevant parent ID without containing the specific evidence itself. Our labels therefore support document-level retrieval claims, not proof that every selected chunk provides sufficient answer context. Relevance also does not mean a scientific claim is true; evidence can address a claim by supporting or refuting it.

BEIR provides context for evaluating retrieval across domains; our single-dataset result is narrower than its benchmark. [Thakur et al.](https://arxiv.org/abs/2104.08663)
