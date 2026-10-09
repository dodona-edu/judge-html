import unittest

from dodona.translator import Translator
from exceptions.double_char_exceptions import MultipleMissingCharsError
from validators.double_chars_validator import DoubleCharsValidator


class TestDoubleCharValidator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = DoubleCharsValidator(Translator(Translator.Language.EN))

    def run_correct(self, xs: list[str]):
        for x in xs:
            self.validator.validate_content(x)

    def run_incorrect(self, xs: list[str]):
        for x in xs:
            with self.assertRaises(MultipleMissingCharsError):
                self.validator.validate_content(x)

    def test_missing_opening(self):
        # incorrect
        self.run_incorrect(
            [
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
            """,
            ]
        )
        # correct
        self.run_correct(
            [
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
                "<html>head><meta charset='UTF-8'></head></html>",
            ]
        )

    def test_nothing(self):
        self.run_correct([""])

    def test_missing_closing(self):
        # incorrect
        self.run_incorrect(
            [
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
                "<html><head<meta charset='UTF-8'</head></html>",
            ]
        )

    def test_nested(self):
        # correct
        self.run_correct(
            [
                """<""> ' IGNORED " <''> IGNORED][)}""",
                """<>IGNORED())))))<>""",
                "{([{{([{}()[]])}}({([{{([{{([{{([{}()[]])}}({([{{([{}()[]])}}()[]])})[{([{{([{}()[]])}}({([{{([{}()[]])}}()[]])})[]])}]])}}()[]])}}()[]])})[{([{{([{}()[]])}}({([{{([{}()[]])}}()[]])})[{([{{([{}()[]])}}({([{{([{}()[]])}}()[]])})[{([{{([{}()[]])}}({([{{([{}()[]])}}()[]])})[]])}]])}]])}]])}",
            ]
        )
        # incorrect
        self.run_incorrect(["""<<<(((((((>>>""", """(<)""", """(>)"""])

    def test_content(self):
        # correct
        self.run_correct(
            [
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
            """,
            ]
        )

    def test_value(self):
        # correct
        self.run_correct(["""<html lang='bi"boe(ba'>""", """<html lang='bi"boe)ba'>"""])

    def get_error(self, text: str) -> MultipleMissingCharsError:
        with self.assertRaises(MultipleMissingCharsError) as cm:
            self.validator.validate_content(text)
        return cm.exception

    def test_line_numbers(self):
        # regression test for #250: line numbers were off by one
        # (stored 0-based, displayed 1-based)
        text = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Websites</title>
</head>
<body>
<ul>
    <li> <a href="https://www.ugent.be/we/nl/" > Faculteit Wetenschappen (FWE) </a> </li>
    <li> <a href="https://www.ugent.be/ea/nl/" > Faculteit Ingenieurswetenschappen en Architectuur (FEA )</a</li>
    <li> <a href="https://www.ugent.be/bw/nl/" > Faculteit Bio-ingenieurswetenschappen (FBW) </a></li>
</ul>
</body>
</html>"""
        error = self.get_error(text)
        self.assertEqual(1, len(error.exceptions))
        self.assertEqual(9, error.exceptions[0].line)  # 0-based
        self.assertIn("at line 10 ", str(error.exceptions[0]))
        self.assertIn("at line 10 ", str(error))

    def test_line_number_first_line(self):
        # an error on the first line must still have a line number
        error = self.get_error("(\nok")
        self.assertEqual(0, error.exceptions[0].line)
        self.assertIn("at line 1 ", str(error.exceptions[0]))
        self.assertIn("at line 1 ", str(error))

    def test_line_number_later_line(self):
        error = self.get_error("ok\n\n  {\nok")
        self.assertEqual(2, error.exceptions[0].line)
        self.assertIn("at line 3 position 3", str(error.exceptions[0]))
