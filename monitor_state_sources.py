#!/usr/bin/env python3
"""Monitor official legislative sites. A page change is NOT a legal finding."""
import datetime as dt
import hashlib
import html.parser
import json
import pathlib
import re
import urllib.request
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent
CENTRAL = ZoneInfo("America/Chicago")
SOURCES = {
    "texas": [
        ("Texas Legislature Online — legislative activity", "https://capitol.texas.gov/Home.aspx"),
        ("Texas Legislature Online — legislation", "https://capitol.texas.gov/MnuLegislation.aspx"),
    ],
    "arkansas": [
        ("Arkansas General Assembly — recent activities", "https://www.arkleg.state.ar.us/"),
        ("Arkansas General Assembly — meetings", "https://www.arkleg.state.ar.us/Calendars/Meetings"),
    ],
    "oklahoma": [
        ("Oklahoma Legislature — bill tracking", "https://www.oklegislature.gov/AdvancedSearchForm.aspx"),
        ("Oklahoma Legislature — official homepage", "https://www.oklegislature.gov/"),
    ],
}
class VisibleText(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self.skip:
            self.skip -= 1
    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

def digest(content):
    p = VisibleText()
    p.feed(content.decode("utf-8", errors="replace"))
    visible = re.sub(r"\s+", " ", " ".join(p.parts)).strip()
    if len(visible) < 80:
        raise ValueError("Page too short to establish usable official content")
    return hashlib.sha256(visible.encode("utf-8")).hexdigest(), len(visible)

def retrieve(url):
    request = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; NewsReaderSourceAudit/1.0)",
        "Accept": "text/html",
    })
    with urllib.request.urlopen(request, timeout=20) as response:
        final = response.geturl()
        if not final.startswith("https://"):
            raise ValueError("Redirected away from HTTPS")
        data = response.read(2_000_001)
        if len(data) > 2_000_000:
            raise ValueError("Page exceeds size limit")
        return digest(data)

def assemble(now, previous, retrieve_page=retrieve):
    prior = {x["url"]: x for state in previous.get("jurisdictions", {}).values() for x in state.get("sources", [])}
    jurisdictions = {}
    for state, entries in SOURCES.items():
        checked = []
        for name, url in entries:
            item = {"name": name, "url": url, "status": "unavailable", "change": "undetermined"}
            try:
                value, count = retrieve_page(url)
                item["status"] = "reachable"
                item["content_sha256"] = value
                item["visible_characters"] = count
                old = prior.get(url, {}).get("content_sha256")
                item["change"] = "changed" if old and old != value else "unchanged" if old else "no_baseline"
            except Exception as exc:
                item["error"] = f"{type(exc).__name__}: {str(exc)[:180]}"
            checked.append(item)
        jurisdictions[state] = {
            "status": "reachable" if any(s["status"] == "reachable" for s in checked) else "unavailable",
            "sources": checked,
            "legal_changes_verified": False,
            "note": "Website monitoring only. A changed page does not establish a bill, rule or court action."
        }
    return {
        "schema_version": 1,
        "report_type": "source_monitor",
        "checked_at": now.astimezone(CENTRAL).isoformat(timespec="seconds"),
        "scope": "Texas, Arkansas and Oklahoma legislature official-source reachability and changes",
        "verification": "Unverified",
        "legal_changes_verified": False,
        "jurisdictions": jurisdictions,
        "notes": "No substantive legal facts inferred. Check individual bills, final rules, official election guidance, and operative court orders before publishing legal effect."
    }

def main():
    target = ROOT / "state-source-monitor.json"
    previous = json.loads(target.read_text()) if target.exists() else {}
    result = assemble(dt.datetime.now(dt.timezone.utc), previous)
    target.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    for state, data in result["jurisdictions"].items():
        print(f"{state}: {data['status']} — " +
              ", ".join(x["name"].split(" — ")[-1] + "=" + x["status"] for x in data["sources"]))
if __name__ == "__main__":
    main()
