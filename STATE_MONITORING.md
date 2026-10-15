# Expanded state-source monitoring — phase 4A

This is an **availability and change-detection monitor**, not verification of legislation or of legal effect. It records the timestamp, accessible official pages, content fingerprints, differences from earlier fingerprints, and failures for official legislative sites in Texas, Arkansas and Oklahoma.

- Run **Actions → Monitor official state sources → Run workflow** to establish the initial baseline.
- Scheduled twice daily (UTC 12:40 and 01:40; subject to GitHub scheduling delays). Unlike the original pilot, this is intentionally a status check, not a legal-news briefing.
- Output: `state-source-monitor.json`. It does not alter `briefing.json` or the existing `official-records.json`.
- A changed fingerprint is **not** evidence that a law changed. Dynamic menus, session counters or other page content may trigger changes.
- When an official website cannot be accessed or parsed, the result is `unavailable` or `undetermined`, not a claim that nothing happened.
- Required next step before substantive reporting: obtain stable machine-readable official bill/committee/rule records, extract exact event dates and identifiers, then verify their status and effective dates against original documents.

Sites monitored:
- Texas Legislature Online homepage and legislation page.
- Arkansas General Assembly homepage and meeting calendar.
- Oklahoma Legislature homepage and bill-tracking page.

The Federal Register pilot remains separately published under `official-records.json`.
