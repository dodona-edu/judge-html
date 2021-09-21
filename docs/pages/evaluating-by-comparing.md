# Evaluating by comparing

Another way of evaluating an exercise is by comparing it to the `solution.html file`.\
This is the default if no `evaluator.py` file is present.

## Options

In the `config.json` file of the exercise you can give some options as to how the comparison should happen.
- `attributes`: (default: False) check whether attributes are exactly the same in solution and submission
- `minimal_attributes`: (default: False) check whether at least the attributes in solution are supplied in the submission
- `contents`: (default: False) check whether the contents of each tag in the solution are exactly the same as in the submission

To do this, simply add `option`: true to the key-value pairs which are the values of the `evalutaion` key

#### Example

As an example we show how to compare when the solution.html contains the minimal required attributes and the required contents, config.json should look like this:

```json
{
  ...
  
  "evaluation": {
    "handler": "html",
    "minimal_attributes": true,
    "contents": true
  },
  
  ...
}
```

## Dummy values

In a lot of cases you're going to want the students to write something or to give some value to an attribute, but you don't care what it is they write down.\
For that you can use the `DUMMY` keyword for attribute values and for text.

#### Example 1 (text)

If you have this as solution.html
```html
<p>DUMMY</p>
```
And this as the submission
```html
<p>Lorem ipsum</p>
```
Then the submission will be accepted\
(remember that contents will only be compared if you set `contents` to true in the config.json)


#### Example 2 (attribute values)

If you have this as solution.html
```html
<html lang="DUMMY"></html>
```
And this as the submission
```html
<html lang="en"></html>
```
Then the submission will be accepted\
(remember that attributes will only be compared if you set `attributes` or `minimal_attributes` to true in the config.json)