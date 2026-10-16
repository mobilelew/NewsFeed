#!/usr/bin/env python3
"""Generate public delivery diagnostics from committed artifacts, not inferred success."""
import argparse
import datetime as dt
import json
import pathlib
from zoneinfo import ZoneInfo

ROOT=pathlib.Path(__file__).resolve().parent
UTC=dt.timezone.utc
def read(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError,ValueError,UnicodeError):
        return None

def time_value(value):
    if not isinstance(value,str): return None
    try:
        result=dt.datetime.fromisoformat(value.replace("Z","+00:00"))
        if not result.tzinfo: return None
        return result.astimezone(UTC)
    except ValueError:
        return None

def evaluate(root=ROOT,now=None):
    now=now or dt.datetime.now(UTC)
    now=now.astimezone(UTC)
    feed=read(root/"feed.json") or {}
    brief=read(root/"briefing.json") or {}
    official=read(root/"official-records.json") or {}
    latest=read(root/"reports"/"latest"/"index.json") or {}
    feed_stamp=time_value(feed.get("updated_at"))
    age_hours=round((now-feed_stamp).total_seconds()/3600,2) if feed_stamp else None
    discovery_ok=isinstance(feed.get("headlines"),list) and bool(feed["headlines"]) and age_hours is not None and 0<=age_hours<=3
    published=brief.get("status")=="published" and isinstance(brief.get("headlines"),list) and bool(brief["headlines"])
    index=(latest.get("latest") or {})
    audit={"schema_version":1,"checked_at":now.isoformat(timespec="seconds"),
        "discovery":{"current":discovery_ok,"item_count":len(feed.get("headlines") or []),
                     "last_updated":feed.get("updated_at"),"age_hours":age_hours,
                     "status":"available_unverified" if discovery_ok else "stale_or_empty"},
        "official_record_pilot":{"last_updated":official.get("updated_at"),
                                 "available_kinds":sorted((official.get("latest") or {}).keys()),
                                 "status":"metadata_only_not_legal_effect"},
        "verified_briefing":{"published":published,"last_updated":brief.get("updated_at"),
                             "report_date":brief.get("report_date"),
                             "report_type":brief.get("report_type"),
                             "status":"published_not_independently_reaudited" if published else "not_published"},
        "archive":{"kinds":sorted(index.keys())},
        "acceptance":{"full_coverage_confirmed":False,
                      "independent_claim_authentication_confirmed":False,
                      "morning_evening_cycle_confirmed":False,
                      "full_briefing_delivery_confirmed":False},
        "overall":"discovery_available_full_service_incomplete" if discovery_ok else "attention_required"}
    return audit

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="service-health.json")
    args=parser.parse_args()
    dest=(ROOT/args.output).resolve()
    if not dest.is_relative_to(ROOT):raise ValueError("Output must remain inside repository")
    dest.write_text(json.dumps(evaluate(),indent=2)+"\n",encoding="utf-8")
    print("Service status written: "+str(dest.relative_to(ROOT)))
if __name__=="__main__":main()
