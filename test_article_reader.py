import io, unittest
from article_reader import article_extract,safe_public_https
class Response:
    def __init__(self,raw):self.raw=io.BytesIO(raw);self.headers={"Content-Type":"text/html"}
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,n):return self.raw.read(n)
    def geturl(self):return "https://publisher.example.com/story"
class Opener:
    def open(self,req,timeout):
        return Response(b"<html><nav><p>Ignore navigation paragraph with enough text to qualify for inclusion blah blah blah blah.</p></nav><article><p>The authority published a detailed order on Thursday. The parties may appeal this ruling and implementation remains subject to later court decisions.</p></article></html>")
class ReaderTests(unittest.TestCase):
    def test_private_or_google_news_refused(self):
        for link in ("http://publisher.example.com/","https://127.0.0.1/", "https://news.google.com/rss/articles/123","https://localhost/"):
            self.assertFalse(safe_public_https(link))
    def test_publisher_text_marked_excerpt(self):
        result=article_extract("https://publisher.example.com/story",Opener())
        self.assertIsNotNone(result)
        self.assertEqual(result["summary_provenance"],"publisher_article_excerpt")
        self.assertIn("authority published",result["summary"])
        self.assertNotIn("Ignore navigation",result["summary"])
if __name__=="__main__":unittest.main()
