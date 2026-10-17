import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from check_task_delivery import inspect

class TaskDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        (self.root/"task-briefings").mkdir()
        self.now=dt.datetime(2026,10,17,13,0,tzinfo=dt.timezone.utc)
    def tearDown(self):
        self.temp.cleanup()
    def test_missing_morning_after_cutoff_is_reported(self):
        result=inspect(self.root,self.now)
        self.assertEqual(result["reports"]["morning"]["status"],"missing_after_cutoff")
        self.assertEqual(result["reports"]["evening"]["status"],"not_due_or_pending")
    def test_valid_full_length_task_document_is_accepted(self):
        path=self.root/"task-briefings/latest-morning.json"
        path.write_text(json.dumps({"status":"published","kind":"morning","report_date":"2026-10-17",
                  "generated_at":"2026-10-17T06:05:00-05:00","content_markdown":"Verified source analysis. "*30}))
        self.assertEqual(inspect(self.root,self.now)["reports"]["morning"]["status"],"published_today")
    def test_short_or_stale_report_not_silently_accepted(self):
        path=self.root/"task-briefings/latest-morning.json"
        path.write_text(json.dumps({"status":"published","kind":"morning","report_date":"2026-10-16",
                  "generated_at":"2026-10-16T06:05:00-05:00","content_markdown":"Summary"}))
        self.assertEqual(inspect(self.root,self.now)["reports"]["morning"]["status"],"missing_after_cutoff")
if __name__=="__main__":unittest.main()
