# Autonomous publication — official-record pilot

This is a **narrow, cautious pilot**, not the full News Reader research engine.

## What runs
- GitHub Actions **Auto-publish official-record pilot** is scheduled for approximately **6:25 AM and 8:25 PM America/Chicago** (subject to GitHub schedule delays), plus manual dispatch.
- It fetches current-day publication metadata from the Federal Register API, chooses up to eight records, and writes an evidence-labelled report into a separate official-records pilot archive.
- It uses `Legal Effect Unclear` on each item and expressly says no operative legal conclusion has been reached. A primary URL proves where the document can be inspected; it does not validate any inferred effects.
- `publish_report.py` validates the resulting structure. If the current day's official-records archive exists, publishing skips without replacing history. If no records are available, it leaves public files unchanged.
- A successful run commits `official-records.json` and dated `reports/official-records/`; temporary generated `submissions/auto-pilot.json` is **not committed**.
- Unit tests run before collection.

## Gaps
The pilot **does not change `briefing.json`** or occupy full morning/evening report dates. It **does not** independently fact-check legal or economic claims or cover Congress, Texas, Arkansas, Oklahoma, court dockets, agriculture, finance, technology, cybersecurity, or complete News Reader reports. It does not use the existing scheduled ChatGPT news tasks or the iPhone Scriptable widget. It relies on a single official index, and its output is intentionally labelled metadata-only. Source outages produce no report, not fabricated data.

## Operational risks
- Multiple jobs writing the same repository can race; this job retries.
- Github Actions schedules may be delayed or paused.
- The pilot uses a separate `reports/official-records/` namespace; full reports and the widget remain unaffected.
- API access can fail or return unexpected schema. The workflow will fail rather than invent records.
