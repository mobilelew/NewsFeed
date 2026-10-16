import copy
import unittest
from federal_register_crosscheck import compare_document,build_verified_metadata
class FederalCrossCheckTests(unittest.TestCase):
    def setUp(self):
        self.index={"document_number":"2026-12345","publication_date":"2026-10-16","type":"Rule"}
        self.original=dict(self.index,html_url="https://www.federalregister.gov/documents/2026/10/16/2026-12345/example")
    def test_matching_primary_document_fields(self):
        report=build_verified_metadata(self.index,self.original)
        self.assertTrue(report["metadata_fields_matched"])
        self.assertFalse(report["legal_effect_authenticated"])
    def test_publication_date_contradiction_detected(self):
        original=dict(self.original,publication_date="2025-10-16")
        report=compare_document(self.index,original)
        self.assertIn("publication_date",report["mismatches"])
        with self.assertRaises(ValueError):
            build_verified_metadata(self.index,original)
    def test_proposed_rule_not_equal_to_final_rule(self):
        original=dict(self.original,type="Proposed Rule")
        self.assertFalse(compare_document(self.index,original)["metadata_fields_matched"])
    def test_bad_source_link_not_accepted(self):
        original=dict(self.original,html_url="https://fake.gov/article")
        self.assertFalse(compare_document(self.index,original)["metadata_fields_matched"])
if __name__=="__main__":unittest.main()
