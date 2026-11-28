# C4 submission handoff

Rechecked November 25, 2026. All listed times are Vietnam time (UTC+7). The assignment was revised November 23: the final submission deadline is now **December 30, 2026 at 22:00**. [Current course brief and rubric](https://drive.google.com/file/d/1F3DQ0tjuXOuzCmrQ4Z9iqS05n7h_M62j/view)

## Before submitting

- Record the three speaking parts from [TALK.md](../TALK.md) in at most eight minutes. Show the replay or raw log. Verify the video link while signed out, then add it to `TALK.md`.
- The public repository is [https://github.com/JakeConal/c4-rag-seminar](https://github.com/JakeConal/c4-rag-seminar). Its URL is the first line of `REPORT.md`. After future edits, refresh `report.pdf` and push the final commit.
- Confirm each claimed mark in `SELF_ASSESSMENT_REPORT.md` against the course template and actual evidence. Increase the talk score only after verifying the recording and update the total accordingly.
- Run `python3 scripts/submission_check.py`. Commit the completed deliverables, then run `python3 scripts/package_submission.py --score <total>` with the self-assessment total. This packages the repository and its `.git` history as `23120045-23120124-23120175_<total>.zip`. Check the extracted copy, linked artifacts, and reproduction commands. One member submits from their student email. [Classroom assignment](https://classroom.google.com/u/1/c/ODg2MTU1OTQ4NDc0/a/ODk4OTA4NDI0NTUx/details)
- If participating in voting, turn in and post by a Sunday at 22:00. The next regular cutoff is November 29 for the December 3 session. Votes are counted Tuesday at 22:00 and presenters announced Wednesday; unselected posts carry forward. The last voting cutoff is December 13 for the December 17 session. Not posting costs no marks. The one-off November 24 cutoff was only for the November 26 session.

## Facebook post draft

> #AWADSeminar23_3
>
> C4 · Chunking and reranking for RAG
>
> Does a cross-encoder reranking the vector top 50 improve MRR@5 and recall@5 over vector top five, and what does it add to p50 and p95 latency?
>
> In five CPU passes over 300 SciFact claims, MRR@5 changed from 61.05% to 67.20% (+6.15 pp), and recall@5 from 73.07% to 77.72% (+4.64 pp). Paired added p95 was 1928.3 ms.
>
> Talk: [public recording link]

## Red-team follow-up

Pairs are announced each Monday for teams that submitted by Sunday 22:00 and have not yet been paired. Reproduce the assigned team's measurement, then open an issue in that team's public repository within seven days, by the following Monday at 22:00. Use the exact title `[red-team] 23120045-23120124-23120175`. Include the commit and command used, reported versus reproduced values with units, and one finding supported by a log or other evidence. Missing your issue deadline costs 10 points.

The last regular Monday pairing is December 28. Teams submitting after it are paired December 31 and file their issue by January 7, 2027 at 22:00. A selected presenting team prepares 10 minutes of presentation and 5 minutes of questions; a random member may be questioned.
