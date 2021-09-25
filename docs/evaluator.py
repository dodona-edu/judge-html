from typing import List
from validators import checks


def create_suites(content: str) -> List[checks.TestSuite]:
    html_suite = checks.HtmlSuite(content)
    css_suite = checks.CssSuite(content)

    return [html_suite, css_suite]
