#!/usr/bin/env python3
"""Publish qualified research without promoting unresolved claims to verified.
The source audit must be run first; the report preserves its uncertainty.
"""
import argparse
import json
import pathlib
import publish_report
from label_uncertain_research import prepare

ROOT=pathlib.Path(__file__).resolve().parent

def process(candidate,authority):
    qualified=prepare(candidate,authority)
    if not qualified.get("headlines"):
        raise ValueError("Cannot publish an empty qualified briefing")
    # A matching quote alone never upgrades model verification claims.
    for h in qualified["headlines"]:
        if h.get("verification") in ("Verified","Corroborated"):
            raise ValueError("Research claim improperly promoted")
    return qualified

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate",default="submissions/ai-research-candidate.json")
    ap.add_argument("--authority",default="submissions/ai-authority-confirmation.json")
    ap.add_argument("--output",default="submissions/ai-qualified-for-publication.json")
    args=ap.parse_args()
    paths=[(ROOT/x).resolve() for x in (args.candidate,args.authority,args.output)]
    if any(not p.is_relative_to(ROOT) for p in paths):raise ValueError("File outside repository")
    if not paths[0].exists():raise ValueError("No research candidate")
    evidence=json.loads(paths[1].read_text()) if paths[1].exists() else {}
    doc=process(json.loads(paths[0].read_text()),evidence)
    paths[2].parent.mkdir(parents=True,exist_ok=True)
    paths[2].write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    publish_report.publish(paths[2])
    print("Published qualified, evidence-labelled "+doc["report_type"]+" briefing")
if __name__=="__main__":main()
