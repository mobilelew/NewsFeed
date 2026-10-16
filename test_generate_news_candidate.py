"""Offline tests for API report decoding; do not spend API credits."""
import json, unittest
from generate_news_candidate import extract

class CandidateTests(unittest.TestCase):
    def test_response_text_parses(self):
        source={"output":[{"content":[{"type":"output_text","text":'{"headlines": []}'}]}]}
        self.assertEqual(extract(source),{"headlines":[]})
    def test_missing_output_fails(self):
        with self.assertRaises(ValueError): extract({"output":[]})
    def test_invalid_json_fails(self):
        with self.assertRaises(json.JSONDecodeError):
            extract({"output":[{"content":[{"type":"output_text","text":"not json"}]}]})

if __name__=="__main__": unittest.main()
