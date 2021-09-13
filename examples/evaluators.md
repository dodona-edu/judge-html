# Writing evaluators

The HTML judge comes with a custom testing framework to verify the code of your students.  This file (and the others in this directory) contain information and examples on how to write your own evaluators.

## Required format

All evaluators should follow a strict interface: the file should always be called `evaluator.py`, and in addition has to follow these rules:

- Contain a `create_suites` function
- This function should take a `string`, being the student's submission, and return a `list` of `TestSuite`s
- The `list` should contain **at least one** `TestSuite`
- The file should import `validators` directly, without any packages above it. To do this, we recommend placing the library at the `root` of your project in which you write the evaluators.

The fragment below contains the boilerplate to make an evaluator:

```python
from typing import List
from validators import checks


def create_suites(content: str) -> List[checks.TestSuite]:
    html_suite = checks.TestSuite("HTML", content)
    css_suite = checks.TestSuite("CSS", content)

    return [html_suite, css_suite]

```

In case you only want to write tests for either `HTML` or `CSS`, and not both, the other suite is not required. It is merely added in the fragment above as an example. Returning `[html_suite]` is equally valid.

## TestSuite class

A `TestSuite` contains a checklist of all checks that should be performed on the student's code. An exercise is only marked as correct once every check in every TestSuite has passed.

### TestSuites on Dodona

TestSuites are displayed as `tabs` on Dodona, and the `name` attribute will be the name of the tab. The image below shows what this would look like for two suites named `HTML` and `CSS`:

```python
from validators.checks import TestSuite

def create_suite(content: str):
    html_suite = TestSuite("HTML", content)
    css_suite = TestSuite("CSS", content)
    return [html_suite, css_suite]
```

<img src="media/tabs.png" alt="image: TestSuites visualized on Dodona.">

The image also shows a `1` next to the `HTML` tab, indicating that 1 test failed. This instantly allows users to see which part of their code caused the exercise to be incorrect, and which parts are already finished.

### Adding checks

In order to add checks, you can either set the entire checklist at once, or add separate `ChecklistItem`s one by one.

```python
suite = TestSuite("HTML", content)

first_item = ChecklistItem("Item 1", ...)
second_item = ChecklistItem("Item 2", ...)

# Directly setting the list content
suite.checklist = [first_item, second_item]

# Adding the items one by one
suite.checklist.append(first_item)
suite.checklist.append(second_item)
```

## ChecklistItem class

`ChecklistItem`s, as the name suggests, represent items on the checklist. This contains a message that will be displayed to the user, and all checks that will run behind the scenes. All of these checks have to pass in order to mark this item as correct.

There is **no** message telling the user which checks failed, as this would allow them to slowly figure out the solution. The only message they can see is the one you pass into the ChecklistItem when creating it. The image below shows what this would look like on Dodona:

```python
item_1 = ChecklistItem("This is the first item", [check1, check2, ...])
item_2 = ChecklistItem("This is the second item", [check3, check4, ...])
```

# TODO image

## Utility functions

These functions add extra functionality to the testing library, and can simplify common behaviour for you.

### all_of

The `all_of` function takes a list of checks, and will only pass if all of these checks passed too. Once one check fails, all other checks in the list will no longer be evaluated.

The example below will fail because there is no `<table>` inside the `<body>`.

```python
document = "<html><body></body></html>"
suite = TestSuite("HTML", document)

body_element = suite.element("body")
table_element = body.get_child("table")

# Check if the <body> exists AND it has a <table> child
all_of([body_element.exists(), table_element.exists()])
```

### any_of

The `any_of` function takes a list of checks, and will pass if at least one of these checks passes as well. Once one check passes, all other checks in the list will no longer evaluated.

The example below will pass because `<body>` exists, even if `<head>` doesn't. It will also pass if `<head>` exists while `<body>`  doesn't, and if both exist. This last scenario, however, will not be evaluated (as stated above).

```python
document = "<html><body></body></html>"
suite = TestSuite("HTML", document)

head_element = suite.element("head")
body_element = suite.element("body")

# Check if the <body> exists OR <head> exists
any_of([body_element.exists(), head_element.exists()])
```