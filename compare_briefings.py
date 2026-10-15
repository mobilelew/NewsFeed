#!/usr/bin/env python3
"""Compare an evening submission to an actual same-date archived morning report.

Reports claims only as text differences or new identifiers; not legal-status changes
without source review. Never use the Federal Register metadata-only pilot as baseline.
"""
import argparse
import datetime as dt
import json
import pathlib
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent
CHICAGO = ZoneInfo("America/Chicago")

def local_day(report):
    time = dt.datetime.fromisoformat(report["report_time"])
    if time.tzinfo is None:
        raise ValueError("Missing time-zone offset")
    return time.astimezone(CHICAGO).date().isoformat()

def key(item):
    return str(item.get("identifier") or item.get("document_number") or item.get("title") or "").strip().casefold()

def compare(morning, evening):
    if evening.get("report_type") != "evening":
        raise ValueError("Expected evening report")
    day = local_day(evening)
    result = {"schema_version": 1, "report_date": day,
              "comparison_status": "morning_unavailable",
              "morning_report_path": None,
              "summary": "Morning briefing unavailable for direct comparison.",
              "new_identifiers": [], "changed_text_identifiers": [],
              "not_seen_in_evening": []}
    if morning is None:
        return result
    if morning.get("report_type") != "morning" or local_day(morning) != day:
        return result
    before = {key(h): h for h in morning.get("headlines", []) if key(h)}
    after = {key(h): h for h in evening.get("headlines", []) if key(h)}
    result["comparison_status"] = "direct_text_comparison"
    result["summary"] = "Same-date morning and evening reports compared by record identifier. Text differences do not by themselves establish real-world changes."
    result["new_identifiers"] = sorted(after.keys() - before.keys())
    result["not_seen_in_evening"] = sorted(before.keys() - after.keys())
    result["changed_text_identifiers"] = sorted(
        k for k in before.keys() & after.keys()
        if any(before[k].get(f) != after[k].get(f) for f in ("summary", "verification", "legal_status")))
    return result

def prepare(root, evening_path):
    evening_path = pathlib.Path(evening_path).resolve()
    if not evening_path.is_relative_to((root / "submissions").resolve()):
        raise ValueError("Evening input must be under submissions")
    evening = json.loads(evening_path.read_text())
    day = local_day(evening)
    path = root / "reports" / day / "morning.json"
    morning = json.loads(path.read_text()) if path.exists() else None
    data = compare(morning, evening)
    if morning is not None and data["comparison_status"] == "direct_text_comparison":
        data["morning_report_path"] = str(path.relative_to(root))
    return data

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evening", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    output = pathlib.Path(args.output).resolve()
    if not output.is_relative_to(ROOT):
        raise ValueError("Output must remain in repository")
    report = prepare(ROOT, args.evening)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(report["comparison_status"])

if __name__ == "__main__":
    main()
