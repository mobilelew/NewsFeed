"""No-network regression tests for conservative Federal Register collector."""
import datetime as dt
import unittest
from zoneinfo import ZoneInfo
from collect_official_records import create_report, make_headline

class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.now = dt.datetime(2026, 10, 14, 6, 25, tzinfo=ZoneInfo("America/Chicago"))
        self.record = {
            "title": "Sample Notice of Proposed Action",
            "document_number": "2026-12345",
            "publication_date": "2026-10-14",
            "type": "Proposed Rule",
            "html_url": "https://www.federalregister.gov/documents/2026/10/14/2026-12345/sample",
        }
    def test_qualified_legal_effect(self):
        record = make_headline(self.record)
        self.assertEqual(record["verification"], "Legal Effect Unclear")
        self.assertIn("have not been independently checked", record["uncertainty"])
        self.assertNotEqual(record["claim_type"], "established_fact")
    def test_reject_wrong_domain(self):
        self.assertIsNone(make_headline(dict(self.record, html_url="https://example.org/")))
    def test_reject_old_data(self):
        report = create_report(self.now, [dict(self.record, publication_date="2026-10-13")], "morning")
        self.assertIsNone(report)
    def test_morning_baseline(self):
        report = create_report(self.now, [self.record], "morning")
        self.assertEqual(report["baseline"][0]["identifier"], "2026-12345")
        self.assertIn("metadata-only", report["coverage_note"])
    def test_evening_no_baseline(self):
        report = create_report(self.now, [self.record], "evening")
        self.assertNotIn("baseline", report)
    def test_empty_results_no_report(self):
        self.assertIsNone(create_report(self.now, [], "morning"))

if __name__ == "__main__":
    unittest.main()
