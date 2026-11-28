# Independent check of the SciFact measurements

On 2026-11-21, an independent Codex reviewer recalculated the results from the saved candidate scores, parent map, query judgments and times. The calculation used Python's standard-library statistics, including inclusive interpolated quantiles. All 22 reported metrics agreed in each of the five passes and for each across-pass summary field (median, minimum, maximum, Q25 and Q75). [Raw logs and summary](../results/20261121T122915162545Z/)

| Check | Observation |
| --- | --- |
| Input identity | The three data files, 16 model artifacts and prepared corpus matched the SHA-256 values in the environment record. The three recorded harness file hashes matched commit `a3d85f5`. All eight primary-result JSON files matched the files from the clean benchmark clone byte-for-byte. |
| Query coverage | Each pass contained all 300 distinct test queries, with text matching the pinned query parquet and 339 unique positive query–document judgments matching the pinned TSV. |
| Fair comparison | Both arms logged the same 50 vector candidates and scores for each query. Every pool contained at least 18 distinct documents (mean 35.32), so vector-order collapse recovered five distinct parents for every query. Stable score sorting and parent collapse reconstructed all 3,000 final rankings. |
| Quality | MRR@5 rose from 0.610500 to 0.672000. Macro recall@5 rose from 0.730722 to 0.777167. By reciprocal rank, 67 queries improved, 193 tied and 40 worsened. By recall, the counts were 30, 259 and 11. Each query's rankings repeated in every pass. |
| Candidate ceiling | Even perfect ranking of the 50 candidates would yield mean recall@5 of 0.886333. For 32 queries the pool contained zero judged positives. |
| Latency | Subtracting the two elapsed times within each query gave a median added p50 of 1,511.02 ms (pass range 1,469.51–1,636.68) and median added p95 of 1,928.33 ms (1,649.70–2,049.38). Median total p95 was 115.74 ms for vector search and 2,000.97 ms with reranking. |

The five passes repeat the same 300 claims. The latency range describes variability on this host, while the quality comparisons describe those 300 claims. The 16 repository tests also passed during review. [Environment and hashes](../results/20261121T122915162545Z/environment.json) · [Test cases](../tests/)

## Chunk-size comparison

The supplemental log identifies the same primary run by its SHA-256 digest. Both chunk maps cover the same 5,183 documents. Independently sorting and scoring the 300 pairs of vector rankings reproduced the gains from shortening windows from 192 to 96 tokens at a fixed 32-token overlap. MRR@5 increased by 0.73 percentage points, recall@5 by 1.40 points and pool recall by 1.07 points. The index grew from 12,434 to 27,090 chunks and from 19,098,624 to 41,610,240 bytes of float32 embeddings. This comparison measures vector ranking under the corresponding 160- and 64-token strides. [Raw observations and summary](../results/20261121T122915162545Z/chunk-ablation/)

## Submission materials

On 2026-11-22 the reviewer inspected all three report pages and nine slides as rendered. The displayed values, pass ranges, index sizes and rank changes agree with the logs. The examples cover claim 5 (vector parent rank eight to reranked rank one), claim 535 (first to outside the top five), and claim 132 (no judged positive in the candidate pool). The tables and figures fit within the pages. [Report](../report.pdf) · [Slides](../slides.pdf) · [First-pass observations](../results/20261121T122915162545Z/run-01.json)

The script allocates speaking parts to all three registered students and includes a raw-log demonstration. Its nine segments contain about 660 words and target 7 minutes 10 seconds. The provisional 82-point assessment supplies all three names and IDs, the six scored criteria, their evidence and both required reflections. At review time the readiness checker passed the other checks and identified two open items, the public repository URL and the recording URL. Recording duration, voices and signed-out playback still require the actual video. [Script](../TALK.md) · [Self-assessment](../SELF_ASSESSMENT_REPORT.md) · [Course templates](REQUIREMENTS.md)

## Expanded deck and narration — 2026-11-26

Independent review compared all sixteen slide texts with the talk, report, saved display values and revised brief. The twelve core slides and four appendix slides preserve all measured quality values, latency ranges, candidate ceiling, three query traces and the supplementary chunking results. The illustrative A/B example matches the narration and is labeled as an illustration. Visual inspection found no text clipping or overlap, and the six source cards have clickable links.

The main narration is approximately 916 words. The 7:45 target leaves about twenty seconds for actions at roughly 124 words per minute; slide 9's trace segment needs particular rehearsal. The optional live additions total two minutes, producing a 9:45 plan. Actual recording duration and accessibility remain unverified. Review clarified that the abstracts are chunked and the claims are evaluation queries. No new benchmark run or changed scientific conclusion is implied by this presentation revision.

## Enriched report review — 2026-11-26

Independent review confirmed all reported quality and latency values, run spreads, chunking storage and quality figures, methodological controls, source references and the three-page limit. The first-pass any-hit partition is 214 claims with a hit in both arms, 25 newly hit, 10 lost, 19 missed by both despite a relevant candidate, and 32 without a relevant candidate. Accordingly, 61 reranked misses comprise 32 coverage failures and 29 ordering failures. Clarified that those 29 finish outside the top five, since ten had been top-five hits in vector order. The report preserves the distinction between these counts and macro recall/MRR changes. No factual blockers remained.
