"""Offline tests for API report decoding; do not spend API credits."""
import json, unittest
from generate_news_candidate import extract, diagnostic, source_registry, coverage_audit

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
    def test_incomplete_response_identified(self):
        output={"id":"resp_sample","status":"incomplete",
                "incomplete_details":{"reason":"max_output_tokens"},
                "usage":{"output_tokens":6500},
                "output":[{"type":"reasoning"}]}
        self.assertEqual(diagnostic(output)["incomplete_reason"],"max_output_tokens")
        with self.assertRaisesRegex(ValueError,"incomplete"):
            extract(output)
    def test_diagnostics_do_not_copy_generated_text(self):
        output={"status":"completed","output":[{"type":"message",
                "content":[{"type":"output_text","text":"private example"}]}]}
        self.assertNotIn("private example",str(diagnostic(output)))
    def test_invalid_json_fails(self):
        with self.assertRaises(json.JSONDecodeError):
            extract({"output":[{"content":[{"type":"output_text","text":"not json"}]}]})

if __name__=="__main__": unittest.main()
