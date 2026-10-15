import datetime as dt
import json
import unittest
import verify_kev_news as v

class KevVerificationTests(unittest.TestCase):
    def setUp(self):
        self.now=dt.datetime(2026,10,15,tzinfo=dt.timezone.utc)
        self.cat=json.dumps({"vulnerabilities":[{"cveID":"CVE-2026-12345","dateAdded":"2026-10-15"}]})
    def rss(self,title):
        from xml.sax.saxutils import escape
        return ('<rss><channel><item><title>'+escape(title)+'</title><link>https://news.google.com/articles/abc</link><pubDate>Thu, 15 Oct 2026 12:00:00 GMT</pubDate><source>Publisher</source></item></channel></rss>')
    def test_matching_claim_is_verified_narrowly(self):
        d=v.build(self.rss("CISA adds CVE-2026-12345 to known exploited list"),self.cat,self.now)
        self.assertEqual(d["findings"][0]["verification"],"Verified")
        self.assertIn("listing only",d["findings"][0]["what_is_known"])
    def test_missing_in_catalog_not_refuted(self):
        d=v.build(self.rss("CISA adds CVE-2026-99999 to known exploited list"),self.cat,self.now)
        self.assertEqual(d["findings"][0]["verification"],"Unverified")
    def test_not_cisa_listing_claim(self):
        d=v.build(self.rss("Hacker exploits CVE-2026-12345"),self.cat,self.now)
        self.assertEqual(d["findings"],[])
    def test_empty_catalog_rejected(self):
        with self.assertRaises(ValueError):
            v.build(self.rss("CISA added CVE-2026-12345"),'{"vulnerabilities":[]}',self.now)

if __name__=="__main__":
    unittest.main()
