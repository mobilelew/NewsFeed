#!/usr/bin/env python3
"""Check scheduled-task publication state, without inventing task delivery."""
import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parent
ZONE=ZoneInfo("America/Chicago")
def inspect(root=ROOT,now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    local=now.astimezone(ZONE)
    reports={}
    for kind,hour in (("morning",6),("evening",20)):
        path=root/"task-briefings"/f"latest-{kind}.json"
        try:
            doc=json.loads(path.read_text(encoding="utf-8"))
            valid=(doc.get("status")=="published" and doc.get("kind")==kind and
                   isinstance(doc.get("content_markdown"),str) and len(doc["content_markdown"].strip())>=500 and
                   doc.get("report_date")==local.date().isoformat() and
                   dt.datetime.fromisoformat(doc["generated_at"]).utcoffset() is not None)
        except (OSError,ValueError,TypeError,KeyError,AttributeError):
            valid=False
        due=local.hour>hour or (local.hour==hour and local.minute>=45)
        reports[kind]={"status":"published_today" if valid else "missing_after_cutoff" if due else "not_due_or_pending",
                        "published_today":bool(valid),"cutoff_local":f"{hour:02d}:45 America/Chicago"}
    return {"schema_version":1,"checked_at":now.isoformat(timespec="seconds"),"local_date":local.date().isoformat(),
            "reports":reports,"note":"This checks whether complete task text was delivered, not the factual correctness of the report."}
def main():
    doc=inspect()
    (ROOT/"task-briefings"/"delivery-status.json").write_text(json.dumps(doc,indent=2)+"\n",encoding="utf-8")
    print("Task report delivery:",json.dumps(doc["reports"]))
if __name__=="__main__":main()
