# C4 recording and speaker script

Recording: pending

**Recording plan: 7:45, slides 1–12.** Slides 13–16 are reference and Q&A material. The recording must remain at or below eight minutes. The timings below are rehearsal targets, not a measured recording duration. Read only the narration paragraphs aloud; directions, commands and Q&A are preparation material. Allow about 20 seconds for the prepared log demonstration and transitions. Rehearse with a stopwatch and aim for a clear, conversational pace; trim optional detail if the exported recording exceeds the limit.

Open `slides.pdf` and a terminal at the repository root. Run the commands in “Prepare the evidence demonstration” before recording, enlarge the terminal font, and keep the resulting output visible. Show the saved measurement logs during the talk; replay validates those observations without rerunning model inference.

## Dương Khánh Khải Hưng · 23120045 · Slides 1–4

### Slide 1 · 0:00–0:30 · The question and headline

A RAG system can produce a poor answer when the right evidence never reaches its generator. Our topic is chunking and reranking: how to divide documents and select useful evidence. We ask whether reranking the vector top fifty improves the five documents we keep, and what it costs. On SciFact, MRR improved by 6.15 percentage points, with about 1.93 seconds of paired added p95 latency.

### Slide 2 · 0:30–1:00 · Where retrieval fits

Offline, we split documents and store an embedding for each chunk. At query time, we embed the question, retrieve candidate chunks, optionally rerank them, and select evidence. A complete RAG application would then pass that evidence to a generator. Our benchmark stops at five document IDs. It evaluates evidence retrieval; it cannot tell us whether generated answers are correct or well supported.

### Slide 3 · 1:00–1:45 · Two ways to score relevance

A bi-encoder represents the query and each chunk separately. Stored chunk vectors make cosine search inexpensive at query time. A cross-encoder reads the query and candidate together, allowing their tokens to interact before it assigns a relevance score. That requires fresh inference for each pair. We score fifty pairs instead of the entire corpus. Both arms receive the same fifty candidate chunks. Since overlapping chunks can come from one abstract, we scan each ranking and keep the first five distinct parent documents. Duplicate chunks cannot earn extra recall credit.

### Slide 4 · 1:45–2:25 · Why boundaries matter

Our main configuration uses 192-token windows and 32-token overlap: the second window starts at token 161. Overlap gives boundary text another chance to stay together, but repeats content and creates more vectors. Small chunks can focus a match while losing surrounding context; larger chunks preserve context but face input limits. Sentence and paragraph splitting preserve structural boundaries; semantic splitting seeks changes in meaning. We test fixed windows only. Keeping chunking identical in the main comparison isolates the reranking change.

## Nguyễn Minh Hiếu · 23120124 · Slides 5–9

### Slide 5 · 2:25–3:05 · A controlled comparison

We split 5,183 SciFact abstracts into 12,434 chunks and evaluate 300 test claims. Each claim runs through both arms. We alternate their order and shuffle the claims across five passes: fifteen hundred paired observations. Models, data, candidate depth and CPU conditions stay fixed. Both arms independently encode the query. Timing ends when five distinct document IDs are ready. Downloads, index construction, model loading and warmup are excluded. Five repeats describe timing variation on this host; they do not create five independent datasets.

### Slide 6 · 3:05–3:40 · What the metrics mean

Consider an illustrative query with two relevant documents, A and B. If our top five contain A at rank two but miss B, reciprocal rank is one half and recall is one half. Move A to rank one and reciprocal rank becomes one. Recover B as well and recall becomes one. MRR averages reciprocal rank over queries; recall averages the recovered fraction for each query. A query with no relevant result in its top five receives zero for both.

### Slide 7 · 3:40–4:15 · Quality improves, but not for everyone

MRR rose from 61.05 to 67.20 percent. Recall rose from 73.07 to 77.72 percent. These are gains of 6.15 and 4.64 percentage points, calculated before rounding. Rankings were identical across the five passes. Looking beyond averages, reciprocal rank improved for 67 claims, stayed unchanged for 193, and worsened for 40. Recall improved for thirty and worsened for eleven. Reranking helps overall here, but it can demote useful evidence.

### Slide 8 · 4:15–5:00 · The latency bill

P50 is the median query time; p95 describes the slower tail. The slide reports the median of five pass-level percentiles, with their minimum and maximum. Baseline p50 and p95 were 27.6 and 115.7 milliseconds. With reranking, they reached 1554.4 and 2001.0 milliseconds. To calculate added latency, we subtract baseline time from treatment time for each paired query before computing percentiles. Added p95 is 1928.3 milliseconds. Subtracting the two displayed p95 values would answer a different question. Joint scoring improves ranking here, but dominates retrieval time on this CPU.

### Slide 9 · 5:00–5:45 · Inspect the evidence

Here is the saved log for claim five. Its judged relevant document moves from vector parent rank eight to reranked rank one. Claim 535 shows the opposite: rank one falls outside the top five. Claim 132 has no judged relevant document in the candidate pool. Thirty-two claims have this problem. Even perfect ordering of these pools would cap recall at 88.63 percent. A reranker cannot recover evidence it never receives.

*Direction: switch to the prepared terminal output, point to claim 5's relevant ID and both rankings, then return to the deck. Reserve about 15 seconds here. Do not describe the saved-log replay as a new benchmark run.*

## Huỳnh Thái Toàn · 23120175 · Slides 10–12

### Slide 10 · 5:45–6:25 · A separate chunking experiment

We also compare 96-token windows with the main 192-token windows, keeping overlap at 32. Stride changes from 160 to 64, so relative overlap increases too. The smaller windows produce 27,090 chunks and grow the embedding matrix from 18.21 to 39.68 mebibytes. MRR improves by 0.73 percentage points and recall by 1.40. This is a modest quality gain for more than twice the matrix storage. This supplementary vector-only comparison measures neither latency nor interaction with reranking.

### Slide 11 · 6:25–7:05 · What the result cannot establish

SciFact judges whole abstracts. A retrieved chunk can inherit a relevant parent ID even when the actual evidence lies elsewhere in that abstract. Evidence may support or refute a claim; relevance does not prove the claim is true. We also test one corpus, one model pair, and warm sequential CPU inference. Unjudged documents receive zero credit. We have not established behavior under concurrent users, cold starts, different hardware, or generation. These limits determine where our recommendation applies.

### Slide 12 · 7:05–7:45 · Make the decision with a budget

For this workload, consider reranking when better document ordering justifies roughly two seconds of total p95 retrieval latency, before generation. Prefer vector ordering when the budget is tighter. If evidence is absent from the pool, improve first-stage retrieval first. Smaller chunks are another option, with a measured storage cost and an unmeasured timing cost here. Next, test candidate depth, passage-level evidence and realistic serving load. Our repository preserves the raw observations, pinned setup and replay commands so these conclusions can be checked.

## Prepare the evidence demonstration

Run this before recording. `make replay` recomputes metrics and checks stored observations; it does not repeat inference or remeasure latency.

```bash
study_dir=$(cat results/latest-study.txt)
make replay RESULTS="$study_dir"
```

This trace reads the saved first pass, maps chunks to parents and prints actual rankings for all three cases. During the recording, show the first case; keep the others available for questions. The per-query times are individual observations, not the aggregate percentiles on slide 8.

```bash
python3 - <<'PY'
from pathlib import Path
from ragstudy.common import read_json

study = Path(Path("results/latest-study.txt").read_text().strip())
run = read_json(study / "run-01.json")
mapping = read_json(study / "chunk-map.json")
for query_id in ("5", "535", "132"):
    row = next(r for r in run["queries"] if r["query_id"] == query_id)
    pool = list(dict.fromkeys(mapping[c] for c in row["baseline"]["candidates"]))
    rank = next((i for i, doc in enumerate(pool, 1) if doc in row["relevant"]), None)
    print("\nSciFact claim", query_id, row["query"])
    print("Judged relevant:", row["relevant"])
    print("First relevant vector parent rank:", rank or "absent from top-50 pool")
    print("Vector top five:  ", row["baseline"]["docs"])
    print("Reranked top five:", row["reranked"]["docs"])
    print("Individual query latency (ms):",
          f'vector {row["baseline"]["latency_ms"]:.1f}',
          f'reranked {row["reranked"]["latency_ms"]:.1f}')
PY
```

## Optional live presentation · 10 minutes, plus 5 minutes of questions

Use this expanded route only if selected for the ten-minute live presentation. It is not the eight-minute recording script. Start with the same core narration and add these segments during rehearsal, targeting 9:45 so handovers have room:

- **Hưng: add 40 seconds after slide 4.** Use the window diagram to show why a sentence crossing token 192 may be preserved by the next window, while an evidence span longer than the overlap may still be split. Explain that overlap mitigates some boundary cuts; it does not guarantee complete evidence. Ask what changes when a title or a distant definition is separated from the matching sentence.
- **Hiếu: add 45 seconds after slide 9.** Show the claim 535 loss and claim 132 pool miss in the prepared terminal. Explain the diagnostic distinction: a ranking failure may be addressed by a better scorer, while a missing candidate needs retrieval changes. Show the replay summary and point to `run-01.json` as the underlying evidence. Do not infer a linguistic cause for either failure without inspecting the passages.
- **Toàn: add 35 seconds after slide 12.** Use appendix slide 14 to propose a follow-up: vary candidate depth while holding the window, model, host and queries fixed; measure quality, candidate coverage and p50/p95 together. Then test chunk-size/reranker combinations separately. Explain that these are proposed experiments, with no claimed results yet.

Keep appendix slides 13, 15 and 16 ready for setup, interpretation and source questions. Every member should be able to explain the whole experiment because the instructor may direct a question to any member.

## Q&A preparation · all members

1. **Why split documents at all?** Models accept bounded inputs. Splitting lets retrieval select smaller portions and represent different parts separately. It introduces boundary and duplication decisions, so chunk size is a measured design choice, not a universal constant.
2. **Why is the cross-encoder slower?** Chunk vectors are precomputed for the bi-encoder. The cross-encoder processes each query–chunk pair again at query time: fifty pairs here, batched at sixteen. Its score is a ranking signal, not a calibrated probability or a truth judgment.
3. **Why top fifty and top five?** They are the registered candidate depth and output size. Fifty limits reranking work; five defines evaluation. We did not optimize either value or prove them optimal. Fifty chunks may represent fewer than fifty documents; the measured mean is 35.3 distinct parents.
4. **Why collapse duplicate parents?** SciFact relevance is defined at document level. Keeping the first occurrence of each parent means multiple overlapping chunks from one relevant document earn one document hit. At least eighteen distinct parents occur in every measured pool, so each arm can return five.
5. **Why did quality have no run spread?** The same fixed queries, corpus, models and deterministic rankings were reused. The host's timings varied. Repetition improves timing characterization; it does not measure statistical uncertainty over new queries. We did not report confidence intervals or significance tests.
6. **Why is added p95 not treatment p95 minus baseline p95?** Quantiles are not additive: the two p95 observations need not belong to the same query. We first calculate each query's treatment-minus-baseline time, then take its pass-level p95, and summarize across passes.
7. **Is the 96-token result purely a size effect?** It is a comparison of two explicit configurations at fixed absolute overlap. Relative overlap rises from about 16.7% to 33.3%, stride shrinks, and more chunks compete for fifty slots. We cannot disentangle those mechanisms with this one comparison.
8. **Does 39.68 MiB mean the full application uses that much memory?** No. It is the float32 embedding matrix only. Models, tokenizers, corpus text and runtime allocations require additional memory. The shared main matrix took 353.4 seconds to build, outside query timing. These local runs incur no API fees; they still consume compute and storage.
9. **Does better retrieval prove better answers?** No. The benchmark returns document IDs and scores document judgments. Passage-level evidence and generated-answer faithfulness need separate evaluation. A SciFact document can be relevant because it refutes a claim.
10. **Would a GPU or a vector database change the result?** They could change cost and possibly ranking behavior, depending on precision and approximate search. We measured exact cosine retrieval and CPU inference. Any deployment claim requires a new controlled measurement on that stack.
11. **What should we improve first?** Diagnose whether useful evidence reaches the pool. Missing candidates motivate retrieval/chunking work; present-but-low-ranked evidence motivates ranking work. Candidate depth, hybrid retrieval, boundary-aware splitting and batching are hypotheses to test, not improvements demonstrated here.
12. **How can someone reproduce or audit this?** Follow README setup and run `make study` for fresh measurements. Use `make replay RESULTS=...` for saved main-run verification, and `python3 -m ragstudy.chunk_ablation "$study_dir" --replay` for the saved supplementary comparison. Raw logs, model/data revisions and environment metadata are preserved. Reproduction on another host may yield different latency.

## Recording and final-link checklist

- Rehearse aloud with all three speakers; verify names and handover timing. The script's planned time is not proof of the final duration.
- Capture all three voices, readable headline results and the log demonstration. Record slides 1–12; do not read the appendix or Q&A during the short recording.
- Check the exported video duration is no more than eight minutes. Listen for clear audio and verify that the terminal text can be read.
- Upload the recording with anyone-with-the-link access, test the actual URL while signed out, and replace `Recording: pending` above.
- Review the AI log and self-assessment honestly. A prepared script and slide deck do not establish that the talk has been recorded or submitted.
