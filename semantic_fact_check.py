#!/usr/bin/env python3
"""Hourly semantic fact-check of latest News Reader findings.

Uses web research to compare the substance of each reported claim with competent
authoritative sources. Exact wording is required only when the claim is itself a
quotation. This is model-assisted evidence review, not an infallible truth oracle.
"""
import datetime as dt
import json, os, pathlib, urllib.request, urllib.error
from zoneinfo import ZoneInfo

ROOT=pathlib.Path(__file__).resolve().parent
ZONE=ZoneInfo("America/Chicago")
ALLOWED={"Verified","Corroborated","Contradicted","Unresolved"}

INSTRUCTIONS="""You are a politically neutral fact-checking analyst. Evaluate the factual SUBSTANCE of each supplied news claim.
Do NOT require exact wording unless the claim is presented as a direct quotation.
For reported statements, determine whether authoritative event records and reliable reporting establish that the speaker substantively said what is reported.
For laws, rules, court decisions and government actions, inspect the controlling official public record and distinguish proposed, passed, enacted, effective, stayed, blocked and pending.
For statistics, inspect the authoritative data/release and compare date, unit and context.
Use web search. Prefer official public sources; use independent reporting to corroborate.
Return ONLY JSON. Never fabricate a source, quotation, docket, bill number, date or verification.
Status rules:
- Verified: controlling authoritative source directly supports the central factual claim.
- Corroborated: authoritative evidence establishes the event/action/context and at least two independent reports agree on the central substance, but the primary record does not itself fully state the reported claim.
- Contradicted: competent evidence materially conflicts with the central claim.
- Unresolved: evidence is insufficient, inaccessible, ambiguous, stale, or only literal-word matching fails.
For each claim return title, status, concise_conclusion (max 45 words), authority_checks (array of {source,url,what_checked,what_found}), independent_checks (same shape), remaining_uncertainty (max 35 words), checked_at. Keep each source finding concise. Do not say an indirect paraphrase is false merely because exact words are absent."""

def latest_claims():
    idx=json.loads((ROOT/"reports/latest/index.json").read_text(encoding="utf-8"))
    claims=[]
    for kind in ("morning","evening"):
        entry=idx.get("latest",{}).get(kind)
        if not entry: continue
        path=(ROOT/entry["path"]).resolve()
        if not path.is_relative_to(ROOT/"reports") or not path.is_file(): continue
        report=json.loads(path.read_text(encoding="utf-8"))
        for h in report.get("headlines",[]):
            claims.append({
                "report_type":kind,
                "report_date":report.get("report_date"),
                "title":h.get("title"),
                "summary":h.get("summary"),
                "jurisdiction":h.get("jurisdiction"),
                "category":h.get("category"),
                "event_date":h.get("event_date"),
                "attribution":h.get("attribution"),
                "evidence":[{"type":e.get("type"),"description":e.get("description"),"url":e.get("url")} for e in (h.get("evidence") or []) if isinstance(e,dict)]
            })
    return claims[:12]

def extract_json(output):
    texts=[]
    for item in output.get("output",[]):
        if not isinstance(item,dict): continue
        for part in item.get("content",[]):
            if isinstance(part,dict) and part.get("type")=="output_text" and isinstance(part.get("text"),str):
                texts.append(part["text"])
    if not texts: raise ValueError("No output_text from semantic verifier")
    data=json.loads("\n".join(texts))
    if not isinstance(data,dict) or not isinstance(data.get("findings"),list):
        raise ValueError("Semantic verifier returned invalid shape")
    return data

def validate(data,titles):
    seen=set()
    cleaned=[]
    for item in data.get("findings",[]):
        if not isinstance(item,dict): continue
        title=item.get("title")
        if title not in titles or title in seen: continue
        status=item.get("status")
        if status not in ALLOWED: status="Unresolved"
        def checks(name):
            out=[]
            for x in item.get(name,[]) or []:
                if not isinstance(x,dict): continue
                url=str(x.get("url") or "")
                if not url.startswith("https://"): continue
                out.append({"source":str(x.get("source") or "")[:120],
                            "url":url[:1000],
                            "what_checked":str(x.get("what_checked") or "")[:300],
                            "what_found":str(x.get("what_found") or "")[:500]})
            return out[:5]
        cleaned.append({"title":title,"status":status,
                        "concise_conclusion":str(item.get("concise_conclusion") or "")[:600],
                        "authority_checks":checks("authority_checks"),
                        "independent_checks":checks("independent_checks"),
                        "remaining_uncertainty":str(item.get("remaining_uncertainty") or "")[:500],
                        "checked_at":str(item.get("checked_at") or "")[:80]})
        seen.add(title)
    for title in titles:
        if title not in seen:
            cleaned.append({"title":title,"status":"Unresolved","concise_conclusion":"No semantic verification result returned.","authority_checks":[],"independent_checks":[],"remaining_uncertainty":"Claim requires further review.","checked_at":""})
    return cleaned

def run():
    if not os.environ.get("OPENAI_API_KEY"): raise RuntimeError("OPENAI_API_KEY missing")
    claims=latest_claims()
    prompt="Fact-check these current News Reader claims. Evaluate substance, not exact wording. Claims:\n"+json.dumps(claims,ensure_ascii=False)
    body={"model":os.environ.get("OPENAI_VERIFY_MODEL","gpt-5-mini"),"instructions":INSTRUCTIONS,"input":prompt,
          "tools":[{"type":"web_search"}],"tool_choice":"auto","reasoning":{"effort":"low"},"max_output_tokens":10000,"store":False}
    req=urllib.request.Request("https://api.openai.com/v1/responses",data=json.dumps(body).encode(),method="POST",
        headers={"Authorization":"Bearer "+os.environ["OPENAI_API_KEY"],"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=210) as response: output=json.load(response)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Semantic verification API failed HTTP {e.code}") from None
    findings=validate(extract_json(output),[x["title"] for x in claims if x.get("title")])
    doc={"schema_version":1,"checked_at":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
         "local_checked_at":dt.datetime.now(dt.timezone.utc).astimezone(ZONE).isoformat(timespec="seconds"),
         "method":"model-assisted substantive claim review with web search; exact wording required only for direct quotations",
         "findings":findings,
         "note":"Verified/Corroborated labels reflect the evidence reviewed at this check and can change with new records."}
    (ROOT/"semantic-verification.json").write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("Semantic fact-check completed for",len(findings),"claims")

if __name__=="__main__": run()
