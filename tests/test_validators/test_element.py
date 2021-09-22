import unittest
from tests.helpers import UnitTestSuite


class TestElement(unittest.TestCase):
    def test_get_child(self):
        suite = UnitTestSuite("test_1")
        body_element = suite.element("body")

        self.assertTrue(suite.check(body_element.get_child("div", 0, direct=True).attribute_exists("id", "first_div")))
        self.assertTrue(suite.check(body_element.get_child("div", 1, direct=True).attribute_exists("id", "second_div")))

        # Index out of range will return nothing
        self.assertFalse(suite.check(body_element.get_child("div", 2, direct=True).exists()))

        # Check nested elements
        self.assertTrue(suite.check(body_element.get_child("div", 1, direct=False).attribute_exists("id", "nested")))

    def test_get_children(self):
        suite = UnitTestSuite("test_1")
        self.assertTrue(suite.element("html").get_children("body>div").exactly(2))

    def test_exists(self):
        suite = UnitTestSuite("test_1")
        body_element = suite.element("body")

        self.assertTrue(suite.check(body_element.exists()))
        self.assertFalse(suite.check(body_element.get_child("body").exists()))

    def test_has_tag(self):
        suite = UnitTestSuite("test_1")
        body_element = suite.element("body")
        body_children = body_element.get_children(direct=True)

        self.assertTrue(suite.check(body_children[0].has_tag("div")))
        self.assertTrue(suite.check(body_children[-1].has_tag("img")))

    def test_has_content(self):
        suite = UnitTestSuite("test_1")
        paragraph = suite.element("p")

        self.assertTrue(suite.check(paragraph.has_content()))
        self.assertTrue(suite.check(paragraph.has_content("Some text.")))
        self.assertTrue(suite.check(paragraph.has_content("Some  \t        text.")))
        self.assertFalse(suite.check(paragraph.has_content("Other text")))

    def test_attribute_exists(self):
        suite = UnitTestSuite("test_1")
        body_element = suite.element("body")
        img_element = body_element.get_child("img")

        self.assertTrue(suite.check(img_element.attribute_exists("src")))
        self.assertFalse(suite.check(img_element.attribute_exists("width")))

    def test_attribute_contains(self):
        suite = UnitTestSuite("test_1")
        body_element = suite.element("body")
        img_element = body_element.get_child("img")

        self.assertTrue(suite.check(img_element.attribute_contains("src", "dodona")))
        self.assertTrue(suite.check(img_element.attribute_contains("src", "DODONA", case_insensitive=True)))
        self.assertFalse(suite.check(img_element.attribute_contains("src", "google.com")))

    def test_attribute_matches(self):
        suite = UnitTestSuite("test_1")
        body_element = suite.element("body")
        img_element = body_element.get_child("img")

        self.assertTrue(suite.check(img_element.attribute_matches("src", r"^https://.*dodona.ugent.be.*.png$")))
        self.assertFalse(suite.check(img_element.attribute_matches("src", r"^www.ufora.ugent.be.*.mp3$")))

    def test_has_table_header(self):
        suite = UnitTestSuite("submission_example")
        table_elements = suite.all_elements("table")

        header = ["Column 1", "Column 2", "Column 3"]
        self.assertTrue(suite.check(table_elements[0].has_table_header(header)))
        self.assertFalse(suite.check(table_elements[1].has_table_header(header)))
        self.assertFalse(suite.check(table_elements[0].has_table_header(list(reversed(header)))))

    def test_has_table_content(self):
        suite = UnitTestSuite("submission_example")
        table_elements = suite.all_elements("table")

        content = [
            ["Value     1", "Value 2", "Value\t 3"],
            ["Value  4", "Value \n\t\n 5", "Value 6"]
        ]

        self.assertTrue(suite.check(table_elements[0].has_table_content(content, has_header=True)))
        self.assertFalse(suite.check(table_elements[0].has_table_content(content, has_header=False)))

        self.assertFalse(suite.check(table_elements[1].has_table_content(content, has_header=True)))
        self.assertFalse(suite.check(table_elements[1].has_table_content(content, has_header=False)))

    def test_table_row_has_content(self):
        suite = UnitTestSuite("submission_example")
        table_elements = suite.all_elements("table")
        rows = table_elements[0].get_children("tr")

        # Only for td's, not for headers
        self.assertFalse(suite.check(rows[0].table_row_has_content(["Column 1", "Column 2", "Column 3"])))
        self.assertTrue(suite.check(rows[1].table_row_has_content(["Value \n1", "Value 2", "Value 3"])))
        self.assertTrue(suite.check(rows[2].table_row_has_content(["Value 4", "Value \t5", "Value      6"])))

    def test_has_color(self):
        suite = UnitTestSuite("css_1")
        div = suite.element("div")

        self.assertTrue(suite.check(div.has_color("color", "red")))
        self.assertTrue(suite.check(div.has_color("color", "rgb(255, 0, 0)")))
        self.assertTrue(suite.check(div.has_color("color", "rgb(255,0,0)")))
        self.assertTrue(suite.check(div.has_color("color", "rgba(255, 0, 0, 1.0)")))
        self.assertTrue(suite.check(div.has_color("color", "rgba(255, 0, 0, 1)")))
        self.assertTrue(suite.check(div.has_color("color", "rgba(255,0,0,1.0)")))
        self.assertTrue(suite.check(div.has_color("color", "rgba(255,0,0,1)")))
        self.assertTrue(suite.check(div.has_color("color", "#FF0000")))

    def test_no_loose_text(self):
        suite = UnitTestSuite("loose_text")
        self.assertFalse(suite.check(suite.element("body").no_loose_text()))
        self.assertFalse(suite.check(suite.element("div").no_loose_text()))
        self.assertTrue(suite.check(suite.element("table").no_loose_text()))

    def test_has_url_with_fragment(self):
        suite = UnitTestSuite("links")
        self.assertFalse(suite.check(suite.element("body").has_url_with_fragment()))
        self.assertFalse(suite.check(suite.element("a", id="outgoing_link").has_url_with_fragment()))
        self.assertTrue(suite.check(suite.element("a", id="fragmented_link").has_url_with_fragment()))
        self.assertTrue(suite.check(suite.element("a", id="fragmented_link").has_url_with_fragment("_1-create-an-api-token")))
        self.assertFalse(suite.check(suite.element("a", id="fragmented_link").has_url_with_fragment("some-other-fragment")))

    def test_has_outgoing_url(self):
        suite = UnitTestSuite("links")
        self.assertFalse(suite.check(suite.element("body").has_outgoing_url()))
        self.assertTrue(suite.check(suite.element("a", id="outgoing_link").has_outgoing_url()))
        self.assertFalse(suite.check(suite.element("a", id="outgoing_link").has_outgoing_url(["youtube.com"])))
        self.assertFalse(suite.check(suite.element("a", id="dodona_link").has_outgoing_url()))
