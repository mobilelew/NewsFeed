# News Reader iPhone Widget — setup

## What works
- Scriptable widget displays recent headlines, a verification label, a weekly trend, and the feed's freshness.
- GitHub Actions automatically refreshes **news-discovery headlines** from accessible official-source RSS feeds approximately hourly. Individual sources can fail or change; errors are stored in feed.json.
- `editorial.json` can supply **human-reviewed verification statuses and weekly analysis**, which take precedence over discovery headlines.
- The widget caches the last accessible feed and marks stale/cached results.

## Important limitation
An RSS article from an official agency is evidence of an agency's announcement; it is **not** independent confirmation of every assertion. The automated updater never labels a headline `Confirmed` on its own. Genuine claim-level fact checking and a weekly synthesis require editorial review and curated publication into `editorial.json` (or a separate trusted automation you set up). Scheduled ChatGPT Project tasks do not automatically export results into this feed.

## Setup (GitHub Pages + Scriptable)
1. Create a **public GitHub repository** (for example `newsreader-widget`). **Everything in this repo and its JSON feed is public. Do not put private news notes, keys, tokens, or personal information there.**
2. Upload `build_feed.py`, `editorial.json`, `feed.json`, and the `.github/workflows/update-feed.yml` file, retaining the folder structure.
3. In GitHub repository **Settings → Pages**, select **Deploy from a branch**, branch `main`, folder `/ (root)`, and save. Wait until Pages shows a published URL.
4. Go to **Actions → Update News Reader feed → Run workflow**. Check that `feed.json` gains genuine sourced headlines. Source feeds are best effort; if all fail, the widget shows the last known feed rather than inventing news.
5. On iPhone, install **Scriptable** from the App Store. Create a new script, paste the contents of `NewsReaderWidget.js`, and replace `FEED_URL` with `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/feed.json` (use your actual account and repository name). Run once inside Scriptable for a preview.
6. Long-press iPhone Home Screen → Edit → Add Widget → Scriptable; choose a **medium or large** widget; long-press widget → Edit Widget → select the `NewsReaderWidget` script.
7. To publish a verified story or weekly trend, edit `editorial.json`, including source references in the full published report, then manually run the GitHub workflow (or let the next scheduled run pick up your edit).

## Suggested human-reviewed headline object
```json
{
  "category": "U.S. POLICY",
  "title": "Concise, verified claim",
  "verification": "Confirmed",
  "url": "https://example.gov/original-record",
  "evidence_urls": ["https://example.gov/original-record", "https://example.org/independent-account"],
  "difference": "Describe what reporting got wrong or what remains uncertain."
}
```

Use the six classifications from your News Reader project: Confirmed, Partially Supported, Disputed, Unsupported, Contradicted, Not Yet Verifiable. The widget shows the text you supply; it **does not itself verify** any claim. Put source-difference details and middle-class implications in a full report, link it via `report_url`.

## What 'automatic' means here
The feed updates from RSS on GitHub's schedule (not guaranteed to run at an exact minute). iOS decides when the widget actually refreshes; `refreshAfterDate` is a request, not a promise. Weekly analysis and fact-checking require a separate publishing process, not provided as fully automated in this starter kit.

## Security and reliability
- No API keys are needed for RSS discovery.
- Use only public data in GitHub Pages.
- If provider endpoints change or stop responding, update the `SOURCES` list in `build_feed.py`.
- Public RSS titles are unverified assertions until independently examined.
- To keep everything private, substitute authenticated hosting and a secure feed-access pattern; do not put secrets in Scriptable source code or a public repository.
