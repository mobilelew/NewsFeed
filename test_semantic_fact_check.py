import unittest
from semantic_fact_check import validate
class SemanticVerifierTests(unittest.TestCase):
    def test_validates_known_claims_and_downgrades_bad_status(self):
        titles=["Claim A"]
        data={"findings":[{"title":"Claim A","status":"Something","concise_conclusion":"x","authority_checks":[],"independent_checks":[]}]}
        out=validate(data,titles)
        self.assertEqual(out[0]["status"],"Unresolved")
    def test_missing_claim_is_unresolved(self):
        out=validate({"findings":[]},["Claim A"])
        self.assertEqual(out[0]["status"],"Unresolved")
    def test_rejects_non_https_sources(self):
        data={"findings":[{"title":"Claim A","status":"Verified","authority_checks":[{"source":"x","url":"http://example.com","what_checked":"a","what_found":"b"}],"independent_checks":[]}]}
        out=validate(data,["Claim A"])
        self.assertEqual(out[0]["authority_checks"],[])
if __name__=="__main__":unittest.main()
