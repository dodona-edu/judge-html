# Rendering HTML and CSS on Dodona

The HTML Judge is capable of rendering the student's code in Dodona. HTML will **only** be shown if their HTML code was valid, and CSS will **only** be shown if **both** HTML **and** CSS were valid.

This means it is required to check for validity at least _once_ when using the `TestSuite`. In order to do this, the `validate_html` and `validate_css` checks can be used.

```python
from validators.checks import TestSuite, ChecklistItem

def create_suites(content: str) -> List[TestSuite]:
    suite = TestSuite("CSS", content)
    
    # Create a ChecklistItem that validates HTML and CSS
    suite.make_item("The HTML and CSS are valid.",
                    suite.validate_html(),
                    suite.validate_css()
                    )

    # ... other checks
    
    return [suite]
```

Alternatively, use the built-in [`HtmlSuite`](default-suites.md#htmlsuite) or [`CssSuite`](default-suites.md#csssuite) that already do this for you. `HtmlSuite` validates `HTML`, `CssSuite` validates both.

```python
from validators.checks import CssSuite, TestSuite

def create_suites(content: str) -> List[TestSuite]:
    # CssSuite automatically validates both HTML and CSS
    suite = CssSuite(content)

    return [suite]
```

## Dodona CSS artifacts

Keep in mind that there may be artifacts from Dodona's own CSS that are applied onto the student's submission. This _can_ result in the rendering not being 100% accurate, but has no influence on the tests being correct or not.

## Embedding images

Your students can embed images into their HTML using the `<img>` tag. The files for these images **must** be placed in `/description/media`, and **not in any subdirectories**. When rendering, the filepath your student uses will be parsed into one that works on Dodona, so they can store the images wherever they want locally. This allows them to have an organized directory structure without having to worry about the file not being found.
