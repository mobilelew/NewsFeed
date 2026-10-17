"""Canonical direct publisher links; no aggregator or tracking intermediary on Read More."""
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
import re
BLOCKED_HOSTS={"news.google.com","google.com","www.google.com","t.co","bit.ly","tinyurl.com","lnkd.in","feedproxy.google.com","click.linksynergy.com","rstyle.me"}
TRACK_KEYS={"fbclid","gclid","dclid","msclkid","mc_cid","mc_eid","igshid","ref_src","cmpid","ocid"}
TRACK_PREFIXES=("utm_","ga_","pk_")
AFFILIATE_KEYS={"aff","affiliate","affiliate_id","aff_id","tag","partner_id","clickid"}
def direct_publisher_url(url):
    try:
        p=urlsplit(url)
        host=(p.hostname or "").lower().rstrip(".")
        if p.scheme!="https" or not host or p.username or p.password or p.port not in (None,443):
            return None
        if host in BLOCKED_HOSTS or host.endswith(".google.com") or host.endswith(".doubleclick.net"):
            return None
        if not re.fullmatch(r"[a-z0-9.-]+",host) or "." not in host:
            return None
        for key,_ in parse_qsl(p.query,keep_blank_values=True):
            if key.lower() in AFFILIATE_KEYS:
                return None
        clean=[(k,v) for k,v in parse_qsl(p.query,keep_blank_values=True)
               if k.lower() not in TRACK_KEYS and not k.lower().startswith(TRACK_PREFIXES)]
        return urlunsplit(("https",p.netloc,p.path or "/",urlencode(clean),""))
    except (ValueError,TypeError,AttributeError):
        return None
