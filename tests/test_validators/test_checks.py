from tests.utils import load_html_file
import unittest
from validators import checks


class TestChecks(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_grouped_checks(self):
        # Open HTML file
        html_content = load_html_file("nested_attributes")

        suite = checks.TestSuite(html_content)

        # Get elements
        body = suite.element("body")
        div1 = body.get_child("div")
        div2 = div1.get_child("div")
        a = div2.get_child("a")

        # Create checks
        message = "Test message"
        grouped_list = [
            body.exists(),
            div1.exists(),
            div2.exists(),
            a.exists(),
            a.has_content(message)
        ]

        # Assign checklist
        suite.checklist = [
            checks.all_of(message, grouped_list).display()
        ]

        # Check that test failed, but the requested message was shown
        evaluation = suite.evaluate()
        self.assertEqual(len(evaluation), 1)
        self.assertFalse(evaluation[0][0])
        self.assertEqual(evaluation[0][1], message)
