"""Offline tests: official-source monitoring does not infer legal actions."""
import datetime as dt
import unittest
from zoneinfo import ZoneInfo
import monitor_state_sources as m

class MonitorTests(unittest.TestCase):
    def test_digest_ignores_scripts(self):
        value, count = m.digest(b"<html><script>ignore secret</script><body>" + b"Official calendar "*10 + b"</body></html>")
        self.assertEqual(len(value), 64)
        self.assertGreater(count, 80)
    def test_changes_only_are_signals(self):
        now = dt.datetime(2026, 10, 14, tzinfo=ZoneInfo("America/Chicago"))
        def fake(url): return ("newhash", 1000)
        first = m.assemble(now, {}, fake)
        second = m.assemble(now, first, fake)
        self.assertFalse(first["legal_changes_verified"])
        for jur in second["jurisdictions"].values():
            self.assertFalse(jur["legal_changes_verified"])
            self.assertTrue(all(x["change"] == "unchanged" for x in jur["sources"]))
    def test_failure_is_explicit(self):
        now = dt.datetime(2026, 10, 14, tzinfo=ZoneInfo("America/Chicago"))
        def fail(url): raise OSError("blocked")
        doc = m.assemble(now, {}, fail)
        self.assertEqual(doc["jurisdictions"]["texas"]["status"], "unavailable")
        self.assertEqual(doc["jurisdictions"]["oklahoma"]["sources"][0]["change"], "undetermined")

if __name__ == "__main__":
    unittest.main()
