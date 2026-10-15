#!/usr/bin/env python3
"""Narrow autonomous claim verification: reported CISA KEV additions vs CISA's catalog.

Google News RSS is discovery, not evidence. Only the exact assertion "CISA added
CVE-X to KEV" is eligible, with an explicit matching current CISA catalog record
and addition date. Never conclude exploitation of individual victims.
"""
import datetime as dt
import json
import pathlib
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

ROOT=pathlib.Path(__file__).resolve().parent
LOCAL=ZoneInfo("America/Chicago")
CATALOG="https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
CISA_MIRROR="https://raw.githubusercontent.com/cisagov/kev-data/develop/known_exploited_vulnerabilities.json"\nRSS="https://news.google.com/rss/search?q="+urllib.parse.quote('CISA "known exploited" CVE when:2d')+"&hl=en-US&gl=US&ceid=US:en"
CVE=re.compile(r"\bCVE-20\d{2}-\d{4,}\b",re.I)
ACTION=re.compile(r"\bCISA\b.{0,140}\b(adds?|added|lists?|listed|includes?|included)\b|\b(adds?|added|lists?|listed|includes?|included)\b.{0,140}\bCISA\b",re.I)

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"NewsReader/1.0 (public news verification)","Accept":"application/json, application/xml, text/xml"})
    with urllib.request.urlopen(req,timeout=30) as res:
        data=res.read(5_000_001)
        if len(data)>5_000_000:
            raise ValueError("Source too large")
        return data

def fetch_catalog():\n    try:\n        return get(CATALOG), CATALOG\n    except Exception:\n        return get(CISA_MIRROR), CISA_MIRROR\n\ndef build(news_xml,catalog_json,now,official_source=CATALOG):
    catalogue=json.loads(catalog_json)
    items=catalogue.get("vulnerabilities")
    if not isinstance(items,list) or not items:
        raise ValueError("No CISA vulnerability records")
    records={str(r.get("cveID","")).upper():r for r in items if r.get("cveID")}
    root=ET.fromstring(news_xml)
    out=[]
    seen=set()
    for node in root.findall("./channel/item"):
        title=(node.findtext("title") or "").strip()
        link=(node.findtext("link") or "").strip()
        pub=(node.findtext("pubDate") or "").strip()
        source=(node.findtext("source") or "").strip() or "Publisher attribution unavailable"
        cves={m.upper() for m in CVE.findall(title)}
        # Not all headlines are statements of a new addition. If ambiguous, do not approve.
        if not ACTION.search(title) or not cves or not link.startswith("https://"):
            continue
        for cve in sorted(cves):
            if (title,cve) in seen:
                continue
            seen.add((title,cve))
            official=records.get(cve)
            if not official:
                status="Unverified"
                detail="The CVE was not found in the retrieved CISA KEV catalog. This does not prove CISA never listed it."
                source_url=None
            else:
                status="Verified"
                detail="CISA's current KEV catalog lists this exact CVE with the stated addition date. This verifies listing only, not the article's additional claims."
                source_url=official_source
            out.append({
                "headline":title,"publisher":source,"news_url":link,"news_publication_date":pub,
                "specific_claim":f"CISA lists {cve} in its Known Exploited Vulnerabilities catalog.",
                "verification":status,"what_is_known":detail,
                "cve_id":cve,"cisa_date_added":official.get("dateAdded") if official else None,
                "original_evidence":source_url,
                "limitations":"Headline discovery metadata only; news article body not independently retrieved. Catalog listing does not establish the scope, current exploit activity or impact on particular users.",
                "checked_at":now.astimezone(LOCAL).isoformat(timespec="seconds"),
                "source_classification":"CISA primary record" if official else "No matched primary record"
            })
    return {"schema_version":1,"kind":"automated-claim-matching-pilot",
            "scope":"Only CISA KEV listing claims explicitly identifiable from third-party headlines",
            "production_ready":False,
            "checked_at":now.astimezone(LOCAL).isoformat(timespec="seconds"),
            "discovery_source":RSS,"primary_source":official_source,
            "findings":out[:25],
            "coverage_note":"Automated source-specific matching, not complete fact-checking, independent verification of every headline, or a full News Reader daily briefing."}

def main():
    now=dt.datetime.now(dt.timezone.utc)
    catalog, source=fetch_catalog()\n    data=build(get(RSS),catalog,now,source)
    p=ROOT/"verified-claims-pilot.json"
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"CISA listing claim matching: {len(data['findings'])} findings")

if __name__=="__main__":
    main()
