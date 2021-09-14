# Evaluators

This file contains information on how to write your own evaluators.

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