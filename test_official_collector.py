"""No-network regression tests for conservative Federal Register collector."""
import datetime as dt
import unittest
from zoneinfo import ZoneInfo
from collect_official_records import create_report, make_headline, crosscheck_report

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

    def test_individual_record_crosscheck_keeps_exact_metadata(self):
        report=create_report(self.now,[self.record],"morning")
        authenticated=crosscheck_report(report,lambda number:dict(self.record))
        self.assertEqual(authenticated["source_crosscheck"]["matched"],1)
        self.assertFalse(authenticated["source_crosscheck"]["legal_effect_authenticated"])
        self.assertEqual(len(authenticated["baseline"]),1)
    def test_official_abstract_and_dates_are_read_from_individual_record(self):
        report=create_report(self.now,[self.record],"morning")
        body=dict(self.record,abstract="The agency proposes to revise its application procedures.",
                  comments_close_on="2026-11-16",effective_on="2026-12-01")
        authenticated=crosscheck_report(report,lambda number:body)
        h=authenticated["headlines"][0]
        self.assertEqual(h["summary"],body["abstract"])
        self.assertEqual(h["summary_provenance"],"federal_register_document_abstract")
        self.assertEqual(h["official_document_details"]["comments_close_on"],"2026-11-16")
        self.assertEqual(h["verification"],"Legal Effect Unclear")
    def test_no_abstract_disclosed(self):
        report=create_report(self.now,[self.record],"morning")
        authenticated=crosscheck_report(report,lambda number:dict(self.record))
        self.assertFalse(authenticated["headlines"][0]["agency_abstract_read"])
    def test_date_mismatch_discards_record_and_baseline(self):
        report=create_report(self.now,[self.record],"morning")
        result=crosscheck_report(report,lambda number:dict(self.record,publication_date="2025-10-14"))
        self.assertIsNone(result)
if __name__ == "__main__":
    unittest.main()
