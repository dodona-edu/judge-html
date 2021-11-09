import unittest
from unittest.mock import Mock

from exceptions.utils import EvaluationAborted
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
        img_exists.then(suite.element("div").exists()).then(suite.element("body").exists()).then(suite.element("html").exists())
        self.assertEqual(len(img_exists.on_success), 1)
        self.assertEqual(len(img_exists.on_success[0].on_success), 1)
        self.assertEqual(len(img_exists.on_success[0].on_success[0].on_success), 1)
        self.assertEqual(len(img_exists.on_success[0].on_success[0].on_success[0].on_success), 0)

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
        self.assertTrue(suite.checklist_item(suite.item(body_checks_div)))
        self.assertTrue(suite.checklist_item(suite.item(body_checks_img)))
        self.assertFalse(suite.checklist_item(suite.item(body_checks_h3)))

    def test_abort(self):
        suite = UnitTestSuite("test_1")
        body_exists = suite.element("body").exists()
        body_exists.callback = Mock()

        """Test succeeding"""
        div_exists = suite.element("div").exists().is_crucial()
        div_exists.then(body_exists)
        self.assertTrue(suite.checklist_item(suite.item(div_exists)))
        body_exists.callback.assert_called()

        """Test failing"""
        body_exists.callback.reset_mock()
        h3_exists = suite.element("h3").exists().is_crucial()
        h3_exists.then(body_exists)

        with self.assertRaises(EvaluationAborted):
            suite.checklist_item(suite.item(h3_exists))

        # The on_success checks should not be called if a crucial test failed
        body_exists.callback.assert_not_called()
