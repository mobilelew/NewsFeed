# News Reader — Shared Approved Report Archive

## Separation of feeds
- `feed.json`: automated RSS research discovery; **not verified**.
- `briefing.json`: latest **approved** morning/evening briefing for Scriptable, starting in `unpublished` status.
- `reports/YYYY-MM-DD/{morning,evening,weekly}.json`: dated reports that the publisher refuses to overwrite.
- `reports/latest/{morning,evening,weekly}.json`: latest approved report for each type.
- `reports/latest/morning-baseline.json`: dated morning baseline the evening process may retrieve.
- `reports/latest/index.json`: stable pointers to archival reports.

## Publish workflow
1. Independently research and verify report claims. This repository **does not** ingest ChatGPT scheduled-task output automatically and the publisher **does not** verify whether cited links substantiate claims.
2. Prepare a JSON under `submissions/`. The sample file `submissions/approved_report.template.json` is intentionally unapproved and contains placeholders; never publish it unchanged.
3. Review each assertion against original records (Congress.gov, Texas Legislature Online, Arkansas General Assembly, Oklahoma Legislature, applicable courts/agencies) and independent reporting when available. Set `approved=true`, `editorial_review=completed`, and a nonempty `reviewed_by` only after that review.
4. In GitHub, configure **Settings → Environments → news-reader-publication**, including required reviewers if supported by your plan and repository visibility. The workflow references this environment, but merely naming an environment in YAML does **not** guarantee review enforcement.
5. Run **Actions → Publish approved News Reader report → Run workflow** using a committed submission path such as `submissions/2026-10-14-morning.json`.
6. Inspect `https://mobilelew.github.io/NewsFeed/briefing.json` and the `reports/latest/` pointers. Confirm the report date is current, the evidence URLs work, and no placeholder content is present.
7. Only after real publication and validation, replace the Scriptable widget code to read `briefing.json`. Its current script may still use `feed.json` and intentionally has not been changed in this deployment.

## Important limits
- RSS source discovery is not an approved report; approval flags and evidence URL formatting alone do not establish independent verification.
- Report content and all links are public on GitHub Pages; avoid personal, confidential or secret information.
- The morning baseline supports comparisons only when the evening researcher can actually access it. Separate scheduled ChatGPT tasks are **not** automatically connected to the archive.
- No audio, podcast, Alexa or automatic ingestion is deployed here.
- Correcting an archived report requires an explicit reviewed versioning/supersession procedure rather than overwriting an existing date+type.
- On a concurrent push, the workflow can fail; rerun it after reviewing branch updates.
