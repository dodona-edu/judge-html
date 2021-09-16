import unittest
from tests.helpers import html_loader, UnitTestSuite


class TestElement(unittest.TestCase):
    def test_exists(self):
        file = html_loader("test_1")
        suite = UnitTestSuite("", file)
        body_element = suite.element("body")

        self.assertTrue(suite.check(body_element.exists()))
        self.assertFalse(suite.check(body_element.get_child("body").exists()))

    def test_has_tag(self):
        file = html_loader("test_1")
        suite = UnitTestSuite("", file)
        body_element = suite.element("body")
        body_children = body_element.get_children(direct=True)

        self.assertTrue(suite.check(body_children[0].has_tag("div")))
        self.assertTrue(suite.check(body_children[-1].has_tag("img")))

    def test_has_content(self):
        file = html_loader("test_1")
        suite = UnitTestSuite("", file)
        paragraph = suite.element("p")

        self.assertTrue(suite.check(paragraph.has_content()))
        self.assertTrue(suite.check(paragraph.has_content("Some text.")))
        self.assertFalse(suite.check(paragraph.has_content("Other text")))

    def test_attribute_exists(self):
        file = html_loader("test_1")
        suite = UnitTestSuite("", file)
        body_element = suite.element("body")
        img_element = body_element.get_child("img")

        self.assertTrue(suite.check(img_element.attribute_exists("src")))
        self.assertFalse(suite.check(img_element.attribute_exists("width")))

    def test_attribute_contains(self):
        file = html_loader("test_1")
        suite = UnitTestSuite("", file)
        body_element = suite.element("body")
        img_element = body_element.get_child("img")

        self.assertTrue(suite.check(img_element.attribute_contains("src", "dodona")))
        self.assertTrue(suite.check(img_element.attribute_contains("src", "DODONA", case_insensitive=True)))
        self.assertFalse(suite.check(img_element.attribute_contains("src", "google.com")))

    def test_attribute_matches(self):
        file = html_loader("test_1")
        suite = UnitTestSuite("", file)
        body_element = suite.element("body")
        img_element = body_element.get_child("img")

        self.assertTrue(suite.check(img_element.attribute_matches("src", r"^https://.*dodona.ugent.be.*.png$")))
        self.assertFalse(suite.check(img_element.attribute_matches("src", r"^www.ufora.ugent.be.*.mp3$")))
