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
    def test_unknown_date_allowed_for_unverified_claim(self):
        h=self.report["headlines"][0]
        h["verification"]="Unverified"
        h["event_date"]=None
        h["source_checked_at"]=None
        result=review(self.report)
        self.assertTrue(result["passed_prepublication_screen"])
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
    def test_first_paid_candidate_regression(self):
        # Mirrors shape/time of the October 15 paid artifact without reproducing
        # its articles: missing per-claim temporal and evidence-inspection fields.
        self.report["report_time"]="2026-10-15T22:05:59-05:00"
        h=self.report["headlines"][0]
        h.pop("event_date")
        h.pop("source_checked_at")
        h.pop("claim_evidence_note")
        result=review(self.report)
        self.assertFalse(result["passed_prepublication_screen"])
        self.assertTrue(any("morning window" in msg for msg in result["issues"]))
        self.assertTrue(any("event_date" in msg for msg in result["issues"]))
        self.assertTrue(any("source_checked_at" in msg for msg in result["issues"]))
        self.assertTrue(any("claim-specific" in msg for msg in result["issues"]))
    def test_source_check_must_include_timezone(self):
        self.report["headlines"][0]["source_checked_at"]="2026-10-15T06:00:00"
        self.assertFalse(review(self.report)["passed_prepublication_screen"])
    def test_source_cannot_be_inspected_after_report(self):
        self.report["headlines"][0]["source_checked_at"]="2026-10-16T06:00:00-05:00"
        self.assertFalse(review(self.report)["passed_prepublication_screen"])
if __name__=="__main__":
    unittest.main()
