# Utility Functions

This document lists and explains the built-in utility functions with examples. These functions add extra functionality to the testing library, and can simplify common behaviour for you.

## Table of Contents

- [`all_of()`](#all_of)
- [`any_of()`](#any_of)
- [`at_least()`](#at_least)
- [`fail_if()`](#fail_if)


## `all_of()`

The `all_of` function takes a list of `Check`s or (nested) iterables such as `list`s, `map`s, generator expressions (including inline list comprehensions), etc. The function will only pass if all of these checks passed too. Once one check fails, all other checks in the list will no longer be evaluated.

#### Signature

```python
def all_of(*args: Checks) -> Check
```

#### Example usage

The example below will fail because there is no `<table>` inside the `<body>`.

```python
content = "<html><body></body></html>"
suite = HtmlSuite(content)

body_element = suite.element("body")
table_element = body_element.get_child("table")
links = suite.all_elements('a')

# Check if the <body> exists AND it has a <table> child
all_of(body_element.exists(), table_element.exists())

# Check if all <a> tags have a url fragment
all_of(link.has_url_with_fragment() for link in links)
```

## `any_of()`

The `any_of` function takes a series of `Check`s or (nested) iterables such as `list`s, `map`s, generator expressions (including inline list comprehensions), etc. The function will pass if at least one of these checks passes as well. Once one check passes, all other checks in the list will no longer evaluated.

#### Signature

```python
def any_of(*args: Checks) -> Check
```

#### Example usage

The example below will pass because `<body>` exists, even if `<head>` doesn't. It will also pass if `<head>` exists while `<body>`  doesn't, and if both exist. This last scenario, however, will not be evaluated (as stated above).

```python
content = "<html><body></body></html>"
suite = HtmlSuite(content)

head_element = suite.element("head")
body_element = suite.element("body")
links = suite.all_elements('a')

# Check if the <body> exists OR <head> exists
any_of(body_element.exists(), head_element.exists())

# Check if at least one <a> tags as a url fragment
any_of(link.has_url_with_fragment() for link in links)
```

## `at_least()`

The `at_least` function takes the amount of `Check`s required, and a series of checks to evaluate (with support for (nested) iterables). The function will pass once at least `amount` checks have passed, and further checks will no longer be evaluated.

#### Signature

```python
def at_least(amount: int, *args: Checks) -> Check
```

#### Example usage

The example below will pass because the first two checks have passed, and only two were required.

```python
content = "<html><body></body></html>"
suite = HtmlSuite(content)

head_element = suite.element("head")  # Exists
body_element = head_element.get_child("body")  # Exists
div_element = body_element.get_child("div")  # Doesn't exist
links = suite.all_elements('a')

# Check if at least two of [<head>, <body>, <div>] exist
at_least(2, head_element.exists(), body_element.exists(), div_element.exists())
at_least(2, [link.has_url_with_fragment() for link in links])
```

## `fail_if()`

The `fail_if` function takes a check, and will fail if the check passes. This is equivalent to the `NOT`-operator.

#### Signature

```python
def fail_if(check: Check) -> Check
```

#### Example usage

```python
content = "<html><body></body></html>"
suite = HtmlSuite(content)

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



