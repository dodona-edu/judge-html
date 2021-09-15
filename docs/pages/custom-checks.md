# Writing custom Checks

In case you want to do something that our library doesn't support, you can always create your own checks. This document will explain how to do so.

## Check structure

A Check takes one argument, being the callable that gets executed when the check is evaluated. This callable may only take one argument as well, a `BeautifulSoup` instance of the student's submission, and returns a `bool`.

It's suggested to wrap this check inside a function that returns it, to allow extra arguments to be passed into it.

Below is the boilerplate to create your own Check:

```python
from bs4 import BeautifulSoup
from validators.checks import Check

# Function that creates a custom check
def my_custom_check() -> Check:
    # Inner function that will evaluate something
    def _inner(bs: BeautifulSoup) -> bool:
        return True

    # Create a new Check that takes our inner function as an argument
    return Check(_inner)
```

Remember that, as these return Check instances, your custom checks can use all methods available to the built-in checks. For example, you can abort testing if your custom check fails:

```python
checklist_item = ChecklistItem("Custom check", my_custom_check().or_abort())
```

## Examples

### Between [min, max] checks passed

This example shows a check that makes sure at least `minimum` and at most `maximum` checks pass.

```python
from bs4 import BeautifulSoup
from typing import List
from validators.checks import Check

def interval_passed(minimum: int, maximum: int, checks: List[Check]) -> Check:
    def _inner(bs: BeautifulSoup) -> bool:
        passed_checks = 0
        
        # Run every check
        for check in checks:
            # If the current Check passed, increase the counter
            if check.callback(bs):
                passed_checks += 1

        return minimum <= passed_checks <= maximum

    return Check(_inner)
```

#### Usage

```python
suite = TestSuite("HTML", content)
html_element = suite.element("html")
body_element = html_element.get_child("body")

checklist_item = ChecklistItem("At least 1 and at most 2 checks passed",
                               interval_passed(1, 2, [
                                   html_element.exists(),
                                   body_element.exists(),
                                   body_element.has_child("div", id="example")
                               ])
                               )
```

### Element has a list of attributes

This example creates a check that makes sure an HTML element has at least the attributes provided in a list.

Note that this can already be achieved with built-in methods (using `utilities.all_of` and `Element.has_attribute`). The main purpose of this example is to show that you can also **simplify** specific use cases instead of inventing completely new checks.

```python
from bs4 import BeautifulSoup
from typing import List
from validators.checks import Check, Element


# The function takes the element and the list of attributes as arguments
def has_all_attributes(element: Element, attributes: List[str]) -> Check:
    def _inner(bs: BeautifulSoup) -> bool:
        # Iterate over every attribute
        for attr in attributes:
            # has_attribute is a Check itself, so we have to run it as well
            if not element.attribute_exists(attr).callback(bs):
                # Element didn't have this attribute, so return False
                return False

        # Element has all of the required attributes, so we can return True
        return True

    return Check(_inner)
```

#### Usage

```python
suite = TestSuite("HTML", content)
img_element = suite.element("img")

required_attributes = ["src", "alt", "width", "height"]
checklist_item = ChecklistItem("The <img> has the required attributes.",
                               has_all_attributes(img_element, required_attributes)
                               )
```