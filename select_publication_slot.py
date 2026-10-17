#!/usr/bin/env python3
"""Select News Reader production slot using both nominal cron and Chicago time."""
import argparse
import datetime as dt
from zoneinfo import ZoneInfo

CHICAGO=ZoneInfo("America/Chicago")
MORNING={"9 11,12 * * *","39 11,12 * * *","15 13,14 * * *"}
EVENING={"9 1,2 * * *","39 1,2 * * *","15 3,4 * * *"}

def select(event,nominal,when):
    local=when.astimezone(CHICAGO)
    if event=="workflow_dispatch":
        return {"mode":"trial","kind":"evening","reason":"manual trial"}
    if event!="schedule":
        raise ValueError("Unsupported event cannot trigger paid production")
    if nominal in MORNING:
        if local.hour<6: return {"mode":"skip","kind":"morning","reason":"standby UTC cron before local 6 AM"}
        if local.hour>=12: raise ValueError("Morning schedule delayed beyond local reporting window; manual review required")
        return {"mode":"production","kind":"morning","reason":"6 AM local target or delayed recovery"}
    if nominal in EVENING:
        if local.hour<20: return {"mode":"skip","kind":"evening","reason":"standby UTC cron before local 8 PM"}
        if local.hour>=24: raise ValueError("Evening execution outside local day")
        return {"mode":"production","kind":"evening","reason":"8 PM local target or delayed recovery"}
    raise ValueError("Unknown nominal GitHub Actions schedule")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--event",required=True)
    p.add_argument("--cron",default="")
    p.add_argument("--output",required=True)
    a=p.parse_args()
    result=select(a.event,a.cron,dt.datetime.now(dt.timezone.utc))
    with open(a.output,"a",encoding="utf-8") as out:
        out.write("mode="+result["mode"]+"\nkind="+result["kind"]+"\n")
    print("Publication slot: "+str(result))
if __name__=="__main__":main()
