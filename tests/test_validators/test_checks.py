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
