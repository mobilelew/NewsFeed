import unittest
from research_source_probe import review
class PrimaryProbeTests(unittest.TestCase):
    def test_located_exact_excerpt_is_not_proof(self):
        headline={"title":"Federal source claim","evidence":[{"type":"primary",
            "url":"https://www.bls.gov/news.release/example","exact_excerpt":"Released October 15"}]}
        def fake(url):
            return {"url":url,"content":"Released October 15, 2026",
                    "sha256":"a"*64,"retrieved_at":"2026-10-16T12:00:00+00:00",
                    "content_type":"text/html"}
        result=review({"headlines":[headline]},fake)
        link=result["findings"][0]["primary_records"][0]
        self.assertTrue(link["quoted_excerpt_found"])
        self.assertFalse(result["publication_approved"])
        self.assertFalse(result["independent_source_authentication"])
    def test_wrong_excerpt_is_not_matched(self):
        headline={"title":"Wrong claim","evidence":[{"type":"primary",
            "url":"https://www.bls.gov/", "exact_excerpt":"Rates fell"}]}
        def fake(url):
            return {"url":url,"content":"Rates rose","sha256":"a"*64,
                    "retrieved_at":"2026-10-16T12:00:00+00:00","content_type":"text/html"}
        self.assertFalse(review({"headlines":[headline]},fake)["findings"][0]["primary_records"][0]["quoted_excerpt_found"])
    def test_non_allowlisted_source_not_fetched(self):
        headline={"title":"No","evidence":[{"type":"primary","url":"https://example.com/"}]}
        result=review({"headlines":[headline]},lambda url: self.fail("must not fetch"))
        self.assertFalse(result["findings"][0]["primary_records"][0]["captured"])
if __name__=="__main__":unittest.main()
