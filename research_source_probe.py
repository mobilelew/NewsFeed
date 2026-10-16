#!/usr/bin/env python3
"""Retrieve the primary-record citations in a research candidate for later audit.

This only authenticates the observed source bytes and exact quote presence.
It NEVER sets a claim to Verified, Corroborated, or publishable.
"""
import argparse
import json
import pathlib
from source_capture import allowed,capture
from claim_evidence_audit import normalize

ROOT=pathlib.Path(__file__).resolve().parent
def review(candidate,capturer=capture,limit=12):
    headlines=candidate.get("headlines")
    if not isinstance(headlines,list):raise ValueError("Candidate headlines missing")
    unique={}
    for h in headlines:
        for e in h.get("evidence",[]) or []:
            if isinstance(e,dict) and e.get("type")=="primary" and isinstance(e.get("url"),str):
                unique[e["url"]]=None
    urls=list(unique)[:limit]
    source_records={}
    for url in urls:
        if not allowed(url):
            source_records[url]={"captured":False,"issue":"primary_url_not_allowlisted"}
            continue
        try:
            record=capturer(url)
            if record.get("url")!=url or not record.get("content"):
                raise ValueError("Captured source URL/content mismatch")
            source_records[url]={"captured":True,"sha256":record["sha256"],
                                "retrieved_at":record["retrieved_at"],
                                "content":record["content"],"content_type":record["content_type"]}
        except Exception as ex:
            source_records[url]={"captured":False,"issue":type(ex).__name__}
    findings=[]
    for i,h in enumerate(headlines):
        found=[]
        for e in h.get("evidence",[]) or []:
            if not isinstance(e,dict) or e.get("type")!="primary":continue
            url=e.get("url")
            record=source_records.get(url)
            if record is None:
                found.append({"url":url,"captured":False,"issue":"source_budget_exceeded"})
                continue
            quote=e.get("exact_excerpt")
            match=bool(record.get("captured") and isinstance(quote,str)
                       and quote.strip() and normalize(quote) in normalize(record["content"]))
            found.append({"url":url,"captured":bool(record["captured"]),
                          "quoted_excerpt_found":match,
                          "excerpt_provided":bool(isinstance(quote,str) and quote.strip()),
                          "sha256":record.get("sha256"),
                          "issue":record.get("issue")})
        findings.append({"headline_index":i,"title":h.get("title"),"primary_records":found,
                         "independently_semantically_verified":False})
    return {"schema_version":1,"candidate_report_time":candidate.get("report_time"),
            "unique_primary_urls":len(unique),"attempted_primary_urls":len(urls),
            "sources":source_records,"findings":findings,
            "independent_source_authentication":False,
            "publication_approved":False,
            "limitation":"Matching literal text or dates in captured pages cannot prove claim entailment, legal status, or actual events."}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",default="submissions/ai-research-candidate.json")
    ap.add_argument("--output",default="submissions/ai-original-source-review.json")
    args=ap.parse_args()
    src=(ROOT/args.input).resolve()
    out=(ROOT/args.output).resolve()
    if not src.is_relative_to(ROOT) or not out.is_relative_to(ROOT):
        raise ValueError("Paths must remain inside repository")
    if not src.exists():
        print("No research candidate available; no source review created")
        return
    result=review(json.loads(src.read_text(encoding="utf-8")))
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("Inspected "+str(result["attempted_primary_urls"])+" primary references; semantic verification remains outstanding")
if __name__=="__main__":main()
