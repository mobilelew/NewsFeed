# News Reader — direct report ingestion (Phase 4C)

The repository can now receive a **complete, externally generated** evidence-status-v1 report without first committing a JSON file to `submissions/`.

## Two ways to send a report
1. Manual integration test: **Actions → Ingest and publish News Reader report → Run workflow**; supply complete `report_json`.
2. Authorized automated producer: POST to the GitHub REST `repos/mobilelew/NewsFeed/dispatches` endpoint using an appropriately scoped GitHub App installation token or fine-grained token authorized for this repository and Actions/contents access. Use `event_type: news_reader_report`, with `client_payload.report` containing the complete report **object**. Do not make tokens public or commit them. GitHub authentication is required; a public visitor cannot publish merely by posting JSON.

Payload must satisfy `publish_report.load_submission`: `schema_version: 1`, `publication_policy: "evidence-status-v1"`, `report_type`, offset-bearing `report_time` and nonempty, evidence-labelled `headlines`. Morning needs an explicit `baseline`. Uncertain claims need full attribution/uncertainty fields. Original links must not be made up. The publisher only checks syntax and claim-framing fields; it does **not** independently verify claims.

The ingest workflow runs tests, stages the report under `submissions/direct-ingest.json` **without committing the temporary file**, and calls the existing archive publisher. Evening publication includes a direct report-text comparison only when a full morning report from the same Central-time day is in `reports/YYYY-MM-DD/morning.json`.

## Important limitations
- **The source generator is NOT yet deployed.** Existing scheduled ChatGPT task conversations are not automatically exported to this workflow, even if moved into the News Reader project.
- `briefing.json` remains unpublished until a genuine validated morning or evening submission is provided.
- Do not paste fictional examples into the publish input as if they were researched findings.
- The full archive is public. Do not submit private or personal content.
- GitHub dispatch requires a securely held token; no credentials have been configured in this change.
- Publication remains immutable by report day and kind. Corrections require versioned supersession; older submissions must not be used to replace current authoritative views.
- Run tests and an end-to-end controlled publication before considering the pipeline production-ready.
