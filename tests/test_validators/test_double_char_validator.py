import unittest
from validators.double_chars_validator import DoubleCharsValidator
from exceptions.double_char_exceptions import MissingOpeningCharError, MissingClosingCharError, MultipleMissingCharsError


class TestHtmlValidator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = DoubleCharsValidator()
        self.all_opening = self.validator.opening
        self.all_closing = self.validator.closing
        self.all_combined = [f"{x[0]}{x[1]}" for x in zip(self.all_opening, self.all_closing)]

    def run_correct(self, xs:[str]):
        for x in xs:
            self.validator.validate_content(x)

    def run_incorrect(self, xs:[str]):
        for x in xs:
            with self.assertRaises(MultipleMissingCharsError):
                self.validator.validate_content(x)

    def test_missing_opening(self):
        # correct
        self.run_correct(self.all_combined)
        # incorrect
        self.run_incorrect(self.all_closing)

    def test_missing_closing(self):
        # correct
        self.run_correct(self.all_combined)
        # incorrect
        self.run_incorrect(self.all_opening)

    def test_nested(self):
        # correct
        self.run_correct([
            """(<> '' "")<''>{[]}"""
        ])
        # incorrect
        self.run_incorrect([
            """<<<(((((((>>>""",
            """)>())))))""",
        ])
