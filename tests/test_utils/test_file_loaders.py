import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from utils.file_loaders import html_loader


class TestFileLoaders(unittest.TestCase):
    CONTENT = "<p>Some content</p>"

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        file_path = Path(self.tmpdir.name) / "fragment.html"
        file_path.write_text(self.CONTENT)
        self.file_path = str(file_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_no_wrap_by_default(self):
        """Without any wrap_* kwarg, the content should be returned unchanged"""
        result = html_loader(self.file_path)
        self.assertEqual(result, self.CONTENT)

    def test_wrap_head(self):
        result = html_loader(self.file_path, wrap_head=True)

        # Properly closed, not doubled open
        self.assertIn("</head>", result)
        self.assertEqual(result.count("<head"), 1)

        soup = BeautifulSoup(result, "html.parser")
        head = soup.find("head")
        self.assertIsNotNone(head)
        self.assertIn(self.CONTENT, str(head))

    def test_wrap_body(self):
        result = html_loader(self.file_path, wrap_body=True)

        self.assertIn("</body>", result)
        self.assertEqual(result.count("<body"), 1)

        soup = BeautifulSoup(result, "html.parser")
        body = soup.find("body")
        self.assertIsNotNone(body)
        self.assertIn(self.CONTENT, str(body))

    def test_wrap_html(self):
        result = html_loader(self.file_path, wrap_html=True)

        self.assertIn("</html>", result)
        self.assertEqual(result.count("<html"), 1)

        soup = BeautifulSoup(result, "html.parser")
        html = soup.find("html")
        self.assertIsNotNone(html)
        self.assertIn(self.CONTENT, str(html))

    def test_wrap_all(self):
        """wrap_head, wrap_body and wrap_html combined should each close properly"""
        result = html_loader(self.file_path, wrap_head=True, wrap_body=True, wrap_html=True)

        self.assertIn("</head>", result)
        self.assertIn("</body>", result)
        self.assertIn("</html>", result)
        self.assertEqual(result.count("<head"), 1)
        self.assertEqual(result.count("<body"), 1)
        self.assertEqual(result.count("<html"), 1)

        soup = BeautifulSoup(result, "html.parser")
        html = soup.find("html")
        body = soup.find("body")
        head = soup.find("head")
        self.assertIsNotNone(html)
        self.assertIsNotNone(body)
        self.assertIsNotNone(head)

        # wrap_head is applied first, then wrap_body, then wrap_html, so the
        # nesting order (per the current implementation) is html > body > head
        self.assertIn(self.CONTENT, str(head))
        self.assertIn(str(head), str(body))
        self.assertIn(str(body), str(html))


if __name__ == "__main__":
    unittest.main()
