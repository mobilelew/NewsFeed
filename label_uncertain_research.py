#!/usr/bin/env python3
"""Conservatively label individual AI research findings using captured authority evidence."""
import copy,json,pathlib,argparse,datetime as dt
from candidate_quality_gate import review
ROOT=pathlib.Path(__file__).resolve().parent
def prepare(candidate,authority):
    result=copy.deepcopy(candidate)
    rows={x.get("headline_index"):x for x in authority.get("findings",[])}
    for i,h in enumerate(result.get("headlines",[])):
        finding=rows.get(i,{})
        citations=finding.get("citations",[])
        located=any(x.get("quoted_excerpt_found") for x in citations)
        h["authority_confirmation"]=finding.get("authority_check","not_inspected")
        h["independent_authentication_record"]={"authority_check":h["authority_confirmation"],
             "quoted_excerpt_located":bool(located),"semantic_entailment":"not_determined"}
        # Missing source support cannot be promoted to Verified/Corroborated.
        if h.get("verification") in ("Verified","Corroborated"):
            h["verification"]="Unverified"
        if h["verification"]!="Verified":
            h["claim_type"]="attributed_claim" if h.get("claim_type")=="established_fact" else h.get("claim_type","attributed_claim")
            h.setdefault("attribution","See individually linked cited reporting; not independently established")
            h.setdefault("what_is_known","The cited reporting makes this assertion.")
            h.setdefault("uncertainty","No independent confirmation of the complete assertion has been established.")
            h.setdefault("what_cannot_be_concluded","The original cited authority verifies the asserted position.")
            h.setdefault("resolution_needed","Inspect the exact controlling original record for the individual factual assertion.")
        # Prevent one unrelated or uninspected source from looking like validated support.
        h["claim_evidence_note"]="Cited authority "+h["authority_confirmation"]+"; literal excerpt presence is not semantic proof."
        if h.get("jurisdiction") not in {"federal","texas","arkansas","oklahoma","national","international","multiple"}:
            h["jurisdiction"]="multiple"
        event=h.get("event_date")
        try:
            event_day=dt.date.fromisoformat(event)
            report_day=dt.datetime.fromisoformat(result["report_time"]).date()
            if event_day < report_day-dt.timedelta(days=1):
                h["temporal_caveat"]="Historical event, not established as new"
                h["summary"]="Historical context (event "+event+"): "+h.get("summary","")
            elif event_day>report_day:
                h["temporal_caveat"]="Future event, not established as completed"
                h["summary"]="Future event not yet completed: "+h.get("summary","")
                h["event_date"]=None
        except (TypeError,ValueError):
            h["temporal_caveat"]="Actual event date not established"
            h["event_date"]=None
        if h.get("source_checked_at"):
            h["model_claimed_source_check_time"]=h.pop("source_checked_at")
            h["source_checked_at"]=None
        # Never synthesize a source inspection time from the report timestamp.
    result["independent_source_authentication"]=False
    result["editorial_caveat"]="Research assertions remain Unverified where competent authority confirmation is not established."
    result["quality_screen"]=review(result)
    return result
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--candidate",default="submissions/ai-research-candidate.json")
    p.add_argument("--authority",default="submissions/ai-authority-confirmation.json")
    p.add_argument("--output",default="submissions/ai-labelled-report.json")
    a=p.parse_args()
    paths=[(ROOT/x).resolve() for x in (a.candidate,a.authority,a.output)]
    if any(not x.is_relative_to(ROOT) for x in paths):raise ValueError("Paths must stay inside repo")
    if not paths[0].exists():raise ValueError("Research candidate unavailable")
    evidence=json.loads(paths[1].read_text()) if paths[1].exists() else {}
    result=prepare(json.loads(paths[0].read_text()),evidence)
    result["trial_only"]=True
    result["publication_status"]="research_preview_not_a_scheduled_briefing"
    paths[2].write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("Preserved "+str(len(result["headlines"]))+" findings; unsupported claims remain labelled Unverified.")
if __name__=="__main__":main()
