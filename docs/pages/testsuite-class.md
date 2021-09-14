# TestSuite Class

A `TestSuite` contains a checklist of all checks that should be performed on the student's code. An exercise is only marked as correct once every check in every TestSuite has passed.

## Table of Contents
- [Attributes](#attributes)
- [TestSuites on Dodona](#testsuites-on-dodona)
- [Referencing (specific) HTML elements](#referencing-specific-html-elements)
- [Adding checks](#adding-checks)

## Attributes

TODO

## TestSuites on Dodona

TestSuites are displayed as `tabs` on Dodona, and the `name` attribute will be the name of the tab. The names can be whatever you want them to be, but the examples here will always use "HTML" and "CSS" for consistency. The image below shows what this would look like for two suites named `HTML` and `CSS`:

```python
from validators.checks import TestSuite

def create_suite(content: str):
    html_suite = TestSuite("HTML", content)
    css_suite = TestSuite("CSS", content)
    return [html_suite, css_suite]
```

<img src="../media/tabs.png" alt="image: TestSuites visualized on Dodona.">

The image also shows a `1` next to the `HTML` tab, indicating that 1 test failed. This instantly allows users to see which part of their code caused the exercise to be incorrect, and which parts are already finished.

## Referencing (specific) HTML elements

You can get a specific HTML element by tag using `suite.element(tag)` in the form of an instance of the `Element` class (explained later). Afterwards, you can use this reference to create extra checks based off of it.

The example below shows how to get the `<html>` tag:

```python
suite = TestSuite("HTML", "<html><body>...</body></html>")
html_tag = suite.element("html")
```

Searching will start from the root element, and work in a breadth-first way recursively. In case you want to disable this and only search the root of the tree, you can pass `from_root=True` into the function.

The example below shows how to get the `<div>` at the root of the tree, and not the one that comes first in the file but is nested deeper.

```python
content =   """
            <span>
                <div>   <!-- We don't want this div -->
                    ...
                </div>
            </span>
            <div>       <!-- We want THIS div -->
                ...
            </div>
            """
suite = TestSuite("HTML", content)
root_div = suite.element("div", from_root=True)
```

Extra filters, such as id's and attributes, can be passed as `kwargs`. You can pass as many filters as you want to.

The example below shows how to get the `<tr>` with id "row_one", and the `<th>` with attribute `colspan` equal to `2`.

```python
content =   """
            <table>
                <tr id="header">    <!-- We don't want this tr -->
                    <th>Wrong Header</th>
                    <th colspan="2">Correct Header</th>
                </tr>
                <tr id="row_one">   <!-- We want THIS tr -->
                    ...
                </tr>
            </table>
            """
suite = TestSuite("HTML", content)
tr_one = suite.element("tr", id="row_one")
th_colspan = suite.element("th", colspan="2")
```

## Adding checks

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
