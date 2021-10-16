# Special type annotations

The checks library uses a few custom type annotations to make functions a bit more readable, or to provide additional information about parameters. This document will explain what they mean.

## Table of Contents

- [`Checks`](#checks)
- [`Emmet`](#emmet)

## `Checks`

```python
Checks = TypeVar("Checks", bound=Union["Check", Iterable["Check"]])
```

``Checks`` is used to indicate that a parameter can be a variable amount of `Check`s. This also allows `lists`, `tuples`, `maps` and `generator expressions` to be passed into this function.

The examples below use the [`all_of`](utility-functions.md#all_of) utility function to show what this is capable of.

```python
html = HtmlSuite(content)
body = html.element("body")

# One argument:
# - <body> exists
all_of(body.exists())

# Multiple arguments:
# - <body> exists
# - <body> contains a <div>
all_of(body.exists(), body.has_child("div"))

# Using map() to quickly check if the body only contains <div> elements
all_of(map(lambda c: c.has_tag("div"), body.get_children()))

# Using a generator expression to check if the body only contains <div> elements
all_of(c.has_tag("div") for c in body.get_children())
```

The use of this specific type also removes the need for unnecessary `spread operators` (`*`) and `list` casts, which allows for slightly cleaner code.

```python
# Before:
all_of(*[c.exists() for c in elements])

# After:
all_of(c.exists() for c in elements)
```

## `Emmet`

```python
Emmet = TypeVar("Emmet", bound=str)
```

The `Emmet` type suggests you can use [`Emmet Syntax`](emmet-syntax.md) on this parameter. You can _not_ create an instance of this class, and these parameters still take a `string`.

```python
def function(arg: Emmet): ...

# Emmet parameters are equal to strings
function("body>table>#some_id")
```

In most cases, the type will be `Union[str, Emmet]`. This is to show that you can _also_ use other means (eg. names of `HTML` tags, ...) instead of only `Emmet Syntax`.
