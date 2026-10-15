#!/usr/bin/env python3
"""Claim-level evidence audit. Conservative: quotations are located, not semantically proven.

Input: JSON with claims and separately captured source excerpts. Every claim retains
its original news attribution. No source-reputation based approval or rejection.
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
from urllib.parse import urlparse

LABELS = {"Verified", "Corroborated", "Unsubstantiated", "Disputed",
          "Legal Effect Unclear", "Unverified", "Refuted"}
RELATIONS = {"supports", "contradicts", "context_only", "unclear"}
KINDS = {"primary", "independent", "attribution"}
ROOT = pathlib.Path(__file__).resolve().parent

def nonempty(value):
    return isinstance(value, str) and bool(value.strip())

def valid_url(url):
    p = urlparse(str(url))
    return p.scheme == "https" and bool(p.hostname) and p.hostname not in {
        "example.com", "example.org", "example.net"
    }

def normalize(s):
    return re.sub(r"\s+", " ", s).strip().casefold()

def audit_claim(claim, documents):
    for key in ("claim_id", "reported_claim", "reported_by", "report_url", "evidence_status",
                "finding", "limitations", "resolution_needed"):
        if not nonempty(claim.get(key)):
            raise ValueError(f"Claim missing {key}")
    if claim["evidence_status"] not in LABELS or not valid_url(claim["report_url"]):
        raise ValueError("Invalid evidence label or report URL")
    if not isinstance(claim.get("evidence_links"), list) or not claim["evidence_links"]:
        raise ValueError("Claim must cite one or more inspected excerpts")
    supports, contradicts, primary_support = [], [], []
    checked = []
    for link in claim["evidence_links"]:
        document = documents.get(link.get("document_id"))
        if not document:
            raise ValueError("Unknown evidence document")
        if not valid_url(document.get("url")) or document.get("kind") not in KINDS:
            raise ValueError("Evidence source invalid")
        if not nonempty(document.get("retrieved_at")) or not nonempty(document.get("content")):
            raise ValueError("Evidence requires retrieved timestamp and captured content")
        excerpt = link.get("excerpt")
        if not nonempty(excerpt) or normalize(excerpt) not in normalize(document["content"]):
            raise ValueError("Cited excerpt not located in captured source")
        if link.get("relation") not in RELATIONS:
            raise ValueError("Invalid evidence relationship")
        checked.append({"document_id": link["document_id"], "url": document["url"],
                        "kind": document["kind"], "excerpt": excerpt,
                        "relation": link["relation"],
                        "retrieved_at": document["retrieved_at"],
                        "content_sha256": hashlib.sha256(document["content"].encode()).hexdigest()})
        if link["relation"] == "supports":
            supports.append(link)
            if document["kind"] == "primary":
                primary_support.append(link)
        if link["relation"] == "contradicts":
            contradicts.append(link)
    if claim["evidence_status"] == "Verified" and (not primary_support or contradicts):
        raise ValueError("Verified requires primary supporting excerpt and no contradiction")
    if claim["evidence_status"] == "Refuted" and not contradicts:
        raise ValueError("Refuted requires a contradicting excerpt")
    if claim["evidence_status"] == "Disputed" and (not supports or not contradicts):
        raise ValueError("Disputed requires supporting and contradicting excerpts")
    # Even a present excerpt may not entail a claim. Relation is an analyst/model
    # assessment, and source identity and publication/version require further review.
    return {"claim_id": claim["claim_id"], "reported_claim": claim["reported_claim"],
            "reported_by": claim["reported_by"], "report_url": claim["report_url"],
            "evidence_status": claim["evidence_status"], "finding": claim["finding"],
            "limitations": claim["limitations"], "resolution_needed": claim["resolution_needed"],
            "excerpts": checked, "semantic_verification": "not_independently_established",
            "audit_note": "Quote presence and evidence label consistency checked. Whether excerpts entail claims, source authenticity and legal effect require separate validation."}

def audit_batch(data):
    if not isinstance(data, dict) or not isinstance(data.get("claims"), list):
        raise ValueError("Expected claims array")
    documents = data.get("documents")
    if not isinstance(documents, dict):
        raise ValueError("Expected captured documents map")
    checked = [audit_claim(c, documents) for c in data["claims"]]
    if len({c["claim_id"] for c in checked}) != len(checked):
        raise ValueError("Duplicate claim IDs")
    return {"schema_version": 1, "audit_type": "claim-evidence", "production_ready": False,
            "audited_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "claims": checked}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    inp = pathlib.Path(args.input).resolve()
    out = pathlib.Path(args.output).resolve()
    if not inp.is_relative_to(ROOT) or not out.is_relative_to(ROOT):
        raise ValueError("Input/output must remain under repository")
    result = audit_batch(json.loads(inp.read_text(encoding="utf-8")))
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Audited {len(result['claims'])} claims; semantic verification remains separate")

if __name__ == "__main__":
    main()
