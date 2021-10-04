# Rendering HTML and CSS on Dodona

## Table of Contents

- [Dodona CSS artifacts](#dodona-css-artifacts)
- [Embedding images](#embedding-images)

The HTML Judge is capable of rendering the student's code in Dodona. HTML will **only** be shown if their HTML code was valid, and CSS will **only** be shown if **both** HTML **and** CSS were valid.

The built-in [`HtmlSuite`](default-suites.md#htmlsuite) or [`CssSuite`](default-suites.md#csssuite) already do this for you. `HtmlSuite` validates HTML, `CssSuite` validates both HTML and CSS.

```python
from validators.checks import CssSuite, TestSuite

def create_suites(content: str) -> List[TestSuite]:
    # CssSuite automatically validates both HTML and CSS
    suite = CssSuite(content)

    return [suite]
```

<details>
 <summary>Click <b>here</b> for how to check for validity with own instance of <code>TestSuite</code>.</summary>
When using an instance of <code>TestSuite</code>, this means it is required to check for validity at least <i>once</i>. In order to do this, the <code>validate_html</code> and <code>validate_css</code> checks can be used.  

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
</details>


## Dodona CSS artifacts

Keep in mind that there may be artifacts from Dodona's own CSS that are applied onto the student's submission. This _can_ result in the rendering not being 100% accurate, but has no influence on the tests being correct or not.

## Embedding images

Your students can embed images into their HTML using the `<img>` tag. The files for these images **must** be placed in `/description/media`, and **not in any subdirectories**. When rendering, the filepath your student uses will be parsed into one that works on Dodona, so they can store the images wherever they want locally. The judge checks if the filename of the image in the submission exists in the `/description/media` folder. This allows them to have an organized directory structure without having to worry about the file not being found.
