# News Reader: Claim-level Verification — Development Stage

**Product objective:** Deliver news from diverse outlets, test each consequential factual assertion against the records of institutions competent to establish or refute it (courts, legislation, regulatory and administrative bodies, original datasets, corporate regulatory filings, authenticated research) and publish the outcome regardless of news-outlet preference.

**Seven evidence statuses:** Verified, Corroborated, Unsubstantiated, Disputed, Legal Effect Unclear, Unverified, Refuted. Include important unresolved items in the **unified briefing**, with qualifications beside their claims.

## Implemented in this step
`claim_evidence_audit.py` accepts individual claims, original news attribution, retrieved source documents with content and retrieval timestamps, exact cited excerpts, an explicit relationship (`supports`, `contradicts`, `context_only`, `unclear`), the evidence category, and a clear limitations/resolution statement. It validates excerpt presence, evidence source URLs/types, and minimum support/contradiction consistency for status labels. Tests guard against treating citation URLs or absent text as proof.

## Explicitly not implemented
The script **does not retrieve news headlines, authenticate the source publisher, independently prove that a quoted document is authentic, determine whether a source passage logically entails or contradicts a claim, reconcile competing court orders, or evaluate the original publication's validity**. Those are the essential next integrations. The code sets `semantic_verification: not_independently_established` and `production_ready: false`. It must not be portrayed as a working automatic fact-checker or used to label claims verified solely because words appear on an official page.

## Required next technical milestones
1. Collect reports from a viewpoint-diverse set of discovery sources; attribute outlet and exact reported claim.
2. Route each claim by *competent authority*: bill history, enacted statute, court docket/operative order, agency rule, official data release, securities filing, published research etc.
3. Retrieve and pin source records with dates, issuing institution, canonical URL, document identifier and content hash. Reject inaccessible/irrelevant sources without fabricating references.
4. Run entailment and contradiction assessment against cited source passages, with independent secondary corroboration where appropriate, temporal/legal-state reconciliation, and a conservative unknown outcome.
5. Publish unified report entries with the original headline and qualified finding. Evaluate real coverage, authentication, morning/evening continuity and distribution acceptance tests before retiring existing scheduled reports.

No human editorial approval is required by policy, but `unverified` or `legal effect unclear` are legitimate outcomes where public evidence is insufficient.
