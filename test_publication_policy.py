"""Policy safety tests; no reports are published during testing."""
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch
import publish_report as publisher

class PublicationPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=publisher.ROOT / "submissions")
        self.path = pathlib.Path(self.temp.name) / "test.json"
        self.base = {
            "schema_version": 1, "publication_policy": "evidence-status-v1",
            "report_type": "evening", "report_time": "2026-10-14T16:00:00-05:00",
            "headlines": [{
                "title": "Illustrative official data release",
                "summary": "A source reports a statistical finding.",
                "jurisdiction": "federal", "claim_type": "data_release",
                "verification": "Verified",
                "evidence": [{"type": "primary", "description": "Official source",
                              "url": "https://www.bls.gov/news.release/cpi.toc.htm"}]
            }]
        }
    def tearDown(self):
        self.temp.cleanup()
    def check(self, data, accepted):
        self.path.write_text(json.dumps(data), encoding="utf-8")
        if accepted:
            publisher.load_submission(self.path)
        else:
            with self.assertRaises(ValueError):
                publisher.load_submission(self.path)
    def test_verified_primary_passes(self):
        self.check(self.base, True)
    def test_old_approval_format_rejected(self):
        data = dict(self.base, publication_policy="manual", approved=True, editorial_review="completed")
        self.check(data, False)
    def test_unverified_with_attribution_passes(self):
        data = json.loads(json.dumps(self.base))
        h = data["headlines"][0]
        h.update(verification="Unverified", claim_type="attributed_claim",
                 attribution="A named source", what_is_known="Source made an assertion",
                 uncertainty="No original record", what_cannot_be_concluded="It is legally effective",
                 resolution_needed="Published court order")
        h["evidence"][0]["type"] = "attribution"
        self.check(data, True)
    def test_uncertainty_cannot_be_declared_fact(self):
        data = json.loads(json.dumps(self.base))
        h = data["headlines"][0]
        h.update(verification="Disputed", attribution="Two accounts",
                 what_is_known="Conflicting documents", uncertainty="Different dates",
                 what_cannot_be_concluded="Operative deadline", resolution_needed="Court order")
        self.check(data, False)
    def test_unverified_without_context_rejected(self):
        data = json.loads(json.dumps(self.base))
        data["headlines"][0]["verification"] = "Unverified"
        self.check(data, False)
    def test_verified_without_primary_rejected(self):
        data = json.loads(json.dumps(self.base))
        data["headlines"][0]["evidence"][0]["type"] = "attribution"
        self.check(data, False)
    def test_placeholder_url_rejected(self):
        data = json.loads(json.dumps(self.base))
        data["headlines"][0]["evidence"][0]["url"] = "https://example.org/replace"
        self.check(data, False)
    def test_legal_uncertainty_needs_legal_status(self):
        data = json.loads(json.dumps(self.base))
        h = data["headlines"][0]
        h.update(verification="Legal Effect Unclear", claim_type="legal_proceeding",
                 attribution="A named court filing", what_is_known="A motion was filed",
                 uncertainty="No operative order", what_cannot_be_concluded="Effective rule",
                 resolution_needed="Operative docket order")
        self.check(data, False)
        h["legal_status"] = "Enforceability unresolved"
        self.check(data, True)

if __name__ == "__main__":
    unittest.main()
