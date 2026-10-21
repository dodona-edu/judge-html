import unittest

from dodona.translator import Translator
from exceptions.structure_exceptions import NotTheSame
from validators.structure_validator import compare


class TestHtmlValidator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.translator = Translator(Translator.Language.EN)
        self.base = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Hogwarts Faculties</title>
</head>
<body>
<table>
    <caption>Hogwarts Faculties</caption>
    <tr>
        <th>Gryffindor</th>
        <th>Ravenclaw</th>
        <th>Hufflepuff</th>
        <th>Slytherin</th>
    </tr>
    <tr>
        <td>Hermione Granger</td>
        <td>Padma Patil</td>
        <td>Cedric Diggory</td>
        <td>Draco Malfoy</td>
    </tr>
    <tr>
        <td>Harry Potter</td>
        <td>Luna Lovegood</td>
        <td>Hannah Longbottom</td>
        <td>Pansy Parkinson</td>
    </tr>
    <tr>
        <td>Ronald Weasley</td>
        <td>Cho Chang</td>
        <td>Susan Bones</td>
        <td>Gregory Goyle</td>
    </tr>
</table>
</body>
</html>
"""

    def test_correct(self):
        compare(self.base, self.base, self.translator)

    def test_tags_differ(self):
        with self.assertRaises(NotTheSame):
            compare(self.base, self.base.replace("th>", "td>"), self.translator)

    def test_attributes_differ(self):
        with self.assertRaises(NotTheSame):
            compare(self.base, self.base.replace('lang="en"', 'lang="en" abc="d"'), self.translator, attributes=True)

    def test_minimal_attributes(self):
        with self.assertRaises(NotTheSame):
            compare(self.base, self.base.replace('charset="utf-8"', 'ab="c"'), self.translator, minimal_attributes=True)

    def test_content_differ(self):
        with self.assertRaises(NotTheSame):
            compare(self.base, self.base.replace("Gregory Goyle", "Harry Potter"), self.translator, contents=True)

    def test_children_differ(self):
        with self.assertRaises(NotTheSame):
            compare(self.base, self.base.replace("</table>", "</table><p>BOE</p>"), self.translator, contents=True)

    def test_empty_sub(self):
        with self.assertRaises(NotTheSame):
            compare(self.base, "        ", self.translator)


class TestTailComparison(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.translator = Translator(Translator.Language.EN)

    def compare(self, solution: str, submission: str):
        compare(solution, submission, self.translator, contents=True)

    # RULE-015 (owner's note): contents=True also compares the text after an inline element
    def test_tail_after_inline_element_differs(self):
        with self.assertRaises(NotTheSame):
            self.compare("<p>Hi <b>x</b> there</p>", "<p>Hi <b>x</b> WRONG</p>")

    # RULE-015 (owner's note): contents=True also compares the text between two inline elements
    def test_tail_between_inline_elements_differs(self):
        with self.assertRaises(NotTheSame):
            self.compare("<p>a <b>x</b> middle <i>y</i></p>", "<p>a <b>x</b> nonsense <i>y</i></p>")

    # RULE-015 (owner's note): contents=True also compares body text after a block element
    def test_tail_after_block_element_differs(self):
        solution = "<html><body><h1>T</h1>Some body text</body></html>"
        with self.assertRaises(NotTheSame):
            self.compare(solution, solution.replace("Some body", "Other"))

    def test_dummy_tail_matches_any_text(self):
        self.compare("<p>Hi <b>x</b> DUMMY</p>", "<p>Hi <b>x</b> anything</p>")

    def test_whitespace_only_tail_difference_is_ignored(self):
        self.compare("<p>Hi <b>x</b>   there</p>", "<p>Hi <b>x</b> there</p>")


class TestDummyAttributes(unittest.TestCase):
    def setUp(self):
        self.translator = Translator(Translator.Language.EN)
        self.solution = '<p><a href="DUMMY" class="x">l</a></p>'

    def test_dummy_attribute_accepts_any_value(self):
        compare(self.solution, '<p><a href="https://example.com" class="x">l</a></p>', self.translator, attributes=True)

    def test_missing_dummy_attribute_fails(self):
        with self.assertRaises(NotTheSame) as ctx:
            compare(self.solution, '<p><a class="x">l</a></p>', self.translator, minimal_attributes=True)
        self.assertEqual(ctx.exception.msg, self.translator.translate(Translator.Text.NOT_ALL_ATTRIBUTES_PRESENT))


class TestCommentComparison(unittest.TestCase):
    def setUp(self):
        self.translator = Translator(Translator.Language.EN)

    def compare(self, solution: str, submission: str):
        compare(solution, submission, self.translator, comments=True)

    def test_missing_comment_fails(self):
        with self.assertRaises(NotTheSame) as ctx:
            self.compare("<div><!-- note --><p>a</p></div>", "<div><p>a</p><p>b</p></div>")
        self.assertEqual(ctx.exception.msg, self.translator.translate(Translator.Text.EXPECTED_COMMENT))

    def test_different_comment_text_fails(self):
        with self.assertRaises(NotTheSame) as ctx:
            self.compare("<div><!-- note --><p>a</p></div>", "<div><!-- other --><p>a</p></div>")
        self.assertEqual(ctx.exception.msg, self.translator.translate(Translator.Text.COMMENT_CORRECT_TEXT))

    def test_same_comment_text_passes(self):
        self.compare("<div><!-- Note --><p>a</p></div>", "<div><!--  note  --><p>a</p></div>")


class TestStyleComparison(unittest.TestCase):
    def setUp(self):
        self.translator = Translator(Translator.Language.EN)

    def page(self, rules: str) -> str:
        return f"<html><head><style>{rules}</style></head><body><p>a</p></body></html>"

    def test_missing_style_key_fails(self):
        with self.assertRaises(NotTheSame) as ctx:
            compare(self.page("p { color: red; margin: 0 }"), self.page("p { color: red }"), self.translator)
        self.assertEqual(ctx.exception.msg, self.translator.translate(Translator.Text.STYLES_DIFFER, tag="p"))

    def test_different_style_value_fails(self):
        with self.assertRaises(NotTheSame) as ctx:
            compare(self.page("p { margin: 0 }"), self.page("p { margin: 5px }"), self.translator)
        self.assertEqual(ctx.exception.msg, self.translator.translate(Translator.Text.STYLES_DIFFER, tag="p"))

    def test_different_color_value_fails(self):
        with self.assertRaises(NotTheSame):
            compare(self.page("p { color: red }"), self.page("p { color: blue }"), self.translator)

    def test_same_color_written_differently_passes(self):
        compare(self.page("p { color: red }"), self.page("p { color: #ff0000 }"), self.translator)
