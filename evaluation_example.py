from validators import checks
from tests.utils import load_html_file


content = load_html_file("submission_example")
suite = checks.TestSuite(content)

# HEAD CHECKS
el_head = suite.element("head")
el_title = el_head.get_child("title")

head_checks = [
    el_head.exists(),
    el_title.exists(),
    el_title.has_content()
]
grouped_head_checks = checks.all_of(head_checks)

# BODY CHECKS
el_body = suite.element("body")
body_children = el_body.get_children()

children_check = el_body.count_children("p", 2).then(el_body.count_children("table", 1))

table: checks.Element = body_children[1]
# Checks for the table
table_check = table.has_tag("table").then(  # Check that the 2nd entry is the table
        table.count_children("tr", 2)  # Check that there are 2 rows
    ).then(
        table.get_child("tr", 0).count_children("th", 3)  # Check that the first row contains the headers
    ).then(
        table.get_child("tr", 1).count_children("td", 3)  # Check that the second row contains tds
    )

# TODO find a solution for potential index errors?
body_checks = [
    body_children[0].has_tag("p").then(body_children[0].has_content()),  # First paragraph is not empty
    table_check,
    body_children[2].has_tag("p").then(body_children[2].has_content())
]

suite.checklist = [
    grouped_head_checks,
    body_checks
]

print("\n".join(
    list(map(lambda x: f"Success: {x[0]} | Message: {x[1]}", suite.evaluate()))
))
