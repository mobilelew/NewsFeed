#!/usr/bin/env python3
"""Low-cost OpenAI API connectivity check; never prints secrets or response bodies."""
import json
import os
import urllib.error
import urllib.request

def main():
    key=os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("OPENAI_API_KEY missing")
    body=json.dumps({"model":"gpt-5-mini","input":"Reply with exactly: READY","max_output_tokens":30,"store":False}).encode()
    req=urllib.request.Request("https://api.openai.com/v1/responses",data=body,
        headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=45) as resp:
            data=json.load(resp)
    except urllib.error.HTTPError as exc:
        # Never print response body; it can contain implementation details.
        raise SystemExit(f"API request failed with HTTP {exc.code}. Check project limits, model access and billing.") from None
    if not isinstance(data.get("id"),str) or not data.get("id","").startswith("resp_"):
        raise SystemExit("API response missing expected response identifier")
    print("OpenAI Responses API connectivity confirmed; no response content or credential logged.")
if __name__=="__main__":
    main()
