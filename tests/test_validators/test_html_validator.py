import unittest
from validators.html_validator import HtmlValidator
from exceptions.htmlExceptions import *


class TestHtmlValidator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = HtmlValidator()

    def test_missing_closing_tag(self):
        # correct tag closing test
        self.validator.validate_content("<div></div>")
        self.validator.validate_content("<body><div></div></body>")
        # incorrect tag closing tests
        with self.assertRaises(MissingClosingTagError):
            self.validator.validate_content("<body><div></div>")
        with self.assertRaises(MissingClosingTagError):
            self.validator.validate_content("<body><div></body>")

    def test_invalid_tag(self):
        # correct tag test
        self.validator.validate_content("<body></body>")
        # incorrect tag test
        with self.assertRaises(InvalidTagError):
            self.validator.validate_content("<jibberjabber></jibberjabber>")

    def test_invalid_attribute(self):
        # correct attribute test
        self.validator.validate_content("<html lang='en'></html>")
        # there is no incorrect attribute checking

    def test_missing_required_attribute(self):
        pass
        # no required arguments are set in the json yet

    def test_missing_recommended_attribute(self):
        # correct required attribute test
        self.validator.validate_content("<html lang='en'></html>")
        # incorrect (missing) required attribute test
        with self.assertRaises(Warnings):  # throws a MissingRecommendedAttributeError but it is collected as Warnings
            self.validator.validate_content("<html></html>")
        with self.assertRaises(Warnings):
            self.validator.validate_content("<html><html><html></html></html></html>")
