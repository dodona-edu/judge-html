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
            ")",
            ">",
            "}",
            "]",
            "'",
            '"',
            "<html>></html>",
            "'test''",
            ")((",
            # "} test {",  # TODO
            "{ { test } } } { }",
            "()}}}",
            "({}))",
            "{([})}",
            # "][[][[]]][]]][[[[]",  # TODO
            # "))",  # TODO
            "<html>head><meta charset='UTF-8'></head></html>"
        ])
        # correct
        self.run_correct([
            "<>",
            "<html><head><meta charset='UTF-8'></head></html>",
            "''",
            "()",
            "{([])}",
            "{()}[[{}]]",
            "{}()[]",
            "[[[[]][]]][[][]]",
            "({(test)})",
            """<meta http-equiv="Content-Type" content="text/html; charset=utf-8">"""
        ])

    def test_nothing(self):
        self.run_correct([
            ""
        ])

    def test_missing_closing(self):
        # incorrect
        self.run_incorrect([
            "(",
            "<",
            "{",
            "[",
            "'",
            '"',
            "{ { }",
            # "((",  # TODO
            # "((((",  # TODO
            "('')(",
            "{{()}",
            "<html><</html>",
            # "<html><head<meta charset='UTF-8'</head></html>"  # TODO 2 >-symbols missing
        ])

    def test_nested(self):
        # correct
        self.run_correct([
            """<""> ' IGNORED " <''> IGNORED][)}""",
            """<>IGNORED())))))<>""",
            "{([{{([{}()[]])}}({([{{([{{([{{([{}()[]])}}({([{{([{}()[]])}}()[]])})[{([{{([{}()[]])}}({([{{([{}()[]])}}()[]])})[]])}]])}}()[]])}}()[]])})[{([{{([{}()[]])}}({([{{([{}()[]])}}()[]])})[{([{{([{}()[]])}}({([{{([{}()[]])}}()[]])})[{([{{([{}()[]])}}({([{{([{}()[]])}}()[]])})[]])}]])}]])}]])}"
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
            """<p>"</p>""",
            """<body><h1>What's On In Toronto (Canada)</h1></body>""",
            """<body><h1>)}]"({['"</h1></body>"""
            """<body><h1>Check if brackets/quotes open and close (`(`, '&lt;', `{`, `[`, `'`, `"`)<h1></body>"""
        ])

    def test_value(self):
        # correct
        self.run_correct([
            """<html lang='bi"boe(ba'>""",
            """<html lang='bi"boe)ba'>"""
        ])
