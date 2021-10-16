import unittest
from validators.checks import ChecklistItem, all_of, any_of
from tests.helpers import UnitTestSuite


class TestFlatten(unittest.TestCase):
    def test_checklistItems(self):
        """Constructor of ChecklistItem uses this"""
        suite = UnitTestSuite("test_1")
        body = suite.element("body")

        # One check
        item = ChecklistItem("", body.exists())
        self.assertEqual(len(item._checks), 1)
        self.assertTrue(suite.checklist_item(item))

        # Varargs
        item = ChecklistItem("", body.exists(), body.has_child("div"), body.has_child("img"))
        self.assertEqual(len(item._checks), 3)
        self.assertTrue(suite.checklist_item(item))

        # Map
        item = ChecklistItem("", map(lambda i: i.has_tag("div"), body.get_children("div")[:2]))
        self.assertEqual(len(item._checks), 2)
        self.assertTrue(suite.checklist_item(item))

        # Generator expression
        item = ChecklistItem("", (c.has_tag("div") for c in body.get_children("div")[:2]))
        self.assertEqual(len(item._checks), 2)
        self.assertTrue(suite.checklist_item(item))

    def test_decorator(self):
        """Test the decorator using some of the utility functions"""
        suite = UnitTestSuite("test_1")
        table = suite.element("table")

        all_trs = all_of(c.has_tag("tr") for c in table.get_children())
        self.assertTrue(suite.check(all_trs))

        no_divs = any_of(c.has_tag("div") for c in table.get_children())
        self.assertFalse(suite.check(no_divs))
