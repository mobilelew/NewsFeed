# News Reader — Permanent Publication Policy (evidence-status-v1)

Effective October 14, 2026. Supersedes mandatory human approval of publication.

## Editorial rule
Publish sourced findings promptly with precise evidence status. Publication means the claim has been accurately attributed and classified; it does **not** certify that the underlying assertion is true. Never silently promote RSS headlines, allegations, court interpretations or proposed legislation into verified conclusions.

## Evidence labels
- **Verified** — directly supported by authoritative primary evidence, with no unresolved material contradiction.
- **Corroborated** — two or more demonstrably independent credible sources support the claim; primary documentation is unavailable.
- **Unsubstantiated** — the assertion is attributable to a named source but adequate supporting evidence is absent.
- **Disputed** — material conflict exists between records, sources or interpretations; describe both and why they differ.
- **Legal Effect Unclear** — a legal action or claim is documented, but scope, enforceability, timing, stay or other operative effect remains unresolved.
- **Unverified** — evidence is insufficient to determine accuracy; identify precisely what has not been confirmed.
- **Refuted** — reliable evidence contradicts the claim; report as a refuted attributed claim, not as a plausible factual statement.

## Requirements for non-Verified findings
Publish with (1) a clear source attribution, (2) what is established, (3) what is missing or contradictory, (4) what cannot be concluded, and (5) what document or development would resolve the uncertainty. Do not provide definitive legal, voting, medical, tax or financial instructions where operative facts remain uncertain. Distinguish proposed, enacted, effective, stayed, and implemented measures. State actual source dates and America/Chicago cutoff.

## Operational policy
No required manual reviewer or artificial publication hold. Automated pipeline validates claim schema, attribution, status, citation URLs and basic placeholder rejection, then publishes qualified findings. A failing validation prevents malformed or misleadingly structured output, not a discretionary editorial review. Publishing must not leak private information, reveal credentials, or amplify ungrounded defamatory allegations.

## Known limitation
The current `publish_report.py` checks whether **metadata and required qualifiers are present**, not whether evidence substantiates the content. The GitHub workflow accepts committed submissions; autonomous research, source fetching, semantic verification, report generation and automatic submission are **not yet deployed**. No claim of full factual verification or end-to-end automation should be made until these systems exist and have been tested.

## Archival integrity
Immutable `reports/YYYY-MM-DD/<type>.json` files; supersede with explicit corrections rather than silently rewriting history. `briefing.json` is the display feed of most recently published morning/evening findings and their labels. `feed.json` remains an unverified discovery feed. Other endpoints and device readers must preserve labels and links.
