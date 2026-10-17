#!/usr/bin/env python3
"""Analyze and substantively fact-check the current News Reader discovery feed."""
import datetime as dt, json, os, pathlib, urllib.request, urllib.error
from zoneinfo import ZoneInfo

ROOT=pathlib.Path(__file__).resolve().parent
ZONE=ZoneInfo("America/Chicago")
STATUSES={"Verified","Corroborated","Contradicted","Unresolved"}
AREAS=[
 "U.S. federal government and national affairs","Texas","Arkansas","Oklahoma",
 "civil/voting rights and civil liberties","financial markets and household economy",
 "housing and mortgages","cryptocurrency","beef/cattle","chicken/broilers","turkey",
 "AI and data centers","major technology companies","cybersecurity",
 "Oklahoma City/Tulsa","Little Rock","Dallas–Fort Worth","Austin"
]

INSTRUCTIONS="""You are the News Reader verification editor. Analyze ONLY the supplied current discovery-feed items as the candidate news set.
Prioritize material developments relevant to the configured areas of interest. Do not introduce unrelated stories merely because web search finds them.
Fact-check the SUBSTANCE of selected discovery claims. Exact wording matters only for direct quotations.
For law/court/government claims inspect the competent official public record and legal status. For statistics inspect authoritative data and dates. For reported remarks determine whether the authoritative event/record and reliable independent reporting support the substance.
Use web search. Prefer original government/court/agency/company filings when competent, then independent reporting.
Labels:
Verified = competent authoritative source directly supports central factual claim.
Corroborated = authoritative context plus independent sources support the central substance, but primary record does not fully establish it.
Contradicted = competent evidence materially conflicts.
Unresolved = evidence insufficient, inaccessible, ambiguous, stale, or verification incomplete.
Return ONLY JSON object:
{
 "executive_summary":[5-8 concise bullets, <=35 words each, summarizing the CURRENT discovery and implications],
 "area_status":[{"area":"configured area name","summary":"<=30 words; say no material discovery item when appropriate"}],
 "findings":[
   {"title":"must exactly match supplied feed title","category":"feed category","status":"Verified|Corroborated|Contradicted|Unresolved",
    "analysis":"<=55 words explaining what happened and why it matters",
    "practical_implication":"<=35 words",
    "authority_checks":[{"source":"name","url":"https://...","finding":"<=45 words"}],
    "independent_checks":[{"source":"name","url":"https://...","finding":"<=45 words"}],
    "remaining_uncertainty":"<=30 words"}
 ]
}
Select at most 14 material findings. Maintain jurisdiction/topic diversity. Do not claim absence across an area unless the feed lacks an item; say 'No material discovery item in current feed' rather than asserting nothing happened in reality.
Never fabricate sources, dates, legal status or verification."""

def feed_items(limit=36):
    feed=json.loads((ROOT/"feed.json").read_text(encoding="utf-8"))
    items=[]
    for h in feed.get("headlines",[])[:limit]:
        if not isinstance(h,dict) or not h.get("title"): continue
        items.append({
          "title":h.get("title"),"category":h.get("category"),"published_at":h.get("published_at"),
          "summary":h.get("summary"),"url":h.get("article_url") or h.get("url"),
          "summary_provenance":h.get("summary_provenance")
        })
    return feed.get("updated_at"),items

def extract(output):
    texts=[]
    for item in output.get("output",[]):
        if isinstance(item,dict):
            for part in item.get("content",[]) or []:
                if isinstance(part,dict) and part.get("type")=="output_text" and isinstance(part.get("text"),str):
                    texts.append(part["text"])
    if not texts: raise ValueError("No output_text")
    data=json.loads("\n".join(texts))
    if not isinstance(data,dict): raise ValueError("Analysis must be object")
    return data

def clean(data,items):
    by_title={x["title"]:x for x in items}
    summary=[str(x)[:500] for x in data.get("executive_summary",[]) if isinstance(x,str) and x.strip()][:8]
    areas=[]
    valid_areas=set(AREAS)
    seen=set()
    for a in data.get("area_status",[]) or []:
        if not isinstance(a,dict): continue
        area=str(a.get("area") or "")
        if area not in valid_areas or area in seen: continue
        areas.append({"area":area,"summary":str(a.get("summary") or "")[:400]});seen.add(area)
    for area in AREAS:
        if area not in seen: areas.append({"area":area,"summary":"No material discovery item identified in the current feed."})
    findings=[];seen_titles=set()
    for f in data.get("findings",[]) or []:
        if not isinstance(f,dict): continue
        title=f.get("title")
        if title not in by_title or title in seen_titles: continue
        status=f.get("status") if f.get("status") in STATUSES else "Unresolved"
        def checks(key):
            out=[]
            for x in f.get(key,[]) or []:
                if not isinstance(x,dict): continue
                u=str(x.get("url") or "")
                if not u.startswith("https://"): continue
                out.append({"source":str(x.get("source") or "")[:120],"url":u[:1200],"finding":str(x.get("finding") or "")[:550]})
            return out[:5]
        findings.append({
          "title":title,"category":by_title[title].get("category"),"published_at":by_title[title].get("published_at"),
          "article_url":by_title[title].get("url"),"status":status,
          "analysis":str(f.get("analysis") or "")[:800],"practical_implication":str(f.get("practical_implication") or "")[:500],
          "authority_checks":checks("authority_checks"),"independent_checks":checks("independent_checks"),
          "remaining_uncertainty":str(f.get("remaining_uncertainty") or "")[:500]
        });seen_titles.add(title)
        if len(findings)>=14: break
    return summary,areas,findings

def run():
    if not os.environ.get("OPENAI_API_KEY"): raise RuntimeError("OPENAI_API_KEY missing")
    updated,items=feed_items()
    prompt="Configured areas: "+json.dumps(AREAS)+"\nCurrent discovery feed (unverified candidates):\n"+json.dumps(items,ensure_ascii=False)
    body={"model":os.environ.get("OPENAI_VERIFY_MODEL","gpt-5-mini"),"instructions":INSTRUCTIONS,"input":prompt,
          "tools":[{"type":"web_search"}],"tool_choice":"auto","reasoning":{"effort":"low"},"max_output_tokens":14000,"store":False}
    req=urllib.request.Request("https://api.openai.com/v1/responses",data=json.dumps(body).encode(),method="POST",
      headers={"Authorization":"Bearer "+os.environ["OPENAI_API_KEY"],"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=240) as response: output=json.load(response)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Discovery analysis API failed HTTP {e.code}") from None
    summary,areas,findings=clean(extract(output),items)
    now=dt.datetime.now(dt.timezone.utc)
    doc={"schema_version":1,"feed_updated_at":updated,"analyzed_at":now.isoformat(timespec="seconds"),
         "local_analyzed_at":now.astimezone(ZONE).isoformat(timespec="seconds"),
         "method":"substantive fact-check of current feed discovery with authoritative and independent web sources",
         "executive_summary":summary,"area_status":areas,"findings":findings,
         "feed_item_count":len(items),"analyzed_finding_count":len(findings),
         "note":"Analysis is limited to current discovery-feed candidates; absence from this analysis does not mean no real-world development occurred."}
    (ROOT/"discovery-analysis.json").write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("Analyzed",len(findings),"current discovery findings from",len(items),"feed items.")

if __name__=="__main__": run()
