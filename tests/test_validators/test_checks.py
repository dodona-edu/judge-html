from os import path
from utils.file_loaders import html_loader
import unittest
from validators import checks

# Location of this test file
basepath = path.dirname(__file__)

# Location of html files
html_dir = path.abspath(path.join(basepath, "../tests/html_files"))


class TestChecks(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_grouped_checks(self):
        # Open HTML file
        html_content = html_loader(path.join(html_dir,"nested_attributes"))

        suite = checks.TestSuite(html_content)
