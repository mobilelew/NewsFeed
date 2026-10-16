#!/usr/bin/env python3
"""Build an evidence-labelled News Reader candidate from one bounded Responses API call.

This is research assistance, NOT a guarantee of semantic source verification.
Publication is gated by existing report-schema validation and evidence review status.
"""
import argparse, datetime as dt, json, os, pathlib, urllib.request, urllib.error
from zoneinfo import ZoneInfo
import publish_report

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
(with supplied timestamp), coverage_note, source_checked (array), headlines (array).
Each headline: title, summary, jurisdiction (federal/texas/arkansas/oklahoma/
national/international/multiple), category, claim_type (established_fact/
attributed_claim/proposal/legal_proceeding/data_release), verification (Verified,
Corroborated, Unsubstantiated, Disputed, Legal Effect Unclear, Unverified, Refuted),
evidence=[{type:primary/independent/attribution,description,url}].
For each non-Verified item also include nonempty attribution, what_is_known,
uncertainty, what_cannot_be_concluded, resolution_needed. For Legal Effect Unclear
include legal_status. For Verified include original authoritative primary support.
For morning, include baseline=[{identifier,status,as_of}]. For evening include
a note on whether an actual morning baseline was supplied, but never claim a
comparison if absent. Every material event needs an actual date and linked source.
Keep findings concise, diverse and relevant. If sources are insufficient, note a
coverage gap rather than invent news. Headlines should be independently meaningful."""
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

def extract(output):
    strings=[]
    for item in output.get("output",[]):
        for part in item.get("content",[]):
            if part.get("type")=="output_text" and isinstance(part.get("text"),str):
                strings.append(part["text"])
    if not strings:
        raise ValueError("No JSON text returned; no report will be published")
    return json.loads("\n".join(strings))
def build(kind, now, input_baseline=None):
    if kind not in ("morning","evening"): raise ValueError("Invalid kind")
    local=now.astimezone(ZONE)
    if not os.environ.get("OPENAI_API_KEY"): raise ValueError("OPENAI_API_KEY missing")
    baseline_note=("No authentic archived morning baseline available." if input_baseline is None else
                   "Morning baseline for comparison: "+json.dumps(input_baseline,ensure_ascii=False)[:10000])
    registry=source_registry()
    sources=json.dumps({"discovery":registry["discovery"],"primary_sources":registry["primary_sources"]},ensure_ascii=False)
    prompt=(f"News Reader {kind} as of {local.isoformat(timespec='seconds')}. "
            "Research material news developments in preceding 24 hours (for evening focus on "
            "developments since 6 AM Central). Verify against official records. "
            "Focus areas: "+TOPICS+"\nSource registry (starting points, not a publisher whitelist): "+sources+"\n"+baseline_note+
            "\nMaximum 12 well-evidenced, newsworthy findings. Strict JSON object only.")
    body={"model":os.environ.get("OPENAI_NEWS_MODEL","gpt-5-mini"),
          "instructions":INSTRUCTIONS,
          "input":prompt,
          "tools":[{"type":"web_search"}],
          "tool_choice":"auto",
          "max_output_tokens":6500,
          "store":False}
    req=urllib.request.Request("https://api.openai.com/v1/responses",
        data=json.dumps(body).encode(),method="POST",
        headers={"Authorization":"Bearer "+os.environ["OPENAI_API_KEY"],"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=190) as response:
            result=json.load(response)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Research API request failed HTTP {e.code}; no report published") from None
    document=extract(result)
    document["schema_version"]=1
    document["publication_policy"]="evidence-status-v1"
    document["report_type"]=kind
    document["report_time"]=local.isoformat(timespec="seconds")
    document["coverage_audit"]=coverage_audit(document)\n    document["coverage_audit"]=coverage_audit(document)
    if kind=="morning":
        document["baseline"]=[{"identifier":str(h.get("identifier") or h.get("title")),
                               "status":str(h.get("verification","Unverified")),
                               "as_of":document["report_time"]} for h in document.get("headlines",[])]
    dest=ROOT/"submissions"/"ai-research-candidate.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(document,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    # Structural validation only; does not independently establish source entailment.
    publish_report.load_submission(dest)
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
