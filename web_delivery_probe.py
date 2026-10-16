#!/usr/bin/env python3
"""Public, unauthenticated site delivery probe; no OpenAI API charges."""
import argparse
import datetime as dt
import json
import urllib.error
import urllib.request

TARGETS={
    "custom_domain":"https://news.palmerfamily.org/",
    "reader":"https://mobilelew.github.io/NewsFeed/reader.html",
    "discovery_json":"https://mobilelew.github.io/NewsFeed/feed.json",
    "published_briefing_json":"https://mobilelew.github.io/NewsFeed/briefing.json"
}
def get(url,opener=None):
    opener=opener or urllib.request.build_opener()
    request=urllib.request.Request(url,headers={"User-Agent":"NewsReader-DeliveryMonitor/1.0","Accept":"text/html,application/json"})
    with opener.open(request,timeout=16) as response:
        body=response.read(350_000)
        return response.status,body

def check(opener=None):
    now=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    results={}
    for key,url in TARGETS.items():
        try:
            status,body=get(url,opener)
            if status!=200:raise ValueError("Non-200 HTTP response")
            if key in ("reader","custom_domain"):
                ok=b"News Reader" in body and b"Current news discovery" in body
                msg="homepage_marker_found" if ok else "missing_news_reader_marker"
            else:
                data=json.loads(body)
                if key=="discovery_json":
                    ok=isinstance(data.get("headlines"),list) and bool(data["headlines"])
                    msg="discovery_feed_nonempty" if ok else "discovery_empty"
                else:
                    ok=data.get("status") in ("published","unpublished")
                    msg="briefing_state_"+str(data.get("status")) if ok else "bad_briefing_schema"
            results[key]={"ok":ok,"url":url,"result":msg}
        except (ValueError, OSError, urllib.error.URLError, json.JSONDecodeError) as e:
            results[key]={"ok":False,"url":url,"result":type(e).__name__}
    return {"schema_version":1,"checked_at":now,"targets":results,
            "web_delivery_available":all(x["ok"] for x in results.values()),
            "verified_full_news_available":False,
            "note":"Successful transport and rendering markers do not prove accurate reporting."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="delivery-health.json")
    args=p.parse_args()
    data=check()
    with open(args.output,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)
        f.write("\n")
    print(json.dumps({k:v["result"] for k,v in data["targets"].items()}))
    if not data["web_delivery_available"]:
        raise SystemExit("Public News Reader delivery probe detected an outage")
if __name__=="__main__":main()
