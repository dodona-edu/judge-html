from typing import List
from validators import checks


def create_suites(content: str) -> List[checks.TestSuite]:
    css_suite = checks.TestSuite("CSS", content)

    html_valid = checks.ChecklistItem("The HTML is valid.", css_suite.validate_html())
    css_suite.add_check(html_valid)

    css_valid = checks.ChecklistItem("The CSS is valid.", css_suite.validate_css())
    css_suite.add_check(css_valid)

    img_element = css_suite.element("img")
    border = checks.ChecklistItem("The image has a border as shown in the image.", [
        img_element.exists(),
        img_element.has_styling("border-style", "dashed"),
        img_element.has_styling("width", "200px")
    ])
    css_suite.add_check(border)

    return [css_suite]
