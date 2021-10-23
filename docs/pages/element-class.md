# Element Class

The `Element` class contains a reference to an HTML element in the student's code. If this element doesn't exist, it will be empty, but can still be used. All checks performed on it will just fail, and the list of children will be empty.

This class is **not** meant for you to instantiate manually, but instances are returned by the library instead.

## Table of Contents

- [HTML-related methods](#html-related-methods)
  - [`get_child()`](#get_child)
  - [`get_children()`](#get_children)
- [Built-in Checks](#built-in-checks)
  - [`attribute_contains()`](#attribute_contains)
  - [`attribute_exists()`](#attribute_exists)
  - [`attribute_matches()`](#attribute_matches)
  - [`exists()`](#exists)
  - [`has_child()`](#has_child)
  - [`has_content()`](#has_content)
  - [`has_tag()`](#has_tag)
  - [`has_outgoing_url()`](#has_outgoing_url)
  - [`has_url_with_fragment()`](#has_url_with_fragment)
  - [`contains_comment()`](#contains_comment)
  - [`no_loose_text()`](#no_loose_text)
- [table-related utility functions](#table-related-utility-functions)
  - [`has_table_content()`](#has_table_content)
  - [`has_table_header()`](#has_table_header)
  - [`table_row_has_content()`](#table_row_has_content)
- [CSS-related methods](#css-related-methods)
  - [`has_styling()`](#has_styling)
  - [`has_color()`](#has_color)

## HTML-related methods

The following methods can be used to obtain references to extra HTML elements starting from another one.

### `get_child()`

**This method supports [`Emmet Syntax`](emmet-syntax.md) through the `tag` parameter.**

This method finds a child element with tag `tag`, optionally with extra filters.

#### Signature

```python
def get_child(tag: Optional[Union[str, Emmet]] = None, index: int = 0, direct: bool = True, **kwargs) -> Element
```

#### Parameters

| Name     | Description                                                                                                                                            | Required? | Default                                 |
:----------|:-------------------------------------------------------------------------------------------------------------------------------------------------------|:---------:|:----------------------------------------|
| `tag`    | The tag to search for, if necessary.                                                                                                                   |           | `None`, which won't filter based on tags. |
| `index`  | In case multiple children match your query, choose which match should be chosen. If the index goes out of range, an empty element is returned instead. |           | `0` (first match)                         |
| `direct` | Boolean that indicates only *direct* children should be searched, so not nested elements.                                                              |           | `True`                                  |

Extra `kwargs` can be passed to filter the results down even more. For example, to find the child with a given `id` use `get_child(tag, id="some_id")`. For `class`es, as "class" is a built-in keyword in Python, use `class_` with an **underscore** after it (`get_child(class_="some_value")`).

#### Example usage

```python
suite = HtmlSuite(content)
body = suite.element("body")

# Find the second <img> inside the body with attribute "height" equal to 500,
# which can be nested in another element
img_element = body.get_child("img", index=1, direct=False, height="500")

# Examples with a kwarg
p_element = body.get_child("p", id="myHeader")  
img_element_with_alt = body.get_child("img", alt="This is a cat.")
```

### `get_children()`

**This method supports [`Emmet Syntax`](emmet-syntax.md) through the `tag` parameter.**

This method finds ALL child elements, optionally with tag `tag` and extra filters. This returns an instance
of `ElementContainer`, which can be used as a list of elements.

#### Signature

```python
def get_children(tag: Optional[Union[str, Emmet]] = None, direct: bool = True, **kwargs) -> ElementContainer
```

#### Parameters

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `tag` | The tag to search for. | | `None`, which won't filter based on tags. |
| `direct` | Boolean that indicates only *direct* children should be searched, so not nested elements. | | `True` |

Extra `kwargs` can be passed to filter the results down even more. For example, to find all children with a given `attribute` use `get_children(attribute="some_value")`. For `class`es, as "class" is a built-in keyword in Python, use `class_` with an **underscore** after it (`get_children(class_="some_value")`).

#### Example usage

```python
suite = HtmlSuite(content)
body = suite.element("body")

# Find all <p>'s with title "Example"
p_elements = body.get_children("p", direct=False, title="Example")

p_warning_elements = body.get_child("p", class_="warning")  # example with kwarg
```

## Built-in Checks

The following methods are Checks that can be used on HTML elements, in order to create specific requirements for your
students to pass the exercise. All of these methods return an instance of the `Check` class.

### `attribute_contains()`

Check that this element has a given attribute, and that the attribute contains a substring. If the element doesn't exist, this check will fail as well. This means it's *not* required to use `attribute_exists` before `attribute_contains`.

#### Signature

```python
def attribute_contains(attr: str, substr: str, case_insensitive: bool = False) -> Check
```

#### Parameters

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `attribute`        | The attribute to check for.                                          |     ✔     |         |
| `substr`           | The substring that should be in the attribute's value.               |     ✔     |         |
| `case_insensitive` | Indicate that the casing of the value does not matter when checking. |           | `False` |

#### Example usage

```python
suite = HtmlSuite(content)
body = suite.element("body")
img_element = body.get_child("img")

# Check if the src of the image contains "dodona".
img_attributes = ChecklistItem("The image's src contains \"dodona\".", [
    img_element.attribute_contains("src", "dodona"),
])
```

### `attribute_exists()`

Check that this element has a given attribute, optionally matching a specific value.

#### Signature

```python
def attribute_exists(attr: str, value: Optional[str] = None, case_insensitive: bool = False) -> Check
```

#### Parameters

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `attribute`        | The attribute to check for. | ✔ | |
| `value`            | The value to compare against. | | `None`, which will make any value pass. This means the check only makes sure the attribute *exists*. |
| `case_insensitive` | Indicate that the casing of the value does not matter when checking. | | `False` |

#### Example usage

```python
suite = HtmlSuite(content)
body = suite.element("body")
img_element = body.get_child("img")

# Check if the image has the src and alt attributes, and a width of 500.
img_attributes = ChecklistItem("The image has the correct attributes.", [
    img_element.attribute_exists("src"),
    img_element.attribute_exists("alt"),
    img_element.attribute_exists("width", "500")
])
```

### `attribute_matches()`

Check if an attribute exists, and if its value matches a regular expression. If the element doesn't exist, this check will fail as well. This means it's *not* required to use `attribute_exists` before `attribute_matches`.

#### Signature

```python
def attribute_matches(attr: str, regex: str, flags: Union[int, re.RegexFlag] = 0) -> Check
```

#### Parameters

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `attribute` | The attribute to check for.                               |  ✔ |                                      |
| `regex`     | The regex pattern to match the attribute's value against. |  ✔ |                                      |
| `flags`     | Extra `RegexFlag`s to use when comparing.                 |    | `0`, meaning no flags will be applied. |

#### Example usage

```python
import re

suite = HtmlSuite(content)
body = suite.element("body")
img_element = body.get_child("img")

# Check if the src of the image starts with "https://", contains "dodona", and ends on ".png", case-insensitive.
pattern = r"^https://.*dodona.*\.png$"
img_attributes = ChecklistItem("The image has the correct attributes.", [
    img_element.attribute_matches("src", pattern, re.IGNORECASE),
])
```

### `exists()`

Check that an element exists, and is not empty. This is equivalent to verifying that an element was found in the
student's code.

#### Signature

```python
def exists() -> Check
```

#### Example usage

```python
suite = HtmlSuite(content)
body = suite.element("body")

body_exists = ChecklistItem("The document has a <body>", body.exists())
```

### `has_child()`

Check that the element has a child that meets the specifications. This is a shortcut to combining `get_child()`
and `exists()`.

**This method supports [`Emmet Syntax`](emmet-syntax.md) through the `tag` parameter.**

#### Signature

```python
def has_child(tag: Optional[Union[str, Emmet]] = None, direct: bool = True, **kwargs) -> Check
```

#### Parameters

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `tag`    | The tag to search for.                                                                    |           | `None`, which will make any child element pass.        |
| `direct` | Boolean that indicates only *direct* children should be searched, so not nested elements. |           | `True` |

Extra `kwargs` can be passed to filter the results down even more. For example, to check that an element has a child
with a given `id` use `has_child(tag, id="some_id")`.

#### Example usage

```python
suite = HtmlSuite(content)
body = suite.element("body")

# Check that the body has a child div
body_has_div = ChecklistItem("The body has a div", body.has_child("div"))

# Equivalent to
body_has_div = ChecklistItem("The body has a div", body.get_child("div").exists())

# Passing extra filters through kwargs
body_has_header_with_id = ChecklistItem("The body has a header with id", body.has_child("h1", id="myHeader"))
```

### `has_content()`

Check that the element has specific content, or any content at all.

This check **ignores** leading and trailing whitespace, and replaces all other whitespace by a single space. The reason
behind this is that HTML does the same, so these spaces shouldn't matter.

This means that

```python
x = "this text" 
```

and

```python
y = "    \t\n     this \t\n\n\t                text           "
```

are considered to be **equal**.

#### Signature

```python
def has_content(text: Optional[str] = None, case_insensitive: bool = False) -> Check
```

#### Parameters

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `text` | The text to compare the element's content to. |           | `None`, which will make any content pass and just checks if the content is not empty. |
| `case_insensitive` | Indicate that the casing of the value does not matter when checking. |           | `False` |

#### Example usage

```python
suite = HtmlSuite(content)
body = suite.element("body")

# Create references to the elements
first_p = body.get_child("p", index=0)
second_p = body.get_child("p", index=1)

# Check that the first <p> has the text "Hello" and the second has anything inside of it
paragraphs_exist = ChecklistItem("The body has two paragraphs that meet the requirements", [
    first_p.has_content("Hello"),
    second_p.has_content()
])
```

### `has_tag()`

Check that this element has the required tag.

#### Signature

```python
def has_tag(tag: str) -> Check
```

#### Parameters

| Name | Description           | Required? | Default |
|:-----|:----------------------|:---------:|:--------|
| `tag`  | The tag to check for. |     ✔     |         |

#### Example usage

```python
suite = HtmlSuite(content)
body = suite.element("body")
body_children = body.get_children()

# Verify that the first child of the body is a <table>
# and the second a <div>
body_structure = ChecklistItem("The body has a table followed by a div.", [
    body_children[0].has_tag("table"),
    body_children[1].has_tag("div")
])
```

### `has_outgoing_url()`

Check that this element has a url that doesn't go to another domain, optionally with a `list` of domains that you want
to allow.

#### Signature

```python
def has_outgoing_url(allowed_domains: Optional[List[str]] = None, attr: str = "href") -> Check
```

#### Parameters

| Name      | Description                                     | Required? | Default                                           |
|:----------|:------------------------------------------------|:---------:|:--------------------------------------------------|
| `allowed_domains`  | An optional list of domains that should *not* be considered "outgoing". |           | `None`, which will default to `["dodona.ugent.be", "users.ugent.be"]`. If you don't want to allow those domains either, simply pass an `empty list` (`[]`). |
| `attr` | The attribute the link should be in, which allows this to be used on multiple types of tags. For example, `<a>`-tags (`attr="href"`) and `<img>`-tags (`attr="src"`). | | `"href"`, used in `<a>`-tags. |

#### Example usage

```python
suite = HtmlSuite(content)
body = suite.element("body")
# href=True means the child should have an href attribute, no matter the value
a_tag = body.get_child("a", href=True)

a_tag.has_outgoing_link(allowed_domains=["ugent.be"])
```

### `has_url_with_fragment()`

Check that this element has a url with a fragment (`#`), optionally comparing the fragment to a `string` that it should
match exactly.

In case the element is not an `<a>`-tag or does not have an `href` attribute, this will also return `False`.

#### Signature

```python
def has_url_with_fragment(fragment: Optional[str] = None) -> Check
```

#### Parameters

| Name      | Description                                     | Required? | Default                                           |
|:----------|:------------------------------------------------|:---------:|:--------------------------------------------------|
| `fragment`  | An optional fragment that should match exactly. |           | `None`, which will make any non-empty fragment pass.|

#### Example usage

```python
suite = HtmlSuite(content)
body = suite.element("body")
# href=True means the child should have an href attribute, no matter the value
a_tag = body.get_child("a", href=True)

a_tag.has_url_with_fragment()
```

### `contains_comment()`

Check if there is a comment inside of this element, optionally with an exact value. Not passing a value will make any
comment pass the check.

#### Signature

```python
def contains_comment(comment: Optional[str] = None) -> Check
```

#### Parameters

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `comment` | The value to look for. |  | `None`, which will accept any comment. |

#### Example usage

```python
suite = HtmlSuite(content)
body = suite.element("body")

# Check if the body contains at least one comment
body.contains_comment()

# Check if the body contains a comment that says "Example"
body.contains_comment("Example")
```

### `no_loose_text()`

Check that this element has no text inside of it that is not inside of another element. Examples include random text
floating around inside of a `<tr>` instead of a `<td>`.

#### Signature

```python
def no_loose_text() -> Check
```

#### Example usage

```python
suite = HtmlSuite(content)
table_element = suite.element("table")

# Verify that the table doesn't have any text inside of it
table_element.no_loose_text()
```

## table-related utility functions

## `has_table_content()`

This method checks if an `Element` with tag `table` has rows (`tr`) with the required content in `td`, **excluding the header (assuming first row)**.

#### Signature

```python
def has_table_content(rows: List[List[str]], has_header: bool = True, case_insensitive: bool = False) -> Check
```

#### Parameters

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `rows` | A 2D `list` of `strings` that represents the content that the rows should match exactly. | ✔ |  |
| `has_header` | Boolean that indicates this table should have a `header`, in which case the first `<tr>` will be ignored.  |  | `True` |
| `case_insensitive` | Indicate that the casing of the value does not matter when checking. |           | `False` |

#### Example usage

```html
<table>
    <tr>
        <th>Header 1</th>
        <th>Header 2</th>
    </tr>
    <tr>
        <td>Row 1 Col 1</td>
        <td>Row 1 Col 2</td>
    </tr>
    <tr>
        <td>Row 2 Col 1</td>
        <td>Row 2 Col 2</td>
    </tr>
</table>
```

```python
suite = HtmlSuite(content)
table_element = suite.element("table")

rows = [
    ["Row 1 Col 1", "Row 1 Col 2"],
    ["Row 2 Col 1", "Row 2 Col 2"]
]
table_element.has_table_content(rows, has_header=True)
```

## `has_table_header()`

This method checks if an `Element` with tag `table` has a header (all `th` tags of the table) with content that matches a list of strings. This avoids having to use `all_of` combined with a *LOT* of `has_content`s.

#### Signature

```python
def has_table_header(header: List[str]) -> Check
```

#### Parameters

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `header` | `List` of `strings` that represents the content that the header should match exactly. | ✔ |  |

#### Example usage

```html
<table>
    <tr>
        <th>Header 1</th>
        <th>Header 2</th>
        <th>Header 3</th>
        <th>Header 4</th>
    </tr>
</table>
```

```python
suite = HtmlSuite(content)
table_element = suite.element("table")

header = ["Header 1", "Header 2", "Header 3", "Header 4"]
table_element.has_table_header(header)
```

## `table_row_has_content()`

This method checks if an `Element` with tag `tr` has the required content. This is the same as [`has_table_content()`](#has_table_content) but for one row, and applied on a `<tr>` instead of a `<table>`.

#### Signature

```python
def table_row_has_content(row: List[str], case_insensitive: bool = False) -> Check
```

#### Parameters

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `row` | A `list` of `strings` that represents the content that the row should match exactly. | ✔ |  |
| `case_insensitive` | Indicate that the casing of the value does not matter when checking. |           | `False` |

#### Example usage

```html
<table>
    <tr>
        <td>Row 1 Col 1</td>
        <td>Row 1 Col 2</td>
    </tr>
    <tr>
        <td>Row 2 Col 1</td>
        <td>Row 2 Col 2</td>
    </tr>
</table>
```

```python
suite = HtmlSuite(content)
table_element = suite.element("table")
rows = table_element.get_children("tr")

row1 = ["Row 1 Col 1", "Row 1 Col 2"]
row2 = ["Row 2 Col 1", "Row 2 Col 2"]

rows[0].table_row_has_content(row1)
rows[1].table_row_has_content(row2)
```

## CSS-related methods

### `has_styling()`

Check that this element is matched by a CSS selector to give it a particular styling. A value can be passed to match the
value of the styling exactly.

#### Signature

```python
def has_styling(self, prop: str, value: Optional[str] = None, important: Optional[bool] = None, allow_inheritance: bool = False) -> Check
```

#### Parameters

| Name      | Description                                                                                               | Required? | Default                                                                                       |
|:----------|:----------------------------------------------------------------------------------------------------------|:---------:|:----------------------------------------------------------------------------------------------|
| `prop`      | The name of the CSS property to look for.                                                                 |     ✔     |                                                                                               |
| `value`     | A value to match the property against.                                                                    |           | `None`, which will make any value pass and only checks if the element has this style property.  |
| `important` | A boolean indicating that this element should (or may not be) marked as important using **`!important`**. |           | `None`, which won't check this.                                                                 |
| `allow_inheritance` | A boolean indicating that a parent element can also have this styling and pass it down onto the child instead.  | | `False`, which will require the element itself to have this property. |

#### Example usage

```python
suite = CssSuite(content)
body = suite.element("body")
div_tag = body.get_child("div")

# Check that the div has any background colour at all
div_tag.has_styling("background-color")

# Check that the div has a background colour, optionally inheriting it from a parent element
div_tag.has_styling("background-color", allow_inheritance=True)

# Check that the div has a horizontal margin of exactly 3px marked as !important
div_tag.has_styling("margin", "3px", important=True)
```

### `has_color()`

Check that this element has a given color on a CSS property. This is a more flexible version
of [`has_styling`](#has_styling) because it allows the value to be in multiple different formats (`RGB`, `hex`, ...).

#### Signature

```python
def has_color(prop: str, color: str, important: Optional[bool] = None, allow_inheritance: bool = False) -> Check
```

#### Parameters

| Name      | Description                                                                                                            | Required? | Default                                                                                       |
|:----------|:-----------------------------------------------------------------------------------------------------------------------|:---------:|:----------------------------------------------------------------------------------------------|
| `attr`      | The name of the CSS attribute to look for.                                                                             |     ✔     |                                                                                               |
| `value`     | A value to match the property against. This value may be in any of the accepted formats: `name`, `rgb`, `rgba`, `hex`. |     ✔     |                                                                                               |
| `important` | A boolean indicating that this element should (or may not be) marked as important using **`!important`**.              |           | `None`, which won't check this.                                                                 |
| `allow_inheritance` | A boolean indicating that a parent element can also have this styling and pass it down onto the child instead.  | | `False`, which will require the element itself to have this property. |

#### Example usage

```html

<html>
<head>
    <style>
        div {
            background-color: rgb(0, 0, 255);
        }
    </style>
</head>
<body>
<div>
    ...
</div>
</body>
</html>
```

```python
suite = CssSuite(content)
div = suite.element("div")

div.has_color("background-color", "blue")  # By name
div.has_color("background-color", "rgb(0, 0, 255)")  # By rgb value
div.has_color("background-color", "rgba(0, 0, 255, 1.0)")  # By rgba value
div.has_color("background-color", "#0000FF")  # By hex value

div.has_color("background-color", "blue", allow_inheritance=True)  # Allow inheriting from the parent <body>
```

