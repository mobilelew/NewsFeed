import json,pathlib,tempfile,unittest
from acceptance_check import audit
class AcceptanceTests(unittest.TestCase):
    def test_empty_repository_not_success(self):
        with tempfile.TemporaryDirectory() as p:
            result=audit(pathlib.Path(p))
            self.assertFalse(result["all_accepted"])
            self.assertFalse(result["acceptance"]["same_day_morning_evening_comparison"])
    def test_discovery_does_not_satisfy_acceptance(self):
        with tempfile.TemporaryDirectory() as p:
            root=pathlib.Path(p)
            (root/"briefing.json").write_text(json.dumps({"status":"unpublished","headlines":[]}))
            self.assertFalse(audit(root)["acceptance"]["claim_authentication"])
    def test_unsubstantiated_headline_is_not_full_authentication(self):
        with tempfile.TemporaryDirectory() as p:
            root=pathlib.Path(p)
            (root/"briefing.json").write_text(json.dumps({"status":"published",
                "headlines":[{"title":"Test","category":"economy","jurisdiction":"federal",
                "evidence":[{"url":"https://www.bls.gov/"}]}]}))
            self.assertFalse(audit(root)["acceptance"]["claim_authentication"])
if __name__=="__main__":unittest.main()
