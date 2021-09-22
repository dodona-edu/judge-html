# Utility Functions

This document lists and explains the built-in utility functions with examples. These functions add extra functionality to the testing library, and can simplify common behaviour for you.

## Table of Contents

- [`all_of`](#all_of)
- [`any_of`](#any_of)
- [`at_least`](#at_least)
- [`Element.has_table_content`](#elementhas_table_content)
- [`Element.has_table_header`](#elementhas_table_header)
- [`Element.table_row_has_content`](#elementtable_row_has_content)
- [`fail_if`](#fail_if)

## `all_of`

The `all_of` function takes a list of `Check`s, and will only pass if all of these checks passed too. Once one check fails, all other checks in the list will no longer be evaluated.

#### Signature:
```python
def all_of(args: List[Check]) -> Check
```

#### Example usage:

The example below will fail because there is no `<table>` inside the `<body>`.

```python
document = "<html><body></body></html>"
suite = TestSuite("HTML", document)

body_element = suite.element("body")
table_element = body.get_child("table")

# Check if the <body> exists AND it has a <table> child
all_of(body_element.exists(), table_element.exists())
```

## `any_of`

The `any_of` function takes a series of checks, and will pass if at least one of these checks passes as well. Once one check passes, all other checks in the list will no longer evaluated.

#### Signature:
```python
def any_of(*args: Check) -> Check
```

#### Example usage:

The example below will pass because `<body>` exists, even if `<head>` doesn't. It will also pass if `<head>` exists while `<body>`  doesn't, and if both exist. This last scenario, however, will not be evaluated (as stated above).

```python
document = "<html><body></body></html>"
suite = TestSuite("HTML", document)

head_element = suite.element("head")
body_element = suite.element("body")

# Check if the <body> exists OR <head> exists
any_of(body_element.exists(), head_element.exists())
```

## `at_least`

The `at_least` function takes the amount of checks required, and a series of checks to evaluate. The function will pass once at least `amount` checks have passed, and further checks will no longer be evaluated.

#### Signature:
```python
def at_least(amount: int, *args: Check) -> Check
```

#### Example usage:

The example below will pass because the first two checks have passed, and only two were required.

```python
document = "<html><body></body></html>"
suite = TestSuite("HTML", document)

head_element = suite.element("head")  # Exists
body_element = head.get_child("body")  # Exists
div_element = body.get_child("div")  # Doesn't exist

# Check if at least two of [<head>, <body>, <div>] exist
at_least(2, head_element.exists(), body_element.exists(), div_element.exists())
```

## `Element.has_table_content`

This method checks if an `Element` with tag `table` has rows with the required content, **excluding the header**.

#### Signature:
```python
def has_table_content(rows: List[List[str]], has_header: bool = True) -> Check
```

#### Parameters:

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `rows` | A 2D `list` of `strings` that represents the content that the rows should match exactly. | ✔ |  |
| `has_header` | Boolean that indicates this table should have a `header`, in which case the first `<tr>` will be ignored.  |  | True |

#### Example usage:

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
suite = TestSuite("HTML", document)
table_element = suite.element("table")

rows = [
    ["Row 1 Col 1", "Row 1 Col 2"],
    ["Row 2 Col 1", "Row 2 Col 2"]
]
table_element.has_table_content(rows, has_header=True)
```

## `Element.has_table_header`

This method checks if an `Element` with tag `table` has a header with content that matches a list of strings. This avoids having to use `all_of` combined with a *LOT* of `has_content`s.

#### Signature:
```python
def has_table_header(header: List[str]) -> Check
```

#### Parameters:

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `header` | `List` of `strings` that represents the content that the header should match exactly. | ✔ |  |

#### Example usage:

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
suite = TestSuite("HTML", document)
table_element = suite.element("table")

header = ["Header 1", "Header 2", "Header 3", "Header 4"]
table_element.has_table_header(header)
```

## `Element.table_row_has_content`

This method checks if an `Element` with tag `tr` has the required content. This is the same as [`Element.has_table_content`](#elementhas_table_content) but for one row, and applied on a `<tr>` instead of a `<table>`.

#### Signature:
```python
def table_row_has_content(self, row: List[str]) -> Check
```

#### Parameters:

| Name | Description | Required? | Default |
|:-----|:------------|:---------:|:--------|
| `row` | A `list` of `strings` that represents the content that the row should match exactly. | ✔ |  |

#### Example usage:

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
suite = TestSuite("HTML", document)
table_element = suite.element("table")
rows = table_element.get_children("tr")

row1 = ["Row 1 Col 1", "Row 1 Col 2"]
row2 = ["Row 2 Col 1", "Row 2 Col 2"]

rows[0].table_row_has_content(row1)
rows[1].table_row_has_content(row2)
```

## `fail_if`

The `fail_if` function takes a check, and will fail if the check passes. This is equivalent to the `NOT`-operator.

#### Signature:
```python
def fail_if(check: Check) -> Check
```

#### Example usage:

```python
document = "<html><body></body></html>"
suite = TestSuite("HTML", document)

script_element = suite.element("script")

# Check that there are no script tags
fail_if(script_element.exists())
```

It is **very** important to note that non-existing HTML elements will cause checks to fail by default, so `fail_if` can make them pass unintentionally. When using an `Element`, you should always check if it **exists** first (using the `Element.exists()` Check).

The example below makes sure that the url doesn't contain a fragment. If the url doesn't exist, this will pass as well!

```python
a_tag = suite.element("a")

# If <a> doesn't exist, this will succeed, and the check will pass!
fail_if(a_tag.has_url_with_fragment())

# Solution: first check if it exists, THEN perform the check
ChecklistItem("The anchor tag does not contain a fragment", a_tag.exists(), fail_if(a_tag.has_url_with_fragment()))
```
