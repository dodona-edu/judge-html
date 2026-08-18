import re
import unittest

from dodona.translator import Translator
from tests.helpers import UnitTestSuite, html_loader
from validators.checks import BoilerplateTestSuite, ChecklistItem, TestSuite


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

    def test_contains_css_with_invalid_css(self):
        valid_suite = UnitTestSuite("css_1")
        self.assertTrue(valid_suite.check(valid_suite.contains_css("p", "color", "gold")))

        # A student typo in the CSS leaves _css_validator as None, and contains_css used to
        # dereference it anyway. Fail the check instead, the same way the @css_check
        # decorator does for the element-level Element.has_styling
        invalid_content = """
                  <html>
                      <head>
                          <style>
                              a ;:{s :}
                          </style>
                      </head>
                      <body><a href="#">link</a></body>
                  </html>
                  """
        invalid_suite = TestSuite("", invalid_content)

        self.assertIsNone(invalid_suite._css_validator)
        self.assertFalse(invalid_suite.contains_css("a", "color").callback(invalid_suite._bs))

    def test_check_minimal_on_bare_boilerplate_suite(self):
        # BoilerplateTestSuite and its check_minimal argument are both part of checks.pyi, so
        # a bare one has to work too, without an HtmlSuite/CssSuite subclass filling in the
        # default checks & translations. _has_minimal_template() runs outside the try/except
        # in evaluate(), so this used to take the entire judge down instead of failing a check
        suite = BoilerplateTestSuite("TEST", html_loader("test_1"), check_minimal=True)

        self.assertEqual(suite.evaluate(Translator(Translator.Language.EN)), 0)

        self.assertEqual(len(suite.checklist), 1)
        self.assertEqual(suite.translations["en"], ["The solution contains the minimal required HTML code."])
        self.assertEqual(suite.translations["nl"], ["De oplossing bevat de minimale vereiste HTML-code."])
