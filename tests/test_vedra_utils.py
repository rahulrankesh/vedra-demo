import unittest
from vedra_utils import normalise_video_result, safe_https_url

class VedraUtilsTests(unittest.TestCase):
    def test_accepts_https_urls(self):
        self.assertEqual(safe_https_url("https://example.com/a"), "https://example.com/a")
    def test_rejects_unsafe_or_invalid_urls(self):
        self.assertIsNone(safe_https_url("javascript:alert(1)"))
        self.assertIsNone(safe_https_url("http://example.com"))
        self.assertIsNone(safe_https_url(None))
    def test_normalises_dictionary_video(self):
        result = normalise_video_result({
            "title": "Demo", "link": "https://example.com/video",
            "thumbnail": "https://example.com/thumb.jpg",
            "channel": {"name": "Example Channel"},
        })
        self.assertEqual(result["title"], "Demo")
        self.assertEqual(result["channel"], "Example Channel")
    def test_normalises_string_video(self):
        result = normalise_video_result("https://example.com/video")
        self.assertEqual(result["link"], "https://example.com/video")
    def test_rejects_invalid_video_shapes(self):
        self.assertIsNone(normalise_video_result({"title": "Missing link"}))
        self.assertIsNone(normalise_video_result(42))

if __name__ == "__main__":
    unittest.main()
