import unittest
from unittest.mock import Mock
from tests.helpers import UnitTestSuite


class TestChecks(unittest.TestCase):
    def test_find_deepest_nested_and_then(self):
        suite = UnitTestSuite("test_1")

        """Test succeeding"""
        div_exists = suite.element("div").exists()
        body_exists = suite.element("body").exists()
        body_exists.callback = Mock(return_value=False)
        div_exists.then(body_exists)

        # Running the item should fail, even though the div exists, because
        # the body_exists callback will return False
        self.assertFalse(suite.checklist_item(suite.item(div_exists)))
        body_exists.callback.assert_called()

        """Test failing"""
        # The table doesn't exist so this always fails
        table_exists = suite.element("table").exists()
        html_valid = suite.validate_html()
        html_valid.callback = Mock()
        table_exists.then(html_valid)

        # If the first check failed, the next ones are not allowed to be called
        suite.checklist_item(suite.item(table_exists))
        html_valid.callback.assert_not_called()

        """Test chaining"""
        img_exists = suite.element("img").exists()
        img_exists.then(suite.element("div").exists()).then(suite.element("body").exists())
        self.assertEqual(len(img_exists.on_success), 1)
        self.assertEqual(len(img_exists.on_success[0].on_success), 1)
        self.assertEqual(len(img_exists.on_success[0].on_success[0].on_success), 0)
