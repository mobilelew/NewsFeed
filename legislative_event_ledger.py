#!/usr/bin/env python3
"""Strict ingestion of explicitly documented legislative events; no legal inference."""
import argparse
import datetime as dt
import json
import pathlib
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent
JURISDICTIONS = {"federal", "texas", "arkansas", "oklahoma"}
ACTIONS = {"introduced", "referred", "committee_approved", "chamber_passed",
           "passed_both", "enrolled", "signed", "vetoed", "veto_overridden",
           "enacted", "effective", "implemented", "stayed", "blocked",
           "judicially_invalidated", "appealed", "other"}
UNCERTAINTY = "Legal Effect Unclear"

def validate(event):
    if not isinstance(event, dict):
        raise ValueError("An event must be an object")
    for k in ("jurisdiction", "identifier", "action", "action_date",
              "source_url", "source_description", "attribution", "status_note"):
        if not isinstance(event.get(k), str) or not event[k].strip():
            raise ValueError(f"Missing required {k}")
    if event["jurisdiction"] not in JURISDICTIONS or event["action"] not in ACTIONS:
        raise ValueError("Invalid jurisdiction/action")
    try:
        day = dt.date.fromisoformat(event["action_date"])
    except ValueError:
        raise ValueError("Invalid action_date")
    if day > dt.datetime.now(dt.timezone.utc).date() + dt.timedelta(days=1):
        raise ValueError("Future action_date")
    url = urlparse(event["source_url"])
    if url.scheme != "https" or not url.hostname or url.hostname.endswith(".example"):
        raise ValueError("Official evidence must be an HTTPS URL")
    if event.get("verification") != UNCERTAINTY:
        raise ValueError("Machine ingestion may not assert verified operative legal status")
    if not event.get("what_cannot_be_concluded") or not event.get("resolution_needed"):
        raise ValueError("Mandatory uncertainty language missing")
    if event.get("effective_date"):
        try:
            dt.date.fromisoformat(event["effective_date"])
        except ValueError:
            raise ValueError("Invalid effective_date")
        if event["action"] not in {"effective", "implemented"}:
            raise ValueError("Effective-date conclusion needs separate confirmed action")
    # Do not infer law status from event labels; assertions are attributed to sources.
    return {k: event[k] for k in sorted(event)}

def build(events):
    validated = [validate(x) for x in events]
    unique = {}
    for ev in validated:
        key = (ev["jurisdiction"], ev["identifier"], ev["action"],
               ev["action_date"], ev["source_url"])
        unique[key] = ev
    return {"schema_version": 1, "status": "documented-events-not-legal-advice",
            "notes": "Entries document attributed procedural events; no independent check of operative court orders or enforceability.",
            "events": sorted(unique.values(), key=lambda x: (x["action_date"], x["jurisdiction"], x["identifier"]), reverse=True)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", default="legislative-events.json")
    args = ap.parse_args()
    source = pathlib.Path(args.input).resolve()
    if not source.is_relative_to((ROOT / "legislative-records").resolve()):
        raise ValueError("Input must be from legislative-records/")
    out = pathlib.Path(args.output).resolve()
    if not out.is_relative_to(ROOT):
        raise ValueError("Output outside repository")
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("events"), list):
        raise ValueError("Expected object containing events array")
    output = build(data["events"])
    out.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Validated {len(output['events'])} attributed legislative events. Legal effect not inferred.")

if __name__ == "__main__":
    main()
