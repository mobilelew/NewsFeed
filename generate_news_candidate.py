#!/usr/bin/env python3
"""Build an evidence-labelled News Reader candidate from one bounded Responses API call.

This is research assistance, NOT a guarantee of semantic source verification.
Publication is gated by existing report-schema validation and evidence review status.
"""
import argparse, datetime as dt, json, os, pathlib, urllib.request, urllib.error
from zoneinfo import ZoneInfo
import publish_report
from candidate_quality_gate import review as quality_review

ROOT=pathlib.Path(__file__).resolve().parent
ZONE=ZoneInfo("America/Chicago")
TOPICS="""United States federal rights, legislation and regulations; Texas; Arkansas;
Oklahoma; financial markets, Fed, dollar, housing and crypto; USDA cattle/beef,
broilers/chicken and turkey; AI, data centers, technology companies and cybersecurity."""
INSTRUCTIONS="""You are an independent, nonpartisan news researcher. Produce a News Reader
morning or evening report, using original authoritative evidence and relevant independent
news articles. Search for actual reported news, not merely press releases. Verify individual
factual assertions against competent original sources wherever accessible. Report only
findings actually supported by inspected evidence. Never fabricate URLs, identifiers,
numbers, dates, court orders, source comparisons, or claims of verification. If unable to
inspect original documents or resolve conflicts, disclose this clearly, label findings
Unverified, Unsubstantiated, Disputed, or Legal Effect Unclear as appropriate.
An official document is evidence of its own content and actions; not automatically proof of
all claims within it. Do not assign Verified merely because a URL exists. Cover each topic
and jurisdiction to the degree supported by available evidence. No filler.
Return ONLY a JSON object compatible with these required report fields:
schema_version=1, publication_policy='evidence-status-v1', report_type, report_time
(with supplied timestamp), coverage_note, source_checked (array), headlines (array), executive_summary (text),\nhousehold_implications (array of concise text), source_differences (array of concise text),\nverified_upcoming_events (array of objects with title, date, source_url),\ncoverage_gaps (array of concise text).
Each headline: title, summary, practical_implication, jurisdiction (federal/texas/arkansas/oklahoma/
national/international/multiple), category, claim_type (established_fact/
attributed_claim/proposal/legal_proceeding/data_release), verification (Verified,
Corroborated, Unsubstantiated, Disputed, Legal Effect Unclear, Unverified, Refuted),
evidence=[{type:primary/independent/attribution,description,url,exact_excerpt}].\nFor primary evidence, exact_excerpt must be a short verbatim quotation found on the original official page, never fabricated. Missing exact_excerpts will be flagged, not fixed by guessing.
For each headline use exactly one permitted jurisdiction, splitting different states into separate findings. A story cannot be Corroborated unless two genuinely independently originating sources can be demonstrated; syndications do not count. For each non-Verified item also include nonempty attribution, what_is_known,
uncertainty, what_cannot_be_concluded, resolution_needed. For Legal Effect Unclear
include legal_status. For Verified include original authoritative primary support.
For morning, include baseline=[{identifier,status,as_of}]. For evening include
a note on whether an actual morning baseline was supplied, but never claim a
comparison if absent. Every material event needs an actual event_date YYYY-MM-DD, source_checked_at ISO timestamp and claim_evidence_note explaining what cited text actually establishes. Do not confuse date printed on search-result page with action date. If unknown, do not fabricate, and allow the publication screen to flag the gap.
Write a substantial but evidence-bounded executive summary, what changed and why it matters to middle-class households. Separate proposals, enacted acts, effectiveness and allegations. Report source conflicts and missing records without implying verification.\nKeep findings concise, diverse and relevant. If sources are insufficient, note a
coverage gap rather than invent news. Headlines should be independently meaningful."""
def discovery_leads(limit=24):
    """Publisher leads only, never independently established facts."""
    path=ROOT/"feed.json"
    if not path.is_file():return []
    try: feed=json.loads(path.read_text(encoding="utf-8"))
    except (ValueError,OSError):return []
    from publisher_links import direct_publisher_url
    leads=[]
    for item in feed.get("headlines",[]):
        if not isinstance(item,dict):continue
        url=direct_publisher_url(item.get("article_url") or item.get("url"))
        if not url or not item.get("title"):continue
        leads.append({"title":str(item["title"])[:160],"category":str(item.get("category",""))[:70],
                      "published_at":item.get("published_at"),"url":url,
                      "status":"UNVERIFIED DISCOVERY LEAD"})
        if len(leads)>=limit:break
    return leads

def source_registry():
    data=json.loads((ROOT/"news_sources.json").read_text(encoding="utf-8"))
    required={"federal_law","texas","arkansas","oklahoma","finance_housing","agriculture","technology_cyber"}
    if data.get("schema_version")!=1 or not required.issubset(data.get("primary_sources",{})):
        raise ValueError("Incomplete source registry")
    return data

def coverage_audit(document):
    jurisdictions={h.get("jurisdiction") for h in document.get("headlines",[]) if isinstance(h,dict)}
    required={"federal","texas","arkansas","oklahoma"}
    return {"jurisdictions_with_findings":sorted(required & jurisdictions),
            "jurisdictions_without_findings":sorted(required-jurisdictions),
            "warning":"Headline presence and source links do not establish exhaustive coverage or genuine authentication."}

def diagnostic(output):
    """Safe metadata only: no response body, secrets, source text or prompts."""
    return {
        "response_id": str(output.get("id", ""))[:80],
        "status": output.get("status"),
        "incomplete_reason": (output.get("incomplete_details") or {}).get("reason"),
        "usage": output.get("usage"),
        "output_item_types": [
            item.get("type") for item in output.get("output", [])
            if isinstance(item, dict)
        ],
        "content_types": [
            part.get("type")
            for item in output.get("output", []) if isinstance(item, dict)
            for part in item.get("content", []) if isinstance(part, dict)
        ],
    }

def extract(output):
    if output.get("status") == "incomplete":
        reason=(output.get("incomplete_details") or {}).get("reason", "unknown")
        raise ValueError(f"API response incomplete ({reason}); no report published")
    strings=[]
    for item in output.get("output",[]):
        if not isinstance(item,dict):
            continue
        for part in item.get("content",[]):
            if part.get("type")=="output_text" and isinstance(part.get("text"),str):
                strings.append(part["text"])
    if not strings:
        raise ValueError("API returned no output_text. Check safe diagnostics artifact; no report published.")
    return json.loads("\n".join(strings))
def build(kind, now, input_baseline=None):
    if kind not in ("morning","evening"): raise ValueError("Invalid kind")
    local=now.astimezone(ZONE)
    if not os.environ.get("OPENAI_API_KEY"): raise ValueError("OPENAI_API_KEY missing")
    baseline_note=("No authentic archived morning baseline available." if input_baseline is None else
                   "Morning baseline for comparison: "+json.dumps(input_baseline,ensure_ascii=False)[:10000])
    registry=source_registry()
    leads=discovery_leads()
    sources=json.dumps({"discovery":registry["discovery"],"primary_sources":registry["primary_sources"]},ensure_ascii=False)
    prompt=(f"News Reader {kind} as of {local.isoformat(timespec='seconds')}. "
            "Research material news developments in preceding 24 hours (for evening focus on "
            "developments since 6 AM Central). Verify against official records. "
            "Focus areas: "+TOPICS+"\nSource registry (starting points, not a publisher whitelist): "+sources+"\nUnverified publisher discovery leads (verify independently before use): "+json.dumps(leads,ensure_ascii=False)+"\n"+baseline_note+
            "\nMaximum 12 concise findings. Before selecting findings, check separately: federal, Texas, Arkansas, Oklahoma; rights/courts/laws; dollar/Fed/mortgages/crypto; USDA beef, chicken and turkey; AI/data centers and cybersecurity. Use separate actual findings for each jurisdiction and sector when supported. Explicitly disclose each jurisdiction and sector with no current verified development in coverage_note, rather than omitting it or inventing stories. No category may dominate the report merely because its sources are easier to find. Strict JSON object only.")
    body={"model":os.environ.get("OPENAI_NEWS_MODEL","gpt-5-mini"),
          "instructions":INSTRUCTIONS,
          "input":prompt,
          "tools":[{"type":"web_search"}],
          "tool_choice":"auto",
          "max_output_tokens":12000,
          "reasoning":{"effort":"low"},
          "store":False}
    req=urllib.request.Request("https://api.openai.com/v1/responses",
        data=json.dumps(body).encode(),method="POST",
        headers={"Authorization":"Bearer "+os.environ["OPENAI_API_KEY"],"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=190) as response:
            result=json.load(response)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Research API request failed HTTP {e.code}; no report published") from None
    diag=ROOT/"submissions"/"ai-response-diagnostic.json"
    diag.parent.mkdir(parents=True,exist_ok=True)
    diag.write_text(json.dumps(diagnostic(result),indent=2)+"\n",encoding="utf-8")
    document=extract(result)
    document["research_origin"]="api_web_research"
    document["independent_source_authentication"]=False
    document["schema_version"]=1
    document["publication_policy"]="evidence-status-v1"
    document["report_type"]=kind
    document["report_time"]=local.isoformat(timespec="seconds")
    document["coverage_audit"]=coverage_audit(document)
    document["quality_screen"]=quality_review(document)
    if kind=="morning":
        document["baseline"]=[{"identifier":str(h.get("identifier") or h.get("title")),
                               "status":str(h.get("verification","Unverified")),
                               "as_of":document["report_time"]} for h in document.get("headlines",[])]
    dest=ROOT/"submissions"/"ai-research-candidate.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(document,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    # Structural validation only; does not independently establish source entailment.
    try:
        publish_report.load_submission(dest)
        validation = {"valid": True, "candidate_path": str(dest.relative_to(ROOT))}
    except (ValueError, KeyError, TypeError) as exc:
        validation = {"valid": False, "reason": str(exc),
                      "candidate_path": str(dest.relative_to(ROOT))}
        print("Candidate retained for correction; publication validation failed: " + str(exc))
    if not document["quality_screen"]["passed_prepublication_screen"]:
        validation["valid"]=False
        validation["quality_screen_issues"]=document["quality_screen"]["issues"]
    (ROOT/"submissions"/"ai-candidate-validation.json").write_text(
        json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    if not validation["valid"]:
        raise ValueError("Research candidate failed prepublication screening; see retained artifact and validation JSON")
    return dest,document
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--kind",required=True,choices=["morning","evening"])
    args=p.parse_args()
    now=dt.datetime.now(dt.timezone.utc)
    morning=None
    if args.kind=="evening":
        f=ROOT/"reports"/now.astimezone(ZONE).date().isoformat()/"morning.json"
        if f.exists(): morning=json.loads(f.read_text())
    path,report=build(args.kind,now,morning)
    print(f"Prepared candidate {args.kind} briefing with {len(report['headlines'])} sourced findings: {path}")
if __name__=="__main__": main()
