import unittest
from validators.checks import ChecklistItem
from tests.helpers import UnitTestSuite


class TestFlatten(unittest.TestCase):
    def test_checklistItems(self):
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
