#!/usr/bin/env python3
"""Safely stage a direct News Reader report payload for existing publisher.

Supports authorized GitHub Actions workflow_dispatch and repository_dispatch.
Does not generate claims, retrieve evidence, or fact-check references.
"""
import argparse
import json
import pathlib
import sys
from publish_report import ROOT, load_submission

MAX_BYTES = 180000

def stage(raw, output):
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > MAX_BYTES:
        raise ValueError("Report payload missing or larger than allowed limit")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON report payload") from exc
    if not isinstance(data, dict):
        raise ValueError("Report payload must be an object")
    path = pathlib.Path(output).resolve()
    submissions = (ROOT / "submissions").resolve()
    if not path.is_relative_to(submissions):
        raise ValueError("Output must be in submissions")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError("Refusing to overwrite staged submission")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        report, _ = load_submission(path)
        print("Staged validated " + report["report_type"] + " report")
        return path
    except Exception:
        path.unlink(missing_ok=True)
        raise

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="File containing raw JSON payload")
    parser.add_argument("--output", default="submissions/direct-ingest.json")
    args = parser.parse_args()
    raw = pathlib.Path(args.input).read_text(encoding="utf-8")
    stage(raw, args.output)

if __name__ == "__main__":
    main()
