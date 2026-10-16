#!/usr/bin/env python3
"""Publish evidence-labelled News Reader reports. Does NOT fact-check cited evidence."""
import argparse
import datetime as dt
import json
import pathlib
import re
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent
TYPES = {"morning", "evening", "weekly"}
STATES = {"federal", "texas", "arkansas", "oklahoma"}
STATUSES = {"Verified", "Corroborated", "Unsubstantiated", "Disputed", "Legal Effect Unclear", "Unverified", "Refuted"}
UNCERTAIN = STATUSES - {"Verified"}
ZONE = ZoneInfo("America/Chicago")

def fail(msg):
    raise ValueError(msg)

def https(s):
    p = urlparse(str(s or ""))
    return p.scheme == "https" and bool(p.netloc)

def load_submission(path):
    if not path.resolve().is_relative_to((ROOT / "submissions").resolve()):
        fail("Submission must be inside submissions/")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or data.get("report_type") not in TYPES:
        fail("Expected schema_version=1 and report_type morning/evening/weekly")
    if data.get("publication_policy") != "evidence-status-v1":
        fail("publication_policy must be evidence-status-v1 (legacy approval templates rejected)")
    try:
        when = dt.datetime.fromisoformat(data["report_time"])
    except (KeyError, TypeError, ValueError):
        fail("Valid ISO 8601 report_time required")
    if when.tzinfo is None or when.utcoffset() is None:
        fail("report_time must specify a timezone offset")
    chicago = when.astimezone(ZONE)
    if when > dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5):
        fail("Future report_time is invalid")
    if not isinstance(data.get("headlines"), list) or not data["headlines"]:
        fail("Reports require at least one headline")
    for i, h in enumerate(data["headlines"]):
        if not isinstance(h, dict) or not str(h.get("title", "")).strip():
            fail(f"Headline {i} lacks title")
        status = h.get("verification")
        if status not in STATUSES:
            fail(f"Headline {i} has unsupported verification status")
        if not str(h.get("summary", "")).strip():
            fail(f"Headline {i} needs a bounded, attributable summary")
        if h.get("claim_type") not in {"established_fact", "attributed_claim", "proposal", "legal_proceeding", "data_release"}:
            fail(f"Headline {i} needs an explicit claim_type")
        if status in UNCERTAIN:
            for field in ("attribution", "what_is_known", "uncertainty", "what_cannot_be_concluded", "resolution_needed"):
                if not str(h.get(field, "")).strip():
                    fail(f"Headline {i} ({status}) needs {field}")
            if h["claim_type"] == "established_fact":
                fail(f"Headline {i}: uncertain finding cannot claim established_fact")
        if status == "Legal Effect Unclear" and not str(h.get("legal_status", "")).strip():
            fail(f"Headline {i} must specify unknown or qualified legal status")
        if status == "Refuted" and h["claim_type"] != "attributed_claim":
            fail(f"Headline {i}: refuted assertion must be presented as an attributed claim")
        if re.search(r"REPLACE|PLACEHOLDER|EXAMPLE\.ORG", json.dumps(h), re.I):
            fail(f"Headline {i} contains placeholder material")
        evidence = h.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            fail(f"Headline {i} needs at least one source for the claim or its uncertainty")
        for e in evidence:
            if not isinstance(e, dict) or not https(e.get("url")) or not str(e.get("description", "")).strip() or e.get("type") not in {"primary", "independent", "attribution"}:
                fail(f"Headline {i} has invalid evidence")
            if urlparse(e["url"]).hostname in {"example.org", "example.com", "example.net"}:
                fail(f"Headline {i} contains an example evidence URL")
        if status == "Verified" and not any(e.get("type") == "primary" for e in evidence):
            fail(f"Verified headline {i} needs primary evidence")
        if status == "Corroborated" and len(set(e["url"] for e in evidence if e["type"] == "independent")) < 2:
            fail(f"Corroborated headline {i} needs two distinct independent-source URLs")
        if h.get("jurisdiction") not in STATES | {"national", "international", "multiple"}:
            fail(f"Headline {i} needs jurisdiction")
    if re.search(r"REPLACE|PLACEHOLDER", json.dumps(data.get("baseline", [])), re.I):
        fail("Baseline contains placeholders")
    if data["report_type"] == "morning":
        baseline = data.get("baseline")
        if not isinstance(baseline, list) or not baseline:
            fail("Morning report requires explicit baseline list")
    if data.get("research_origin") == "api_web_research":
        from candidate_quality_gate import review
        screen = review(data)
        if not screen["passed_prepublication_screen"]:
            fail("AI research candidate fails prepublication screen: " + "; ".join(screen["issues"][:4]))
        if not data.get("independent_source_authentication"):
            # Publish qualified, attributed uncertainty; never falsely certify the story.
            for i, h in enumerate(data["headlines"]):
                if h["verification"] in {"Verified", "Corroborated"}:
                    fail(f"Unreviewed AI headline {i} cannot claim independent verification")
                if not h.get("authority_confirmation"):
                    fail(f"AI headline {i} must disclose the authority check outcome")
    return data, chicago

def publish(source):
    report, when = load_submission(source)
    date = when.date().isoformat()
    kind = report["report_type"]
    dest = ROOT / "reports" / date / f"{kind}.json"
    if dest.exists():
        fail(f"Archive already exists; never overwrite: {dest.relative_to(ROOT)}")
    latest = ROOT / "reports" / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    dest.parent.mkdir(parents=True, exist_ok=True)
    published = dict(report)
    if kind == "evening":
        from compare_briefings import compare
        morning_path = ROOT / "reports" / date / "morning.json"
        morning = json.loads(morning_path.read_text(encoding="utf-8")) if morning_path.exists() else None
        comparison = compare(morning, report)
        if comparison["comparison_status"] == "direct_text_comparison":
            comparison["morning_report_path"] = str(morning_path.relative_to(ROOT))
        published["morning_comparison"] = comparison
    published["report_date"] = date
    published["published_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    serialized = json.dumps(published, indent=2, ensure_ascii=False) + "\n"
    dest.write_text(serialized, encoding="utf-8")
    (latest / f"{kind}.json").write_text(serialized, encoding="utf-8")
    index_path = latest / "index.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else {"schema_version": 1, "latest": {}}
    index["latest"][kind] = {"report_date": date, "report_time": report["report_time"], "path": str(dest.relative_to(ROOT))}
    index_path.write_text(json.dumps(index, indent=2) + "\n")
    if kind == "morning":
        baseline = {"schema_version": 1, "report_date": date, "report_time": report["report_time"],
                    "source_path": str(dest.relative_to(ROOT)), "baseline": report["baseline"]}
        (latest / "morning-baseline.json").write_text(json.dumps(baseline, indent=2, ensure_ascii=False) + "\n")
    if kind in {"morning", "evening"}:
        public = {"schema_version": 1, "status": "published", "updated_at": published["published_at"],
                  "report_date": date, "report_type": kind, "report_time": report["report_time"],
                  "headlines": report["headlines"][:8], "report_path": str(dest.relative_to(ROOT)),
                  "weekly_trend": None,
                  "notes": "Evidence-labelled published reporting. Verification labels describe evidentiary support, not guarantees of accuracy. Check original sources and operative legal guidance."}
        weekly = latest / "weekly.json"
        if weekly.exists():
            w = json.loads(weekly.read_text())
            public["weekly_trend"] = w.get("weekly_trend")
        (ROOT / "briefing.json").write_text(json.dumps(public, indent=2, ensure_ascii=False) + "\n")
    elif kind == "weekly":
        brief = ROOT / "briefing.json"
        current = json.loads(brief.read_text()) if brief.exists() else {"schema_version": 1, "status": "unpublished", "headlines": []}
        current["weekly_trend"] = report.get("weekly_trend")
        brief.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n")
    print(f"Published evidence-labelled {kind} report: {dest.relative_to(ROOT)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    publish(pathlib.Path(args.input).resolve())
