from utils import regexes
import unittest
import re


class TestRegexes(unittest.TestCase):
    def test_doctype(self):
        regex = re.compile(regexes.doctype_re.pattern, regexes.doctype_re.flags)

        self.assertIsNotNone(regex.search("<!-- Comment -->\n<!DOCTYPE HTML>\n"))
        self.assertIsNotNone(regex.search("<!-- https:// something comment -->\n\n<!-- more comments --><!DOCTYPE HTML>\n"))
        self.assertIsNotNone(regex.search("<!DOCTYPE HTML>\n<html..."))
        self.assertIsNone(regex.search("<html lang='en'></html>"))
