from utils.html_navigation import compare_content
import unittest


class TestCompareContent(unittest.TestCase):
    def test_cc(self):
        self.assertTrue(compare_content("test", "test"))
        self.assertTrue(compare_content("  test   ", " test       "))
        self.assertTrue(compare_content(" \t\n test \n\t\t\n      ", " test       "))
        self.assertTrue(compare_content(" test       ", " \t\n test \n\t\t\n      "))
        self.assertTrue(compare_content(" test  with  \t\t  \n    whitespace  \n\t\t         in between          \n",
                                        "test with whitespace in between"))
