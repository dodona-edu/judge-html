import re
import unittest
from tests.helpers import html_loader, UnitTestSuite
from validators.checks import TestSuite, ChecklistItem


class TestTestSuite(unittest.TestCase):
    def test_document_matches(self):
        file = html_loader("self_closing_tag")
        suite = TestSuite("", file)

        # Check that the document has a self-closing tag
        self.assertTrue(suite.document_matches(r"<[^>]+/>").callback(suite._bs))

        # Check that the document starts with "<!doctype"
        self.assertFalse(suite.document_matches(r"^<!doctype").callback(suite._bs))

        # Check that the document starts with "<!doctype", but with the IGNORECASE flag
        self.assertTrue(suite.document_matches(r"^<!doctype", re.IGNORECASE).callback(suite._bs))

    def test_doctype(self):
        suite = TestSuite("", "<!DOCTYPE HTML>")
        self.assertTrue(suite.has_doctype().callback(suite._bs))

        suite = TestSuite("", "<!DOCTYPE>")
        self.assertFalse(suite.has_doctype().callback(suite._bs))

        suite = TestSuite("", "<!DOCTYPE somethingelse>")
        self.assertFalse(suite.has_doctype().callback(suite._bs))

    def test_invalid_css(self):
        valid_suite = UnitTestSuite("css_1")
        self.assertIsNotNone(valid_suite._css_validator)
        self.assertTrue(valid_suite._css_validated)
        self.assertTrue(valid_suite.css_is_valid())

        invalid_content = """
                  <html>
                      <head>
                          <style>
                              a ;:{s :}
                          </style>
                      </head>
                  </html>
                  """
        invalid_suite = TestSuite("", invalid_content)

        self.assertIsNone(invalid_suite._css_validator)
        self.assertFalse(invalid_suite._css_validated)
        self.assertFalse(invalid_suite.css_is_valid())

    def test_add_item(self):
        suite = UnitTestSuite("test_1")
        self.assertEqual(len(suite.checklist), 0)

        item = ChecklistItem("message", suite.validate_html())
        suite.add_item(item)
        self.assertEqual(len(suite.checklist), 1)
        self.assertEqual(suite.checklist[0], item)

    def test_make_item(self):
        suite = UnitTestSuite("test_1")
        suite.make_item("message", suite.validate_html())
        self.assertEqual(len(suite.checklist), 1)
        self.assertEqual(suite.checklist[0].message, "message")
        self.assertEqual(len(suite.checklist[0]._checks), 1)

        suite.make_item("message2", suite.validate_html(), suite.validate_css())
        self.assertEqual(len(suite.checklist), 2)
        self.assertEqual(suite.checklist[1].message, "message2")
        self.assertEqual(len(suite.checklist[1]._checks), 2)
