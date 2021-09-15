from typing import List
from validators import checks


def create_suites(content: str) -> List[checks.TestSuite]:
    html_suite = checks.TestSuite("HTML", content)
    css_suite = checks.TestSuite("CSS", content)

    return [html_suite, css_suite]
