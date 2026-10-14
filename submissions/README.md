# Approved report submissions

Place a JSON file here only after independent editorial verification. Run the GitHub Actions **Publish approved News Reader report** workflow with its path, for example `submissions/2026-10-14-morning.json`.

Required: `schema_version: 1`, `report_type` (morning/evening/weekly), offset-aware `report_time`, `approved: true`, `editorial_review: completed`, `reviewed_by`, and nonempty `headlines`. Each headline needs `title`, `jurisdiction` (federal/texas/arkansas/oklahoma/national/international/multiple), `verification`, and `evidence` [{type: primary/independent, description, url}]. Confirmed conclusions must cite a primary source. Morning reports also require a nonempty `baseline` array. Weekly reports may contain `weekly_trend`.

**Approval flags are not proof of verification.** The publisher checks structure, not the accuracy of the evidence or conclusions. Do not publish private information. The GitHub Pages archive is public. Do not use placeholder/example evidence as actual citations.

Reports are immutable by path: publication refuses to overwrite an existing date+type. A correction needs a deliberate, reviewed versioning process.
