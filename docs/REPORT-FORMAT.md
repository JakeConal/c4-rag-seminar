# Research-report format review

Reviewed November 26, 2026 using the Agent Reach research skill with the native web search and page-reading tools. These are established reporting approaches, not a measured popularity ranking.

| Approach | Official guidance | Fit for this study |
| --- | --- | --- |
| IMRaD | [ICMJE manuscript preparation](https://www.icmje.org/recommendations/browse/manuscript-preparation/preparing-for-submission.html) describes Introduction, Methods, Results and Discussion for original research. Its subject-specific medical requirements do not apply to this seminar. | Useful separation of motivation, protocol, observations and interpretation. |
| IEEE conference-paper structure | [IEEE Author Center](https://conferences.ieeeauthorcenter.ieee.org/write-your-paper/structure-your-paper/) covers a descriptive title, concise abstract, keywords, introduction, reproducible methods, results/discussion, conclusion and references. | Closely matches an empirical computing study with a controlled comparison. |
| ACM manuscript/proceedings workflow | [ACM Hypertext 2026 instructions](https://ht.acm.org/ht2026/open-calls/submission-instructions/) distinguish a single-column review manuscript from a two-column final proceedings paper. | Demonstrates that the layout depends on the submission stage and venue; two columns are not a universal requirement. |

## Applied decision

Use an IMRaD research structure with an explicit conclusion and reproducibility section, drawing on IEEE's organizational guidance. Keep a single-column A4 seminar layout to accommodate readable latency ranges and the instructor's three-page limit. This is a course report adaptation, not an official IEEEtran/acmart template or a claim of publisher compliance. No conference branding, DOI, acceptance statement, affiliation or funding claim is invented.

Applied changes:

- Descriptive title, all three author names and student IDs, a self-contained abstract and five keywords.
- Introduction; Methods, including metric definitions and aggregation; Results with primary and supplementary subsections; Discussion; Conclusion; Reproducibility; References.
- Roman-numbered major sections, lettered results subsections, two numbered table captions and in-text table/section references.
- Serif body text, restrained horizontal table rules, hanging reference entries and clickable evidence links.
- Repository URL stays on the first line. Existing measurements and their limitations remain traceable to the saved logs.

IEEE recommends a self-contained abstract without unexplained abbreviations; the revised abstract spells out its measures and units. References [1]–[4] follow first-citation order. Bibliographic metadata for the RAG, SciFact and chunking papers was rechecked against [arXiv](https://arxiv.org/abs/2005.11401), [the SciFact ACL entry](https://aclanthology.org/2020.emnlp-main.609/) and [the chunking ACL entry](https://aclanthology.org/2025.findings-naacl.114/).

The renderer bundles DejaVu Sans solely for Vietnamese author names; the font's redistribution notice is in `assets/fonts/LICENSE-DejaVu.txt`. Built-in PDF fonts handle the body. This avoids reliance on host-installed fonts.
