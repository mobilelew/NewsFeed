import copy
import unittest
from captured_claim_audit import assemble

class CaptureJoinTests(unittest.TestCase):
    def setUp(self):
        self.captures={"records":[{"url":"https://www.bls.gov/news.release/example",
            "retrieved_at":"2026-10-16T10:00:00+00:00",
            "sha256":"a"*64,"source_authentication":"capture_only_not_semantic_verification",
            "content":"The release was published on October 14, 2026."}]}
        self.claims={"claims":[{"claim_id":"bls-release","reported_claim":"BLS released data",
            "reported_by":"Named reporting outlet","report_url":"https://www.reuters.com/",
            "evidence_status":"Verified","finding":"The original document contains the quoted text",
            "limitations":"This does not establish the report's exact interpretation",
            "resolution_needed":"Check meaning of document and date against claim",
            "evidence_links":[{"document_id":"capture-0","excerpt":"published on October 14, 2026",
                "relation":"supports"}]}]}
    def test_exact_quote_joins_but_does_not_approve(self):
        result=assemble(self.captures,self.claims)
        self.assertFalse(result["publication_approved"])
        self.assertEqual(result["claims"][0]["semantic_verification"],"not_independently_established")
        self.assertEqual(result["capture_sha256"]["capture-0"],"a"*64)
    def test_invented_excerpt_is_rejected(self):
        c=copy.deepcopy(self.claims)
        c["claims"][0]["evidence_links"][0]["excerpt"]="BLS said taxes decreased"
        with self.assertRaises(ValueError):assemble(self.captures,c)
    def test_missing_source_provenance_rejected(self):
        c=copy.deepcopy(self.captures)
        c["records"][0].pop("source_authentication")
        with self.assertRaises(ValueError):assemble(c,self.claims)
if __name__=="__main__":unittest.main()
