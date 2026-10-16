"""Conservative authority-site claim matching.

This check answers whether a claimed official-source excerpt is present in
the retrieved page. Absence means 'not confirmed by cited source', not false.
Positive excerpt matching is text confirmation only, not broad semantic proof.
"""
from research_source_probe import review as capture_review

def audit(candidate,capturer=None):
    probe=capture_review(candidate,**({"capturer":capturer} if capturer else {}))
    findings=[]
    for headline,record in zip(candidate.get("headlines",[]),probe["findings"]):
        citations=record["primary_records"]
        matched=any(e.get("quoted_excerpt_found") for e in citations)
        reached=any(e.get("captured") for e in citations)
        outcome=("cited_source_contains_excerpt" if matched else
                 "cited_source_does_not_confirm_position" if reached else
                 "cited_authority_unavailable_or_not_inspected")
        findings.append({"title":headline.get("title"),
                         "authority_check":outcome,
                         "claim_proven":False,
                         "legal_effect_confirmed":False,
                         "original_claim_status":headline.get("verification"),
                         "citations":citations})
    return {"schema_version":1,"report_time":candidate.get("report_time"),
            "findings":findings,
            "publication_approved":False,
            "note":"No excerpt in a captured page does not refute a claim. A matching excerpt confirms text only."}

def main():
    import argparse
    import json
    import pathlib
    p=argparse.ArgumentParser()
    p.add_argument("--candidate",default="submissions/ai-research-candidate.json")
    p.add_argument("--source-audit",default="submissions/ai-original-source-review.json")
    p.add_argument("--output",default="submissions/ai-authority-confirmation.json")
    args=p.parse_args()
    root=pathlib.Path(__file__).resolve().parent
    paths=[(root/x).resolve() for x in (args.candidate,args.source_audit,args.output)]
    if any(not x.is_relative_to(root) for x in paths):
        raise ValueError("Files must remain in repository")
    if not paths[0].exists() or not paths[1].exists():
        print("No captured research to assess")
        return
    candidate=json.loads(paths[0].read_text(encoding="utf-8"))
    probe=json.loads(paths[1].read_text(encoding="utf-8"))
    entries=[]
    for item in probe.get("findings",[]):
        citations=item.get("primary_records",[])
        matched=any(x.get("quoted_excerpt_found") for x in citations)
        reached=any(x.get("captured") for x in citations)
        entries.append({"headline_index":item.get("headline_index"),
                        "title":item.get("title"),
                        "authority_check":"cited_source_contains_excerpt" if matched else
                        "cited_source_does_not_confirm_position" if reached else
                        "cited_authority_unavailable_or_not_inspected",
                        "claim_proven":False,"citations":citations})
    result={"schema_version":1,"candidate_report_time":candidate.get("report_time"),
            "findings":entries,"publication_approved":False,
            "note":"An absent passage means cited record did not confirm it, not that the claim is false. A present passage establishes text occurrence, not claim truth."}
    paths[2].parent.mkdir(parents=True,exist_ok=True)
    paths[2].write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("Prepared authority assessment for",len(entries),"headlines")

if __name__=="__main__":main()
