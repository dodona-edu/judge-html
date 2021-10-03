import unittest

from dodona.translator import Translator
from validators.structure_validator import compare, NotTheSame


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
            compare(self.base, self.base.replace('Gregory Goyle', 'Harry Potter'), self.translator, contents=True)

    def test_children_differ(self):
        with self.assertRaises(NotTheSame):
            compare(self.base, self.base.replace('</table>', '</table><p>BOE</p>'), self.translator, contents=True)

    def test_empty_sub(self):
        with self.assertRaises(NotTheSame):
            compare(self.base, "        ", self.translator)
