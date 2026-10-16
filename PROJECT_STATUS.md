# News Reader — Project Status and Decision Log

Last reviewed: 2026-10-15 (America/Chicago). Maintained as the project handoff/status record; update after material engineering milestones. Do not equate green tests with editorial readiness.

## Goal
At 6:00 AM and 8:00 PM America/Chicago, automatically discover significant news, isolate reported factual assertions, evaluate them against competent original public records regardless of news-outlet preference, and publish a unified, source-linked evidence-labelled briefing to https://news.palmerfamily.org/. Retain the morning baseline for real evening comparison and preserve versioned archives. No routine human editorial approval; unresolved claims clearly classified.

## Seven evidence classifications
Verified; Corroborated; Unsubstantiated; Disputed; Legal Effect Unclear; Unverified; Refuted.

## Four mandatory editorial acceptance tests
1. **Coverage:** Complete federal/TX/AR/OK government, rights, finance/housing/crypto, beef/chicken/turkey agriculture, AI/data centers/technology/cybersecurity and practical household implications, with dated scope and explicit source gaps.
2. **Authentication:** Inspect real consequential claims against actual original records, content and relevant dates/operative legal status; preserve citations and source conflicts. Mere URL validation is not proof.
3. **Continuity:** Actual evening report compares a full same-date archived morning report, with real sourced changes and missing-baseline disclosure.
4. **Delivery:** The same current complete report is observable in archive, public website and each claimed supported device; labels and source links survive rendering.

Production ready only if all four have actually passed a real end-to-end morning/evening cycle.

## Current system and evidence
| Component | Status | Notes |
|---|---|---|
| Namecheap cPanel hosting, HTTPS and separate subdomain | Configured by owner | Screenshot confirms news.palmerfamily.org front end loads |
| Front-end news website | Deployed | Displays 'Full verified briefing not yet published' until data exists |
| GitHub repo mobilelew/NewsFeed | Active | Code, workflows, metadata pilot, archival publisher |
| Google News RSS discovery | Pilot | feed.json discovery is not fact checked |
| CISA KEV report-to-catalog matching | Pilot code | Narrow claim only; live successful publication not yet demonstrated |
| Federal Register collector | Metadata-only pilot | No semantic legal verification |
| State legislative web monitors | Active pilot | Page changes are not legislative events |
| Claim-level audit structure | Partial | Excerpt presence != semantic entailment |
| Full source retrieval + claim interpretation and evidence reasoning | Missing | Essential for requested service |
| Full AI-generated evidence-backed report scheduler | Candidate generator now reads source registry; not exercised | ChatGPT scheduled task chats do not automatically submit to GitHub |
| Morning/evening report publisher and JSON archive | Built, not exercised end to end | briefing.json remains unpublished as last observed |
| Actual full evening-to-morning baseline comparison | Unproven | Comparison script exists |
| Website automatic presentation | Frontend installed; no full reports | Depends on report publication |
| iPhone and voice delivery | Not integrated with full published report | Existing Scriptable widget reads RSS discovery |
| Old ChatGPT morning/evening tasks | Keep enabled | Stop only after verified replacement works |
| Development follow-up task | Scheduled daily | Does not guarantee engineering task completion |

## Current decision and blocking dependency
Use GitHub Actions as scheduled research/verification compute initially; Namecheap hosts frontend; FreshRSS optional later as additional discovery source. A functioning API-based research generator requires dedicated API credentials and separately billed OpenAI API usage. Owner reports OpenAI API project created, billing credits and spend controls configured, and GitHub Actions secret `OPENAI_API_KEY` saved. Credential value has not been exposed to the assistant or independently tested. The redundant API-only connectivity test was removed at the owner's request. First paid API call should generate a substantive news report candidate.

## Next engineering milestone
Implement real OpenAI API-driven research generator using live original-source retrieval with source pinning, claim entailment/contradiction, conservative uncertainty, full briefing JSON output, publisher integration and two scheduled America/Chicago report cycles. Validate real source audit and public site rendering. Do not claim done merely because an API key is set.

## Change log
- 2026-10-14: Evidence status policy adopted; no mandatory human publication hold.
- 2026-10-14 to 15: Metadata official-record pilot, state availability checks, report archive, continuity logic and direct-ingestion workflow committed.
- 2026-10-15: Human-assisted Reuters/BLS sample evidence audit committed; claim excerpt audit and CISA-specific automated matching pilots committed.
- 2026-10-15: Website uploaded to Namecheap by owner and visually confirmed; full briefing still absent.
- 2026-10-15: Owner requested persistent progress log and OpenAI API setup walkthrough. API project billing/key is the present external configuration dependency.

## Progress reporting convention
For each milestone, record what changed, direct link to source/commit, demonstrated result, unresolved limitations, and next dependency. Distinguish code-tests, live source verification, editorial coverage, and observed website delivery.

- 2026-10-15: Owner confirmed OPENAI_API_KEY stored in GitHub repository secret; committed secure minimal API connectivity workflow `.github/workflows/test-openai-api.yml` and `test_openai_connection.py`. Live invocation not yet run or confirmed. API test is not editorial authentication or full-report generation.

- 2026-10-15: Owner set resource-efficiency rule: no standalone paid API smoke calls. Deleted `.github/workflows/test-openai-api.yml` and `test_openai_connection.py`. First billed API run must produce a real source-backed briefing attempt with reusable evidence; dry-run structural checks remain free. Do not assert connectivity until the real workflow runs.

- 2026-10-15: Added `generate_news_candidate.py` and manual GitHub Actions `Generate real News Reader report candidate`. Makes one Responses API request with web_search, tries to generate a sourced full-coverage morning/evening candidate, validates schema, and retains candidate as an Actions artifact. Added offline tests. **Not run**, content authenticity not established, no automatic full-report publishing, no scheduled production cycle. First execution should be a useful paid research attempt, not an isolated API connection test.\n
- 2026-10-15: Source registry connected to `generate_news_candidate.py` research request; candidate now exposes jurisdiction coverage gaps. The paid workflow `generate-news-candidate.yml` remains a manual research run (preserves a usable report artifact). **No paid research run or automatic full-report publication has been confirmed.** Next: execute one genuine candidate run, audit claims against the referenced original records, then authorize scheduled publication only once evidence-level and coverage acceptance checks work. No RSS discovery item is automatically treated as verified.

- 2026-10-15: First API-backed candidate workflow returned no output_text and failed safely with no briefing published. Root cause not yet established (possible incomplete model response). Updated generator to preserve safe API response metadata, flag incomplete responses, use low reasoning effort, reduce headline count and permit more output tokens. Added artifact capture for diagnostics and offline regression tests. Next run must first pass free compile/unit checks; inspect diagnostic status/usage and report artifact before further billing or scheduling.

- 2026-10-15: Real generator failed in preflight Python compilation due to a literal escaped `\\n` between `max_output_tokens` and `reasoning` dictionary entries. Fixed at commit `c430b41`. Earlier failures also arose from malformed YAML and pasted escape sequences. Explicit engineering quality concern: do not request another paid research run before free compile/unit-test workflow passes. No real briefing was produced or published during these failures.

- 2026-10-15: First API research produced JSON text and reached publisher validation but failed on `Headline 0 needs jurisdiction`. The preexisting `if: always()` artifact step should preserve `submissions/ai-research-candidate.json` from that failed run. Do NOT spend credits regenerating until the retained candidate has been inspected and corrected offline. Updated generator to save a machine-readable validation result alongside the candidate without suppressing or inventing missing jurisdiction. This is structural progress only, not verified news publication.

- 2026-10-15 late evening: Inspected user-supplied successful-run ZIP (8 headlines, API response completed; 23,630 total tokens). Embedded validation file states `valid:false`: `Corroborated headline 0 needs two distinct independent-source URLs`; hence GitHub run success was not publication-quality success. Independently inspected official Federal Reserve, Texas Legislature, and USDA source pages; found event/publication-date confusion (Oct 19 vs Oct 20 Fed meetings; Texas report stamp Oct 2026 on Sep 2025 actions), and USDA Poultry Slaughter date confusion (Oct 23 vs asserted Oct 15). All eight items require correction, qualification or further evidence before public display. Saved full assessment at `audits/2026-10-15-first-api-candidate-assessment.json`. Publication remains blocked. Next: implement source-level temporal/corroboration guardrails before any paid rerun.

- 2026-10-16: Implemented no-cost `candidate_quality_gate.py` and offline tests based on first real eight-headline audit: flags unrecognized jurisdiction, weak Corroborated source-origin counts, missing event dates/source inspection timestamps/claim-specific evidence rationale, absent primary reference for Verified, and morning reports generated outside a morning window. The API generator now saves a `quality_screen` and marks candidates invalid when these checks fail; it still retains candidate artifacts. Updated generation instructions and free CI coverage. This is a conservative structural risk screen, **not substantive authentication**; tests and a new live report remain to be verified. No new API research was run for this change.

- 2026-10-16: Re-inspected the actual user-supplied Oct 15 research ZIP offline: embedded validation `valid:false` due Corroborated headline 0; 8/8 headlines have no `event_date`, `source_checked_at`, or `claim_evidence_note`, and `arkansas/oklahoma` is invalid. Generator previously returned exit code 0 despite validation false; corrected it to write artifacts/diagnostics and then exit nonzero on rejection. Paid generation workflow now runs quality-gate unit tests before API; added regression reproducing known first-candidate omissions. No additional API call made. GitHub CI result not independently observed following these commits.

- 2026-10-16 overnight: User confirmed free CI validation passed for previous quality-gate changes. Added timezone-aware `source_checked_at` validation and regressions; added explicit `research_origin=api_web_research` and set `independent_source_authentication=false` on all generated reports. `publish_report.load_submission` now refuses API candidates that fail the quality screen or lack independently authenticated source evidence; regression tests added. GitHub CI results for these *new* commits are not yet confirmed. This is a fail-closed publication protection, not a completed independent claim authentication engine; do not describe the API generator as fully automated publication.

- 2026-10-16: User confirmed previous free validation green. Added `source_capture.py`, a bounded, allowlisted official-HTTPS source retriever that stores UTC retrieval time, original URL, media type, byte count, raw SHA-256 and extracted text; refuses redirects, disallowed origins/media types, and >1MB responses. Added offline mock-network tests and registered them in no-cost CI. This establishes inspectable source snapshots, **not independent semantic authentication**, legal-effect verification, or production source coverage. Source capture is not yet integrated into automated API candidate generation/publishing; no publication claims warranted. Current new CI outcome not yet confirmed and no paid API calls made.

- Added `.github/workflows/capture-source.yml`: manual GitHub Actions entrypoint for a nominated allowlisted official URL, running free tests then retaining an original-source snapshot as a downloadable artifact. This is an operational primary-record retrieval demonstration only; source availability and live run results have not yet been checked. No OpenAI API usage.

- 2026-10-16: Added `captured_claim_audit.py` to join provenance-labelled original source snapshots with claim-specific excerpts and existing `claim_evidence_audit` checks; requires exact excerpt presence, tracks capture hashes, rejects missing provenance and fabricated quotes, and explicitly sets `publication_approved=false` and `semantic_verification=not_independently_established`. Added offline tests and no-cost CI wiring. This is a useful captured-record-to-claim evidence trail, not independent truth/entailment verification or an automatic publisher. The current commits have not yet been confirmed green; no paid API research or public news publication.

- 2026-10-16: Responded to operator fatigue: no more manual workflow-run checks requested as routine practice. Implemented `reader.html` as a public live news-viewer against existing hourly `feed.json`, scheduled isolated `official-records.json`, and independently published `briefing.json`. UI explicitly labels discovery stories unverified and Federal Register index entries legal-effect unclear. Expanded RSS discovery to include dedicated Texas, Arkansas, and Oklahoma categories and up to 24 slots. This is *readable automatically updated discovery plus a separate metadata-only official digest*, **not** completed authenticated full morning/evening news; external GitHub Pages rendering and update delivery have not been live-verified as of this commit. Complete source-verified publication and transfer to news.palmerfamily.org remain outstanding. No paid API calls or human editorial approval required for the current discovery display.

- 2026-10-16: User independently demonstrated GitHub Pages `reader.html` rendering current discovery feed via screenshot. Prepared one-time cPanel deployment artifact `deployment/namecheap/index.html` with feeds anchored to `https://mobilelew.github.io/NewsFeed/`, so `news.palmerfamily.org` can use current hourly discovery and existing isolated official-record digest without further file changes for content updates. **NOT YET DEPLOYED TO NAMECHEAP:** this ChatGPT/GitHub connector cannot write to cPanel. Deployment requires a one-time replacement/upload into the correct subdomain document root or a separately connected hosting deployment integration. Live domain behavior and cross-origin fetch remain to be verified after upload. No firm publication time can be guaranteed until hosting action performed.

- 2026-10-16: Responding to owner request for unattended end-to-end operation, implemented `service_health.py` and unit tests, integrated `service-health.json` into the existing hourly `update-feed` workflow. Added `web_delivery_probe.py` and test suite, with `.github/workflows/monitor-delivery.yml` scheduled every three hours to check public `news.palmerfamily.org`, GitHub reader, `feed.json` and `briefing.json`, failing visibly and retaining diagnostics on outage. Registered tests in free CI. These improvements monitor delivery and honestly disclose incomplete full-briefing acceptance; they do NOT provide the still-missing independent claim authentication. Full AI reports remain blocked because generator explicitly marks `independent_source_authentication=false`; scheduling paid API calls now would predictably generate candidates that cannot publish. No billable API run, no verified morning/evening report, and no claim of completion. GitHub Actions runs for these new commits not yet observed.
