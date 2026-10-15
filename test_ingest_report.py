import datetime as dt
import json
import pathlib
import tempfile
import unittest
from zoneinfo import ZoneInfo
import ingest_report as ingest

class DirectIngestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ingest.ROOT / "submissions")
        self.path = pathlib.Path(self.temp.name) / "report.json"
        local = dt.datetime.now(ZoneInfo("America/Chicago")).replace(microsecond=0)
        self.good = {
            "schema_version": 1, "publication_policy": "evidence-status-v1",
            "report_type": "morning", "report_time": local.isoformat(),
            "headlines": [{
                "title": "BLS statistical publication",
                "summary": "BLS maintains a consumer price statistics release page.",
                "jurisdiction": "federal", "claim_type": "data_release",
                "verification": "Verified",
                "evidence": [{"type":"primary","description":"BLS publication index",
                              "url":"https://www.bls.gov/news.release/cpi.toc.htm"}]
            }],
            "baseline": [{"identifier":"BLS-PUBLICATION","status":"Official page indexed",
                          "as_of":local.isoformat()}]
        }
    def tearDown(self):
        self.temp.cleanup()
    def test_stage_valid(self):
        ingest.stage(json.dumps(self.good), self.path)
        self.assertTrue(self.path.exists())
    def test_reject_missing_qualifiers(self):
        report = json.loads(json.dumps(self.good))
        report["headlines"][0]["verification"] = "Unverified"
        with self.assertRaises(ValueError):
            ingest.stage(json.dumps(report), self.path)
        self.assertFalse(self.path.exists())
    def test_reject_nonobject(self):
        with self.assertRaises(ValueError):
            ingest.stage("[]", self.path)
    def test_reject_oversized(self):
        with self.assertRaises(ValueError):
            ingest.stage("X" * (ingest.MAX_BYTES + 1), self.path)
    def test_reject_restage(self):
        ingest.stage(json.dumps(self.good), self.path)
        with self.assertRaises(ValueError):
            ingest.stage(json.dumps(self.good), self.path)

if __name__ == "__main__":
    unittest.main()
