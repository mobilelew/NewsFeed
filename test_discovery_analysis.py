import unittest
from discovery_analysis import clean, AREAS
class DiscoveryAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.items=[{"title":"Story A","category":"TEXAS","published_at":"2026-10-17T10:00:00Z","url":"https://example.com/a"}]
    def test_only_feed_titles_can_be_analyzed(self):
        data={"executive_summary":["x"],"area_status":[],"findings":[{"title":"Not in feed","status":"Verified"}]}
        _,_,findings=clean(data,self.items)
        self.assertEqual(findings,[])
    def test_status_and_https_checks_are_bounded(self):
        data={"executive_summary":["x"],"area_status":[],"findings":[{"title":"Story A","status":"Verified","analysis":"a","authority_checks":[{"source":"x","url":"http://bad","finding":"bad"},{"source":"ok","url":"https://example.gov","finding":"ok"}]}]}
        _,areas,findings=clean(data,self.items)
        self.assertEqual(findings[0]["status"],"Verified")
        self.assertEqual(len(findings[0]["authority_checks"]),1)
        self.assertEqual({a["area"] for a in areas},set(AREAS))
    def test_invalid_status_becomes_unresolved(self):
        data={"executive_summary":[],"area_status":[],"findings":[{"title":"Story A","status":"Certain"}]}
        self.assertEqual(clean(data,self.items)[2][0]["status"],"Unresolved")
if __name__=="__main__": unittest.main()
