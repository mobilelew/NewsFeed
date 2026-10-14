# News Reader — Shared Evidence-Labelled Report Archive

## Separation of feeds
- `feed.json`: automated RSS research discovery; **not verified**.
- `briefing.json`: latest evidence-labelled morning/evening briefing for Scriptable, starting in `unpublished` status.
- `reports/YYYY-MM-DD/{morning,evening,weekly}.json`: dated reports that the publisher refuses to overwrite.
- `reports/latest/{morning,evening,weekly}.json`: latest published report for each type.
- `reports/latest/morning-baseline.json`: dated morning baseline the evening process may retrieve.
- `reports/latest/index.json`: stable pointers to archival reports.

## Publish workflow

Publication policy: **evidence-status-v1**. Findings may be published with qualifications (Verified, Corroborated, Unsubstantiated, Disputed, Legal Effect Unclear, Unverified, Refuted) without mandatory human review. No automated verification engine has been deployed: publisher validation checks formatting, attribution fields, evidence-link syntax, and status-dependent requirements, **not source truth**.
1. Research and identify credible source material; classify each claim accurately. Never describe unknown legal effect as currently operative.
2. Prepare an `evidence-status-v1` JSON under `submissions/`, following `submissions/README.md`. Old approval-format submissions are rejected.
3. Run **Actions → Publish evidence-labelled News Reader report → Run workflow** with the committed submission path. The workflow no longer specifies the `news-reader-publication` environment, so GitHub environment manual review is not a publication prerequisite.
4. Inspect `https://mobilelew.github.io/NewsFeed/briefing.json` and archive pointers; ensure original URLs and time frames are correct.
5. The widget still needs migration from `feed.json` to `briefing.json` and installed iPhone Scriptable updates.

## Important limits
- RSS source discovery is not an approved report; approval flags and evidence URL formatting alone do not establish independent verification.
- Report content and all links are public on GitHub Pages; avoid personal, confidential or secret information.
- The morning baseline supports comparisons only when the evening researcher can actually access it. Separate scheduled ChatGPT tasks are **not** automatically connected to the archive.
- No audio, podcast, Alexa or automatic ingestion is deployed here.
- Correcting an archived report requires an explicit reviewed versioning/supersession procedure rather than overwriting an existing date+type.
- On a concurrent push, the workflow can fail; rerun it after reviewing branch updates.
