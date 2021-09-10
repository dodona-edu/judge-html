from tests.utils import html_test_loader
import unittest
from validators import checks


class TestChecks(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_grouped_checks(self):
        # Open HTML file
        html_content = html_test_loader("nested_attributes")

        suite = checks.TestSuite(html_content)
