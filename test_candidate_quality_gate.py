import unittest
from candidate_quality_gate import review

class QualityGateTests(unittest.TestCase):
    def setUp(self):
        self.report={"report_type":"morning","report_time":"2026-10-15T06:05:00-05:00",
            "headlines":[{"title":"Official report","jurisdiction":"texas",
            "verification":"Verified","event_date":"2026-10-14",
            "source_checked_at":"2026-10-15T06:00:00-05:00",
            "claim_evidence_note":"Document expressly lists the reported action.",
            "evidence":[{"type":"primary","url":"https://capitol.texas.gov/"}]}]}
    def test_valid_shape_not_proof(self):
        r=review(self.report)
        self.assertTrue(r["passed_prepublication_screen"])
        self.assertIn("cannot authenticate",r["caution"])
    def test_no_stale_morning_label(self):
        self.report["report_time"]="2026-10-15T22:05:00-05:00"
        self.assertFalse(review(self.report)["passed_prepublication_screen"])
    def test_dates_required(self):
        self.report["headlines"][0].pop("event_date")
        self.assertFalse(review(self.report)["passed_prepublication_screen"])
    def test_corroboration_origin(self):
        h=self.report["headlines"][0]
        h["verification"]="Corroborated"
        h["evidence"]=[{"type":"independent","url":"https://example-news.com/a"},
                       {"type":"independent","url":"https://example-news.com/b"}]
        self.assertFalse(review(self.report)["passed_prepublication_screen"])
    def test_rejects_combined_state(self):
        self.report["headlines"][0]["jurisdiction"]="arkansas/oklahoma"
        self.assertFalse(review(self.report)["passed_prepublication_screen"])
if __name__=="__main__":
    unittest.main()
