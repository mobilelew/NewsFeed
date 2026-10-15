# Morning and evening report continuity

## Authoritative storage
The full briefing archive is `reports/YYYY-MM-DD/morning.json` and `reports/YYYY-MM-DD/evening.json`, generated only from evidence-labelled report submissions. The official-record pilot in `reports/official-records/` is **not** a full morning baseline and is never accepted for direct briefing comparison.

## Evening check
When `publish_report.py` publishes an evening report it looks up **that same Central-time date's** `morning.json` in the full archive:
- If missing, `morning_comparison.comparison_status` is `morning_unavailable` and the report explicitly says no direct comparison was possible.
- If present, `direct_text_comparison` lists identifiers newly included, omitted, or with changed text/labels. These are **report differences, not verified real-world changes**. Source-based legal/economic analysis must separately establish the underlying event.
- Publication never borrows yesterday's baseline and never substitutes the Federal Register pilot.

## Platform boundary
Moving ChatGPT task chats into the News Reader project makes them easier to locate for the user but does not establish reliable automatic access to their content from GitHub Actions or other scheduled ChatGPT task runs. A scheduled task cannot be assumed to import its output into `submissions/`. As of this phase, `briefing.json` remains unpublished; original ChatGPT scheduled tasks must not be disabled until a complete replacement is tested.

## Next engineering steps
1. Implement an API-based generation job that follows the complete News Reader detailed reference, retrieves official sources for all jurisdictions and topics, and writes correctly classified `submissions/` documents.
2. Run automated validation and publish to the full archive. Confirm morning output exists **before** the evening report runs.
3. Verify a complete end-to-end cycle and compare the actual historical artifacts.
4. Connect the iPhone widget to `briefing.json`; retire parallel ChatGPT schedules only after proven parity.
