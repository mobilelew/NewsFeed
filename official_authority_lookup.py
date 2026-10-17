"""Bounded lookup of competent public indexes when news lacks primary citations.

Index inspection is a discovery step, not proof that a judgment, bill, or rule
exists or has taken legal effect. Missing index matches cannot disprove claims.
"""
import re
from source_capture import capture

def authority_targets(headline):
    title=str(headline.get("title") or "")
    summary=str(headline.get("summary") or "")
    jurisdiction=str(headline.get("jurisdiction") or "").lower()
    words=(title+" "+summary).lower()
    targets=[]
    if re.search(r"scotus|supreme court|federal court|appeals court|court ruled|judicial decision",words):
        targets.append(("U.S. Supreme Court opinions","https://www.supremecourt.gov/opinions/slipopinions.aspx"))
        if "supreme court" in words or "scotus" in words:
            targets.append(("U.S. Supreme Court orders","https://www.supremecourt.gov/orders/ordersofthecourt/"))
    if jurisdiction=="texas" and re.search(r"bill|legislat|lawmakers|passed law|statute|enacted",words):
        targets.append(("Texas Legislature Online","https://capitol.texas.gov/"))
    if jurisdiction=="arkansas" and re.search(r"bill|legislat|lawmakers|passed law|statute|enacted",words):
        targets.append(("Arkansas General Assembly","https://www.arkleg.state.ar.us/"))
    if jurisdiction=="oklahoma" and re.search(r"bill|legislat|lawmakers|passed law|statute|enacted",words):
        targets.append(("Oklahoma Legislature","https://www.oklegislature.gov/"))
    if re.search(r"federal register|federal rule|administrative rule|proposed regulation",words):
        targets.append(("Federal Register","https://www.federalregister.gov/"))
    if re.search(r"federal reserve|fed chair|fomc|warsh",words):
        targets.append(("Federal Reserve official speeches","https://www.federalreserve.gov/newsevents/speeches.htm"))
    if re.search(r"mortgage|freddie mac|pmms",words):
        targets.append(("Freddie Mac PMMS data","https://www.freddiemac.com/pmms/archive"))
    if re.search(r"usda|slaughter cattle|turkey report|broiler report",words):
        targets.append(("USDA Agricultural Marketing Service","https://www.ams.usda.gov/market-news"))
    if re.search(r"cisa|known exploited vulnerabilities|cve-",words):
        targets.append(("CISA vulnerability catalog","https://www.cisa.gov/known-exploited-vulnerabilities-catalog"))
    return targets[:3]

def review_indexes(headline,capturer=capture):
    title=str(headline.get("title") or "")
    # A claim-specific docket, measure ID, or release date is required before an index
    # search can be treated as matching a particular legislative/court action.
    ids=re.findall(r"\b(?:HB|SB|HJR|SJR|CVE)-?\s?\d+(?:-\d+)?\b",title,re.I)
    checked=[]
    for name,url in authority_targets(headline):
        try:
            source=capturer(url)
            body=str(source.get("content") or "")
            found=[ident for ident in ids if ident.lower().replace(" ","") in body.lower().replace(" ","")]
            notes=("Official index retrieved; candidate identifiers visible: "+", ".join(found)
                   if found else
                   "Official index retrieved; no claim-specific identifier matched. This does not confirm or refute the claim.")
            rates=re.findall(r"\d+(?:\.\d+)?%",title+" "+str(headline.get("summary") or ""))
            observed=set(re.findall(r"\d+(?:\.\d+)?%",body))
            confirmed_numbers=[rate for rate in rates if any(float(rate[:-1])==float(x[:-1]) for x in observed)]
            if confirmed_numbers and not found:
                notes="Official index contains a reported number: "+", ".join(sorted(set(confirmed_numbers)))+". Source date and full claim remain unconfirmed."
            checked.append({"authority":name,"url":url,"status":"retrieved",
                            "checked_at":source.get("retrieved_at"),"finding":notes,
                            "claim_verified":False})
        except Exception as exc:
            checked.append({"authority":name,"url":url,"status":"unavailable",
                            "checked_at":None,"finding":"Official index retrieval failed: "+type(exc).__name__,
                            "claim_verified":False})
    return checked
