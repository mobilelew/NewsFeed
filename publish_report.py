#!/usr/bin/env python3
"""Publish manually approved News Reader reports. This does NOT independently fact-check claims."""
import argparse
import datetime as dt
import json
import pathlib
import re
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent
TYPES = {"morning", "evening", "weekly"}
STATES = {"federal", "texas", "arkansas", "oklahoma"}
ZONE = ZoneInfo("America/Chicago")

def fail(msg):
    raise ValueError(msg)

def https(s):
    p = urlparse(str(s or ""))
    return p.scheme == "https" and bool(p.netloc)

def load_submission(path):
    if not path.resolve().is_relative_to((ROOT / "submissions").resolve()):
        fail("Submission must be inside submissions/")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or data.get("report_type") not in TYPES:
        fail("Expected schema_version=1 and report_type morning/evening/weekly")
    if data.get("approved") is not True or data.get("editorial_review") != "completed":
        fail("Report has not passed explicit editorial approval")
    if not str(data.get("reviewed_by", "")).strip():
        fail("Reviewed-by attribution required")
    try:
        when = dt.datetime.fromisoformat(data["report_time"])
    except (KeyError, TypeError, ValueError):
        fail("Valid ISO 8601 report_time required")
    if when.tzinfo is None or when.utcoffset() is None:
        fail("report_time must specify a timezone offset")
    chicago = when.astimezone(ZONE)
    if when > dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5):
        fail("Future report_time is invalid")
    if not isinstance(data.get("headlines"), list) or not data["headlines"]:
        fail("Approved reports require at least one headline")
    for i, h in enumerate(data["headlines"]):
        if not isinstance(h, dict) or not str(h.get("title", "")).strip():
            fail(f"Headline {i} lacks title")
        if h.get("verification") not in {"Confirmed", "Partially Supported", "Disputed", "Not Yet Verifiable"}:
            fail(f"Headline {i} has unsupported verification status")
        evidence = h.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            fail(f"Headline {i} needs cited evidence")
        for e in evidence:
            if not isinstance(e, dict) or not https(e.get("url")) or not e.get("description"):
                fail(f"Headline {i} has invalid evidence")
        if h["verification"] == "Confirmed" and not any(e.get("type") == "primary" for e in evidence):
            fail(f"Confirmed headline {i} needs primary evidence")
        if h.get("jurisdiction") not in STATES | {"national", "international", "multiple"}:
            fail(f"Headline {i} needs jurisdiction")
    if data["report_type"] == "morning":
        baseline = data.get("baseline")
        if not isinstance(baseline, list) or not baseline:
            fail("Morning report requires explicit baseline list")
    return data, chicago

def publish(source):
    report, when = load_submission(source)
    date = when.date().isoformat()
    kind = report["report_type"]
    dest = ROOT / "reports" / date / f"{kind}.json"
    if dest.exists():
        fail(f"Archive already exists; never overwrite: {dest.relative_to(ROOT)}")
    latest = ROOT / "reports" / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    dest.parent.mkdir(parents=True, exist_ok=True)
    published = dict(report)
    published["report_date"] = date
    published["published_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    serialized = json.dumps(published, indent=2, ensure_ascii=False) + "\n"
    dest.write_text(serialized, encoding="utf-8")
    (latest / f"{kind}.json").write_text(serialized, encoding="utf-8")
    index_path = latest / "index.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else {"schema_version": 1, "latest": {}}
    index["latest"][kind] = {"report_date": date, "report_time": report["report_time"], "path": str(dest.relative_to(ROOT))}
    index_path.write_text(json.dumps(index, indent=2) + "\n")
    if kind == "morning":
        baseline = {"schema_version": 1, "report_date": date, "report_time": report["report_time"],
                    "source_path": str(dest.relative_to(ROOT)), "baseline": report["baseline"]}
        (latest / "morning-baseline.json").write_text(json.dumps(baseline, indent=2, ensure_ascii=False) + "\n")
    if kind in {"morning", "evening"}:
        public = {"schema_version": 1, "status": "published", "updated_at": published["published_at"],
                  "report_date": date, "report_type": kind, "report_time": report["report_time"],
                  "headlines": report["headlines"][:8], "report_path": str(dest.relative_to(ROOT)),
                  "weekly_trend": None,
                  "notes": "Only independently approved, evidence-linked findings. Verify citations for details."}
        weekly = latest / "weekly.json"
        if weekly.exists():
            w = json.loads(weekly.read_text())
            public["weekly_trend"] = w.get("weekly_trend")
        (ROOT / "briefing.json").write_text(json.dumps(public, indent=2, ensure_ascii=False) + "\n")
    elif kind == "weekly":
        brief = ROOT / "briefing.json"
        current = json.loads(brief.read_text()) if brief.exists() else {"schema_version": 1, "status": "unpublished", "headlines": []}
        current["weekly_trend"] = report.get("weekly_trend")
        brief.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n")
    print(f"Published approved {kind} report: {dest.relative_to(ROOT)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    publish(pathlib.Path(args.input).resolve())
