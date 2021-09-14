# Utility Functions

This document lists and explains the built-in utility functions. These functions add extra functionality to the testing library, and can simplify common behaviour for you.

## Table of Contents

- [all_of](#all_of)
- [any_of](#any_of)

## all_of

The `all_of` function takes a list of `Check`s, and will only pass if all of these checks passed too. Once one check fails, all other checks in the list will no longer be evaluated.

The example below will fail because there is no `<table>` inside the `<body>`.

```python
document = "<html><body></body></html>"
suite = TestSuite("HTML", document)

body_element = suite.element("body")
table_element = body.get_child("table")

# Check if the <body> exists AND it has a <table> child
all_of([body_element.exists(), table_element.exists()])
```

## any_of

The `any_of` function takes a list of checks, and will pass if at least one of these checks passes as well. Once one check passes, all other checks in the list will no longer evaluated.

The example below will pass because `<body>` exists, even if `<head>` doesn't. It will also pass if `<head>` exists while `<body>`  doesn't, and if both exist. This last scenario, however, will not be evaluated (as stated above).

```python
document = "<html><body></body></html>"
suite = TestSuite("HTML", document)

head_element = suite.element("head")
body_element = suite.element("body")

# Check if the <body> exists OR <head> exists
any_of([body_element.exists(), head_element.exists()])
```