"""Verify intended News Reader discovery lanes exist without fetching live news."""
import unittest
import build_feed
class CoverageTests(unittest.TestCase):
    def test_priority_states_and_household_sectors(self):
        required={"TEXAS","ARKANSAS","OKLAHOMA","U.S. POLICY",
                  "CIVIL RIGHTS","ECONOMY","HOUSING","CRYPTO",
                  "BEEF","CHICKEN","TURKEY","AGRICULTURE",
                  "AI","DATA CENTERS","TECH & SECURITY"}
        self.assertTrue(required.issubset(build_feed.SOURCES),
                        required-set(build_feed.SOURCES))
        self.assertTrue(required.issubset(build_feed.KEYWORDS))
        for category in required:
            self.assertTrue(build_feed.SOURCES[category])
            self.assertTrue(build_feed.KEYWORDS[category])
    def test_no_discovery_is_promoted_to_verified(self):
        # Source discovery is always a separate evidentiary class.
        self.assertNotIn("Verified",build_feed.ALLOWED_STATUSES)
if __name__=="__main__":unittest.main()
