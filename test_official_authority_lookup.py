import unittest
from official_authority_lookup import authority_targets,review_indexes

class OfficialIndexLookupTests(unittest.TestCase):
    def test_scotus_ruling_targets_official_opinions_and_orders(self):
        urls=[u for _,u in authority_targets({"title":"Supreme Court issues ruling in new case"})]
        self.assertTrue(any("supremecourt.gov/opinions" in u for u in urls))
        self.assertTrue(any("supremecourt.gov/orders" in u for u in urls))
    def test_texas_bill_targets_official_legislature(self):
        urls=[u for _,u in authority_targets({"title":"Texas lawmakers passed HB 123","jurisdiction":"texas"})]
        self.assertIn("https://capitol.texas.gov/",urls)
    def test_index_presence_cannot_certify_claim(self):
        def capturer(url):
            return {"content":"Bill HB 123 introduced yesterday","retrieved_at":"2026-10-17T12:00:00+00:00"}
        checks=review_indexes({"title":"Texas lawmakers passed HB 123","jurisdiction":"texas"},capturer=capturer)
        self.assertEqual(checks[0]["status"],"retrieved")
        self.assertFalse(checks[0]["claim_verified"])
    def test_official_numeric_match_is_only_narrow_support(self):
        def capture(url):
            return {"content":"Freddie Mac Oct 15 average 30-year fixed rate 7.40%.","retrieved_at":"2026-10-17T16:00:00+00:00"}
        checks=review_indexes({"title":"Freddie Mac rate 7.4%","jurisdiction":"national"},capturer=capture)
        self.assertEqual(len(checks),1)
        self.assertIn("7.4%",checks[0]["finding"])
        self.assertFalse(checks[0]["claim_verified"])
    def test_unavailable_is_different_from_unchecked(self):
        def fail(url):raise TimeoutError("timed out")
        checks=review_indexes({"title":"Supreme Court ruled on a dispute"},capturer=fail)
        self.assertTrue(checks)
        self.assertTrue(all(x["status"]=="unavailable" for x in checks))
        self.assertTrue(all("TimeoutError" in x["finding"] for x in checks))
if __name__=="__main__":unittest.main()
