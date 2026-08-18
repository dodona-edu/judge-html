import unittest

from tests.helpers import UnitTestSuite


class TestEmmetMethods(unittest.TestCase):
    def test_find_methods(self):
        suite = UnitTestSuite("emmet_finding")

        # Basic navigation
        self.assertTrue(suite.check(suite.element("body>div").attribute_exists("id", "the_first_div")))

        # Wrong index on first div
        self.assertFalse(suite.check(suite.element("body>div[0]>table").exists()))

        # Correct index, also negative index works
        self.assertTrue(suite.check(suite.element("body>div[1]>table>tr[0]>td[-1]").has_content("Content")))

        # Pass #id
        self.assertTrue(suite.check(suite.element("body>div#the_second_div").has_child("table")))

        # Pass classnames and id's
        self.assertTrue(
            suite.check(suite.element("body>div#the_second_div>table>tr.tr-class-name>td").has_content("Some td"))
        )

        # Allow kwargs
        self.assertTrue(suite.check(suite.element("body>div", id="the_second_div").has_child("table")))

        # Path takes priority over kwargs
        self.assertFalse(suite.check(suite.element("body>div#the_first_div", id="the_second_div").has_child("table")))

        # Allow index
        self.assertTrue(suite.check(suite.element("body>div", index=1).attribute_exists("id", "the_second_div")))

        # Path index takes priority
        self.assertTrue(suite.check(suite.element("body>div[0]", index=1).attribute_exists("id", "the_first_div")))

    def test_empty_path_segment(self):
        # A leading or trailing ">" leaves an empty segment in the path, which makes
        # find_emmet return all children of the current element. Those used to come back as
        # a bs4 generator: always truthy, not subscriptable, and yielding NavigableStrings
        # (whitespace, the doctype) that the callers then called .get() on
        suite = UnitTestSuite("emmet_finding")

        # Trailing ">": the direct children of <body> are two <div>s, the whitespace
        # in between them shouldn't be counted
        self.assertTrue(suite.check(suite.element("body>").attribute_exists("id", "the_first_div")))
        self.assertEqual(len(suite.all_elements("body>")), 2)

        # Leading ">": the children of the document itself, so the doctype should be skipped
        self.assertTrue(suite.check(suite.element(">div").attribute_exists("lang", "en")))
        self.assertEqual(len(suite.all_elements(">div")), 1)
