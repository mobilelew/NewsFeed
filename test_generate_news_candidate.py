"""Offline tests for API report decoding; do not spend API credits."""
import json, unittest
from generate_news_candidate import extract, source_registry, coverage_audit

class CandidateTests(unittest.TestCase):
    def test_source_registry_includes_all_required_groups(self):
        sources=source_registry()
        self.assertIn("texas",sources["primary_sources"])
        self.assertIn("agriculture",sources["primary_sources"])
        self.assertIn("technology_cyber",sources["primary_sources"])
    def test_missing_jurisdiction_is_not_claimed_covered(self):
        result=coverage_audit({"headlines":[{"jurisdiction":"federal"}]})
        self.assertEqual(result["jurisdictions_without_findings"],["arkansas","oklahoma","texas"])
    def test_response_text_parses(self):
        source={"output":[{"content":[{"type":"output_text","text":'{"headlines": []}'}]}]}
        self.assertEqual(extract(source),{"headlines":[]})
    def test_missing_output_fails(self):
        with self.assertRaises(ValueError): extract({"output":[]})
    def test_invalid_json_fails(self):
        with self.assertRaises(json.JSONDecodeError):
            extract({"output":[{"content":[{"type":"output_text","text":"not json"}]}]})

if __name__=="__main__": unittest.main()
