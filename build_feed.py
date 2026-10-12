"""Build the News Reader public feed using official RSS/Atom sources.

Discovered headlines are NOT fact-checked. Only curated editorial.json entries
may carry verification conclusions.
"""
import datetime as dt
import email.utils
import html
import json
import pathlib
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent
SOURCES = [
    ("U.S. POLICY", [
        "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Btype%5D%5B%5D=PRESDOCU",
        "https://www.federalregister.gov/api/v1/documents.rss",
    ]),
    ("ECONOMY", ["https://www.bls.gov/feed/bls_latest.rss"]),
    ("TECH & SECURITY", [
        "https://www.cisa.gov/cybersecurity-advisories/cybersecurity-advisories.xml",
        "https://www.cisa.gov/cybersecurity-advisories/alerts.xml",
        "https://www.cisa.gov/rss.xml",
    ]),
]


def clean(value):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", "", value or ""))).strip()


def get(url):
    request = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; NewsReaderWidget/1.1; RSS reader)",
        "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.5",
    })
    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read(3_000_000)
        if not data.lstrip().startswith(b"<"):
            raise ValueError("Response is not XML")
        return data


def parse(data, category):
    root = ET.fromstring(data)
    atom_ns = "{http://www.w3.org/2005/Atom}"
    entries = root.findall("./channel/item")
    is_atom = False
    if not entries:
        entries = root.findall(f"{atom_ns}entry")
        is_atom = True
    if not entries:
        raise ValueError("No RSS or Atom entries found")
    results = []
    for item in entries[:25]:
        if is_atom:
            title = item.findtext(f"{atom_ns}title")
            links = item.findall(f"{atom_ns}link")
            link = next((v.get("href") for v in links if v.get("rel", "alternate") == "alternate" and v.get("href")), "")
            date = item.findtext(f"{atom_ns}updated") or item.findtext(f"{atom_ns}published") or ""
        else:
            title = item.findtext("title")
            link = item.findtext("link", "")
            date = item.findtext("pubDate", "")
        if title and link and link.startswith("https://"):
            results.append({
                "category": category, "title": clean(title)[:150],
                "url": link, "published_at": date,
                "verification": "Not yet verified",
            })
    if not results:
        raise ValueError("Feed has no usable HTTPS headlines")
    return results


def published_key(item):
    value = item.get("published_at", "")
    try:
        return email.utils.parsedate_to_datetime(value).timestamp()
    except (TypeError, ValueError, IndexError):
        try:
            return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except (TypeError, ValueError, AttributeError):
            return 0


def main():
    editorial_path = ROOT / "editorial.json"
    editorial = json.loads(editorial_path.read_text(encoding="utf-8")) if editorial_path.exists() else {}
    previous_path = ROOT / "feed.json"
    previous = json.loads(previous_path.read_text(encoding="utf-8")) if previous_path.exists() else {}
    errors = []
    discovered = []
    status = {}
    for category, endpoints in SOURCES:
        failures = []
        for url in endpoints:
            try:
                items = parse(get(url), category)
                discovered.extend(items[:10])
                status[category] = {"ok": True, "items": len(items), "url": url}
                break
            except (urllib.error.URLError, ValueError, ET.ParseError, TimeoutError, OSError) as exc:
                failures.append(f"{type(exc).__name__}: {str(exc)[:100]}")
        else:
            status[category] = {"ok": False, "items": 0}
            errors.append(f"{category}: all endpoints failed ({'; '.join(failures)})")

    curated = [x for x in editorial.get("headlines", []) if isinstance(x, dict) and x.get("title")]
    merged = curated[:]
    seen = {x["title"].strip().casefold() for x in merged}
    for item in sorted(discovered, key=published_key, reverse=True):
        key = item["title"].strip().casefold()
        if key not in seen:
            merged.append(item)
            seen.add(key)
    if not merged:
        merged = [{**x, "verification": "Not yet verified"} for x in previous.get("headlines", [])]
        if merged:
            errors.append("Feeds unavailable; retained cached unverified headlines.")

    feed = {
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "headlines": merged[:15],
        "weekly_trend": editorial.get("weekly_trend", {"title": "No verified weekly trend published yet", "summary": ""}),
        "report_url": editorial.get("report_url", "https://chatgpt.com/"),
        "notes": "Automated RSS entries are NOT independently fact-checked. Verification conclusions require editorial review.",
        "source_status": status,
        "source_errors": errors,
    }
    previous_path.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(feed['headlines'])} headlines. Sources: {status}. Errors: {errors}")


if __name__ == "__main__":
    main()
