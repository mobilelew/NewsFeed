#!/usr/bin/env python3
"""Exact-field original-source authentication for Federal Register documents.

A match proves only that the named official API record reports these fields.
It does not establish enforceability, implementation, or current court status.
"""
import datetime as dt
import json
import re

VALID_TYPES={"Rule","Proposed Rule","Notice","Presidential Document"}
DOCUMENT_NUMBER=re.compile(r"^(?:C[0-9]+-)?[0-9]{4}-[0-9]{4,6}$")

def compare_document(index_record,original_record):
    number=index_record.get("document_number")
    if not isinstance(number,str) or not DOCUMENT_NUMBER.fullmatch(number):
        raise ValueError("Invalid Federal Register document number")
    if not isinstance(original_record,dict):
        raise ValueError("Original document JSON must be object")
    fields=("document_number","publication_date","type")
    mismatches=[]
    for field in fields:
        if index_record.get(field)!=original_record.get(field):
            mismatches.append(field)
    if original_record.get("type") not in VALID_TYPES:
        mismatches.append("unsupported_document_type")
    try:
        dt.date.fromisoformat(original_record.get("publication_date",""))
    except (ValueError,TypeError):
        mismatches.append("invalid_publication_date")
    link=original_record.get("html_url","")
    if not isinstance(link,str) or not link.startswith("https://www.federalregister.gov/documents/"):
        mismatches.append("official_document_link")
    return {"document_number":number,"metadata_fields_matched":not mismatches,
            "compared_fields":list(fields),"mismatches":sorted(set(mismatches)),
            "original_document_url":link if isinstance(link,str) else "",
            "source":"Federal Register individual-document API",
            "verified_scope":"document identity, publication date, document category only",
            "legal_effect_authenticated":False}

def build_verified_metadata(index_record,original_record):
    assessment=compare_document(index_record,original_record)
    if not assessment["metadata_fields_matched"]:
        raise ValueError("Original Federal Register document disagrees with listing: "+",".join(assessment["mismatches"]))
    return assessment
