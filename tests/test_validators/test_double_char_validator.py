import unittest

from dodona.translator import Translator
from validators.double_chars_validator import DoubleCharsValidator
from exceptions.double_char_exceptions import MultipleMissingCharsError


class TestHtmlValidator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = DoubleCharsValidator(Translator(Translator.Language.EN))

    def run_correct(self, xs: [str]):
        for x in xs:
            self.validator.validate_content(x)

    def run_incorrect(self, xs: [str]):
        for x in xs:
            with self.assertRaises(MultipleMissingCharsError):
                self.validator.validate_content(x)

    def test_missing_opening(self):
        # incorrect
        self.run_incorrect([
            ">",
            "<html>></html>",
            "'",
            ")"
        ])

    def test_missing_closing(self):
        # incorrect
        self.run_incorrect([
            "<",
            "<html><</html>"
        ])

    def test_nested(self):
        # correct
        self.run_correct([
            """<""> ' IGNORED " <''> IGNORED][)}""",
            """<>IGNORED())))))<>"""
        ])
        # incorrect
        self.run_incorrect([
            """<<<(((((((>>>""",
            """(<)""",
            """(>)"""
        ])

    def test_content(self):
        # correct
        self.run_correct([
            """<p>It's a red text — check it out!</p>""",
            """<body><h1>What's On In Toronto</h1></body>"""
        ])

    def test_value(self):
        # correct
        self.run_correct([
            """<html lang='bi"boe(ba'>""",
            """<html lang='bi"boe)ba'>"""
        ])