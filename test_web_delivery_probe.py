import io
import unittest
from web_delivery_probe import check
class Response:
    status=200
    def __init__(self,data):self.data=data
    def __enter__(self):return self
    def __exit__(self,*x):pass
    def read(self,n):return self.data[:n]
class Opener:
    def open(self,req,timeout):
        url=req.full_url
        if url.endswith(".json"):
            return Response(b'{"headlines":[{"title":"Sample"}]}' if url.endswith("feed.json") else b'{"status":"unpublished","headlines":[]}')
        return Response(b"<html><h1>News Reader</h1>Current news discovery</html>")
class Failed(Opener):
    def open(self,req,timeout):
        if "news.palmerfamily.org" in req.full_url:raise OSError("offline")
        return super().open(req,timeout)
class DeliveryTests(unittest.TestCase):
    def test_healthy_without_falsely_claiming_verified_content(self):
        d=check(Opener())
        self.assertTrue(d["web_delivery_available"])
        self.assertFalse(d["verified_full_news_available"])
    def test_custom_domain_outage_detected(self):
        d=check(Failed())
        self.assertFalse(d["web_delivery_available"])
        self.assertFalse(d["targets"]["custom_domain"]["ok"])
if __name__=="__main__":unittest.main()
