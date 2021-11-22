# Default TestSuites

This file contains information on TestSuites that handle some common behaviour for you. Using these can help reduce boilerplate code, and make your evaluators more compact.

Remember that these are still `TestSuite`s, so you can still **add your own ChecklistItems** to them. They merely provide defaults (e.g. HTML validation) behind the scenes, so you don't have to do it yourself every single time.

## Table of Contents

- [`HtmlSuite`](#htmlsuite)
- [`CssSuite`](#csssuite)
- [`Minimal HTML Template`](#minimal-html-template)

## `HtmlSuite`

The `HtmlSuite` will automatically create a TestSuite called "HTML", and add a `ChecklistItem` for **HTML** validation (along with the translations for this item).

### Attributes

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `content` | A string that contains the student's submission. This is passed as an argument into the `create_suites` method. |  ✔  |  |
| `check_recommended` | <a id="check-recommended-image"/> A boolean that indicates if the student should see warnings about missing recommended attributes.<br /><br /><img src="../media/warnings-dodona.png" alt="image: warnings on Dodona."> These warnings do **not** cause their submission to be marked incorrect, and are purely informational.<br /><br /> | | `True` |
| `allow_warnings` | Boolean that indicates that the check should *not* be marked incorrect if any warnings arise. |  | `True` |
| `abort` | Boolean that indicates that testing should abort (and all future checks should be marked incorrect) when validation fails. This is default `True`, because you usually don't want to keep evaluating an exercise if the code isn't valid. |  | `True` |
| `check_minimal` | Boolean that indicates that the [minimal HTML code](#minimal-html-template) required for a valid document should be present. Shortcut to adding 8 checks manually. | | `False` |

#### Example usage

The example below shows the code required *before* and *after* using this custom suite.

**Without the HtmlSuite**:

```python
from typing import List
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

**With the HtmlSuite**:

```python
from typing import List
from validators.checks import HtmlSuite, TestSuite


def create_suites(content: str) -> List[TestSuite]:
    html_suite = HtmlSuite(content, allow_warnings=False)

    return [html_suite]
```

## `CssSuite`

The `CssSuite` will automatically create a TestSuite called "CSS", and add `ChecklistItem`s for **HTML** and **CSS** validation (along with the translations for those items).

### Attributes

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `content` | A string that contains the student's submission. This is passed as an argument into the `create_suites` method. |  ✔  |  |
| `check_recommended` | <a id="check-recommended-image"/> A boolean that indicates if the student should see warnings about missing recommended attributes.<br /><br /><img src="../media/warnings-dodona.png" alt="image: warnings on Dodona."> These warnings do **not** cause their submission to be marked incorrect, and are purely informational.<br /><br /> | | `True` |
| `allow_warnings` | Boolean that indicates that the check should *not* be marked incorrect if any warnings arise. |  | `True` |
| `abort` | Boolean that indicates that testing should abort (and all future checks should be marked incorrect) when validation fails. This is default `True`, because you usually don't want to keep evaluating an exercise if the code isn't valid. |  | `True` |
| `check_minimal` | Boolean that indicates that the [minimal HTML code](#minimal-html-template) required for a valid document should be present. Shortcut to adding 8 checks manually. | | `False` |

#### Example usage

The example below shows the code required *before* and *after* using this custom suite.

**Without the CssSuite**:

```python
from typing import List
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

**With the CssSuite**:

```python
from typing import List
from validators.checks import CssSuite, TestSuite


def create_suites(content: str) -> List[TestSuite]:
    css_suite = CssSuite(content, allow_warnings=False)

    return [css_suite]

    # Or even shorter in case you only want validation:
    # return [CssSuite(content, allow_warnings=False)]
```

## `Minimal HTML Template`

Both the [`HtmlSuite`](#htmlsuite) and the [`CssSuite`](#csssuite) have a `check_minimal`-kwarg that checks if the code below is present in the submission:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <!--  Any non-empty title suffices  -->
    <title>Document</title>
</head>
<body>
    
</body>
</html>
```