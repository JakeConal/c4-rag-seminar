# Presentation source and run of show

`slides.pdf` uses a 16:9 page size with **12 core slides and 4 appendix slides**. The expanded narration, three speaking assignments, saved-log demo, optional ten-minute live route and twelve Q&A answers are in [TALK.md](../TALK.md).

A Vietnamese version of the narration and preparation material is available in [TALK.vi.md](../TALK.vi.md). Rehearse that version separately to check its duration.

The short recording is planned for **7:45**, including a prepared terminal demonstration and handovers. This is a rehearsal target; the exported recording must be checked against the eight-minute limit. Appendix slides support questions and further study and are not narrated in the short recording.

| Slide | Content | Speaker / recording time |
| --- | --- | --- |
| 1 · Research question | Chunking and reranking; headline quality gain and paired latency cost | Dương Khánh Khải Hưng · 0:00–0:30 |
| 2 · RAG workflow | Offline indexing, online retrieval, generation context, measured boundary | Hưng · 0:30–1:00 |
| 3 · Bi-encoder and cross-encoder | Separate versus joint scoring; shared top-50 pool; duplicate-parent collapse | Hưng · 1:00–1:45 |
| 4 · Chunking choices | 192/32 windows, overlap and stride; context, boundaries and alternative splitters | Hưng · 1:45–2:25 |
| 5 · Controlled protocol | SciFact, fixed conditions, five paired passes, timing inclusion and exclusion | Nguyễn Minh Hiếu · 2:25–3:05 |
| 6 · Worked metric example | Illustrative rankings explaining reciprocal rank, recall and query averages | Hiếu · 3:05–3:40 |
| 7 · Measured quality | MRR@5 and recall@5, percentage-point gains, improved/tied/worsened counts | Hiếu · 3:40–4:15 |
| 8 · Measured latency | Baseline, treatment and paired added p50/p95; median and range over passes | Hiếu · 4:15–5:00 |
| 9 · Inspect raw cases | Claim 5 promotion, 535 demotion, 132 missing candidate; pool ceiling and terminal demo | Hiếu · 5:00–5:45 |
| 10 · Separate chunk comparison | 192 vs. 96 tokens; fixed absolute overlap; vector quality and matrix storage | Huỳnh Thái Toàn · 5:45–6:25 |
| 11 · Failure modes and limits | Candidate coverage, ordering, document labels and serving conditions | Toàn · 6:25–7:05 |
| 12 · Recommendation | Quality versus retrieval budget; when to use reranking; next measurements | Toàn · 7:05–7:45 |
| 13 · Reproducibility | Setup, pinned inputs, raw observations and replay | Appendix / any member |
| 14 · Follow-up experiments | Candidate depth, chunking and deployment hypotheses; unmeasured outcomes | Appendix / live extension |
| 15 · Q&A | Interpretation, evidence and evaluation boundaries | Appendix / any member |
| 16 · Sources | Primary sources and local evidence links | Appendix / any member |

## Recording versus live presentation

For the short recording, use slides 1–12 and the narration paragraphs in TALK.md. Prepare replay output before recording and show claim 5's saved rankings. Do not read the setup commands, Q&A or appendix aloud. For the ten-minute live presentation, TALK.md adds a boundary example, two further query traces and a proposed controlled follow-up, targeting 9:45 before questions.

All three members should be able to explain the complete study. Neither the slide count nor a written timing plan establishes that a completed recording meets the rubric.

## Regenerate the PDFs

Run from the repository root after `make setup`. The separate PDF environment uses pinned packages and hashes. [ReportLab 4.4.4](https://pypi.org/project/reportlab/4.4.4/) · [markdown-it-py 4.0.0](https://pypi.org/project/markdown-it-py/4.0.0/) · [PyMuPDF 1.26.6](https://pypi.org/project/pymupdf/1.26.6/)

```bash
.cache/uv-bin/uv venv --python .venv/bin/python --allow-existing .cache/docs-venv
.cache/uv-bin/uv pip sync --python .cache/docs-venv/bin/python --require-hashes --only-binary :all: requirements-docs.txt
.cache/docs-venv/bin/python -m scripts.render_seminar --results results/20261121T122915162545Z
```

The renderer lays out [REPORT.md](../REPORT.md) as `report.pdf` and reads the primary run's environment, aggregate, candidate map, first run, and supplemental chunking summary to populate `slides.pdf`. It also saves source paths and displayed-value rounding in `presentation-values.json` in the result directory. The worked metric example is explicitly illustrative; measured results remain sourced from the saved observations. After adding the repository URL, run `.cache/docs-venv/bin/python -m scripts.render_seminar --report-only` to refresh the report PDF.

To refresh only the deck, use `.cache/docs-venv/bin/python -m scripts.render_seminar --results results/20261121T122915162545Z --slides-only`. This leaves the report PDF untouched.

The report uses a separate single-column research-paper layout. Its format research and adaptation notes are in [REPORT-FORMAT.md](REPORT-FORMAT.md); the required author font and license are tracked under `assets/fonts/`.
