import datetime as dt
import json
import pathlib
import tempfile
import unittest
from service_health import evaluate
UTC=dt.timezone.utc
class HealthTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=pathlib.Path(self.temp.name)
        self.now=dt.datetime(2026,10,16,12,0,tzinfo=UTC)
    def tearDown(self):self.temp.cleanup()
    def write(self,name,data):
        p=self.root/name
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(data))
    def test_fresh_discovery_not_mislabeled_as_verified(self):
        self.write("feed.json",{"updated_at":"2026-10-16T11:00:00+00:00","headlines":[{"title":"Candidate"}]})
        d=evaluate(self.root,self.now)
        self.assertTrue(d["discovery"]["current"])
        self.assertFalse(d["verified_briefing"]["published"])
        self.assertFalse(d["acceptance"]["full_briefing_delivery_confirmed"])
    def test_stale_discovery_flags_attention(self):
        self.write("feed.json",{"updated_at":"2026-10-16T03:00:00+00:00","headlines":[{"title":"Old"}]})
        self.assertEqual(evaluate(self.root,self.now)["overall"],"attention_required")
    def test_missing_sources_are_safe(self):
        d=evaluate(self.root,self.now)
        self.assertEqual(d["discovery"]["status"],"stale_or_empty")
        self.assertFalse(d["verified_briefing"]["published"])
    def test_published_indicator_requires_headlines(self):
        self.write("briefing.json",{"status":"published","headlines":[]})
        self.assertFalse(evaluate(self.root,self.now)["verified_briefing"]["published"])
if __name__=="__main__":unittest.main()
