# Emmet Syntax

All `find_*` methods support `Emmet Syntax`, which allows you to perform search queries in a (**much**) shorter way. This comes in handy when you want to quickly find a deeply-nested element along a very specific path. This document aims to first explain this syntax, and then provide a few examples to show how it works (and to show how much shorter it can be).

To indicate that a specific method supports this, all of them have the following line underneath their header in their respective documentation: 

_**This method supports Emmet Syntax through the [PARAMETER] parameter**_

### Note:

The `index` and `kwargs` parameters passed into the `find` methods are still allowed, but will only be applied to the _**last**_ element from the query. The path will always take priority when clashing, so if the query itself ends with an index (eg. `table>tr[3]`) then this index will be used instead of the parameter.

## Basics of Emmet Syntax

Before we dive in, a `tag` is still referenced by its name. `element("div")` is valid.

### Finding nested elements

To indicate that an element should contain another, use the `>` symbol (from left to right).

#### Example usage:

Problem: "Find the `<div>` inside of the `<td>` inside of the `<tr>` inside of the `<table>` inside of the `<div>` inside of the `<body>` starting from the root element (`<html>`)"

```python
# Without Emmet Syntax
div_element = suite.element("html", from_root=True)
    .get_child("body")
    .get_child("div")
    .get_child("table")
    .get_child("tr")
    .get_child("td")
    .get_child("div")

# With Emmet Syntax
div_element = suite.element("html>body>div>table>tr>td>div", from_root=True)
```

### Specifying indexes

By default, the first match will always be chosen for every step. To specify that the `n-th` match should be used, you may do so by adding the index between square brackets **at the end of the step**.

#### Example usage:

Problem: "Find the _third_ `<div>` inside of the _fourth_ `<td>` inside of the _first_ `<tr>` inside of the `<table>`"

```python
# Without Emmet Syntax
div_element = suite.element("table", from_root=False)
    .get_child("tr", 0)
    .get_child("td", 3)
    .get_child("div", 2)

# With Emmet Syntax
div_element = suite.element("table>tr[0]>td[3]>div[2]", from_root=False)

# The first is chosen by default, so [0] is always obsolete
div_element = suite.element("table>tr>td[3]>div[2]", from_root=False)
```