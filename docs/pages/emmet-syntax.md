# Emmet Syntax

> _For more information, refer to the [official Emmet docs](https://docs.emmet.io/abbreviations/syntax/)._  
> _For an overview, refer to the [official Emmet cheat sheet](https://docs.emmet.io/cheat-sheet/) or [unofficial Emmet cheat sheet](https://devhints.io/emmet)._
>
> _**Note that the `$` operator is not supported**_

All `find_*` methods support `Emmet Syntax`, which allows you to perform search queries in a (**much**) shorter way. This comes in handy when you want to quickly find a deeply-nested element along a very specific path. This document aims to first explain this syntax, and then provide a few examples to show how it works (and to show how much shorter it can be). The methods will always display the character count, to show you that `Emmet Syntax` is always **almost twice** as compact (and for more complex cases, even more than that).

To indicate that a specific method supports this, it's added to the type hint and all of them have the following line underneath their header in their respective documentation: 

_**This method supports Emmet Syntax through the [PARAMETER] parameter.**_

Furthermore, these parameters will be typehinted as `param: Union[str, Emmet]`, to further indicate that this argument can use Emmet Syntax. An `Emmet` is nothing more than a `string`, so don't worry about doing anything special to it. Any `string` will work just fine, this is just a type annotation.

> Note: the `index` and `kwargs` parameters passed into the `find` methods are still allowed, but will only be applied to the _**last**_ element from the query. The path will always take priority when clashing, so if the query itself ends with an index (e.g. `table>tr[3]`) then this index will be used instead of the parameter.

## Table of Contents
- [Basics of Emmet Syntax](#basics-of-emmet-syntax)
    - [Finding nested elements with `>`](#finding-nested-elements-with-)
    - [Specifying indexes with `[ ]`](#specifying-indexes-with--)
    - [Specifying id's with `#`](#specifying-ids-with-)
    - [Specifying class names with `.`](#specifying-class-names-with-)
- [`make_item_from_emmet()` : Creating Checks using Emmet Syntax](#make_item_from_emmet--creating-checks-using-emmet-syntax)  
    - [Signature](#signature)
    - [Parameters](#parameters)
    - [Examples](#examples)
        - [Check that an element exists](#check-that-an-element-exists)
        - [Check that sibling structure exists](#check-that-sibling-structure-exists)
        - [Check the content of an element](#check-the-content-of-an-element)
        - [Check that X amount of children exist](#check-that-x-amount-of-children-exist)
        - [Check that elements with an id and/or class exist](#check-that-elements-with-an-id-andor-class-exist)
        - [Check that an element has attributes (with values)](#check-that-an-element-has-attributes-with-values)

## Basics of Emmet Syntax

Before we dive in, a `tag` is still referenced by its name. `element("div")` is valid. If you want to include a tag name in your path, **it should _always_ be in the beginning**.

### Finding nested elements with `>`

To indicate that an element should contain another, use the `>` symbol (from left to right).

#### Example usage

Problem: "Find the `<div>` inside of the `<td>` inside of the `<tr>` inside of the `<table>` inside of the `<div>` inside of the `<body>` starting from the root element (`<html>`)"

```python
# Without Emmet Syntax | 140 characters
div_element = suite.element("html", from_root=True)
    .get_child("body")
    .get_child("div")
    .get_child("table")
    .get_child("tr")
    .get_child("td")
    .get_child("div")

# With Emmet Syntax | 62 characters
div_element = suite.element("html>body>div>table>tr>td>div", from_root=True)
```

### Specifying indexes with `[ ]`

By default, the first match will always be chosen for every step. To specify that the `n-th` match should be used, you may do so by adding the index between square brackets **at the end of the step**.

#### Example usage

Problem: "Find the _third_ `<div>` inside of the _fourth_ `<td>` inside of the _first_ `<tr>` inside of the `<table>`"

```python
# Without Emmet Syntax | 97 characters
div_element = suite.element("table", from_root=False)
    .get_child("tr", 0)
    .get_child("td", 3)
    .get_child("div", 2)

# With Emmet Syntax | 58 characters
div_element = suite.element("table>tr[0]>td[3]>div[2]", from_root=False)

# The first is chosen by default, so [0] is always obsolete | 55 characters
div_element = suite.element("table>tr>td[3]>div[2]", from_root=False)
```

### Specifying id's with `#`

To filter down based on id's, you can specify an id by adding a hashtag (`#`) in front of it.

An id should only contain `letters`, `numbers`, `underscores` and `hyphens`, and should contain at least one character. In essence, they should match the following regex: `#([a-zA-Z0-9_-]+)`.

#### Example usage

Problem: "Find the `<div>` with id `example` inside of the `<body>`"

```python
# Without Emmet Syntax | 52 characters
div_element = suite.element("body")
    .get_child("div", id="example")

# With Emmet Syntax | 33 characters
div_element = suite.element("body>div#example")

# With Emmet Syntax, only specifying the id and not the tag | 30 characters
div_element = suite.element("body>#example")

# With Emmet Syntax, using kwargs for the id as it is for the final step of the path | 39 characters
div_element = suite.element("body>div", id="example")
```

### Specifying class names with `.`

Class names can be specified by adding a dot (`.`) in front of them, and multiple class names in a row are **allowed**.

A class name should only contain `letters`, `numbers`, `underscores` and `hyphens`, and should contain at least one character. These are the same rules as for the `id`'s, so the same regex can be used to check: `\.[a-zA-z0-9_-]+`.

**However**, a class name can **not** start with:
- A `number`
- Two `hyphens`
- A `hyphen` followed by a `number`

This means your class name may **never** match the following regex: `\.([0-9]|--|-[0-9])`.

#### Example usage

Problem: "Find the `<td>` with class names `ex-1` **and** `ex-2`, inside of the `<tr>` with class name `tr-example` inside of the `<table>`"

```python
# Without Emmet Syntax | 95 characters
div_element = suite.element("table")
    .get_child("tr", class_="tr-example")
    .get_child("td", class_="ex-1 ex-2")

# With Emmet Syntax | 49 characters
div_element = suite.element("table>tr.tr-example>td.ex-1.ex-2")
```

## `make_item_from_emmet()` : Creating Checks using Emmet Syntax

You can, however, use Emmet Syntax for more than just finding elements. The `checks` library also supports creating `Checks` using this syntax, which can be accomplished via the `TestSuite.make_item_from_emmet()` method.

This method creates (and adds) a `ChecklistItem` by parsing your Emmet-string into a series of Checks. Examples are listed below.

**Note**: these examples use more advanced Emmet Syntax found in the [official documentation](https://docs.emmet.io/abbreviations/syntax/).

#### Signature

```python
def make_item_from_emmet(message: , emmet_str: Union[str, Emmet])
```

### Parameters

| Name     | Description                                                                                                                                            | Required? | Default |
:----------|:-------------------------------------------------------------------------------------------------------------------------------------------------------|:---------:|:--------|
| `message`    | The message to add to the ChecklistItem.                                                                                                           |     ✔     |         |
| `emmet_str`  | A `string` in `Emmet Syntax` to create the checks from.                                                                                            |     ✔     |         |

### Examples

All these checks should be taken in an *at_least* context. They check that your required structure is present, but still allow other elements to be present as well. These elements are ignored.

#### Check that an element exists

```python
suite = HtmlSuite(content)

message = "The <table> has a <tr> with id \"example\"."

# Without Emmet Syntax
suite.make_item(message, suite.element("table").has_child("tr", id="example"))
# Alternatively: suite.element("table").get_child("tr", id="example").exists()

# With Emmet Syntax
suite.make_item_from_emmet(message, "table>tr#example")
```

#### Check that sibling structure exists

```python
suite = HtmlSuite(content)

message = "The <body> has: a <div>, a <p>, and a <blockquote>."

# Without Emmet Syntax
body = suite.element("body")
suite.make_item(message, body.has_child("div"), body.has_child("p"), body.has_child("blockquote"))

# With Emmet Syntax
suite.make_item_from_emmet(message, "body>div+p+blockquote")
```

#### Check the content of an element

The following is a good example of how this syntax can greatly simplify otherwise complex queries.

```python
suite = HtmlSuite(content)

message = "The <body> has a <table>, which contains a <tr> with a <td> with content \"example\"."

# Without Emmet Syntax
table = suite.element("body").get_child("table")

checks_list = []

for tr in table.get_children("tr"):
    checks_list.append(tr.has_child("td", text="example"))

# Without Emmet Syntax, using a complex and hard-to-read construction
table = suite.element("body").get_child("table")
suite.make_item(message, any_of(
        *list(map(lambda tr: tr.has_child("td", text="example"), table.get_children("tr")))
    )
)

# With Emmet Syntax
suite.make_item_from_emmet(message, "body>table>tr>td{example}")
```

#### Check that X amount of children exist

```python
suite = HtmlSuite(content)

message = "The <body> has a <table> which contains at least 6 <tr>s."

# Without Emmet Syntax
suite.make_item(message, suite.element("body").get_child("table").get_children("tr").at_least(6))

# With Emmet Syntax
suite.make_item_from_emmet(message, "body>table>tr*6")
```

#### Check that elements with an id and/or class exist

```python
suite = HtmlSuite(content)

message = "The <body> contains a <div> with id \"header\", and another <div> with class \"page\"."

# Without Emmet Syntax
body = suite.element("body")
suite.make_item(message, body.has_child("div", id="header"), body.has_child("div", class_="page"), fail_if(body.has_child("div", id="header", class_="page")))

# With Emmet Syntax
suite.make_item_from_emmet(message, "body>div#header+div.page")
```

#### Check that an element has attributes (with values)

```python
suite = HtmlSuite(content)

message = "The <table> has a <tr> which contains a <td> with title \"Hello world\", and colspan \"3\"."

# Without Emmet Syntax
table = suite.element("table")

checks_list = []

for tr in table.get_children("tr"):
    checks_list.append(tr.has_child("td", title="Hello world", colspan="3"))

suite.make_item(message, any_of(*checks_list))
    
# Without Emmet Syntax, using a complex and hard-to-read construction
table = suite.element("table")
suite.make_item(message, any_of(
    *list(map(lambda tr: tr.has_child("td", title="Hello world", colspan="3"), table.get_children("tr")))
))

# With Emmet Syntax
suite.make_item_from_emmet(message, "table>tr>td[title='Hello world' colspan='3']")
```