# Assignment review — rechecked 2026-11-25

Sources: [Classroom assignment](https://classroom.google.com/u/1/c/ODg2MTU1OTQ4NDc0/a/ODk4OTA4NDI0NTUx/details), [brief and rubric](https://drive.google.com/file/d/1F3DQ0tjuXOuzCmrQ4Z9iqS05n7h_M62j/view), [registration sheet](https://docs.google.com/spreadsheets/d/1PE-Y-SbEwu7D15L3LdB2D8x0SSqZ2oAnlkMwsInF2i4/edit).

Re-read the live assignment, revised brief and separate template posts through the authenticated connector. The assignment was updated on 2026-11-23; its revised PDF SHA-256 is `fd7d3283f6a5fcf5548d8b818aeadf8a0a5f397999552029276b500a55a3eb1d`. Registration row C4 still lists 23120045-23120124-23120175 and no lecturer comment. No Classroom or registration changes were made. This schedule supersedes the earlier November 29 submission / December 2 red-team dates.

## Scope and dates

Team of up to three, 100 points, 7% of the course. One measurable question, a baseline and one change; hold machine, data and load fixed. English or Vietnamese is allowed.

All deadlines are 22:00 Vietnam time (UTC+7):

| Date | Requirement |
| --- | --- |
| Before submission | Register topic; your C4 row is already populated. Several teams may share a topic using Extra rows |
| December 30, 2026 | Final study submission deadline |
| Each Sunday | Submit and post by 22:00 to enter that week's vote; unselected posts carry forward |
| Tuesday / Wednesday | Votes counted Tuesday 22:00; presenters announced Wednesday |
| November 26–December 17 | Three selected teams present each Thursday |
| December 13 | Last voting cutoff for the December 17 session |
| Each Monday | Teams submitted by Sunday 22:00 and not yet paired receive red-team assignments |
| Next Monday after pairing | Red-team issue due within 7 days, by 22:00 |
| December 28 | Last regular Monday pairing round |
| December 31 / January 7, 2027 | Teams submitted after the last regular round are paired December 31; issue due January 7 at 22:00 |

The one-off November 24, 22:00 cutoff applied only to the November 26 presentation vote, not final submission. Teams for that round are announced November 25 evening. For the next regular round, submit and post by Sunday, November 29, 22:00 for the December 3 session.

## Deliverables

- Public GitHub repository accessible to the red team.
- README.md: fresh clone to one measurement command.
- At least five runs; median and spread; raw output for every reported number under results/.
- REPORT.md: **at most three pages**, repository URL on first line. Include question, setup/versions/machine/data/load, baseline/change and controls, findings with units/spread, cost, recommendation, when not to use it, limitations and official sources with access dates.
- slides.pdf and TALK.md with a public-link recording, **at most 8 minutes**, with a speaking part for every team member. Show the measurement or its logs and readable headline numbers.
- AI-LOG.md identifying tool/use, real Changed/Rejected entries, and at least one assistant error plus how it was caught.
- SELF_ASSESSMENT_REPORT.md: one row per criterion, claimed mark and concrete evidence; total and a short account of unfinished work.
- One zip **including .git**, named `23120045-23120124-23120175_<total>.zip`; one member submits from their student email.
- Facebook post begins `#AWADSeminar23_3` and includes title, question, one measured headline number and talk link. The brief says skipping the post forfeits vote participation but costs no marks.
- Red team: within seven days of your pairing announcement, open one issue on the assigned team's repo titled `[red-team] 23120045-23120124-23120175`, with command, reproduced versus reported numbers, and an evidence-backed finding. Missing your issue deadline costs 10 points.

No paid APIs are needed by this setup. If any are introduced, cap spending and retain raw responses plus a keyless replay mode. Load tests and adversarial traffic must use systems you own.

## Scoring and implications

| Criterion | Points | Evidence to prepare |
| --- | ---: | --- |
| Question and baseline | 15 | Registered question and explicit controls |
| Reproducible measurement | 30 | Fresh-clone instructions, five raw runs, median/spread, traceable numbers |
| Findings and recommendation | 20 | Improvement or lack of it, latency cost, limits, when to avoid reranking |
| Talk | 15 | Accessible recording within 8 min, all members speak |
| Sources and facts | 10 | Official sources for every version/status/API claim, with read dates |
| AI log | 10 | Specific edits/rejections and verified assistant mistake |

The lecturer reruns the study. A null or negative improvement can earn full marks. Do not select only the best run. A self-assessment with unsupported claims affects the honesty adjustment; missing the file costs 10 points.

## Separate official templates

Read from the same course on 2026-11-21:

- [Self-assessment PDF](https://drive.google.com/file/d/1A6PXFg7KjQ3G-r6ScVNRGttSc--kw2Kr/view), attached to [the template post](https://classroom.google.com/c/ODg2MTU1OTQ4NDc0/m/ODg3NDcyODY0OTkw/details). Include a Submitted by line for each member's student ID and full name, an explicit claimed total out of 100, the columns Criterion / Max / I claim / Evidence, and both What I did not manage and What I would do differently. PDF SHA-256: `91a64f5154dd81ed6c7f6c694f27d221ef4a4bb26a1d6fa8c784e84cf66318b4`.
- [AI-LOG.md template and rules](https://classroom.google.com/c/ODg2MTU1OTQ4NDc0/m/ODg2ODE3NTEzMjE2/details). Use one dated entry per assisted task with Tool, Asked for, Kept, Changed and Rejected. Explain the reason for changes/rejections and the check that exposed the issue. Keep the log at repository root.

## Suggested work sequence

1. Finish the host prerequisites and downloads; run a 10-query pilot and inspect candidate IDs, judgments and timing stages.
2. Freeze the resolved dependencies, verify formulas and data identity, then run all test queries five times on one machine.
3. Inspect per-query wins/losses and latency tails; trace every table value to summary.json and raw logs.
4. Write the three-page report, export slides, record all members within 8 min, and test the recording in a signed-out browser.
5. Publish the repo, self-assess with evidence, zip the repo including its history and submit by December 30 at 22:00. Submit and post by a Sunday voting cutoff if seeking a live presentation; the last listed voting cutoff is December 13.
6. Check the weekly pairing announcement, reproduce the assigned team's study and file the issue within seven days of pairing. Prepare for a live 10-minute presentation plus 5 minutes of questions if selected.
