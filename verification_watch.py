#!/usr/bin/env python3
"""Hourly original-source recheck of published News Reader findings.

Source-text presence is NOT claim truth. This pipeline must never silently
upgrade a previously unverified assertion to Verified.
"""
import datetime as dt
import json
import pathlib
from research_source_probe import review

ROOT=pathlib.Path(__file__).resolve().parent
def examine(report,capturer=None):
    result=review(report,**({"capturer":capturer} if capturer else {}))
    checked=[]
    for idx,headline in enumerate(report.get("headlines",[])):
        record=next((r for r in result.get("findings",[]) if r.get("headline_index")==idx),{})
        citations=record.get("primary_records",[])
        found=any(c.get("quoted_excerpt_found") for c in citations)
        captured=any(c.get("captured") for c in citations)
        checked_sources=[]
        for item in citations:
            if item.get("captured"):
                finding="Source retrieved; cited exact passage located." if item.get("quoted_excerpt_found") else "Source retrieved; cited exact passage not found."
            elif item.get("issue")=="source_budget_exceeded":
                finding="Not checked: source inspection budget exhausted."
            elif item.get("issue")=="primary_url_not_allowlisted":
                finding="Not checked: authority domain not on capture allowlist."
            else:
                finding="Unavailable or retrieval failed: "+str(item.get("issue") or "unknown error")
            checked_sources.append({"url":item.get("url"),"outcome":finding,"retrieved_at":item.get("retrieved_at"),"sha256":item.get("sha256")})
        if not citations:
            outcome="Not checked: no eligible primary authority was cited; locate the controlling original record before verification."
        elif found:
            outcome="Source checked: a cited passage was found, but it does not independently prove the full claim."
        elif captured:
            outcome="Source checked: retrieved page did not contain the cited exact passage. Claim remains unresolved."
        else:
            outcome="Cited authority was not accessible or not inspected; see each source outcome."
        checked.append({
            "title":headline.get("title",""),
            "verification":headline.get("verification","Unverified"),
            "source_check_status":"source_excerpt_located" if found else "source_retrieved_no_exact_excerpt" if captured else "source_not_inspected",
            "claim_independently_verified":False,
            "legal_effect_confirmed":False,
            "authority_confirmation":outcome,
            "sources_checked":checked_sources,
            "sources_reached":sum(bool(x.get("captured")) for x in citations),
            "quoted_passages_located":sum(bool(x.get("quoted_excerpt_found")) for x in citations),
        })
    return {"schema_version":1,
            "checked_at":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "report_date":report.get("report_date"),
            "report_type":report.get("report_type"),
            "source_check_scope":"original-source excerpts and reachability; NOT independent semantic verification",
            "findings":checked,
            "independently_verified_findings":0,
            "pending_findings":len(checked)}

def main():
    latest=ROOT/"reports"/"latest"/"index.json"
    data=json.loads(latest.read_text(encoding="utf-8"))
    items=data.get("latest",{})
    reports=[]
    for kind in ("morning","evening"):
        entry=items.get(kind)
        if not entry:continue
        f=(ROOT/entry.get("path","")).resolve()
        if not f.is_relative_to(ROOT/"reports") or not f.is_file():continue
        reports.append(json.loads(f.read_text(encoding="utf-8")))
    results=[examine(r) for r in reports]
    output={"schema_version":1,"checked_at":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "status":"source_audit_only_not_semantic_verification",
            "reports":results,
            "note":"Original source extraction never automatically certifies entire claims. Publish Verified only after a separately grounded semantic verification step."}
    (ROOT/"verification-status.json").write_text(json.dumps(output,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("Hourly primary-source recheck completed for",sum(len(x["findings"]) for x in results),"findings; none upgraded by excerpt matching alone.")
if __name__=="__main__":main()
