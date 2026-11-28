# Validation — 2026-11-21

## Tests and real environment

- `make test`: **16 tests passed** after the independent review. They cover recall/rank formulas, parent collapse, window coverage, paired latency, raw-score reconstruction, incomplete/changed run rejection, and submission-check false positives. Output: [tests.log](../results/verification/tests.log).
- `make smoke`: standard-Python synthetic logging/replay check. Fixtures are ignored under results/smoke and are not scientific evidence.
- `python3 -m compileall -q ragstudy scripts tests` and `bash -n scripts/bootstrap.sh`: passed.
- The real CPU environment imports successfully and executes a CPU tensor; all 34 installed packages match the hash lock. See [environment evidence](ENVIRONMENT.md) and [resolved versions](../results/environment/requirements.resolved.txt).

## Fresh-clone study

Source commit: `a3d85f5`. Created a new local clone and a new virtual environment. Only verified download caches were shared with the original working directory. An optional offline-only setup attempt missed one cached wheel. The documented network-enabled `make setup` then succeeded; preparation and measurement used the pinned local inputs offline.

Commands: `make setup`, `make prepare`, `make study`.

Preparation regenerated the same JSON bytes from 5,183 documents, producing 12,434 chunks and 300 labeled test queries. Prepared-data SHA-256: `e03460dc22c768f7e2be4c545f5ec13ee3585b884a1aa8ad55da7fb56f38d231`.

All five complete primary passes are saved in [the official run directory](../results/20261121T122915162545Z/). Each pass contains both arms for every query. No paid inference API, GPU, query-result cache or fixture prediction was used.

`make replay RESULTS=results/20261121T122915162545Z` succeeded with standard Python. Output: [replay.log](../results/verification/replay.log). It reconstructed all document rankings from raw scores and reproduced the stored summary.

The independent [review](REVIEW.md) checked every per-pass metric and all across-pass statistics, all query texts/judgments, source/model hashes, and mirrored raw files. Quality is identical across passes; latency spread is measured from the five real passes. The shared top-50 pools always contain at least five parents, so the baseline gives the exact first five vector-ranked parents.

## Scope

The full `make study` pipeline exited 0, including the separate 96/32 window comparison. Standard-Python secondary replay succeeded; output is in [chunk-replay.log](../results/verification/chunk-replay.log). This comparison is vector-only quality and matrix storage analysis. Its single deterministic pass is not a latency result or a reranker interaction study.

Publication, all-member recording, public-link access and final self-assessment calibration require their own completion checks; local PDFs or a draft archive do not establish those facts.

## Expanded presentation — 2026-11-26

The regenerated `slides.pdf` contains twelve core slides and four appendix slides at 960 × 540 points. Visual inspection covered all sixteen pages; the text bounds fit the pages, the metric example matches the narration, and the displayed scientific values and cases agree with the saved observations. The deck's six source cards contain clickable links. The renderer's `--slides-only` mode leaves the three-page report untouched and produces identical PDF bytes on repeat; `presentation-values.json` is unchanged.

The main narration contains approximately 916 spoken words across all three named speakers. The 7:45 schedule allows a prepared log demonstration; it remains a rehearsal target rather than a verified video duration. The separate live extension and Q&A notes are excluded from the short recording. The three-case terminal snippet in TALK.md executed successfully for claims 5, 535 and 132. All sixteen existing tests pass. Final recording and public repository access remain pending.

## Public repository verification — 2026-11-26

Published at https://github.com/JakeConal/c4-rag-seminar. An unauthenticated GitHub API request confirmed public visibility. A fresh HTTPS clone with credential helpers disabled succeeded, then standard-Python replay passed for both the primary study and the supplementary chunk comparison. This verifies public access and the published logs; no new inference or latency measurement was performed. GitHub Actions run 45785146027 passed the existing offline checks for publication commit 81a64ac. Write invitations to Toanapr and XuXinhNo1 are pending acceptance. The recording remains pending.

## Report revision — 2026-11-26

The enriched report retains three A4 pages, with a research abstract, explicit protocol and metric definitions, primary and supplementary tables, query-level failure analysis, limitations and references. Visual inspection and PDF text-bound checks passed; repeated rendering produces identical bytes. Relative evidence links resolve to public GitHub URLs in the standalone PDF. The report's additional any-hit counts were recomputed from `run-01.json` and `chunk-map.json`: 61 reranked misses comprise 32 missing candidates and 29 ordering failures; 25 claims gain their first top-five hit and 10 lose all such hits. These counts are distinct from the existing MRR/recall change counts. No scientific run was replaced or repeated.

## Research-paper format — 2026-11-26

Applied the source-backed decision in [REPORT-FORMAT.md](REPORT-FORMAT.md). The final report has three pages, correct Unicode author names, all six numbered sections, two captioned tables and four separate bibliography entries. Visual inspection covered the rendered pages; text-bound and deterministic-regeneration checks passed. Metric definitions and aggregation now appear in Methods; the measured result tables and failure analysis are preserved. The renderer uses a bundled licensed font for author names and built-in PDF fonts for the body. The automated readiness checker still identifies only the pending recording URL.
