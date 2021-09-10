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
