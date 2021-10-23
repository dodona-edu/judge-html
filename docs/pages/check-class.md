# Check Class

`Check`s are classes with a function that *checks* (...) something, and returns `True` or `False` to indicate that the check passed.

It is important to note that the Check class uses a `fluent interface`, meaning the methods can be chained together, and using a method will return a `Check`. This means the methods can be used inside `ChecklistItem`s, and so on.

## Table of Contents

- [`or_abort()`](#or_abort)
- [`is_crucial()`](#is_crucial)
- [`then()`](#then)

## `or_abort()`

This function will cause the check's TestSuite to **stop** evaluating, and cause **all future checks to fail**. This should be used in case a first check is a necessary requirement for the following checks to succeed.

#### Signature

```python
def or_abort() -> Check
```

#### Example usage

The example below will abort testing if the document's HTML is invalid. Even if a `<table>` exists, this item will still be marked as `incorrect` on Dodona.

```html
<!-- This document contains invalid HTML (missing closing tags, and unclosed elements) -->
<html>
    <body
        <table>
            ...
        </table>
</html>
```

```python
suite = TestSuite("HTML", content)
table_element = suite.element("table")

# Note the use of .or_abort() here!
html_valid = ChecklistItem("The HTML is valid.", suite.validate_html().or_abort())

table_exists = ChecklistItem("The document has a table.", table_element.exists())
```

## `is_crucial()`

This is an alias to [`or_abort`](#or_abort), and can be used in the exact same way.

## `then()`

This function registers one or more checks that should *only* run if the current check succeeds.

The checks will be added to an internal list of `on_success` checks. In case the current check already has such a list, the checks will be added to the deepest child without any `on_success`-checks so far instead. The function returns a reference to the last check in the list, to which future checks will be added when calling `.then()` again.

This function `then()` also takes (nested) iterables such as `list`s, `map`s, generator expressions (including inline list comprehensions), etc.

#### Signature

```python
def then(*args: Checks) -> Check
```

#### Example usage

The example below only checks if the `<div>` exists in case the `<body>` does too.

```python
suite = HtmlSuite(content)

body_element = suite.element("body")
div_element = body_element.get_child("div")

body_checks = body_element.exists().then(div_element.exists()).then(...).then(...)
```

Note that consecutive `.then()` calls can stay on the outside and do NOT have to be nested. This avoids a complicated mess of brackets and holds the same result. The results are the same because, as mentioned earlier, the checks are added to the deepest child without any checks attached to it so far.

```python
check_1.then(check_2).then(check_3)
```

is completely equivalent to

```python
check_1.then(check_2.then(check_3))
```
