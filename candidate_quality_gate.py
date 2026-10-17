"""No-cost candidate risk screen; detects structural red flags, never proves truth."""
import datetime as dt
import re
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

ALLOWED={"federal","texas","arkansas","oklahoma","national","international","multiple"}
REQUIRED={"federal","texas","arkansas","oklahoma"}
LOCAL=ZoneInfo("America/Chicago")

def date_value(value):
    try:
        return dt.date.fromisoformat(value)
    except (ValueError, TypeError):
        return None

def review(report):
    problems=[]
    report_type=report.get("report_type")
    stamp=report.get("report_time")
    try:
        current=dt.datetime.fromisoformat(stamp).astimezone(LOCAL)
    except (ValueError, TypeError, AttributeError):
        current=None
        problems.append("Report timestamp missing or invalid")
    if current and report_type=="morning" and not 5 <= current.hour < 12:
        problems.append("Morning report generated outside morning window; cannot be represented as a 6 AM baseline")
    counts={}
    for i,h in enumerate(report.get("headlines",[])):
        loc=h.get("jurisdiction")
        if loc not in ALLOWED:
            problems.append(f"Headline {i}: invalid jurisdiction {loc!r}")
        if loc in REQUIRED:
            counts[loc]=counts.get(loc,0)+1
        evidence=h.get("evidence") or []
        if h.get("verification")=="Corroborated":
            links=[e.get("url","") for e in evidence if e.get("type")=="independent"]
            hosts=[urlparse(link).hostname or "" for link in links]
            if len(set(hosts))<2:
                problems.append(f"Headline {i}: Corroborated lacks two separate independent-origin domains")
            # Different domains alone are not proof of independence.
        if h.get("verification")=="Verified" and not any(e.get("type")=="primary" for e in evidence):
            problems.append(f"Headline {i}: Verified lacks a primary-source reference")
        event=h.get("event_date")
        if not date_value(event) and h.get("verification")=="Verified":
            problems.append(f"Headline {i}: verified finding requires a valid event_date")
        elif current and date_value(event) is not None and date_value(event)>current.date():
            problems.append(f"Headline {i}: event_date in future, identify as scheduled not occurred")
        checked=h.get("source_checked_at")
        try:
            parsed=dt.datetime.fromisoformat(checked)
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise ValueError("timezone required")
            if current and parsed > current + dt.timedelta(minutes=5):
                problems.append(f"Headline {i}: source_checked_at is later than report time")
        except (ValueError, TypeError):
            if h.get("verification")=="Verified":
                problems.append(f"Headline {i}: verified finding requires valid timezone-aware source_checked_at")
        if not h.get("claim_evidence_note"):
            problems.append(f"Headline {i}: no claim-specific evidence explanation")
    return {"passed_prepublication_screen":not problems,"issues":problems,
            "jurisdictions_with_findings":sorted(counts),
            "jurisdictions_without_findings":sorted(REQUIRED-set(counts)),
            "caution":"Passing cannot authenticate sources, determine entailment, or prove completeness."}
