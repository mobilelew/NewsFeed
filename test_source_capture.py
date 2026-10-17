import io
import unittest
import urllib.request
from source_capture import allowed,capture,run_manifest,MAX_BYTES,OfficialRedirects
class Headers(dict):
    def get_content_type(self): return self.get("type","text/html")
    def get_content_charset(self): return "utf-8"
class Response:
    def __init__(self,body,kind="text/html"):
        self.data=io.BytesIO(body)
        self.headers=Headers(type=kind)
    def __enter__(self): return self
    def __exit__(self,*a): pass
    def read(self,n): return self.data.read(n)
class Opener:
    def __init__(self,data,kind="text/html"): self.data=data;self.kind=kind
    def open(self,request,timeout=12): return Response(self.data,self.kind)
class CaptureTests(unittest.TestCase):
    def test_redirects_restricted_to_approved_https_hosts(self):
        opener=OfficialRedirects()
        req=urllib.request.Request("https://www.bls.gov/")
        safe=opener.redirect_request(req,None,302,"Found",{},"https://www.bls.gov/news.release/")
        self.assertTrue(safe.full_url.startswith("https://www.bls.gov/"))
        with self.assertRaises(ValueError):
            opener.redirect_request(req,None,302,"Found",{},"https://news.google.com/")
        with self.assertRaises(ValueError):
            opener.redirect_request(req,None,302,"Found",{},"http://www.bls.gov/")
    def test_rejects_external_and_local(self):
        for u in ("http://www.bls.gov/", "https://example.com/", "https://127.0.0.1/",
                  "https://evil.com/?source=www.bls.gov","https://www.bls.gov.evil.com/"):
            self.assertFalse(allowed(u),u)
    def test_allows_original_host(self):
        self.assertTrue(allowed("https://www.bls.gov/news.release/cpi.htm"))
    def test_text_and_provenance(self):
        r=capture("https://www.bls.gov/news.release/cpi.htm",Opener(b"<h1>Official</h1><script>bad()</script>Data"))
        self.assertEqual(r["content"],"Official Data")
        self.assertEqual(r["source_authentication"],"capture_only_not_semantic_verification")
        self.assertEqual(r["bytes"],len(b"<h1>Official</h1><script>bad()</script>Data"))
    def test_large_source_refused(self):
        with self.assertRaises(ValueError):
            capture("https://www.bls.gov/",Opener(b"x"*(MAX_BYTES+1)))
    def test_manifest_refuses_unauthorized_domain(self):
        with self.assertRaises(ValueError):
            run_manifest({"urls":["https://www.bls.gov/","https://example.com/"]},Opener(b"ok"))
if __name__=="__main__": unittest.main()
