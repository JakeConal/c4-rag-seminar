# C4 self-assessment report

**Study:** Chunking and reranking for RAG

**Course:** CSC13114 CQ2023/3

**Submitted by**

- 23120045 · Dương Khánh Khải Hưng
- 23120124 · Nguyễn Minh Hiếu
- 23120175 · Huỳnh Thái Toàn

**Claimed total:** 82/100

Provisional while the recording and final score review remain pending.

| Criterion | Max | I claim | Evidence |
| --- | ---: | ---: | --- |
| Question and baseline | 15 | 15 | [Registered question and assignment](docs/REQUIREMENTS.md) · [Shared candidate pool and controlled comparison](REPORT.md) · [Pinned configuration](config.json) |
| Measurement re-runs | 30 | 27 | Five paired passes on all 300 test claims from a fresh local clone. An unauthenticated public clone and both saved-log replays passed on November 26. A new full measurement from that public clone has not been run. [Raw results and environment](results/20261121T122915162545Z) · [Replay summary](results/20261121T122915162545Z/summary.json) · [Reproduction commands](README.md) |
| Findings and recommendation | 20 | 20 | Quality, total and paired latency with spread, rank gains and losses, candidate ceiling, costs, and operating limits. [Report](REPORT.md) · [Chunk-size comparison](results/20261121T122915162545Z/chunk-ablation/summary.json) |
| Talk (recording) | 15 | 0 | The slides, script and demo are ready. A viewable recording is pending. [Slides](slides.pdf) · [Three speaking assignments and raw-log demo](TALK.md) |
| Sources and facts | 10 | 10 | Sources cover the data, models, package releases, and concepts. [Official sources and access dates](docs/SOURCES.md) |
| AI log | 10 | 10 | Dated records of kept, changed and rejected work and how assistant errors were caught. [Usage log](AI-LOG.md) |
| **Total** | **100** | **82** | Provisional local review score |

## What I did not manage

The all-member recording, its signed-out playback check, and the course submission are pending. The study is published at [https://github.com/JakeConal/c4-rag-seminar](https://github.com/JakeConal/c4-rag-seminar). The red-team issue follows the course pairing announcement.

## What I would do differently

Run the pilot earlier to estimate the full CPU timing budget. Repeat the protocol on a second corpus and include evidence annotations at passage level for a more direct test of the context a RAG system would receive.

The final zip uses `23120045-23120124-23120175_<total>.zip` and includes Git history. [Official self-assessment template](https://drive.google.com/file/d/1A6PXFg7KjQ3G-r6ScVNRGttSc--kw2Kr/view)
