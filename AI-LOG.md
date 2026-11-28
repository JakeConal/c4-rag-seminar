# AI usage log

## 2026-11-25 — Recheck the current Classroom requirements

Tool: OpenAI Codex with authenticated, read-only Composio Classroom and Drive calls.

Asked for: Check the requirements again and identify the team's remaining manual tasks.

Kept: The existing experiment, report, slides and confirmed C4 registration. The fresh registration read still showed the same three student IDs and no lecturer comment.

Changed: Updated the local requirement and submission checklists after the lecturer revised the assignment on November 23. The final deadline is December 30, with weekly voting and red-team rounds. Recorded the current brief's hash and distinguished the November 24 first-vote cutoff from final submission.

Rejected: Reusing the previous November 29 final deadline or fixed December 2 red-team deadline. The live assignment's update timestamp and newly downloaded brief exposed those as superseded instructions. No Classroom submission, Facebook post, repository publication or registration edit was performed.

Format checked against the course's [AI-LOG.md template and rules](https://classroom.google.com/c/ODg2MTU1OTQ4NDc0/m/ODg2ODE3NTEzMjE2/details), read 2026-11-21. Each assisted task records Tool, Asked for, Kept, Changed and Rejected.

## 2026-11-21 — Codex environment preparation

Tool: OpenAI Codex, using authenticated Composio reads and official PyPI/Hugging Face records.

Asked for: Review the Classroom seminar requirements for topic C4 and prepare the environment.

Kept: The registered team/question, requirement checklist, CPU experiment scaffold, pinned model/data revisions, document templates and standard-library metric tests. Selected versions and revisions were checked against official PyPI/Hugging Face APIs.

Changed: kept chunking identical in both arms to isolate reranking; counted distinct parent documents so overlapping chunks cannot inflate recall; specified MRR@5; used paired per-query latency deltas and separate synthetic-fixture output.

Rejected / assistant error caught: the assistant initially attempted a standard `python3 -m venv .venv`, assuming the host had venv support. The command failed because ensurepip was absent; `python3 -m pip --version` also showed pip was missing. The setup now detects that failure and documents the host prerequisite. This environment must not be described as fully installed.

Rejected: attempting to use a canonical BEIR ZIP download as the data path failed with an SSL error in the remote environment. The scaffold instead uses the official BeIR Hugging Face parquet files and test.tsv at observed commit hashes.

Verification: standard-library metric tests and synthetic logging/replay are recorded in docs/VALIDATION.md after execution. Real dependencies/model inference and experimental conclusions remain unverified. Human review of the protocol, candidate rankings, and final numbers is still required.

Add real subsequent changes, rejected suggestions, bugs caught, and how the team verified them. Do not invent human review or benchmark results.

## 2026-11-21 — Parallel seminar completion

Tool: OpenAI Codex, with GPT-6.2 Astra at high effort for experiment design/code and independent review, and GPT-6.2 Sol at high effort for environment/reproducibility and report/presentation materials.

Asked for: Spawn appropriate agents to help finish the English C4 seminar, covering the entire topic, then resume those agents after interruption.

Kept: Separate ownership of scientific code, environment, deliverables and independent review; pinned offline measurement; source-backed English materials; real-pilot checks; a fresh-clone full-study command. The coordinator integrated the work and controlled the measurement schedule.

Changed: separated the registered reranking experiment (fixed 192/32 token chunks) from a secondary 96/32 chunk-size comparison. This allows discussion of both parts of topic C4 while changing one factor in each comparison. The secondary comparison explicitly makes no timing claim.

Changed / assistant benchmark error caught: the initial scaffold set PyTorch/OMP threads but did not explicitly cap NumPy's OpenBLAS or MKL threads. The experiment agent inspected the timing code and added those limits before imports, so vector search and reranking use the documented CPU thread budget.

Changed / assistant benchmark error caught: the original replay trusted the stored final document rankings without reconstructing them from raw scores or checking paired candidate pools. The experiment agent added reconstruction and validation, plus rejection of incomplete runs, changed judgments and invalid timings. Metric tests exercise these failure cases.

Environment correction: once the user enabled unrestricted filesystem/network access, local downloads and GPU inspection became possible. The team rechecked these conditions instead of retaining the earlier blocked-state claims. The primary protocol remains CPU-based unless the measured run metadata explicitly says otherwise.

Human-facing boundaries: publication and recording links must be real. Draft report, slides and speaking notes do not establish that a public repository or an all-member recording exists. The final submission checker reports those items separately.

Rejected: the coordinator's first submission checker accepted five empty JSON run files as five measurements, accepted an unrelated Drive link as a recording, and accepted a numeric total while criterion scores were still TBD. The independent reviewer reproduced all three using temporary fixtures. The checker now validates raw run content and the stored summary, requires a labeled recording field, and checks all six criterion scores, bounds, evidence fields and their sum. Three regression tests cover those false positives. This was a defect in the assistant's verification code, not a scientific result.

## 2026-11-21 — Check the instructor's separate templates

Tool: OpenAI Codex with authenticated Classroom reads through Composio.

Asked for: Find the separate self-assessment and AI-log templates referenced by the seminar brief.

Kept: Links to the exact course materials and their required fields. The self-assessment belongs at the zip root and needs criterion scores, concrete evidence, unfinished work and a filename-matching total.

Changed: Added explicit Asked for and Kept labels to the earlier AI-log entries after checking the instructor's exact format.

Rejected: Treating the initial free-form AI log as format-complete. The actual template read exposed missing labels; the log was corrected before packaging. No submission, external message or public repository was created by these reads.

## 2026-11-22 — Resume agents and review the completed package

Tool: OpenAI Codex with the existing experiment, environment, deliverables and independent-review agents.

Asked for: Wake the previous agents and continue the seminar work from the saved checkpoint.

Kept: The completed five-pass CPU experiment, separate chunk-size observations, audited raw results, three-page report, nine-slide PDF, and speaking assignments for the three names supplied by the user.

Changed: Checked the actual rendered PDF pages and independently rechecked their numbers. Replaced a literal timestamp placeholder in the replay example with the checked-in study-path file so the example can be pasted into a shell.

Rejected: Treating local document generation as evidence that publication or recording had happened. The final checker explicitly flags those two remaining URLs. The 82/100 self-assessment is provisional and assigns zero to the recording until a real video can be checked.

## 2026-11-26 — Enrich the slides and speaking material

Tool: OpenAI Codex with the resumed deliverables and independent-review agents.

Asked for: Enrich the slide deck and talk because the previous versions were too short.

Kept: The registered question, measured study, three named speakers and eight-minute recording limit. The report and scientific measurements remain the evidence for the presentation.

Changed: Expanded the presentation to twelve core slides and four appendix slides, with a RAG workflow, bi-encoder/cross-encoder explanation, chunking trade-offs, an illustrative metric calculation, measured failure cases, interpretation limits and reproducibility/source references. Expanded the narration to about 916 spoken words, added a separate ten-minute live route and twelve Q&A answers, and prepared a three-case saved-log demonstration. The terminal trace was executed successfully against the checked-in observations.

Rejected: Treating a longer script as a verified eight-minute recording, narrating all appendix material within the recording, or presenting the illustrative metric example as measured data. The planned 7:45 duration needs an actual timed rehearsal and exported-video check. Retained the distinction between document-level relevance and evidence in the selected chunk, paired added percentiles and subtraction of aggregate percentiles, and measured chunking quality versus unmeasured chunking latency.

Verification: Visually inspected the sixteen-slide PDF, checked the displayed values against the saved results, and executed the three-case log snippet. The renderer produced identical slide bytes on repeat, the report remained three pages and unchanged, and all sixteen existing tests passed.

## 2026-11-26 — Vietnamese talk script

Tool: OpenAI Codex.

Asked for: Provide a Vietnamese version of the TALK script.

Kept: All twelve core slide assignments, three named speakers, measured figures, illustrative metric example, saved-log commands, live extension and twelve Q&A answers.

Changed: Added TALK.vi.md with Vietnamese narration and preparation guidance, Vietnamese decimal formatting, and a link to the English original. Kept the command blocks identical to the English version for reproducibility.

Rejected: Assuming the English rehearsal targets establish the Vietnamese recording duration. The translated script explicitly requires its own timed rehearsal and exported-video check. Verified twelve slide sections, twelve Q&A answers and exact equality of the demo command blocks; no new measurements were needed.

## 2026-11-26 — Publish the seminar repository and invite teammates

Tool: OpenAI Codex using the authenticated GitHub CLI.

Asked for: Create the public JakeConal/c4-rag-seminar repository, publish the files, and invite the other members from JakeConal/leetkob with write access.

Kept: The local Git history, verified measurements, English and Vietnamese scripts, and provisional self-assessment score.

Changed: Created the public repository, configured its origin, inserted the real URL into REPORT.md and README.md, regenerated the report PDF, and sent write-access invitations to Toanapr and XuXinhNo1. GitHub's pending invitation list confirms both accounts and permissions.

Rejected: Treating a sent invitation as accepted membership or a published repository as completion of the recording. The recording remains pending. A credential-pattern scan of tracked files found no matches before publication; ignored model caches and environments are excluded.

Verification: After pushing, confirmed public visibility with an unauthenticated API request and cloned over HTTPS with credential helpers disabled. Both primary and supplementary saved-log replays passed from that clone. The report remains three pages with the actual repository URL. GitHub Actions completed successfully for publication commit 81a64ac. Updated the public-clone evidence without increasing the provisional score; a fresh full inference run from the public clone was not performed.

## 2026-11-26 — Enrich and professionally format the report

Tool: OpenAI Codex with the resumed independent-review agent.

Asked for: Make the report more professional and enrich its content.

Kept: The registered research question, pinned protocol, measured values, repository URL on the first line, and three-page limit.

Changed: Added an abstract, numbered research sections, clearer metric and timing definitions, a supplementary chunking table, a failure decomposition and concrete follow-up experiments. The raw first-pass log independently confirms 61 reranked queries with no judged hit: 32 lack a relevant candidate and 29 have one below the top five; reranking newly finds a hit for 25 queries and loses all top-five hits for 10. Refined typography, table spacing, running headers and clickable GitHub evidence links in the PDF.

Rejected: Adding unsupported statistical significance, reranker/chunk-size interaction or serving-performance claims. The added analysis comes from existing observations and distinguishes any-hit counts from macro recall. No new model inference or latency measurement was performed.

Verification: The report renders deterministically to three pages. Inspected the rendered pages, checked text bounds, preserved all displayed primary results, and confirmed HTTPS links for standalone PDF citations. The submission checker passes all automated checks except the still-pending recording URL.

## 2026-11-26 — Research and apply a research-paper format

Tool: OpenAI Codex, Agent Reach research skill, native web search and official publisher/author guidance.

Asked for: Research popular research-report formats and apply a suitable format to this report.

Kept: The instructor's first-line repository URL and three-page limit, all measured tables and query-level findings, and the report's existing scientific scope.

Changed: Compared official IMRaD, IEEE structure and ACM manuscript/proceedings guidance; recorded sources and the course-specific decision in docs/REPORT-FORMAT.md. Applied Introduction–Methods–Results–Discussion with Conclusion, Reproducibility and References; moved metric definitions into Methods; added keywords, author names, table captions, section cross-references and separate numbered bibliography entries. Applied restrained serif typography and horizontal table rules. Bundled licensed DejaVu Sans for correct Vietnamese author names.

Rejected: Calling the adapted course report an official IEEE/ACM template, assuming all research uses two columns, or imposing publication-only anonymity and rights blocks. An initial font-path assumption failed locally; the corrected renderer loads the bundled font from an explicit repository path. An intermediate PDF exceeded three pages; abstract editing and spacing adjustments restored the limit without dropping measured results.

Verification: Inspected all rendered pages and verified three-page output, exact author-name text, section and caption presence, page bounds and deterministic PDF bytes. The submission checker passes all automated requirements except the pending recording URL. Existing scientific observations were not rerun or replaced.

## 2026-11-26 — Build a Vietnamese learning guide

Tool: OpenAI Codex with the resumed independent-review agent; local code/log inspection and official model/documentation reads.

Asked for: Create a Markdown file that teaches the topic and explains the report and presentation.

Kept: The measured scope, configured models, recorded results and limits. Used Vietnamese explanations with English technical vocabulary to match the speaking materials.

Changed: Added docs/STUDY-GUIDE.vi.md with a staged learning path, RAG pipeline diagrams, vector/chunking/encoder explanations, worked metric and percentile examples, experiment interpretation, code/evidence navigation, slide mapping, defense questions and self-check exercises with answers. Linked the guide from README and the concise topic guide.

Rejected: Treating reranker scores as truth probabilities, document hits as proof of passage evidence, five repeated passes as independent datasets, or potential optimizations as measured improvements. All invented teaching examples are labeled and separated from real observations.

Verification: Executed the guide's metric/percentile/window example and both saved-log replay commands successfully. Checked all relative file links, confirmed the recorded 384-dimensional index and parent counts, and preserved the report and presentation measurements. No new model inference or latency measurement was performed.

Independent-review correction: an earlier teaching sentence said that document A at rank six implies RR@5 is zero, without excluding another relevant document in the first five. The reviewer identified the counterexample. Corrected it to require that the first relevant parent is at rank six or lower, and clarified that MRR averages reciprocal rank rather than rank itself. The reviewer verified the numerical examples and the guide's mapping to the report and slides.
