from utils.html_navigation import compare_content
import unittest


class TestCompareContent(unittest.TestCase):
    def test_cc(self):
        self.assertTrue(compare_content("test", "test"))
        self.assertTrue(compare_content("  test   ", " test       "))
        self.assertTrue(compare_content(" \t\n test \n\t\t\n      ", " test       "))
        self.assertTrue(compare_content(" test       ", " \t\n test \n\t\t\n      "))
        self.assertTrue(
            compare_content(
                " test  with  \t\t  \n    whitespace  \n\t\t         in between          \n",
                "test with whitespace in between",
            )
        )

    def test_cc_many_whitespace_runs(self):
        # More than 8 internal whitespace runs, to catch a regression where only the
        # first 8 runs of whitespace were being collapsed
        self.assertTrue(compare_content("a  b\tc \n d   e\t\tf \n\n g  h\ti  j\t k", "a b c d e f g h i j k"))

    def test_cc_many_whitespace_runs_case_insensitive(self):
        self.assertTrue(
            compare_content("A  B\tC \n D   E\t\tF \n\n G  H\tI  J\t K", "a b c d e f g h i j k", case_insensitive=True)
        )
