import unittest
from publisher_links import direct_publisher_url
class DirectPublisherTests(unittest.TestCase):
    def test_removes_tracking(self):
        self.assertEqual(direct_publisher_url("https://www.foxnews.com/politics/story?utm_source=google&fbclid=abc#comments"),"https://www.foxnews.com/politics/story")
    def test_preserves_nontracking_query(self):
        self.assertEqual(direct_publisher_url("https://www.nbcdfw.com/article/?id=12&utm_campaign=foo"),"https://www.nbcdfw.com/article/?id=12")
    def test_blocks_aggregators_and_affiliates(self):
        for url in ("https://news.google.com/rss/articles/abc","https://t.co/abc","https://bit.ly/abc","https://example.com/article?affiliate_id=abc","http://publisher.com/story"):
            self.assertIsNone(direct_publisher_url(url),url)
    def test_direct_publishers(self):
        self.assertIsNotNone(direct_publisher_url("https://fortworthreport.org/2026/10/16/article/"))
        self.assertIsNotNone(direct_publisher_url("https://www.kxan.com/news/local/austin/example/"))
if __name__=="__main__": unittest.main()
