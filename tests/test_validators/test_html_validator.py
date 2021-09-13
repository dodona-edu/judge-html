import unittest

from dodona.translator import Translator
from validators.html_validator import HtmlValidator
from exceptions.html_exceptions import MissingClosingTagError, InvalidTagError, UnexpectedTagError, MissingRequiredAttributeError, Warnings


class TestHtmlValidator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = HtmlValidator(Translator(Translator.Language.EN))

    def setup(self, required, recommended, nesting):
        self.validator.set_check_required(required)
        self.validator.set_check_recommended(recommended)
        self.validator.set_check_nesting(nesting)

    def test_missing_closing_tag(self):
        self.setup(False, False, False)
        # correct tag closing test
        self.validator.validate_content("<div></div>")
        self.validator.validate_content("<body><div></div></body>")
        # incorrect tag closing tests
        with self.assertRaises(MissingClosingTagError):
            self.validator.validate_content("<body><div></div>")
        with self.assertRaises(MissingClosingTagError):
            self.validator.validate_content("<body><div></body>")
        # omittable tags (tags that don't need to be closed
        self.validator.validate_content("<base>")
        self.validator.validate_content("<meta>")
        self.validator.validate_content("<body><meta></body>")

    def test_invalid_tag(self):
        self.setup(False, False, False)
        # correct tag test
        self.validator.validate_content("<body></body>")
        # incorrect tag test
        with self.assertRaises(InvalidTagError):
            self.validator.validate_content("<jibberjabber></jibberjabber>")
        # script tag is also seen as an invalid tag
        with self.assertRaises(InvalidTagError):
            self.validator.validate_content("<script>")
        with self.assertRaises(InvalidTagError):
            self.validator.validate_content("<noscript>")

    def test_invalid_attribute(self):
        self.setup(True, True, False)
        # correct attribute test
        self.validator.validate_content("<html lang='en'></html>")
        # there is no incorrect attribute checking

    def test_missing_required_attribute(self):
        self.setup(True, False, False)
        # correct attributes test
        self.validator.validate_content("<img src='' />")
        pass
        # incorrect (missing) required attributes test
        with self.assertRaises(MissingRequiredAttributeError):
            self.validator.validate_content("<img/>")
        with self.assertRaises(MissingRequiredAttributeError):
            self.validator.validate_content("<img/>")
        with self.assertRaises(MissingRequiredAttributeError):
            self.validator.validate_content("<body><img/></body>")

    def test_missing_recommended_attribute(self):
        self.setup(False, True, False)
        # correct recommended attribute test
        self.validator.validate_content("<html lang='en'></html>")
        # incorrect (missing) recommended attribute test
        with self.assertRaises(Warnings):  # throws a MissingRecommendedAttributeError but it is collected as Warnings
            self.validator.validate_content("<html></html>")
        with self.assertRaises(Warnings):
            self.validator.validate_content("<html><html><html></html></html></html>")

    def test_nesting(self):
        self.setup(False, False, True)
        # correct nesting (partial html is also valid, wrapping everything in <html> and <body> is not needed)
        self.validator.validate_content("<html><head/><body/></html>")
        #   partial html
        self.validator.validate_content("<head/><body/>")
        #   partial html with nesting
        self.validator.validate_content("<table><tr><td></td></tr></table>")
        #   nesting with multiple elements that require the same parent
        self.validator.validate_content("<html><table><caption></caption><tr><td></td></tr></table></html>")
        #   partial html
        self.validator.validate_content("<tr/>")
        # incorrect nesting
        with self.assertRaises(UnexpectedTagError):
            self.validator.validate_content("<body><html/></body>")
        with self.assertRaises(UnexpectedTagError):
            self.validator.validate_content("<html><html></html></html>")
