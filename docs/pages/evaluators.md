# Evaluators

This file contains information on how to write your own evaluators.

## Required format

All evaluators should follow a strict interface: the file should always be called **`evaluator.py`**, and in addition has to follow these rules:

- Contain a `create_suites` function
- This function should take a `string`, being the student's submission, and return a `list` of `TestSuite`s
- The `list` should contain **at least one** `TestSuite`
- The file should import `validators` directly, without any packages above it. To do this, we recommend placing the library at the **root** of your project in which you write the evaluators.
- **Important: do NOT add `print()`s in your evaluator!** The Judge communicates with Dodona using console output, and printing your own things here will cause exceptions because Dodona can't parse them.

The fragment below contains the [boilerplate](https://en.wikipedia.org/wiki/Boilerplate_code) to make an evaluator:

> `evaluator.py`
>
> ```python
> from typing import List
> from validators import checks
> 
> 
> def create_suites(content: str) -> List[checks.TestSuite]:
>     html = checks.TestSuite("HTML", content)
>     css = checks.TestSuite("CSS", content)
> 
>     return [html, css]
> ```

_Don't forget to take a look at the [built-in TestSuites](default-suites.md) that can simplify this even further!_

In case you only want to write tests for either `HTML` or `CSS`, and not both, the other suite is not required. It is merely added in the fragment above as an example. Returning `[html]` is equally valid.
