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


class TestDoubleCharErrors(unittest.TestCase):
    """Characterizes which errors are reported, and where (line and position are 0-based)"""

    def errors(self, text: str) -> list[tuple[str, int, int]]:
        validator = DoubleCharsValidator(Translator(Translator.Language.EN))
        try:
            validator.validate_content(text)
        except MultipleMissingCharsError as e:
            return [(type(x).__name__, x.line, x.pos) for x in e.exceptions]
        return []

    def test_balanced(self):
        self.assertEqual([], self.errors("(a)[b]{c}"))
        self.assertEqual([], self.errors("{[(x)]}"))
        self.assertEqual([], self.errors("<p>it's (fine)</p>"))

    def test_missing_closing_round(self):
        self.assertEqual([("MissingClosingCharError", 0, 0)], self.errors("(a[b]"))

    def test_missing_opening_square(self):
        self.assertEqual([("MissingOpeningCharError", 0, 1)], self.errors("a]b"))

    def test_missing_opening_on_later_line(self):
        self.assertEqual([("MissingOpeningCharError", 1, 0)], self.errors("a\n]"))

    def test_nested_mix_missing_closing(self):
        self.assertEqual([("MissingClosingCharError", 0, 7)], self.errors("{[(x)]}("))

    def test_interleaved_pairs(self):
        # errors are reported in the order they are found: the stack is unwound last-in first
        self.assertEqual(
            [
                ("MissingOpeningCharError", 0, 3),
                ("MissingOpeningCharError", 0, 2),
                ("MissingClosingCharError", 0, 1),
                ("MissingClosingCharError", 0, 0),
            ],
            self.errors("([)]"),
        )

    def test_unterminated_quote(self):
        # pins today's behaviour: an unterminated quote is reported as a missing opening character
        self.assertEqual([("MissingOpeningCharError", 0, 0)], self.errors("'abc"))
        self.assertEqual([("MissingOpeningCharError", 0, 2)], self.errors('x "y'))

    def test_run_of_opening_chars(self):
        self.assertEqual([("MissingClosingCharError", 0, pos) for pos in (4, 3, 2, 1, 0)], self.errors("((((("))
