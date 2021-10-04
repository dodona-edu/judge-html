# ElementContainer Class

The `ElementContainer` is a container for `Elements` (...), and can be used as a standard Python `list`. Instances of this class are returned by methods that can return more than one element (for example: `Element.get_children()`, `TestSuite.all_elements()`).

The main purpose of `ElementContainer`s is verification of a document's structure. If your solution wants to check if the second `<div>` contains something, and the student's submission only has one `<div>`, then this would cause an IndexError. When getting indexes that go out of bounds, the ElementContainer will return an empty element instead. Empty elements will make *checks* fail, and rightfully so because the element doesn't exist even though it should, but the suite itself won't crash.

## Methods
- [`get()`](#get)
- [Built-in Checks](#built-in-checks)
  - [`at_least()`](#at_least)
  - [`at_most()`](#at_most)
  - [`exactly()`](#exactly)

## `get()`

Get the `Element` at a specific index of the container. In case there aren't enough elements in the container this returns an empty element instead.

Alternatively, you can also use the `[]`-operator.

#### Signature
```python
def get(index: int) -> Element
```

#### Parameters

| Name  | Description                                | Required? | Default |
| :---- | :----------------------------------------- | :-------: | :------ |
| `index` | The index at which to look for an element. |     ✔     |         |

#### Example usage
Let's say we want to perform checks on two `<div>`s inside of the `<body>`. That means we first have to get references to those `<div>`s, which means they should exist.

However, only one single `<div>` is present in the student's code. This means the `second_div` variable will contain an empty element, but checks can still be performed on it.

```html
<html>
    <body>
        <div>
            ...   
        </div>
    </body>
</html>
```
```python
suite = HtmlSuite(content)
body = suite.element("body")

# Get an ElementContainer with all divs inside of the body
all_divs = body.get_children("div")

# Using .get
first_div = all_divs.get(0)

# Using []-operator
second_div = all_divs[1]  # Doesn't exist, so it will be empty

# Checks can still be performed on the second div, but they will fail
second_div.exists()
second_div.attribute_exists("something")
```

## Built-in Checks

The `ElementContainer` comes with a few checks relating to the amount of elements found.

### `at_least()`

Check that a container has at least a certain amount of elements.

#### Signature
```python
def at_least(amount: int) -> Check
```

#### Parameters

| Name   | Description                             | Required? | Default |
| :----- | :-------------------------------------- | :-------: | :------ |
| `amount` | The minimum amount of elements allowed. |     ✔     |         |

#### Example usage
```python
suite = HtmlSuite(content)
body = suite.element("body")
table = body.get_child("table")

# Get an ElementContainer with all trs inside of the table
all_trs = table.get_children("tr")

# Check that there are at least 4 trs inside of the table
all_trs.at_least(4)
```

### `at_most()`

Check that a container has at most a certain amount of elements.

#### Signature
```python
def at_most(amount: int) -> Check
```

#### Parameters

| Name     | Description                             | Required? | Default |
| :------- | :-------------------------------------- | :-------: | :------ |
| `amount` | The maximum amount of elements allowed. |     ✔     |         |

#### Example usage
```python
suite = HtmlSuite(content)
body = suite.element("body")

# Get an ElementContainer with all divs inside of the body
all_divs = body.get_children("div")

# Check that there are no more than 5 divs
all_divs.at_most(5)
```

### `exactly()`

Check that a container has exactly a certain amount of elements.

#### Signature
```python
def exactly(amount: int) -> Check
```

#### Parameters

| Name     | Description                           | Required? | Default |
| :------- | :------------------------------------ | :-------: | :------ |
| `amount` | The exact amount of elements allowed. |     ✔     |         |

#### Example usage
```python
suite = HtmlSuite(content)
body = suite.element("body")

# Get an ElementContainer with all p's inside of the body
all_ps = body.get_children("p")

# Check that there are exactly 3 paragraphs
all_ps.exactly(3)
```
