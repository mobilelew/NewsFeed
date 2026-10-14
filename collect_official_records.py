#!/usr/bin/env python3
"""Conservative official-record pilot, NOT semantic fact-checking.

Produces evidence-status-v1 morning/evening submissions from Federal Register
publication metadata. This does not interpret a document's legal effect.
"""
import argparse
import datetime as dt
import json
import pathlib
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent
CHICAGO = ZoneInfo("America/Chicago")
API = "https://www.federalregister.gov/api/v1/documents.json"

def fetch_register(day):
    query = urllib.parse.urlencode({
        "conditions[publication_date][is]": day,
        "per_page": "50",
        "order": "newest",
    })
    req = urllib.request.Request(API + "?" + query, headers={
        "User-Agent": "NewsReader/1.0 (official-record research)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=25) as response:
        payload = json.load(response)
    if not isinstance(payload.get("results"), list):
        raise ValueError("Federal Register response missing results")
    return payload["results"]

def make_headline(record):
    title = str(record.get("title") or "").strip()
    number = str(record.get("document_number") or "").strip()
    date = str(record.get("publication_date") or "")
    doc_type = str(record.get("type") or "")
    url = str(record.get("html_url") or "")
    if not title or not number or len(date) != 10 or doc_type not in {"Rule", "Proposed Rule", "Notice", "Presidential Document"}:
        return None
    if not url.startswith("https://www.federalregister.gov/"):
        return None
    # Do NOT infer what the rule changes or whether it is currently operative.
    return {
        "title": f"Federal Register: {title}"[:220],
        "summary": f"The Federal Register lists document {number} as a {doc_type.lower()} published {date}. Its legal effect and any implementation timetable have not been independently analyzed.",
        "category": "U.S. POLICY",
        "jurisdiction": "federal",
        "claim_type": "legal_proceeding",
        "verification": "Legal Effect Unclear",
        "legal_status": "Publication metadata located; operative legal status not determined",
        "attribution": "Federal Register document index (U.S. National Archives)",
        "what_is_known": f"Document {number} is listed for publication {date}, with document type {doc_type}.",
        "uncertainty": "Document text, applicability, amendments, judicial stays and effective dates have not been independently checked.",
        "what_cannot_be_concluded": "This document currently imposes an enforceable duty or changes any individual's rights.",
        "resolution_needed": "Review the full published document, relevant effective-date provisions, implementing guidance, and controlling court orders.",
        "evidence": [{"type": "primary", "description": f"Federal Register listing for {number}", "url": url}],
        "document_number": number,
        "publication_date": date
    }

def create_report(now, records, kind):
    local = now.astimezone(CHICAGO)
    if kind not in {"morning", "evening"}:
        raise ValueError("Unsupported report kind")
    # Only exact-day official records. Never repackage yesterday's news as new.
    valid = []
    for record in records:
        item = make_headline(record)
        if item and item["publication_date"] == local.date().isoformat():
            valid.append(item)
    valid = sorted(valid, key=lambda h: h["document_number"])
    if not valid:
        return None
    report = {
        "schema_version": 1,
        "publication_policy": "evidence-status-v1",
        "report_type": kind,
        "report_time": local.isoformat(timespec="seconds"),
        "coverage_note": "Automated Federal Register metadata-only pilot; not a comprehensive News Reader briefing. Federal law impacts, Texas, Arkansas, Oklahoma, markets, agriculture, and technology remain outside this pilot. No substantive independent legal verification performed.",
        "source_checked": [{"name": "Federal Register public API", "date": local.date().isoformat(), "status": "metadata_only"}],
        "headlines": valid[:8],
    }
    if kind == "morning":
        report["baseline"] = [
            {"identifier": h["document_number"], "status": h["legal_status"], "as_of": local.isoformat(timespec="seconds")}
            for h in report["headlines"]
        ]
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["morning", "evening"], required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--date", help="For offline tests only; YYYY-MM-DD")
    args = parser.parse_args()
    now = dt.datetime.now(dt.timezone.utc)
    date = args.date or now.astimezone(CHICAGO).date().isoformat()
    if args.date and date != now.astimezone(CHICAGO).date().isoformat():
        raise ValueError("Production refuses to publish historical dates")
    records = fetch_register(date)
    report = create_report(now, records, args.kind)
    if report is None:
        print("NO_PUBLISHABLE_RECORDS: No matching official records for today; leaving public archive unchanged")
        return 0
    dest = pathlib.Path(args.output).resolve()
    if not dest.is_relative_to((ROOT / "submissions").resolve()):
        raise ValueError("Output must be under submissions/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Prepared metadata-only {args.kind} pilot with {len(report['headlines'])} records: {dest}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
