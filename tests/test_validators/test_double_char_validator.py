import unittest

from dodona.translator import Translator
from validators.double_chars_validator import DoubleCharsValidator
from exceptions.double_char_exceptions import MultipleMissingCharsError


class TestDoubleCharValidator(unittest.TestCase):
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
            "'test''",
            ")((",
            "} test {",
            "{ { test } } } { }",
            "()}}}",
            "({}))",
            "{([})}",
            "][[][[]]][]]][[[[]",
            "))",
            """
              width: 500px;
              font-size: 25px;
            }
            """,
            """
            p
              width: 500px;
              font-size: 25px;
            }
            """
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
            """<meta http-equiv="Content-Type" content="text/html; charset=utf-8">""",
            "<html>  >  </html>",
            "<html>head><meta charset='UTF-8'></head></html>"
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
            "((",
            "((((",
            "('')(",
            "{{()}",
            "<html><</html>",
            "<html><head<meta charset='UTF-8'</head></html>"
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
            """<body><h1>)}]"({['"</h1></body>""",
            """
            <!--
            Or you can
            comment out
            a large number of -> lines.
            -->
            """,
            """
            <!--
            function displayMsg) {
              alert"Hello World!")
            
            //-->
            """,
            """<body><h1>Check if brackets/quotes open and close (`(`, '&lt;', `{`, `[`, `'`, `"`)<h1></body>""",
            """<style>
                .chat > div {
                background-color: black;
                padding: 10px;
                }
            </style>
            """
        ])

    def test_value(self):
        # correct
        self.run_correct([
            """<html lang='bi"boe(ba'>""",
            """<html lang='bi"boe)ba'>"""
        ])
