import copy
import unittest
from claim_evidence_audit import audit_batch

class ClaimEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.data = {"documents":{"bls":{"url":"https://www.bls.gov/news.release/cpi.toc.htm",
              "kind":"primary","retrieved_at":"2026-10-15T15:00:00Z",
              "content":"The consumer price index report is published monthly."}},
            "claims":[{"claim_id":"c1","reported_claim":"BLS publishes CPI monthly",
                "reported_by":"Example news publisher",
                "report_url":"https://www.reuters.com/",
                "evidence_status":"Verified","finding":"A publication schedule exists",
                "limitations":"Specific figures are not examined",
                "resolution_needed":"Retrieve dated release for numbers",
                "evidence_links":[{"document_id":"bls","excerpt":"consumer price index report is published monthly",
                                   "relation":"supports"}]}]}
    def test_located_primary_quote(self):
        result=audit_batch(self.data)
        self.assertEqual(result["claims"][0]["evidence_status"],"Verified")
        self.assertEqual(result["claims"][0]["semantic_verification"],"not_independently_established")
    def test_unlocated_quote_rejected(self):
        data=copy.deepcopy(self.data)
        data["claims"][0]["evidence_links"][0]["excerpt"]="not on this page"
        with self.assertRaises(ValueError): audit_batch(data)
    def test_verified_no_primary_rejected(self):
        data=copy.deepcopy(self.data)
        data["documents"]["bls"]["kind"]="attribution"
        with self.assertRaises(ValueError): audit_batch(data)
    def test_verified_with_contradiction_rejected(self):
        data=copy.deepcopy(self.data)
        data["claims"][0]["evidence_links"].append({"document_id":"bls","excerpt":"published monthly","relation":"contradicts"})
        with self.assertRaises(ValueError): audit_batch(data)
    def test_disputed_requires_both_sides(self):
        data=copy.deepcopy(self.data)
        data["claims"][0]["evidence_status"]="Disputed"
        with self.assertRaises(ValueError): audit_batch(data)
    def test_refuted_requires_contradiction(self):
        data=copy.deepcopy(self.data)
        data["claims"][0]["evidence_status"]="Refuted"
        with self.assertRaises(ValueError): audit_batch(data)
    def test_duplicate_claims_rejected(self):
        data=copy.deepcopy(self.data)
        data["claims"].append(copy.deepcopy(data["claims"][0]))
        with self.assertRaises(ValueError): audit_batch(data)

if __name__=="__main__":
    unittest.main()
