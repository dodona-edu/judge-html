from tests.helpers import UnitTestSuite
from validators.checks import Element, EmptyElement, ElementContainer
import unittest


class TestElementContainer(unittest.TestCase):
    def test_out_of_range(self):
        el = Element("div", "el_id", None)
        container = ElementContainer([el])

        # Right index gets correct item
        self.assertEqual(container[0], el)
        self.assertTrue(container[0].id is not None)

        # Out of range index gets empty element
        self.assertTrue(isinstance(container[1], EmptyElement))

    def test_get(self):
        el1 = Element("div", "el_id_1", None)
        el2 = Element("body", "el_id_2", None)
        container = ElementContainer([el1, el2])

        self.assertEqual(container[0], container.get(0))
        self.assertEqual(container[1], container.get(1))
        self.assertNotEqual(container[0], container.get(1))

    def test_at_least(self):
        suite = UnitTestSuite("my_first_html_exercise")
        body = suite.element("body")
        table = body.get_child("table")

        all_trs = table.get_children("tr")

        self.assertTrue(suite.check(all_trs.at_least(3)))
        self.assertTrue(suite.check(all_trs.at_least(4)))
        self.assertFalse(suite.check(all_trs.at_least(5)))

    def test_at_most(self):
        suite = UnitTestSuite("my_first_html_exercise")
        body = suite.element("body")
        table = body.get_child("table")

        all_trs = table.get_children("tr")

        self.assertFalse(suite.check(all_trs.at_most(3)))
        self.assertTrue(suite.check(all_trs.at_most(4)))
        self.assertTrue(suite.check(all_trs.at_most(5)))

    def test_exactly(self):
        suite = UnitTestSuite("my_first_html_exercise")
        body = suite.element("body")
        table = body.get_child("table")

        all_trs = table.get_children("tr")

        self.assertFalse(suite.check(all_trs.exactly(3)))
        self.assertTrue(suite.check(all_trs.exactly(4)))
        self.assertFalse(suite.check(all_trs.exactly(5)))

    def test_length(self):
        suite = UnitTestSuite("test_1")
        ps = suite.all_elements("p")
        h3s = suite.all_elements("h3")

        self.assertEqual(len(ps), 3)
        self.assertEqual(len(h3s), 0)

    def test_utility_functions(self):
        suite = UnitTestSuite("test_1")

        divs = suite.all_elements("div")
        self.assertTrue(suite.check(divs.all(lambda x: x.attribute_exists("id"))))
        self.assertTrue(suite.check(divs.any(lambda x: x.attribute_exists("id", "first_div"))))

        h3s = suite.all_elements("h3")
        self.assertFalse(suite.check(h3s.all(lambda x: x.attribute_exists("id"))))
        self.assertFalse(suite.check(h3s.any(lambda x: x.attribute_exists("id"))))
