#!/usr/bin/env python3
"""Join captured source records to explicitly supplied claim excerpts.

An exact excerpt located in a retrieved snapshot is evidence of text presence,
NOT semantic proof that the claim follows. Publication is never approved here.
"""
import argparse
import json
import pathlib
from claim_evidence_audit import audit_batch, normalize

ROOT=pathlib.Path(__file__).resolve().parent

def assemble(captures,claims):
    records=captures.get("records")
    if not isinstance(records,list) or not records:
        raise ValueError("Captured source records required")
    documents={}
    for index,record in enumerate(records):
        if record.get("source_authentication")!="capture_only_not_semantic_verification":
            raise ValueError("Unrecognized capture provenance")
        if not record.get("sha256") or not record.get("retrieved_at") or not record.get("content"):
            raise ValueError("Incomplete captured source record")
        identifier="capture-"+str(index)
        documents[identifier]={
            "url":record["url"],"retrieved_at":record["retrieved_at"],
            "kind":"primary","content":record["content"]}
    input_claims=claims.get("claims")
    if not isinstance(input_claims,list):
        raise ValueError("Claims list required")
    # Input must identify exact snapshot and a located excerpt, not merely
    # quote a model's unsupported assessment.
    audit=audit_batch({"documents":documents,"claims":input_claims})
    audit["capture_sha256"]={("capture-"+str(i)):rec["sha256"] for i,rec in enumerate(records)}
    audit["publication_approved"]=False
    audit["semantic_verification"]="not_independently_established"
    return audit

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--capture",required=True)
    p.add_argument("--claims",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    paths=[pathlib.Path(x).resolve() for x in (args.capture,args.claims,args.output)]
    if any(not p.is_relative_to(ROOT) for p in paths):
        raise ValueError("All file paths must remain inside repository")
    captures=json.loads(paths[0].read_text(encoding="utf-8"))
    claims=json.loads(paths[1].read_text(encoding="utf-8"))
    audit=assemble(captures,claims)
    paths[2].parent.mkdir(parents=True,exist_ok=True)
    paths[2].write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("Audited "+str(len(audit["claims"]))+" claim excerpts; independent semantic verification remains outstanding")
if __name__=="__main__":main()
