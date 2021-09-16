import re
import unittest
from tests.helpers import html_loader
from validators.checks import TestSuite


class TestTestSuite(unittest.TestCase):
    def test_document_matches(self):
        file = html_loader("self_closing_tag")
        suite = TestSuite("", file)

        # Check that the document has a self-closing tag
        self.assertTrue(suite.document_matches(r"<[^>]+/>").callback(suite._bs))

        # Check that the document starts with "<!doctype"
        self.assertFalse(suite.document_matches(r"^<!doctype").callback(suite._bs))

        # Check that the document starts with "<!doctype", but with the IGNORECASE flag
        self.assertTrue(suite.document_matches(r"^<!doctype", re.IGNORECASE).callback(suite._bs))
