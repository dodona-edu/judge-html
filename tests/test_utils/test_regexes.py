import unittest

from utils import regexes


class TestRegexes(unittest.TestCase):
    def test_doctype(self):
        has_doctype = regexes.has_leading_doctype

        self.assertTrue(has_doctype("<!-- Comment -->\n<!DOCTYPE HTML>\n"))
        self.assertTrue(has_doctype("<!-- https:// something comment -->\n\n<!-- more comments --><!DOCTYPE HTML>\n"))
        self.assertTrue(has_doctype("<!DOCTYPE HTML>\n<html..."))
        self.assertTrue(
            has_doctype("""
        <!--
            multiline comment
        --><!--another comment with an > inside of it -->
        <!--comment--><!doctype html><html></html>
        """)
        )
        self.assertFalse(has_doctype("<html lang='en'></html>"))
