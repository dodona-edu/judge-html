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
        # incorrect tag closing test
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

