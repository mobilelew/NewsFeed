# Phase 4B — Structured legislative events (foundation)

This module introduces a **documented-event ledger**, not autonomous legal fact checking.

`legislative_event_ledger.py` accepts a JSON file of attributed procedural events in `legislative-records/`, checks status vocabulary, dated action, attribution, URL syntax and uncertainty disclosure, deduplicates records and writes `legislative-events.json`. It expressly refuses to imply that introduced, signed or challenged measures are operative law solely because metadata says so.

**Event schema**: `jurisdiction` (federal, texas, arkansas, oklahoma), `identifier`, `action`, `action_date`, `source_url`, `source_description`, `attribution`, `status_note`, `verification: "Legal Effect Unclear"`, `what_cannot_be_concluded`, `resolution_needed`. An optional `effective_date` can only be attached to an expressly documented effective or implemented action; this rule checks consistency, not underlying evidence.

**Important**: No production events have been submitted, and no `legislative-events.json` feed is yet published. The ledger is not connected to the state page-fingerprint monitor and does not automatically extract bill history from state portals. Claim-level evidence remains unverified until source documents can be retrieved and cross-checked. Existing state source monitoring has not yet published `state-source-monitor.json`.

Next integration must build stable document-specific collectors, corroborate action dates and statuses against actual records, distinguish individual provisions and litigation stays, and preserve corrections. Do not publish fabricated example events.
