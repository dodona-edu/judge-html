import re
import time
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

    def has_doctype(self, content: str) -> bool:
        suite = TestSuite("", content)
        return suite.has_doctype().callback(suite._bs)

    def test_doctype_after_leading_comments(self):
        self.assertTrue(self.has_doctype("<!-- a -->\n<!doctype html>\n<html></html>"))
        self.assertTrue(self.has_doctype("<!-- a --><!-- b -->\n\n<!DOCTYPE HTML>"))

    def test_doctype_leading_comment_run(self):
        # a short run of comments stays fast
        self.assertTrue(self.has_doctype("<!-- c -->\n" * 10 + "<!DOCTYPE html>"))
        self.assertFalse(self.has_doctype("<!-- c -->\n" * 10 + "<html></html>"))

    def test_doctype_many_leading_comments_is_fast(self):
        start = time.perf_counter()
        self.assertFalse(self.has_doctype("<!-- c -->" * 40 + "<html></html>"))
        self.assertLess(time.perf_counter() - start, 1)

    def test_no_doctype(self):
        self.assertFalse(self.has_doctype("<html><body></body></html>"))
        self.assertFalse(self.has_doctype(""))

    def test_doctype_case_variants(self):
        for variant in ("<!DOCTYPE html>", "<!doctype html>", "<!DocType HTML>", "<!Doctype Html>"):
            with self.subTest(variant=variant):
                self.assertTrue(self.has_doctype(variant))

    def test_doctype_whitespace_variants(self):
        self.assertTrue(self.has_doctype("  \n\t<!doctype html>"))
        # exactly one space between "doctype" and "html" is accepted
        self.assertFalse(self.has_doctype("<!doctype  html>"))
        self.assertFalse(self.has_doctype("<!doctype\thtml>"))

    def test_doctype_prefix_only(self):
        # the pattern only looks at the start of the declaration, what follows is not checked
        self.assertTrue(self.has_doctype('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">'))
        self.assertTrue(self.has_doctype("<!doctype htmlfoo>"))

    def test_doctype_on_later_line_is_accepted(self):
        # pins today's behaviour: the pattern is multiline, so any line may start with the doctype
        self.assertTrue(self.has_doctype("<html>\n<!DOCTYPE html>\n</html>"))
        self.assertTrue(self.has_doctype("text\n<!DOCTYPE html>"))

    def test_doctype_after_text_on_same_line_is_rejected(self):
        self.assertFalse(self.has_doctype("<html><!DOCTYPE html>"))

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

    @staticmethod
    def _css_suite(css: str) -> TestSuite:
        return TestSuite("", f"<html><head><style>{css}</style></head><body><nav><a>x</a></nav></body></html>")

    def test_contains_css_descendant_selector(self):
        suite = self._css_suite("nav a { color: red }")
        self.assertTrue(suite.contains_css("nav a", "color", "red").callback(suite._bs))
        self.assertTrue(suite.contains_css("nav   a", "color").callback(suite._bs))
        self.assertFalse(suite.contains_css("nava", "color").callback(suite._bs))
        self.assertFalse(suite.contains_css("nav", "color").callback(suite._bs))

    def test_contains_css_combinator_spacing(self):
        for css_selector in ("ul > li", "ul>li", " ul >li "):
            for stylesheet_selector in ("ul > li", "ul>li"):
                suite = self._css_suite(f"{stylesheet_selector} {{ color: red }}")
                self.assertTrue(suite.contains_css(css_selector, "color").callback(suite._bs))

        suite = self._css_suite("h1 + p, h1 ~ ul { color: red }")
        self.assertTrue(suite.contains_css("h1+p", "color").callback(suite._bs))
        self.assertTrue(suite.contains_css("h1 ~ ul", "color").callback(suite._bs))

    def test_contains_css_multiline_selector(self):
        suite = self._css_suite("nav\n  a { color: red }")
        self.assertTrue(suite.contains_css("nav a", "color").callback(suite._bs))
        self.assertTrue(suite.contains_css("nav\na", "color").callback(suite._bs))

    def test_contains_css_selector_case(self):
        suite = self._css_suite("#Main { color: red }")
        self.assertTrue(suite.contains_css("#Main", "color").callback(suite._bs))
        self.assertTrue(suite.contains_css("#main", "color").callback(suite._bs))

    def test_contains_css_property_case(self):
        suite = self._css_suite("p { Color: red }")
        self.assertTrue(suite.contains_css("p", "color", "red").callback(suite._bs))
        self.assertTrue(suite.contains_css("p", "COLOR", "red").callback(suite._bs))

    def test_contains_css_duplicate_declaration_later_wins(self):
        suite = self._css_suite("p { color: red; color: blue } p { color: green }")
        self.assertTrue(suite.contains_css("p", "color", "green").callback(suite._bs))
        self.assertFalse(suite.contains_css("p", "color", "red").callback(suite._bs))

        suite = self._css_suite("p { color: red; color: blue }")
        self.assertTrue(suite.contains_css("p", "color", "blue").callback(suite._bs))
        self.assertFalse(suite.contains_css("p", "color", "red").callback(suite._bs))

    def test_contains_css_attribute_string_whitespace_is_kept(self):
        for quote in ('"', "'"):
            suite = self._css_suite(f"[title={quote}a  b{quote}] {{ color: red }}")
            self.assertTrue(suite.contains_css('[title="a  b"]', "color").callback(suite._bs))
            self.assertTrue(suite.contains_css("[title='a  b']", "color").callback(suite._bs))
            self.assertFalse(suite.contains_css('[title="a b"]', "color").callback(suite._bs))

    def test_contains_css_invalid_or_grouped_query_fails(self):
        suite = self._css_suite("p, a { color: red } p { color: red }")
        self.assertFalse(suite.contains_css("p >", "color").callback(suite._bs))
        self.assertFalse(suite.contains_css("p, a", "color").callback(suite._bs))

    def test_contains_css_simple_selectors(self):
        suite = self._css_suite("p { color: red } .box { margin: 0 } #yellow:hover { color: yellow }")
        self.assertTrue(suite.contains_css("p", "color", "red").callback(suite._bs))
        self.assertTrue(suite.contains_css(".box", "margin", "0").callback(suite._bs))
        self.assertTrue(suite.contains_css("#yellow:hover", "color", "yellow").callback(suite._bs))
        self.assertFalse(suite.contains_css(".box", "color").callback(suite._bs))

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
