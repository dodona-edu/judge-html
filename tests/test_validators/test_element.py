import re
import unittest
from tests.helpers import UnitTestSuite
from validators.checks import all_of, any_of, at_least, fail_if


class TestElement(unittest.TestCase):
    def test_get_child(self):
        suite = UnitTestSuite("test_1")
        body_element = suite.element("body")
        phantom = suite.element("video")  # does not exist

        self.assertTrue(suite.check(body_element.get_child("div", 0, direct=True).attribute_exists("id", "first_div")))
        self.assertTrue(suite.check(body_element.get_child("div", 1, direct=True).attribute_exists("id", "second_div")))
        self.assertFalse(suite.check(phantom.get_child("source").attribute_exists("type", "video/mp4")))

        # Index out of range will return nothing
        self.assertFalse(suite.check(body_element.get_child("div", 2, direct=True).exists()))

        with self.assertRaises(IndexError):
            suite.check(body_element.get_child("div", -42, direct=True).exists())

        # Check nested elements
        self.assertTrue(suite.check(body_element.get_child("div", 1, direct=False).attribute_exists("id", "nested")))

        # First tag
        self.assertTrue(suite.check(body_element.get_child(index=0).attribute_exists("id", "first_div")))

        # kwargs
        self.assertTrue(suite.check(body_element.get_child("div", direct=True, id="second_div").exists()))
        self.assertFalse(suite.check(body_element.get_child("div", direct=True, id="nested").exists()))
        self.assertTrue(suite.check(body_element.get_child("img", alt="dodona-icon").exists()))
        self.assertTrue(suite.check(body_element.get_child("h2", direct=False, class_="city").has_content("London")))

        # Emmet
        self.assertTrue(suite.check(body_element.get_child("div>p").has_content("Some text.")))

    def test_get_children(self):
        suite = UnitTestSuite("test_1")
        self.assertTrue(suite.element("html").get_children("body>div").exactly(2))
        self.assertFalse(suite.element("html").get_children("body>div>p").exactly(2))  # TODO
        self.assertTrue(suite.element("html").get_children("img").exactly(1))

        self.assertTrue(suite.element("body").get_children("p", direct=True).exactly(1))
        self.assertTrue(suite.element("html").get_children("p", direct=False).exactly(3))
        self.assertTrue(suite.element("html").get_children("p", direct=False, class_="city").exactly(2))
        self.assertTrue(suite.element("html").get_children("img", direct=False, alt="dodona-icon").exactly(1))

    def test_exists(self):
        suite = UnitTestSuite("test_1")
        body_element = suite.element("body")

        self.assertTrue(suite.check(body_element.exists()))
        self.assertFalse(suite.check(body_element.get_child("body").exists()))

    def test_has_child(self):
        suite = UnitTestSuite("test_1")
        body = suite.element("body")
        div_nested = suite.element("div", id="nested")
        div_first = suite.element("div", id="first_div")
        div_second = suite.element("div", id="second_div")
        phantom = suite.element("video")  # does not exist

        self.assertTrue(suite.check(body.has_child("div", id="second_div")))
        self.assertTrue(suite.check(div_nested.has_child("h2")))
        self.assertTrue(suite.check(div_nested.has_child("h2", class_="city")))
        self.assertTrue(suite.check(div_nested.has_child("p")))
        self.assertFalse(suite.check(div_nested.has_child("img")))
        self.assertFalse(suite.check(div_second.has_child("p")))
        self.assertFalse(suite.check(phantom.has_child("source")))

        self.assertTrue(suite.check(div_first.has_child("h2", direct=False)))
        self.assertTrue(suite.check(div_first.has_child("p", direct=False)))
        self.assertFalse(suite.check(div_first.has_child("img", direct=False)))

    def test_has_tag(self):
        suite = UnitTestSuite("test_1")
        body_element = suite.element("body")
        body_children = body_element.get_children(direct=True)

        self.assertTrue(suite.check(body_children[0].has_tag("div")))
        self.assertTrue(suite.check(body_children[-1].has_tag("img")))

    def test_has_content(self):
        suite = UnitTestSuite("test_1")
        ps = suite.all_elements("p")
        paragraph1 = ps[0]
        paragraph3 = ps[2]
        phantom = suite.element("video")  # does not exist

        self.assertTrue(suite.check(paragraph1.has_content()))
        self.assertTrue(suite.check(paragraph1.has_content("Some text.")))
        self.assertTrue(suite.check(paragraph1.has_content("Some  \t        text.")))
        self.assertFalse(suite.check(paragraph1.has_content("Other text")))
        self.assertTrue(suite.check(paragraph1.has_content("SOME text.", case_insensitive=True)))
        self.assertFalse(suite.check(paragraph1.has_content("SOME", case_insensitive=True)))

        self.assertFalse(suite.check(paragraph3.has_content()))
        self.assertTrue(suite.check(paragraph3.has_content("")))
        self.assertFalse(suite.check(phantom.has_content()))

    def test_el_from_elementcontainer(self):
        suite = UnitTestSuite("test_1")
        ps = suite.all_elements("p")  # three elements

        first, second = ps[0], ps[1]
        self.assertTrue(suite.check(first.has_content("Some text.")))
        self.assertTrue(suite.check(second.has_content("London is the capital of England.")))

        first_and_last = ps[::2]  # slicing is supported
        self.assertTrue(len(first_and_last) == 2)

        with self.assertRaises(TypeError):
            phantom_p = ps['not a number']
            self.assertFalse(suite.check(phantom_p.has_content()))

    def test_attribute_exists(self):
        suite = UnitTestSuite("test_1")
        body_element = suite.element("body")
        img_element = body_element.get_child("img")

        self.assertTrue(suite.check(img_element.attribute_exists("src")))
        self.assertFalse(suite.check(img_element.attribute_exists("width")))
        self.assertTrue(suite.check(img_element.attribute_exists("alt", "dodona-icon")))
        self.assertTrue(suite.check(img_element.attribute_exists("alt", "DoDoNA-icON", case_insensitive=True)))
        self.assertFalse(suite.check(img_element.attribute_exists("alt", "icon")))

        # Lists
        suite = UnitTestSuite("class_names")
        body_element = suite.element("body")
        div_element = body_element.get_child("div")

        self.assertFalse(suite.check(body_element.attribute_exists("class")))
        self.assertTrue(suite.check(div_element.attribute_exists("class")))
        self.assertTrue(suite.check(div_element.attribute_exists("class", "SOMETHING")))
        self.assertTrue(suite.check(div_element.attribute_exists("class", "something", case_insensitive=True)))
        self.assertFalse(suite.check(div_element.attribute_exists("class", "something else")))
        self.assertTrue(suite.check(div_element.attribute_exists("class", "else")))

    def test_attribute_contains(self):
        suite = UnitTestSuite("test_1")
        body_element = suite.element("body")
        img_element = body_element.get_child("img")
        h3 = body_element.get_child("h3", direct=False)  # does not exist

        self.assertTrue(suite.check(img_element.attribute_contains("src", "dodona")))
        self.assertTrue(suite.check(img_element.attribute_contains("src", "DODONA", case_insensitive=True)))
        self.assertFalse(suite.check(img_element.attribute_contains("src", "google.com")))
        self.assertFalse(suite.check(h3.attribute_contains("class", "city")))

        # Lists
        suite = UnitTestSuite("class_names")
        body_element = suite.element("body")
        div_element = body_element.get_child("div")

        self.assertFalse(suite.check(body_element.attribute_contains("class", "text")))
        self.assertTrue(suite.check(div_element.attribute_contains("class", "SO")))
        self.assertFalse(suite.check(div_element.attribute_contains("class", "so")))
        self.assertFalse(suite.check(div_element.attribute_contains("class", "something else")))
        self.assertTrue(suite.check(div_element.attribute_contains("class", "so", case_insensitive=True)))

    def test_attribute_matches(self):
        suite = UnitTestSuite("test_1")
        body_element = suite.element("body")
        img_element = body_element.get_child("img")
        h3 = body_element.get_child("h3", direct=False)  # does not exist

        self.assertTrue(suite.check(img_element.attribute_matches("src", r"^https://.*dodona.ugent.be.*.png$")))
        self.assertFalse(suite.check(img_element.attribute_matches("src", r"^www.ufora.ugent.be.*.mp3$")))
        self.assertFalse(suite.check(h3.attribute_matches("class", "^ci.*")))

        # Lists
        suite = UnitTestSuite("class_names")
        body_element = suite.element("body")
        div_element = body_element.get_child("div")

        self.assertFalse(suite.check(body_element.attribute_matches("class", r"[0-9]")))
        self.assertTrue(suite.check(div_element.attribute_matches("class", r"^[A-Z]+$")))
        self.assertTrue(suite.check(div_element.attribute_matches("class", r"^[a-z]+$")))
        self.assertTrue(suite.check(div_element.attribute_matches("class", r"^[a-zA-Z]+$", flags=re.IGNORECASE)))

    def test_has_table_header(self):
        suite = UnitTestSuite("submission_example")
        table_elements = suite.all_elements("table")
        phantom = suite.element("video")  # does not exist

        header = ["Column 1", "Column 2", "Column 3"]
        self.assertTrue(suite.check(table_elements[0].has_table_header(header)))
        self.assertFalse(suite.check(table_elements[1].has_table_header(header)))
        self.assertFalse(suite.check(table_elements[0].has_table_header(list(reversed(header)))))

        self.assertFalse(suite.check(phantom.has_table_header(['no content'])))
        self.assertFalse(suite.check(table_elements[4].has_table_header(header)))  # does not exist

    def test_has_table_content(self):
        suite = UnitTestSuite("submission_example")
        table_elements = suite.all_elements("table")
        phantom = suite.element("video")  # does not exist

        content = [
            ["Value     1", "Value 2", "Value\t 3"],
            ["Value  4", "Value \n\t\n 5", "Value 6"]
        ]

        self.assertTrue(suite.check(table_elements[0].has_table_content(content, has_header=True)))
        self.assertFalse(suite.check(table_elements[0].has_table_content(content, has_header=False)))

        self.assertFalse(suite.check(table_elements[1].has_table_content(content, has_header=True)))
        self.assertFalse(suite.check(table_elements[1].has_table_content(content, has_header=False)))

        self.assertFalse(
            suite.check(table_elements[1].has_table_content([['Value 7', 'Value 8', 'Value9']], has_header=True)))

        self.assertTrue(
            suite.check(table_elements[1].has_table_content([['Value 7', 'Value 8', 'Value 9']], has_header=False)))
        self.assertFalse(
            suite.check(table_elements[1].has_table_content([['7', '8', '9']], has_header=False)))
        self.assertFalse(
            suite.check(table_elements[1].has_table_content([['Value 7', 'Value 8']], has_header=False)))

        self.assertFalse(suite.check(table_elements[2].has_table_content([['no content']])))

        self.assertFalse(suite.check(phantom.has_table_content(content)))

    def test_table_row_has_content(self):
        suite = UnitTestSuite("submission_example")
        table_elements = suite.all_elements("table")
        rows = table_elements[0].get_children("tr")
        phantom = suite.element("video")  # does not exist
        ph_row = phantom.get_child("tr")

        # Only for td's, not for headers
        self.assertFalse(suite.check(rows[0].table_row_has_content(["Column 1", "Column 2", "Column 3"])))
        self.assertTrue(suite.check(rows[1].table_row_has_content(["Value \n1", "Value 2", "Value 3"])))
        self.assertFalse(suite.check(rows[1].table_row_has_content(["Value \n1", "Value 2", "Wrong content"])))
        self.assertTrue(
            suite.check(rows[2].table_row_has_content(["Value 4", "Value \t5", "VALUE      6"], case_insensitive=True)))

        self.assertFalse(suite.check(ph_row.table_row_has_content(["Column 1", "Column 2", "Column 3"])))

    def test_has_color(self):
        suite = UnitTestSuite("css_1")
        div = suite.element("div")
        span = suite.element('span')
        phantom = suite.element("video")  # does not exist
        # p = suite.element("p")

        self.assertTrue(suite.check(div.has_color("color", "red")))
        self.assertTrue(suite.check(div.has_color("color", "rgb(255, 0, 0)")))
        self.assertTrue(suite.check(div.has_color("color", "rgb(255,0,0)")))
        self.assertTrue(suite.check(div.has_color("color", "rgba(255, 0, 0, 1.0)")))
        self.assertTrue(suite.check(div.has_color("color", "rgba(255, 0, 0, 1)")))
        self.assertTrue(suite.check(div.has_color("color", "rgba(255,0,0,1.0)")))
        self.assertTrue(suite.check(div.has_color("color", "rgba(255,0,0,1)")))
        self.assertTrue(suite.check(div.has_color("color", "#FF0000")))

        self.assertFalse(suite.check(phantom.has_color("color", "gold")))
        self.assertFalse(suite.check(span.has_color("color", "gold")))  # TODO

        # TODO #106
        # self.assertTrue(suite.check(p.has_color("color", "gold")))
        # self.assertTrue(suite.check(p.has_color("color", "#FFD700FF")))
        # self.assertTrue(suite.check(p.has_color("color", "rgb(255, 215, 0)")))
        # self.assertTrue(suite.check(p.has_color("color", "rgba(255, 215, 0, 1)")))

    def test_has_styling(self):
        suite = UnitTestSuite("css_1")
        div = suite.element("div")
        p = suite.element("p")
        span = suite.element("span")
        phantom = suite.element("video")  # does not exist

        self.assertTrue(suite.check(div.has_styling("margin", "3px")))
        self.assertTrue(suite.check(p.has_styling("background-color")))
        self.assertTrue(suite.check(p.has_styling("text-align")))
        self.assertTrue(suite.check(p.has_styling("text-align", "left")))

        self.assertTrue(suite.check(p.has_styling("font-weight", "bold")))
        self.assertFalse(suite.check(p.has_styling("font-weight", "normal")))
        self.assertTrue(suite.check(p.has_styling("text-align", "left", important=False)))
        self.assertFalse(suite.check(p.has_styling("text-align", "left", important=True)))
        self.assertFalse(suite.check(p.has_styling("font-weight", "bold", important=False)))
        self.assertTrue(suite.check(p.has_styling("font-weight", "bold", important=True)))

        self.assertFalse(suite.check(span.has_styling("background-color")))
        self.assertFalse(suite.check(phantom.has_styling("border")))

    def test_no_loose_text(self):
        suite = UnitTestSuite("loose_text")
        phantom = suite.element("video")  # does not exist

        self.assertFalse(suite.check(suite.element("body").no_loose_text()))
        self.assertFalse(suite.check(suite.element("div").no_loose_text()))
        self.assertTrue(suite.check(suite.element("table").no_loose_text()))
        self.assertFalse(suite.check(suite.element("h1").no_loose_text()))
        self.assertFalse(suite.check(phantom.no_loose_text()))

    def test_has_url_with_fragment(self):
        suite = UnitTestSuite("links")
        phantom = suite.element("video")  # does not exist

        self.assertFalse(suite.check(suite.element("body").has_url_with_fragment()))
        self.assertFalse(suite.check(suite.element("a", id="outgoing_link").has_url_with_fragment()))
        self.assertTrue(suite.check(suite.element("a", id="fragmented_link").has_url_with_fragment()))
        self.assertTrue(
            suite.check(suite.element("a", id="fragmented_link").has_url_with_fragment("_1-create-an-api-token")))
        self.assertFalse(
            suite.check(suite.element("a", id="fragmented_link").has_url_with_fragment("some-other-fragment")))
        self.assertTrue(suite.check(suite.element("a", id="internal_link").has_url_with_fragment("section2")))
        self.assertTrue(suite.check(suite.element("a", id="no_link").has_url_with_fragment("section42")))
        self.assertTrue(suite.check(suite.element("a", id="no_href").has_url_with_fragment("section101")))
        self.assertFalse(suite.check(phantom.has_url_with_fragment()))

    def test_has_outgoing_url(self):
        suite = UnitTestSuite("links")
        phantom = suite.element("video")  # does not exist

        self.assertFalse(suite.check(suite.element("body").has_outgoing_url()))
        self.assertTrue(suite.check(suite.element("a", id="outgoing_link").has_outgoing_url()))
        self.assertFalse(suite.check(suite.element("a", id="outgoing_link").has_outgoing_url(["youtube.com"])))
        self.assertFalse(suite.check(suite.element("a", id="dodona_link").has_outgoing_url()))
        self.assertFalse(suite.check(suite.element("img", id="internal_image").has_outgoing_url(attr="src")))
        self.assertTrue(suite.check(suite.element("img", id="external_image").has_outgoing_url(attr="src")))
        self.assertFalse(suite.check(phantom.has_outgoing_url()))

    def test_contains_comment(self):
        suite = UnitTestSuite("test_1")
        phantom = suite.element("video")  # does not exist

        # Entire suite
        self.assertTrue(suite.check(suite.contains_comment()))
        self.assertTrue(suite.check(suite.contains_comment("This is a comment")))
        self.assertFalse(suite.check(suite.contains_comment("Random garbage")))

        # Specific elements
        self.assertTrue(suite.check(suite.element("body").contains_comment()))
        self.assertTrue(suite.check(suite.element("body").contains_comment("This is a comment")))
        self.assertFalse(suite.check(suite.element("body").contains_comment("Random garbage")))
        self.assertFalse(suite.check(suite.element("body>div").contains_comment()))
        self.assertFalse(suite.check(suite.element("body>div").contains_comment("This is a comment")))
        self.assertFalse(suite.check(suite.element("body>div").contains_comment("Random garbage")))
        self.assertFalse(suite.check(phantom.contains_comment("no content")))

    def test_then(self):
        suite = UnitTestSuite("test_1")
        body_element = suite.element("body")
        div_element = body_element.get_child("div")
        p_element = div_element.get_child("p")

        img_element = body_element.get_child("img")
        h3_element = body_element.get_child("h3")  # Does not exist

        body_checks_div = body_element.exists().then(div_element.exists()).then(p_element.exists())
        body_checks_img = body_element.exists().then(img_element.exists())
        body_checks_h3 = body_element.exists().then(h3_element.exists())
        self.assertTrue(suite.check(body_checks_div))
        self.assertTrue(suite.check(body_checks_img))
        self.assertFalse(suite.check(body_checks_h3))

    def test_all_of(self):
        suite = UnitTestSuite("test_1")

        body_element = suite.element("body")
        img_element = suite.element("img")
        h2_elements = suite.all_elements('h2')
        phantom = suite.element("video")  # does not exist

        self.assertTrue(suite.check(all_of(body_element.exists(), body_element.has_child("div"), img_element.exists())))
        self.assertFalse(suite.check(all_of(phantom.exists(), body_element.has_child("div"), img_element.exists())))
        self.assertFalse(suite.check(all_of(body_element.exists(), phantom.exists(), img_element.exists())))
        self.assertTrue(suite.check(all_of(h2.attribute_exists('class', 'city') for h2 in h2_elements)))

    def test_any_of(self):
        suite = UnitTestSuite("test_1")

        body_element = suite.element("body")
        img_element = suite.element("img")
        h3_element = body_element.get_child("h3")  # Does not exist

        self.assertTrue(suite.check(any_of(body_element.exists(), body_element.has_child("div"),
                                           img_element.exists(), h3_element.exists())))

    def test_at_least(self):
        suite = UnitTestSuite("test_1")

        body_element = suite.element("body")
        img_element = suite.element("img")
        h3_element = body_element.get_child("h3")  # Does not exist

        self.assertTrue(suite.check(at_least(2, body_element.exists(), body_element.has_child("div"),
                                             img_element.exists(), h3_element.exists())))
        self.assertTrue(suite.check(at_least(3, body_element.exists(), body_element.has_child("div"),
                                             img_element.exists(), h3_element.exists())))
        self.assertFalse(suite.check(at_least(4, body_element.exists(), body_element.has_child("div"),
                                              img_element.exists(), h3_element.exists())))

    def test_fail_if(self):
        suite = UnitTestSuite("test_1")
        body_element = suite.element("body")
        h3_element = body_element.get_child("h3")  # Does not exist

        self.assertFalse(suite.check(fail_if(body_element.exists())))
        self.assertTrue(suite.check(fail_if(h3_element.exists())))
