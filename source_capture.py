#!/usr/bin/env python3
"""Bounded, allowlisted primary-source capture. Does not establish claim truth."""
import argparse
import datetime as dt
import hashlib
from html.parser import HTMLParser
import ipaddress
import json
import pathlib
import socket
import urllib.parse
import urllib.request

ROOT=pathlib.Path(__file__).resolve().parent
MAX_BYTES=1_000_000
MAX_ITEMS=12
SOURCE_HOSTS={
"congress.gov","govinfo.gov","federalregister.gov","regulations.gov",
"capitol.texas.gov","sos.state.tx.us","arkleg.state.ar.us",
"sos.arkansas.gov","oklegislature.gov","oklahoma.gov",
"bls.gov","bea.gov","federalreserve.gov","treasury.gov",
"sec.gov","freddiemac.com","usda.gov","ams.usda.gov",
"nass.usda.gov","ers.usda.gov","cisa.gov","nist.gov",
"data.nass.usda.gov"
}
class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.bits=[]
        self.hidden=0
    def handle_starttag(self,tag,attrs):
        if tag in ("script","style"): self.hidden+=1
    def handle_endtag(self,tag):
        if tag in ("script","style"): self.hidden=max(0,self.hidden-1)
    def handle_data(self,data):
        if not self.hidden: self.bits.append(data)
    def text(self):
        return " ".join(" ".join(self.bits).split())

def allowed(url):
    parsed=urllib.parse.urlsplit(url)
    if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password or parsed.port not in (None,443):
        return False
    host=parsed.hostname.lower().rstrip(".")
    if host not in SOURCE_HOSTS and not any(host.endswith("."+h) for h in SOURCE_HOSTS):
        return False
    # Network is limited to authoritative public domains; reject numeric IPs.
    try:
        ipaddress.ip_address(host)
        return False
    except ValueError:
        pass
    return True

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        raise ValueError("Redirect refused; inspect final authoritative URL manually")

def capture(url,opener=None):
    if not isinstance(url,str) or not allowed(url):
        raise ValueError("URL is not an allowlisted authoritative HTTPS source")
    opener=opener or urllib.request.build_opener(NoRedirect())
    request=urllib.request.Request(url,headers={"User-Agent":"NewsReaderSourceCapture/1.0","Accept":"text/html,application/json,text/plain"})
    with opener.open(request,timeout=12) as response:
        mime=response.headers.get_content_type()
        if mime not in {"text/html","application/json","text/plain"}:
            raise ValueError("Unsupported source media type")
        raw=response.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES: raise ValueError("Source exceeds capture size limit")
        charset=response.headers.get_content_charset() or "utf-8"
    source=raw.decode(charset,errors="replace")
    if mime=="text/html":
        parser=Text()
        parser.feed(source)
        extracted=parser.text()
    else:
        extracted=source
    return {"url":url,"retrieved_at":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "content_type":mime,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),
            "content":extracted[:200_000],"source_authentication":"capture_only_not_semantic_verification"}

def run_manifest(data,opener=None):
    urls=data.get("urls")
    if not isinstance(urls,list) or not 1<=len(urls)<=MAX_ITEMS:
        raise ValueError("Expected 1-12 source URLs")
    if any(not isinstance(u,str) or not allowed(u) for u in urls):
        raise ValueError("Manifest includes disallowed URL")
    return {"schema_version":1,"records":[capture(u,opener) for u in urls],
            "publication_approved":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    src=pathlib.Path(args.input).resolve()
    dst=pathlib.Path(args.output).resolve()
    if not src.is_relative_to(ROOT) or not dst.is_relative_to(ROOT):
        raise ValueError("Paths must remain within repository")
    record=run_manifest(json.loads(src.read_text(encoding="utf-8")))
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("Captured "+str(len(record["records"]))+" source records; no claims independently verified")
if __name__=="__main__": main()
