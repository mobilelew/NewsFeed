import unittest
from compare_briefings import compare

class CompareReportsTests(unittest.TestCase):
    def setUp(self):
        self.m = {"report_type":"morning", "report_time":"2026-10-15T06:00:00-05:00", "headlines":[{"identifier":"HB123","summary":"Introduced","verification":"Legal Effect Unclear"}]}
        self.e = {"report_type":"evening", "report_time":"2026-10-15T20:00:00-05:00", "headlines":[{"identifier":"HB123","summary":"New filing","verification":"Legal Effect Unclear"},{"identifier":"SB456","summary":"Reported","verification":"Unverified"}]}
    def test_missing_morning(self):
        self.assertEqual(compare(None,self.e)["comparison_status"],"morning_unavailable")
    def test_same_day_text_diff(self):
        c=compare(self.m,self.e)
        self.assertEqual(c["comparison_status"],"direct_text_comparison")
        self.assertEqual(c["new_identifiers"],["sb456"])
        self.assertEqual(c["changed_text_identifiers"],["hb123"])
    def test_different_date_no_comparison(self):
        m=dict(self.m,report_time="2026-10-14T06:00:00-05:00")
        self.assertEqual(compare(m,self.e)["comparison_status"],"morning_unavailable")
    def test_no_real_world_change_assertion(self):
        self.assertIn("do not by themselves",compare(self.m,self.e)["summary"])

if __name__=="__main__":
    unittest.main()
