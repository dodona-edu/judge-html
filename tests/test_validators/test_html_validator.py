import unittest
from validators.html_validator import HtmlValidator
from exceptions.htmlExceptions import MissingClosingTagError, InvalidTagError, UnexpectedTagError, MissingRequiredAttributeError, Warnings


class TestHtmlValidator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = HtmlValidator(nesting=False)

    def test_missing_closing_tag(self):
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
        # correct attribute test
        self.validator.validate_content("<html lang='en'></html>")
        # there is no incorrect attribute checking

    def test_missing_required_attribute(self):
        # correct attributes test
        self.validator.validate_content("<img src='' alt='' />")
        pass
        # incorrect (missing) required attributes test
        with self.assertRaises(MissingRequiredAttributeError):
            self.validator.validate_content("<img alt=''/>")
        with self.assertRaises(MissingRequiredAttributeError):
            self.validator.validate_content("<img alt=''/>")
        with self.assertRaises(MissingRequiredAttributeError):
            self.validator.validate_content("<body><img alt=''/></body>")

    def test_missing_recommended_attribute(self):
        # correct recommended attribute test
        self.validator.validate_content("<html lang='en'></html>")
        # incorrect (missing) recommended attribute test
        with self.assertRaises(Warnings):  # throws a MissingRecommendedAttributeError but it is collected as Warnings
            self.validator.validate_content("<html></html>")
        with self.assertRaises(Warnings):
            self.validator.validate_content("<html><html><html></html></html></html>")

    def test_nesting(self):
        self.validator.set_check_nesting(True)
        # correct nesting
        self.validator.validate_content("<html lang=''><table><caption></caption><tr><td></td></tr></table></html>")
        # incorrect nesting
        with self.assertRaises(UnexpectedTagError):
            self.validator.validate_content("<body/>")
            with self.assertRaises(UnexpectedTagError):
                self.validator.validate_content("<html lang=''><html lang=''></html></html>")

