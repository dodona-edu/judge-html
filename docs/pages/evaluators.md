# Evaluate in checklist mode with `evaluator.py`

This file contains information on how to write your own evaluators.

## Required format

All evaluators should follow a strict interface: the file should always be called **`evaluator.py`**, and in addition has to follow these rules:

- `evaluator.py` should contain a `create_suites` function.
- This function should take a `string`, being the student's submission, and return a `list` of `TestSuite`s.
- The `list` should contain **at least one** `TestSuite`.
- The file should import `validators` directly, without any packages above it. To do this, we recommend placing the library at the **root** of your project in which you write the evaluators.
- **Important: do NOT add `print()`s in your evaluator!** The Judge communicates with Dodona using console output, and printing your own things here will cause exceptions because Dodona can't parse them.

The fragment below contains the [boilerplate](https://en.wikipedia.org/wiki/Boilerplate_code) to make an evaluator:

> `evaluator.py`
>
> ```python
> from typing import List
> from validators.checks import HtmlSuite, CssSuite, TestSuite, ChecklistItem
> 
> 
> def create_suites(content: str) -> List[TestSuite]:
>     html = HtmlSuite(content)
>     css = CssSuite(content)
>
>     # Add checks here
> 
>     return [html, css]
> ```

_Take a look at the [built-in TestSuites documentation](default-suites.md) which show how to write your own custom TestSuites with(out) validation._

*[Emmet syntax](emmet-syntax.md) is supported on selected methods, which allows for fast development of checklists.*

In case you only want to write tests for either `HTML` or `CSS`, and not both, the other suite is not required. It is merely added in the fragment above as an example. Returning `[html]` is equally valid.
