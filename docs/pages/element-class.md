# Element Class

The `Element` class contains a reference to an HTML element in the student's code. If this element doesn't exist, it will be empty, but can still be used. All checks performed on it will just fail, and the list of children will be empty.

This class is **not** meant for you to instantiate manually, but instances are returned by the library instead.

## Table of Contents
- [HTML-related methods](#html-related-methods)
  - [`get_child`](#get_child)
  - [`get_children`](#get_children)
- [Built-in Checks](#built-in-checks)
  - [`attribute_contains`](#attribute_contains)
  - [`attribute_exists`](#attribute_exists)
  - [`attribute_matches`](#attribute_matches)
  - [`exists`](#exists)
  - [`has_child`](#has_child)
  - [`has_content`](#has_content)
  - [`has_tag`](#has_tag)

## HTML-related methods

The following methods can be used to obtain references to extra HTML elements starting from another one.

### `get_child`

This method finds a child element with tag `tag`, optionally with extra filters.

#### Signature:
```python
def get_child(tag: str, index: int = 0, direct: bool = True, **kwargs) -> Element
```

#### Parameters:

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `tag`    | The tag to search for | ✔ | |
| `index`  | In case multiple children match your query, choose which match should be chosen. | | 0 (first match) |
| `direct` | Boolean that indicates only *direct* children should be searched, so not nested elements. | | `True` |

Extra `kwargs` can be passed to filter the results down even more. For example, to find the child with a given `id` use `get_child(tag, id="some_id")`.

#### Example usage:
```python
suite = TestSuite("HTML", content)
body = suite.element("body")

# Find the second <img> inside the body with attribute "height" equal to 500,
# which can be nested in another element
img_element = body.get_child("img", index=1, direct=False, height="500")
```

### `get_children`

This method finds ALL child elements, optionally with tag `tag` and extra filters. This returns an instance of `ElementContainer`, which can be used as a list of elements.

#### Signature:
```python
def get_children(tag: Optional[str] = None, direct: bool = True, **kwargs) -> ElementContainer
```

#### Parameters:

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `tag` | The tag to search for | | None, which will result in no tag-filter being applied. |
| `direct` | Boolean that indicates only *direct* children should be searched, so not nested elements. | | `True` |

Extra `kwargs` can be passed to filter the results down even more. For example, to find all children with a given `attribute` use `get_children(attribute="some_value")`.

#### Example usage:
```python
suite = TestSuite("HTML", content)
body = suite.element("body")

# Find all <p>'s with title "Example"
p_elements = body.get_children("p", direct=False, title="Example")
```

## Built-in Checks

The following methods are Checks that can be used on HTML elements, in order to create specific requirements for your students to pass the exercise. All of these methods return an instance of the `Check` class.

### `attribute_contains`

Check that this element has a given attribute, and that the attribute contains a substring. If the element doesn't exist, this check will fail as well. This means it's *not* required to use `attribute_exists` before `attribute_contains`.

#### Signature:
```python
def attribute_contains(attr: str, substr: str, case_insensitive: bool = False) -> Check
```

#### Parameters:

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `attribute`        | The attribute to check for.                                          |     X     |         |
| `substr`           | The substring that should be in the attribute's value.               |     X     |         |
| `case_insensitive` | Indicate that the casing of the value does not matter when checking. |           | `False` |

#### Example usage:
```python
suite = TestSuite("HTML", content)
body = suite.element("body")
img_element = body.get_child("img")

# Check if the src of the image contains "dodona".
img_attributes = ChecklistItem("The image's src contains \"dodona\".", [
  img_element.attribute_contains("src", "dodona"),
])
```

### `attribute_exists`

Check that this element has a given attribute, optionally matching a specific value.

#### Signature:
```python
def attribute_exists(attr: str, value: Optional[str] = None, case_insensitive: bool = False) -> Check
```

#### Parameters:

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `attribute`        | The attribute to check for. | ✔ | |
| `value`            | The value to compare against. | | None, which will make any value pass. This means the check only makes sure the attribute *exists*. |
| `case_insensitive` | Indicate that the casing of the value does not matter when checking. | | `False` |

#### Example usage:
```python
suite = TestSuite("HTML", content)
body = suite.element("body")
img_element = body.get_child("img")

# Check if the image has the src and alt attributes, and a width of 500.
img_attributes = ChecklistItem("The image has the correct attributes.", [
  img_element.attribute_exists("src"),
  img_element.attribute_exists("alt"),
  img_element.attribute_exists("width", "500")
])
```

### `attribute_matches`

Check if an attribute exists, and if its value matches a regular expression. If the element doesn't exist, this check will fail as well. This means it's *not* required to use `attribute_exists` before `attribute_matches`.

#### Signature:
```python
def attribute_matches(attr: str, regex: Pattern[AnyStr], flags: Union[int, re.RegexFlag] = 0) -> Check
```

#### Parameters:

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `attribute` | The attribute to check for.                               |  ✔ |                                      |
| `regex`     | The regex pattern to match the attribute's value against. |  ✔ |                                      |
| `flags`     | Extra `RegexFlag`s to use when comparing.                 |    | 0, meaning no flags will be applied. |

#### Example usage:

```python
import re

suite = TestSuite("HTML", content)
body = suite.element("body")
img_element = body.get_child("img")

# Check if the src of the image starts with "https://", contains "dodona", and ends on ".png", case-insensitive.
img_attributes = ChecklistItem("The image has the correct attributes.", [
  img_element.attribute_matches("src", "dodona", re.IGNORECASE),
])
```

### `exists`

Check that an element exists, and is not empty. This is equivalent to verifying that an element was found in the student's code.

#### Signature:
```python
def exists() -> Check
```

#### Example usage
```python
suite = TestSuite("HTML", content)
body = suite.element("body")

body_exists = ChecklistItem("The document has a <body>", body.exists())
```

### `has_child`

Check that the element has a child that meets the specifications. This is a shortcut to combining `get_child()` and `exists()`.

#### Signature:
```python
def has_child(tag: str, direct: bool = True, **kwargs) -> Check
```

#### Parameters:

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `tag`    | The tag to search for.                                                                    |     ✔     |         |
| `direct` | Boolean that indicates only *direct* children should be searched, so not nested elements. |           | True    |

Extra `kwargs` can be passed to filter the results down even more. For example, to check that an element has a child with a given `id` use `has_child(tag, id="some_id")`.

#### Example usage
```python
suite = TestSuite("HTML", content)
body = suite.element("body")

# Check that the body has a child div
body_has_div = ChecklistItem("The body has a div", body.has_child("div"))

# Equivalent to
body_has_div = ChecklistItem("The body has a div", body.get_child("div").exists())
```

### `has_content`

Check that the element has specific content, or any content at all.

#### Signature:
```python
def has_content(text: Optional[str] = None) -> Check
```

#### Parameters:

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| text | The text to compare the element's content to. |           | None, which will make any content pass and just checks if the content is not empty. |

#### Example usage
```python
suite = TestSuite("HTML", content)
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

### `has_tag`

Check that this element has the required tag.

#### Signature:
```python
def has_tag(tag: str) -> Check
```
#### Parameters:

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| tag  | The tag to check for. |     ✔     |         |

#### Example usage
```python
suite = TestSuite("HTML", content)
body = suite.element("body")
body_children = body.get_children()

# Verify that the first child of the body is a <table>
# and the second a <div>
body_structure = ChecklistItem("The body has a table followed by a div.", [
  body_children[0].has_tag("table"),
  body_children[1].has_tag("div")
])
```
