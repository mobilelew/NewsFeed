"""Build a public widget feed from a few publisher RSS feeds.

IMPORTANT: RSS items are discovery, NOT independently fact-checked.
Curated verification and weekly trends live in editorial.json and must be evidence-backed.
"""
import datetime as dt
import email.utils
import html
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent
SOURCES = [
    ("U.S. POLICY", "https://www.federalregister.gov/documents/search.rss?conditions%5Btype%5D%5B%5D=PRESDOCU"),
    ("ECONOMY", "https://www.bls.gov/feed/bls_latest.rss"),
    ("TECH & SECURITY", "https://www.cisa.gov/cybersecurity-advisories/all.xml"),
]


def clean(text):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", "", text or ""))).strip()


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "NewsReaderWidget/1.0 (RSS aggregation)"})
    with urllib.request.urlopen(req, timeout=18) as res:
        return res.read()


def parse(xml_bytes, category):
    root = ET.fromstring(xml_bytes)
    out = []
    entries = root.findall("./channel/item")
    atom = False
    if not entries:
        entries = root.findall("{http://www.w3.org/2005/Atom}entry")
        atom = True
    for item in entries[:10]:
        if atom:
            title = item.findtext("{http://www.w3.org/2005/Atom}title")
            link = next((v.get('href') for v in item.findall("{http://www.w3.org/2005/Atom}link") if v.get('href')), "")
            date = item.findtext("{http://www.w3.org/2005/Atom}updated", "")
        else:
            title = item.findtext("title")
            link = item.findtext("link", "")
            date = item.findtext("pubDate", "")
        if title and link and link.startswith("https://"):
            out.append({"category": category, "title": clean(title)[:150],
                        "url": link, "published_at": date,
                        "verification": "Not yet verified"})
    return out


def main():
    editorial_path = ROOT / 'editorial.json'
    editorial = json.loads(editorial_path.read_text(encoding='utf-8')) if editorial_path.exists() else {}
    items = []
    errors = []
    for category, url in SOURCES:
        try:
            items.extend(parse(get(url), category))
        except Exception as exc:
            errors.append(f"{category}: {type(exc).__name__}")
    curated = editorial.get('headlines', [])
    # Human-reviewed claims take precedence; do not automatically upgrade source items to confirmed.
    merged = [x for x in curated if isinstance(x, dict) and x.get('title')]
    seen = {x['title'].casefold() for x in merged}
    for x in items:
        if x['title'].casefold() not in seen:
            merged.append(x)
            seen.add(x['title'].casefold())
    previous_path = ROOT / 'feed.json'
    prev = json.loads(previous_path.read_text(encoding='utf-8')) if previous_path.exists() else {}
    if not merged:
        # Never fabricate new material when all feeds fail.
        merged = prev.get('headlines', [])
    report_url = editorial.get('report_url', 'https://chatgpt.com/')
    feed = {
        'updated_at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
        'headlines': merged[:15],
        'weekly_trend': editorial.get('weekly_trend', {'title': 'No verified weekly trend published yet', 'summary': ''}),
        'report_url': report_url,
        'notes': 'Automated RSS headlines are NOT independently fact-checked. Only curated editorial.json entries may carry Confirmed status.',
        'source_errors': errors,
    }
    previous_path.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Wrote {len(feed['headlines'])} headlines. Feed errors: {errors}")


if __name__ == '__main__':
    main()
