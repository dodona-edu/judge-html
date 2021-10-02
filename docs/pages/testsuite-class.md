# TestSuite Class

A `TestSuite` contains a checklist of all checks that should be performed on the student's code. An exercise is only marked as correct once every check in every `TestSuite` has passed.

**Note**: There are a few built-in implementations of TestSuites that already handle some common behaviour for you automatically. We strongly recommend you to take a look at these, as you will most likely use these in almost every exercise. Creating an instance of `TestSuite` should only be done when you don't want any behaviour such as `validation`. See [`Default TestSuites`](default-suites.md) for more information.

## Table of Contents
- [Attributes](#attributes)
- [`TestSuites` on Dodona](#testsuites-on-dodona)
- [Referencing (specific) HTML elements](#referencing-specific-html-elements)
- [Referencing multiple HTML elements](#referencing-multiple-html-elements)
- [Adding items to the checklist](#adding-items-to-the-checklist)
- [Adding multiple languages](#adding-multiple-languages)
- [Built-in Checks](#built-in-checks)
  - [`validate_css`](#validate_css)
  - [`validate_html`](#validate_html)
  - [`contains_comment`](#contains_comment)
  - [`document_matches`](#document_matches)
  - [`has_doctype`](#has_doctype)

## Attributes

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `name` | The name of this `TestSuite`, used as the name of the Tab on Dodona (see [`TestSuites` on Dodona](#testsuites-on-dodona)) |  ✔ | |
| `content` | A string that contains the student's submission. This is passed as an argument into the `create_suites` method. |  ✔  |  |
| `check_recommended` | <a id="check-recommended-image"/> A boolean that indicates if the student should see warnings about missing recommended attributes.<br /><br /><img src="../media/warnings-dodona.png" alt="image: warnings on Dodona."> These warnings do **not** cause their submission to be marked incorrect, and are purely informational.<br /><br /> | | `True` |

## `TestSuites` on Dodona

`TestSuites` are displayed as **tabs** on Dodona, and the `name` attribute will be the name of the tab. The names can be whatever you want them to be, but the examples here will always use "HTML" and "CSS" for consistency. The image below shows what this would look like for two suites named `HTML` and `CSS`:

```python
from validators.checks import TestSuite

def create_suites(content: str):
    html_suite = TestSuite("HTML", content)
    css_suite = TestSuite("CSS", content)
    return [html_suite, css_suite]
```

![image: TestSuites visualized on Dodona](../media/tabs.png)

The image also shows a `1` next to the **HTML** tab, indicating that 1 test failed. This instantly allows users to see which part of their code caused the exercise to be incorrect, and which parts are already finished.

## Referencing (specific) HTML elements

**This method supports [`Emmet Syntax`](emmet-syntax.md) through the `tags` parameter**

You can get a specific HTML element by tag using `suite.element(tag)` in the form of an instance of the `Element` class (explained later). Afterwards, you can use this reference to create extra checks based off of it.

#### Signature
```python
def element(tag: Optional[Union[str, Emmet]] = None, index: int = 0, from_root: bool = False, **kwargs) -> Element
```

#### Parameters

| Name     | Description                                                                                                                                            | Required? | Default                                 |
:----------|:-------------------------------------------------------------------------------------------------------------------------------------------------------|:---------:|:----------------------------------------|
| `tag`    | The tag to search for.                                                                                                                                  |           | None, which won't filter based on tags. |
| `index`  | In case multiple children match your query, choose which match should be chosen. If the index goes out of range, an empty element is returned instead. |           | 0 (first match)                         |
| `from_root` | Boolean that indicates only children of the root element should be searched.                                                                        |           | False                                   |

#### Example usage

The example below shows how to get the `<html>` tag:

```html
<html lang="en">
    <body>
        ...
    </body>
</html>
```

```python
suite = TestSuite("HTML", content)
html_tag = suite.element("html")
```

Searching will start from the root element, and work in a breadth-first way recursively. In case you want to disable this and only search the root of the tree, you can pass `from_root=True` into the function.

The example below shows how to get the `<div>` at the root of the tree, not the one that comes first in the file but is nested deeper.

```html
<span>
    <!-- We don't want this div -->
    <div>
        ...
    </div>
</span>
<!-- We want THIS div -->
<div>
    ...
</div>
```

```python
suite = TestSuite("HTML", content)

# from_root=True: only check children of the root node, so ignore the very first (nested) <div>
root_div = suite.element("div", from_root=True)
```

In case multiple elements were matched, you can specify which one should be chosen using the `index` parameter.

The example below shows how to get the third `<tr>`.

```html
<tbody>
<!-- We don't want this tr -->
<tr>
  ...
</tr>
<!-- We don't want this tr -->
<tr>
  ...
</tr>
<!-- We want THIS tr -->
<tr>
  ...
</tr>
</tbody>
```

```python
suite = TestSuite("HTML", content)

# index=2: take the third element in case it exists
root_div = suite.element("div", index=2)
```

Extra filters, such as id's and attributes, can be passed as _kwargs_. You can pass as many filters as you want to.

The example below shows how to get the `<tr>` with id `row_one`, and the `<th>` with attribute `colspan` equal to `2`.

```html
<table>
    <!-- We don't want this tr -->
    <tr id="header">
        <!-- We don't want this th -->
        <th>Wrong Header</th>
        
        <!-- We want THIS th -->
        <th colspan="2">Correct Header</th>
    </tr>
     <!-- We want THIS tr -->
    <tr id="row_one">
        ...
    </tr>
</table>
```

```python
suite = TestSuite("HTML", content)

tr_one = suite.element("tr", id="row_one")
th_colspan = suite.element("th", colspan="2")
```

Remember that values should be `strings`.

In case an attribute only has to *exist*, and the value doesn't matter, set the value to `True`. In the example above, this would mean that you request the students have at least one `<th>` with a `colspan` attribute, no matter how big it may be. The code for this would be `suite.element("th", colspan=True)`

For `class`es, as "class" is a built-in keyword in Python, use `class_` with an **underscore** after it (`element(class_="some_value")`).

## Referencing multiple HTML elements

**This method supports [`Emmet Syntax`](emmet-syntax.md) through the `tags` parameter**

In case you want to get a list of all elements (optionally matching filters), use `suite.all_elements` instead. This method takes the exact same arguments as `elements`, and thus the same filters can be applied.

Note that this method returns an instance of `ElementContainer`, which can be used like a regular Python `list`:

More info on `ElementContainer`s can be found in the respective [documentation page](elementcontainer-class.md).

## Adding items to the checklist

In order to add `ChecklistItem`s, you can either set the entire checklist at once, or add separate `ChecklistItem`s one by one.

Adding items one by one can either be done by adding them to the internal checklist (`TestSuite.checklist.append(item)`) or by using the shortcuts `TestSuite.add_item(item)` and `TestSuite.make_item(message, checks)`. Just like the constructor of `ChecklistItem`, `make_check` can take both a variable amount of `Checks` and a `List` of `Check`s.

If you want to add a `ChecklistItem` by comparing the submission to an emmet expression, you can use `TestSuite.make_item_from_emmet(message, emmet_str)`.
You can find more documentation about the Emmet Syntax [here](emmet-syntax.md).

```python
suite = TestSuite("HTML", content)

first_item = ChecklistItem("Item 1", check1)
second_item = ChecklistItem("Item 2", check2, check3)

# Directly setting the list content
suite.checklist = [first_item, second_item]

# Adding the items one by one
suite.checklist.append(first_item)
# TestSuite.add_item is a shortcut to TestSuite.checklist.append()
suite.add_item(second_item)

# TestSuite.make_item is a shortcut to create a ChecklistItem inline
# The line below is equal to suite.add_item(ChecklistItem("Item 3", check1, check2, check3))
suite.make_item("Item 3", check1, check2, check3)

# Adding a ChecklistItem from an emmet expression
suite.make_item_from_emmet("Item 4", "body>div#mydiv")

# Just like make_item, this can take multiple arguments that will be grouped under one ChecklistItem
suite.make_item_from_emmet("Item 5", "body>div#mydiv", "body>table>tr*4", "body>.classname", ...)
```

## Adding multiple languages

It's possible that your course might have students from different countries, and you'd like to give feedback in more than one language. You can do this by using the `translations` attribute.

`translations` is a `dict` that maps a two-letter language code (`string`, **lowercase**) to a `list` of `string`s. In case the student's own language was not found in the `dict`, the message that you pass to the `ChecklistItem` will be used as the default. In case the list for the student's language doesn't contain *enough* elements, the remaining items will also use their default message. Excess elements are ignored.

Accepted languages are currently `nl` and `en`.

```python
from validators.checks import TestSuite, ChecklistItem

def create_suites(content: str):
    html_suite = TestSuite("HTML", content)

    # Check that the HTML is valid, the default message is in English here
    valid_check = ChecklistItem("The HTML is valid.", html_suite.validate_html())
    html_suite.add_item(valid_check)
    
    # Add Dutch translation
    html_suite.translations["nl"] = [
      "De HTML is geldig."
    ]
    
    return [html_suite]
```

In case the supplied list of translations is shorter than the checklist, the checks that don't have a translation will fall back to the message that was passed to the ChecklistItem.

## Built-in Checks

The `TestSuite` class comes with a few Checks that you can use, and they are documented below. More Checks can be found in different classes.

### `validate_css`

Check that the code between the `<style>`-tag of the submission is valid CSS. If no style tag is present, this Check will also pass.

#### Signature
```python
def validate_css() -> Check
```

#### Example usage
```python
suite = TestSuite("CSS", content)
css_valid = ChecklistItem("The CSS is valid.", suite.validate_css())
```

### `validate_html`

Check that the student's submitted code is valid HTML without syntax errors. The errors will not be reported to the student as to not reveal the answer.

#### Signature
```python
def validate_html(allow_warnings: bool = True) -> Check
```

#### Parameters

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `allow_warnings` | Boolean that indicates that the check should *not* be marked incorrect if any warnings arise. |  | `True` |

In case the `check_recommended` attribute for this class is `True` (default), this will also show the student warnings about missing recommended attributes (see [Attributes](#check-recommended-image)).

#### Example usage
```python
suite = TestSuite("HTML", content)
html_valid = ChecklistItem("The HTML is valid.", suite.validate_html())
```

### `contains_comment`

Check if there is a comment inside of this document, optionally with an exact value. Not passing a value will make any comment pass the check.

#### Signature
```python
def contains_comment(comment: Optional[str] = None) -> Check
```

#### Parameters

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `comment` | The value to look for. |  | None, which will accept any comment. |

#### Example usage

```python
suite = TestSuite("HTML", content)

# Check if the document contains at least one comment
suite.contains_comment()

# Check if the document contains a comment that says "Example"
suite.contains_comment("Example")
```

### `document_matches`

Check that the student's submitted code matches a `regex string`.

#### Signature
```python
def document_matches(regex: str, flags: Union[int, re.RegexFlag] = 0) -> Check
```

#### Parameters

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `regex` | The pattern to match the student's code against. |  ✔  |  |
| `flags` | Extra `RegexFlag`s to use when comparing. |  | 0, meaning no flags will be applied. |

#### Example usage

```python
suite = TestSuite("HTML", content)

pattern = r".*<[^>]+/>.*"
self_closing = ChecklistItem("The document contains at least one self-closing tag.", suite.document_matches(pattern))
```

### `has_doctype`

Check that the document has the `<!DOCTYPE html>` declaration. This declaration is **not** case sensitive and must always be at the first non-empty line.

#### Signature
```python
def has_doctype() -> Check
```

#### Example usage

```python
suite = TestSuite("HTML", "<!DOCTYPE html>")

has_doctype = ChecklistItem("The document has the correct DOCTYPE declaration.", suite.has_doctype())
```