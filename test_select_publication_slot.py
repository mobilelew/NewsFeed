import datetime as dt
import unittest
from select_publication_slot import select

UTC=dt.timezone.utc
class SlotTests(unittest.TestCase):
    def test_dst_summer_primary_at_six(self):
        self.assertEqual(select("schedule","9 11,12 * * *",dt.datetime(2026,10,17,11,9,tzinfo=UTC))["mode"],"production")
    def test_winter_utc_backup_does_not_publish_at_five(self):
        self.assertEqual(select("schedule","9 11,12 * * *",dt.datetime(2026,12,1,11,9,tzinfo=UTC))["mode"],"skip")
    def test_winter_six_am_runs(self):
        self.assertEqual(select("schedule","9 11,12 * * *",dt.datetime(2026,12,1,12,9,tzinfo=UTC))["kind"],"morning")
    def test_delayed_october_run_at_nine_am_recovers(self):
        self.assertEqual(select("schedule","9 11,12 * * *",dt.datetime(2026,10,17,14,12,tzinfo=UTC))["mode"],"production")
    def test_evening_dst_backup_waits(self):
        self.assertEqual(select("schedule","9 1,2 * * *",dt.datetime(2026,12,1,1,9,tzinfo=UTC))["mode"],"skip")
    def test_unknown_event_is_rejected(self):
        with self.assertRaises(ValueError): select("push","",dt.datetime.now(UTC))
    def test_very_late_evening_fails_instead_of_green_skip(self):
        with self.assertRaises(ValueError): select("schedule","9 1,2 * * *",dt.datetime(2026,10,18,14,9,tzinfo=UTC))
if __name__=="__main__":unittest.main()
