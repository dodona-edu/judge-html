import unittest
from utils import html_checks


class TestHTMLChecks(unittest.TestCase):
    def test_is_empty_document(self):
        self.assertTrue(html_checks.is_empty_document(""))
        self.assertTrue(html_checks.is_empty_document(" "))
        self.assertTrue(html_checks.is_empty_document("\t"))
        self.assertTrue(html_checks.is_empty_document("\n\n\n"))
        self.assertTrue(html_checks.is_empty_document("<!-- comment-->\n"))
        self.assertTrue(html_checks.is_empty_document("<!-- comment\n<html>\n</html> -->"))

        self.assertFalse(html_checks.is_empty_document("<html></html>"))
        self.assertFalse(html_checks.is_empty_document("  \n<html></html>\n   "))
        self.assertFalse(html_checks.is_empty_document("<!-- comment -->\n<html></html>"))
        self.assertFalse(html_checks.is_empty_document("<!-- comment\n<html>\n</html> --><body></body>"))
        self.assertFalse(html_checks.is_empty_document("<html> <!-- inline comment -->\n</html>"))
