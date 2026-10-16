import unittest
from authority_claim_check import audit
class AuthorityCheckTests(unittest.TestCase):
    def setUp(self):
        self.c={"report_time":"2026-10-16T06:00:00-05:00","headlines":[{"title":"An official claim","verification":"Verified","evidence":[{"type":"primary","url":"https://www.bls.gov/news.release/example","exact_excerpt":"Event on October 16"}]}]}
    def test_missing_text_does_not_refute(self):
        def fetch(url):return {"url":url,"content":"Event on October 14",
            "sha256":"f"*64,"retrieved_at":"2026-10-16T13:00:00+00:00","content_type":"text/html"}
        result=audit(self.c,fetch)
        self.assertEqual(result["findings"][0]["authority_check"],"cited_source_does_not_confirm_position")
        self.assertFalse(result["findings"][0]["claim_proven"])
    def test_present_text_only_confirms_excerpt(self):
        def fetch(url):return {"url":url,"content":"Event on October 16",
            "sha256":"f"*64,"retrieved_at":"2026-10-16T13:00:00+00:00","content_type":"text/html"}
        result=audit(self.c,fetch)
        self.assertEqual(result["findings"][0]["authority_check"],"cited_source_contains_excerpt")
        self.assertFalse(result["publication_approved"])
if __name__=="__main__":unittest.main()
