"""News Reader: source discovery, freshness/relevance, and separately reviewed editorial findings.
RSS is discovery ONLY. This script never independently validates a headline.
"""
import datetime as dt
import email.utils
import html
import json
import pathlib
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent
NOW = dt.datetime.now(dt.timezone.utc)
# Google News is a secondary discovery aggregator, never proof of a claim.
def news(query):
    return "https://news.google.com/rss/search?q=" + urllib.parse.quote(query) + "&hl=en-US&gl=US&ceid=US:en"

SOURCES = {
    "TEXAS": [news("Texas legislature governor courts policy economy when:3d")],
    "ARKANSAS": [news("Arkansas legislature governor courts economy when:3d")],
    "OKLAHOMA": [news("Oklahoma legislature governor courts economy when:3d")],
    "U.S. POLICY": [
        "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Btype%5D%5B%5D=PRESDOCU",
        news("executive order congress legislation when:3d"),
    ],
    "ECONOMY": [
        "https://www.bls.gov/feed/bls_latest.rss",
        news("Federal Reserve dollar inflation treasury yields when:3d"),
    ],
    "HOUSING": [
        news("mortgage rates FHFA Census housing inventory affordability when:3d"),
    ],
    "AGRICULTURE": [
        news("USDA beef cattle chicken turkey livestock prices farms when:3d"),
    ],
    "CRYPTO": [
        news("bitcoin ethereum SEC stablecoin regulation when:3d"),
    ],
    "AI": [
        "https://export.arxiv.org/rss/cs.AI",
        news("AI models OpenAI NVIDIA data centers electricity when:3d"),
    ],
    "TECH & SECURITY": [
        "https://github.com/advisories.atom",
        news("CISA cybersecurity breach ransomware vulnerability when:3d"),
    ],
}
KEYWORDS = {
    "TEXAS": ("texas", "austin", "dallas", "houston", "senate", "governor", "legislature", "court", "bill", "property tax"),
    "ARKANSAS": ("arkansas", "little rock", "governor", "legislature", "court", "bill", "schools", "tax"),
    "OKLAHOMA": ("oklahoma", "oklahoma city", "tulsa", "governor", "legislature", "court", "bill", "tax"),
    "U.S. POLICY": ("executive", "rule", "law", "tariff", "policy", "budget", "military", "sanction", "congress", "federal", "legislation", "order"),
    "ECONOMY": ("dollar", "inflation", "payroll", "employment", "rates", "treasury", "federal reserve", "wages", "economic", "consumer", "cpi"),
    "HOUSING": ("housing", "mortgage", "home", "rental", "rent", "inventory", "construction", "foreclosure"),
    "AGRICULTURE": ("usda", "cattle", "beef", "poultry", "chicken", "turkey", "livestock", "feed", "farm", "avian", "meat"),
    "CRYPTO": ("bitcoin", "ethereum", "crypto", "stablecoin", "blockchain", "digital asset", "tokenization"),
    "AI": ("artificial intelligence", "ai ", "model", "agent", "nvidia", "compute", "data center", "gpu", "automation"),
    "TECH & SECURITY": ("cve-", "vulnerability", "breach", "ransomware", "exploit", "security", "attack", "malware", "patch"),
}
LOW_VALUE = ("national day", "awareness month", "proclamation", "commemorating", "celebrating", "holiday observance")
ALLOWED_STATUSES = {"Confirmed", "Partially Supported", "Disputed", "Unsupported", "Contradicted", "Not Yet Verifiable"}

def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", "", s or ""))).strip()

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 NewsReader/2.0", "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*"})
    with urllib.request.urlopen(req, timeout=18) as response:
        return response.read(2_000_000)

def parse_date(value):
    try:
        parsed = email.utils.parsedate_to_datetime(value)
    except (ValueError, TypeError):
        try:
            parsed = dt.datetime.fromisoformat(value.replace("Z","+00:00"))
        except (ValueError, TypeError, AttributeError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)

def parse(xml, category):
    root = ET.fromstring(xml)
    atom = "{http://www.w3.org/2005/Atom}"
    entries = root.findall("./channel/item")
    is_atom = False
    if not entries:
        entries = root.findall(f"{atom}entry")
        is_atom = True
    if not entries:
        raise ValueError("No RSS/Atom entries")
    items=[]
    for entry in entries[:35]:
        if is_atom:
            title = entry.findtext(f"{atom}title","")
            date = entry.findtext(f"{atom}updated","") or entry.findtext(f"{atom}published","")
            links = entry.findall(f"{atom}link")
            link = next((l.get("href") for l in links if l.get("href") and l.get("rel","alternate")=="alternate"),"")
        else:
            title=entry.findtext("title","")
            link=entry.findtext("link","")
            date=entry.findtext("pubDate","")
        title=clean(title)
        if not title or not link.startswith("https://"):
            continue
        when=parse_date(date)
        if when is None or when > NOW + dt.timedelta(hours=2):
            continue
        age=(NOW-when).total_seconds()/3600
        if age > 168:  # never imply week-old discoveries are breaking news
            continue
        lower=title.casefold()
        keyword_hits=sum(1 for word in KEYWORDS[category] if word in lower)
        if not keyword_hits or any(term in lower for term in LOW_VALUE):
            continue
        # 24h freshness gets priority; keep 72h context and up to 7d as fallback.
        score= (100 if age<=24 else 35 if age<=72 else 0) + 10*min(keyword_hits,3) - age/12
        items.append({
            "category":category, "title":title[:155], "url":link,
            "published_at": when.isoformat(timespec="seconds"),
            "verification":"Not yet verified", "is_editorial":False,
            "discovery_score":round(score,2)
        })
    return items

def validate_editorial(item):
    if not isinstance(item,dict) or not item.get("title") or not str(item.get("url","")).startswith("https://"):
        return None
    copy=dict(item)
    status=copy.get("verification","Not yet verified")
    if status not in ALLOWED_STATUSES:
        status="Not yet verified"
    # Confirmed conclusions need accessible evidence links; a news URL alone is insufficient.
    evidence=copy.get("evidence",[])
    evidence=[x for x in evidence if isinstance(x,dict) and str(x.get("url","")).startswith("https://") and x.get("description")]
    copy["evidence"]=evidence
    if status != "Not yet verified" and not evidence:
        status="Not yet verified"
    copy["verification"]=status
    copy["is_editorial"]=True
    copy.setdefault("source_differences","")
    return copy

def main():
    editorial=json.loads((ROOT/"editorial.json").read_text(encoding="utf-8"))
    previous_file=ROOT/"feed.json"
    previous=json.loads(previous_file.read_text(encoding="utf-8")) if previous_file.exists() else {}
    source_status={}
    source_errors=[]
    discovery=[]
    for category,urls in SOURCES.items():
        errors=[]
        all_found=[]
        succeeded=[]
        for url in urls:
            try:
                found=parse(fetch(url),category)
                if not found: raise ValueError("No fresh, relevant items")
                all_found.extend(found)
                succeeded.append(url)
            except Exception as exc:
                errors.append(f"{type(exc).__name__}: {str(exc)[:90]}")
        source_status[category]={"ok":bool(succeeded),"items":len(all_found),"working_sources":succeeded}
        if not succeeded:
            source_errors.append(f"{category}: " + "; ".join(errors))
        discovery.extend(all_found)
    curated=[e for x in editorial.get("headlines",[]) if (e:=validate_editorial(x))]
    # Always show reviewed editorial first, then represent multiple categories.
    bycat={category:[] for category in SOURCES}
    seen={x["title"].casefold() for x in curated}
    for x in sorted(discovery,key=lambda x:x["discovery_score"],reverse=True):
        key=x["title"].casefold()
        if key not in seen:
            bycat[x["category"]].append(x)
            seen.add(key)
    selected=list(curated[:8])
    # First pass: fair representation across categories.
    for category in SOURCES:
        if bycat[category]: selected.append(bycat[category].pop(0))
    remaining=sorted((x for values in bycat.values() for x in values),key=lambda x:x["discovery_score"],reverse=True)
    selected=(selected+remaining)[:24]
    # Cached previous discovery is NOT re-used when any live source works.
    if not selected and previous.get("headlines"):
        source_errors.append("No fresh discoveries; prior headlines intentionally not republished as current.")
    weekly=editorial.get("weekly_trend",{})
    if not weekly.get("evidence"):
        weekly={"title":"No evidence-backed weekly trend published yet","summary":"Publish a sourced trend in editorial.json.","evidence":[]}
    feed={
        "updated_at":NOW.isoformat(timespec="seconds"),
        "headlines":selected,
        "weekly_trend":weekly,
        "report_url":editorial.get("report_url","https://chatgpt.com/"),
        "notes":"RSS and aggregators are discovery only. Verification requires separately curated original evidence; no automatic fact-checking is claimed.",
        "source_status":source_status,
        "source_errors":source_errors,
    }
    previous_file.write_text(json.dumps(feed,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"Published {len(selected)} items across {len(set(x['category'] for x in selected))} categories. Source issues: {len(source_errors)}")

if __name__=="__main__":
    main()
