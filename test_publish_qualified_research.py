import copy,unittest
from publish_qualified_research import process
class QualifiedResearchTests(unittest.TestCase):
    def setUp(self):
        self.doc={"schema_version":1,"report_type":"evening","report_time":"2026-10-16T20:00:00-05:00",
        "headlines":[{"title":"Cited assertion","summary":"An outlet asserts a change.","jurisdiction":"federal",
        "claim_type":"attributed_claim","verification":"Verified","event_date":"2026-10-16",
        "source_checked_at":"2026-10-16T19:00:00-05:00","claim_evidence_note":"Provisional",
        "evidence":[{"type":"primary","description":"Authority page","url":"https://www.bls.gov/"}]}]}
    def test_verified_claim_demoted_without_source_entailment(self):
        doc=process(self.doc,{})
        self.assertEqual(doc["headlines"][0]["verification"],"Unverified")
        self.assertFalse(doc["independent_source_authentication"])
        self.assertTrue(doc["headlines"][0]["authority_confirmation"])
    def test_blank_attribution_fields_are_filled_without_promoting_claim(self):
        doc=copy.deepcopy(self.doc)
        doc["headlines"][0]["attribution"]=""
        doc["headlines"][0]["uncertainty"]=" "
        checked=process(doc,{})["headlines"][0]
        self.assertEqual(checked["verification"],"Unverified")
        self.assertTrue(checked["attribution"].strip())
        self.assertTrue(checked["uncertainty"].strip())
    def test_no_claims_rejected(self):
        self.doc["headlines"]=[]
        with self.assertRaises(ValueError):process(self.doc,{})
if __name__=="__main__":unittest.main()
