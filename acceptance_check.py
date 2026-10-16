#!/usr/bin/env python3
"""Fail-closed News Reader production acceptance audit from actual saved artifacts."""
import argparse
import datetime as dt
import json
import pathlib

ROOT=pathlib.Path(__file__).resolve().parent
CATEGORIES={"federal","texas","arkansas","oklahoma"}
TOPICS={"economy","housing","crypto","agriculture","ai","technology","cybersecurity"}
def load(path):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError,OSError):return None
def audit(root=ROOT):
    published=load(root/"briefing.json") or {}
    index=load(root/"reports/latest/index.json") or {}
    pointers=(index.get("latest") or {})
    morning=load(root/pointers.get("morning",{}).get("path","__not_found")) if pointers.get("morning") else None
    evening=load(root/pointers.get("evening",{}).get("path","__not_found")) if pointers.get("evening") else None
    stories=(published.get("headlines") or []) if isinstance(published.get("headlines"),list) else []
    present_states={h.get("jurisdiction") for h in stories if isinstance(h,dict)}
    found_topics={str(h.get("category","")).lower() for h in stories if isinstance(h,dict)}
    coverage=CATEGORIES.issubset(present_states) and TOPICS.issubset(found_topics)
    evidence=bool(stories) and all(isinstance(h,dict) and
                isinstance(h.get("evidence"),list) and h["evidence"] and
                h.get("independent_authentication_record") and
                h.get("claim_evidence_note") for h in stories)
    continuity=bool(morning and evening and
                    morning.get("report_date")==evening.get("report_date") and
                    evening.get("morning_comparison",{}).get("comparison_status")=="direct_text_comparison")
    delivery=published.get("status")=="published" and bool(stories) and
             bool(published.get("report_path"))
    checks={"coverage":coverage,"claim_authentication":evidence,
            "same_day_morning_evening_comparison":continuity,
            "published_feed_exists":delivery,
            "live_custom_domain_delivery":"not_tested_by_repository_audit"}
    return {"schema_version":1,"evaluated_at":dt.datetime.now(dt.timezone.utc).isoformat(),
            "acceptance":checks,"all_accepted":all(x is True for x in checks.values()),
            "note":"Repository-level audit cannot prove factual entailment or remotely viewed website rendering. Acceptance remains blocked pending independent evidence and live delivery."}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="acceptance-status.json")
    a=p.parse_args()
    out=(ROOT/a.output).resolve()
    if not out.is_relative_to(ROOT):raise ValueError("Output outside repo")
    status=audit()
    out.write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(status["acceptance"],indent=2))
if __name__=="__main__":main()
