import datetime as dt
import unittest
from legislative_event_ledger import build, validate

class LegislativeLedgerTests(unittest.TestCase):
    def setUp(self):
        self.event = {
            "jurisdiction": "texas", "identifier": "HB-TEST",
            "action": "introduced", "action_date": "2026-10-14",
            "source_url": "https://capitol.texas.gov/",
            "source_description": "Official legislative record",
            "attribution": "Texas Legislature Online",
            "status_note": "Record describes introduction only",
            "verification": "Legal Effect Unclear",
            "what_cannot_be_concluded": "This proposal has become law",
            "resolution_needed": "Current bill history and statute text"
        }
    def test_one_event(self):
        x = build([self.event, self.event])
        self.assertEqual(len(x["events"]), 1)
    def test_state_jurisdictions(self):
        for state in ("federal", "texas", "arkansas", "oklahoma"):
            self.assertEqual(validate(dict(self.event, jurisdiction=state))["jurisdiction"], state)
    def test_effective_date_not_inferred(self):
        with self.assertRaises(ValueError):
            validate(dict(self.event, effective_date="2026-10-15"))
    def test_reject_verified_claim(self):
        with self.assertRaises(ValueError):
            validate(dict(self.event, verification="Verified"))
    def test_requires_uncertainty(self):
        with self.assertRaises(ValueError):
            validate(dict(self.event, resolution_needed=""))
    def test_refuses_http(self):
        with self.assertRaises(ValueError):
            validate(dict(self.event, source_url="http://capitol.texas.gov"))

if __name__ == "__main__":
    unittest.main()
