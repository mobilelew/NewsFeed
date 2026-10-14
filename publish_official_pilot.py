#!/usr/bin/env python3
"""Publish a clearly separated official-record digest without changing briefing.json."""
import argparse
import datetime as dt
import json
import pathlib
from zoneinfo import ZoneInfo

import publish_report

ROOT = pathlib.Path(__file__).resolve().parent
LOCAL = ZoneInfo("America/Chicago")

def publish(source):
    report, chicago = publish_report.load_submission(pathlib.Path(source).resolve())
    if report.get("report_type") not in {"morning", "evening"}:
        raise ValueError("Official pilot only supports morning/evening")
    if "metadata-only" not in str(report.get("coverage_note", "")):
        raise ValueError("Pilot must visibly declare metadata-only scope")
    if any(h["verification"] != "Legal Effect Unclear" for h in report["headlines"]):
        raise ValueError("Pilot claims must retain the legal-effect uncertainty status")
    date = chicago.date().isoformat()
    kind = report["report_type"]
    dest = ROOT / "reports" / "official-records" / date / f"{kind}.json"
    if dest.exists():
        print(f"Pilot already archived: {dest.relative_to(ROOT)}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    report["published_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    dest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    index_path = ROOT / "official-records.json"
    current = json.loads(index_path.read_text()) if index_path.exists() else {
        "schema_version": 1, "status": "pilot", "latest": {}
    }
    current["updated_at"] = report["published_at"]
    current["latest"][kind] = {
        "date": date, "path": str(dest.relative_to(ROOT)),
        "headlines": report["headlines"],
        "coverage_note": report["coverage_note"]
    }
    index_path.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Published separate metadata-only pilot: {dest.relative_to(ROOT)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    publish(parser.parse_args().input)
