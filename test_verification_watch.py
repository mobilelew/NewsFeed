import unittest
from verification_watch import examine
class HourlyReviewTests(unittest.TestCase):
    def test_exact_primary_quote_does_not_promote_entire_claim(self):
        report={"report_date":"2026-10-16","report_type":"evening","report_time":"2026-10-16T20:00:00-05:00",
                "headlines":[{"title":"A disputed economic claim","verification":"Unverified",
                  "evidence":[{"type":"primary","url":"https://www.bls.gov/news.release/cpi.toc.htm",
                               "exact_excerpt":"Data for September were published."}]}]}
        def capture(url):
            return {"url":url,"sha256":"abcd","retrieved_at":"2026-10-17T00:00:00+00:00",
                    "content":"Data for September were published.","content_type":"text/html"}
        result=examine(report,capturer=capture)
        self.assertEqual(result["findings"][0]["source_check_status"],"source_excerpt_located")
        self.assertFalse(result["findings"][0]["claim_independently_verified"])
        self.assertEqual(result["pending_findings"],1)
        self.assertEqual(result["findings"][0]["sources_checked"][0]["outcome"],"Source retrieved; cited exact passage located.")
    def test_unreachable_remains_pending(self):
        result=examine({"headlines":[{"title":"X","verification":"Unverified","evidence":[]}]})
        self.assertEqual(result["findings"][0]["source_check_status"],"source_not_inspected")
        self.assertIn("no eligible primary authority",result["findings"][0]["authority_confirmation"])
if __name__=="__main__":unittest.main()
