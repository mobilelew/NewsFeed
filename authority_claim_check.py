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
