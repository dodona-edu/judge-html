# Default TestSuites

This file contains information on TestSuites that handle some common behaviour for you. Using these can help reduce boilerplate code, and make your evaluators more compact.

Remember that these are still `TestSuite`s, so you can still **add your own ChecklistItems** to them. They merely provide defaults (eg. HTML validation) behind the scenes, so you don't have to do it yourself every single time.

## Table of Contents
- [`CssSuite`](#csssuite)
- [`HTMLSuite`](#htmlsuite)

## `CssSuite`

The `CssSuite` will automatically create a TestSuite called "CSS", and add `ChecklistItem`s for `HTML` and `CSS` validation (along with the translations for those items).

Note that this class will `abort` in case the HTML or CSS are invalid. This is because you usually don't want to keep evaluating an exercise if the code is not valid to begin with.

### Attributes

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `content` | A string that contains the student's submission. This is passed as an argument into the `create_suites` method. |  ✔  |  |
| `check_recommended` | <a id="check-recommended-image"/> A boolean that indicates if the student should see warnings about missing recommended attributes.<br /><br /><img src="../media/warnings-dodona.png" alt="image: warnings on Dodona."> These warnings do **not** cause their submission to be marked incorrect, and are purely informational.<br /><br /> | | `True` |
| `allow_warnings` | Boolean that indicates that the check should *not* be marked incorrect if any warnings arise. |  | `True` |

#### Example usage:

The example below shows the code required *before* and *after* using this custom suite.

Before:

```python
from validators.checks import TestSuite


def create_suites(content: str) -> List[TestSuite]:
    css_suite = TestSuite("CSS", content)
    
    # Create ChecklistItems
    css_suite.make_item("The HTML is valid.", css_suite.validate_html(allow_warnings=False).or_abort())
    css_suite.make_item("The CSS is valid.", css_suite.validate_css().or_abort())
    
    # Add English translation
    css_suite.translations["en"] = [
        "The HTML is valid.",
        "The CSS is valid."
    ]
    
    # Add Dutch translation
    css_suite.translations["nl"] = [
        "De HTML is geldig.",
        "De CSS is geldig."
    ]
    
    return [css_suite]
```

After:

```python
from validators.checks import CssSuite, TestSuite


def create_suites(content: str) -> List[TestSuite]:
    css_suite = CssSuite(content, allow_warnings=False)

    return [css_suite]

    # Or even shorter in case you only want validation:
    # return [CssSuite(content, allow_warnings=False)]
```

## `HTMLSuite`

The `HTMLSuite` will automatically create a TestSuite called "HTML", and add a `ChecklistItem` for `HTML` validation (along with the translations for this item).

Note that this class will `abort` in case the HTML is invalid. This is because you usually don't want to keep evaluating an exercise if the code is not valid to begin with.

### Attributes

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `content` | A string that contains the student's submission. This is passed as an argument into the `create_suites` method. |  ✔  |  |
| `check_recommended` | <a id="check-recommended-image"/> A boolean that indicates if the student should see warnings about missing recommended attributes.<br /><br /><img src="../media/warnings-dodona.png" alt="image: warnings on Dodona."> These warnings do **not** cause their submission to be marked incorrect, and are purely informational.<br /><br /> | | `True` |
| `allow_warnings` | Boolean that indicates that the check should *not* be marked incorrect if any warnings arise. |  | `True` |

#### Example usage:

The example below shows the code required *before* and *after* using this custom suite.

Before:

```python
from validators.checks import TestSuite


def create_suites(content: str) -> List[TestSuite]:
    html_suite = TestSuite("HTML", content)
    
    # Create ChecklistItem
    html_suite.make_item("The HTML is valid.", html_suite.validate_html(allow_warnings=False).or_abort())
    
    # Add English translation
    html_suite.translations["en"] = [
        "The HTML is valid.",
    ]
    
    # Add Dutch translation
    html_suite.translations["nl"] = [
        "De HTML is geldig.",
    ]
    
    return [html_suite]
```

After:

```python
from validators.checks import HTMLSuite, TestSuite


def create_suites(content: str) -> List[TestSuite]:
    html_suite = HTMLSuite(content, allow_warnings=False)

    return [html_suite]

    # Or even shorter in case you only want validation:
    # return [HTMLSuite(content, allow_warnings=False)]
```
