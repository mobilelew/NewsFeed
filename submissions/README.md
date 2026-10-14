# Evidence-labelled report submissions

News Reader uses the **evidence-status-v1** policy: publish qualified findings without mandatory human editorial approval. This repository does **not** automatically ingest ChatGPT reports or independently check whether cited documents prove a finding.

Add a JSON document under `submissions/` and run **Actions → Publish evidence-labelled News Reader report** with its repository path. The workflow has no protected-environment reviewer requirement; the existing GitHub environment settings remain saved but are not used by this workflow.

Required top-level: `schema_version: 1`, `publication_policy: "evidence-status-v1"`, `report_type` (morning/evening/weekly), timezone-aware `report_time`, and nonempty `headlines`. Morning reports require `baseline`; weekly reports may include `weekly_trend`.

Each headline must include `title`, `summary`, `jurisdiction`, `claim_type`, `verification`, and `evidence`. `claim_type` is one of `established_fact`, `attributed_claim`, `proposal`, `legal_proceeding`, `data_release`. `verification` is one of **Verified**, **Corroborated**, **Unsubstantiated**, **Disputed**, **Legal Effect Unclear**, **Unverified**, or **Refuted**.

Every evidence entry has `type` (`primary`, `independent`, or `attribution`), `description`, and an HTTPS `url`. **Verified** requires a primary source. **Corroborated** requires two different independent-source URLs. Any other classification requires `attribution`, `what_is_known`, `uncertainty`, `what_cannot_be_concluded`, and `resolution_needed`. **Legal Effect Unclear** additionally requires `legal_status`. A **Refuted** claim must be explicitly attributed, not treated as an established fact.

This is a **structural and editorial-language gate, not substantive fact checking**. Automated workflows must avoid publishing private or sensitive information, defamatory allegations without appropriate sourcing and framing, and unsafe legal instructions derived from uncertain evidence. A placeholder/example URL is rejected. Existing dated archives are immutable; corrections need a superseding entry rather than silent overwriting.

A sample is available at `submissions/evidence_report.template.json`. Never publish sample content.
