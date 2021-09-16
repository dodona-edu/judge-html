# Utility Functions

This document lists and explains the built-in utility functions with examples. These functions add extra functionality to the testing library, and can simplify common behaviour for you.

## Table of Contents

- [`all_of`](#all_of)
- [`any_of`](#any_of)
- [`at_least`](#at_least)
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
all_of([body_element.exists(), table_element.exists()])
```

## `any_of`

The `any_of` function takes a list of checks, and will pass if at least one of these checks passes as well. Once one check passes, all other checks in the list will no longer evaluated.

#### Signature:
```python
def any_of(args: List[Check]) -> Check
```

#### Example usage:

The example below will pass because `<body>` exists, even if `<head>` doesn't. It will also pass if `<head>` exists while `<body>`  doesn't, and if both exist. This last scenario, however, will not be evaluated (as stated above).

```python
document = "<html><body></body></html>"
suite = TestSuite("HTML", document)

head_element = suite.element("head")
body_element = suite.element("body")

# Check if the <body> exists OR <head> exists
any_of([body_element.exists(), head_element.exists()])
```

## `at_least`

The `at_least` function takes two arguments: the first being the amount of checks required, and the second list of checks to evaluate. The function will pass once at least `amount` checks have passed, and further checks will no longer be evaluated.

#### Signature:
```python
def at_least(amount: int, args: List[Check]) -> Check
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
at_least(2, [head_element.exists(), body_element.exists(), div_element.exists()])
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
