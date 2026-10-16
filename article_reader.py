"""Conservative publisher article excerpt reader.

Attempts to read a publisher page, but does not bypass paywalls or claim
that an extracted passage summarizes the complete story.
"""
from html.parser import HTMLParser
import ipaddress
import re
import socket
import urllib.parse
import urllib.request

class Paragraphs(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ignore=0
        self.paragraph=0
        self.parts=[]
        self.current=[]
    def handle_starttag(self,tag,attrs):
        if tag in ("script","style","nav","footer","header"):self.ignore+=1
        if tag=="p" and not self.ignore:
            self.paragraph+=1;self.current=[]
    def handle_endtag(self,tag):
        if tag=="p" and self.paragraph:
            value=" ".join(" ".join(self.current).split())
            if len(value)>=100:self.parts.append(value)
            self.paragraph-=1;self.current=[]
        if tag in ("script","style","nav","footer","header"):self.ignore=max(self.ignore-1,0)
    def handle_data(self,data):
        if self.paragraph and not self.ignore:self.current.append(data)

def safe_public_https(url):
    try:
        p=urllib.parse.urlsplit(url)
        if p.scheme!="https" or not p.hostname or p.username or p.password or p.port not in (None,443):
            return False
        host=p.hostname.lower().rstrip(".")
        if host in {"localhost","news.google.com"}:return False
        ipaddress.ip_address(host)
        return False
    except ValueError:
        return True
    except (TypeError,AttributeError):
        return False

def article_extract(url,opener=None):
    if not safe_public_https(url):return None
    # The feed often links to Google News rather than the original publisher.
    # Do not call an aggregator's snippet the full article.
    opener=opener or urllib.request.build_opener()
    req=urllib.request.Request(url,headers={"User-Agent":"NewsReader/2.0","Accept":"text/html"})
    try:
        with opener.open(req,timeout=8) as resp:
            final=resp.geturl() if hasattr(resp,"geturl") else url
            if not safe_public_https(final) or "text/html" not in resp.headers.get("Content-Type","text/html"):
                return None
            raw=resp.read(250_001)
            if len(raw)>250_000:return None
        parser=Paragraphs()
        parser.feed(raw.decode("utf-8",errors="replace"))
        paragraphs=[p for p in parser.parts if not re.search(r"cookies|subscribe to our newsletter",p,re.I)]
        if not paragraphs:return None
        return {"summary":" ".join(paragraphs)[:450].rsplit(" ",1)[0]+"…",
                "summary_provenance":"publisher_article_excerpt","article_url":final}
    except (OSError,ValueError,UnicodeError):
        return None
