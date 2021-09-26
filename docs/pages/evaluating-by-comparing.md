# Evaluate in comparison mode with `solution.html`

Another way of evaluating an exercise is by comparing it to the `solution.html` file. This is the default if no `evaluator.py` file is present. In this case, the structure of the student's submission will be compared to your solution, and you can provide extra options to specify how strict this comparison should be.

It does have to be noted that this way of evaluation allows for a lot less freedom, both to the students submitting it and the teacher who wants to evaluate the submission. **For flexible tests, consider using the [`checks library`](../readme.md#checks-library-documentation).**

## Table of Contents

- [Optional `evaluation settings` in `config.json`](#optional-evaluation-settings-in-configjson)
- [DUMMY values](#dummy-values)

## Optional `evaluation settings` in `config.json`

In the `config.json` file of the exercise you can give some options as to how the comparison should happen. If these settings are not defined, the default value is chosen.

| Evaluation setting | Description | Possible values | Default |
| ------------------ | ----------- | --------------  | ------- |
| `attributes` |  Check whether attributes are exactly the same in solution and submission.* | `true`/`false` | `false`  |
| `minimal_attributes`| Check whether **at least** the attributes in the solution are supplied in the submission, extra attributes are **allowed**. | `true`/`false` | `false` |
| `contents`| Check whether the contents of each tag in the solution are exactly the same as in the submission. | `true`/`false` | `false` |
| `css` | If there are CSS rules defined in the solution, check if the submission can match these rules. We don't compare the CSS rules themselves, but rather whether every element in the submission has at least the CSS-rules defined in the solution. | `true`/`false` | `true` |
| `comments` | Check whether the submission has the same comments as the solution. | `true`/`false` | `false` |

*\*Note: when both `attributes` and `minimal_attributes` are supplied, `attributes` will take preference as it is stricter.*

To do this, simply add `"evaluation_setting": true` to the key-value pairs which are the values of the `evaluation` key.

### Examples

#### Example 1 (`config.json`)

As an example we show how to compare when the `solution.html` contains the minimal required attributes and the required contents, `config.json` should look like this:

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

#### Example 2 (css rules)

If you have this as `solution.html`

```html
<html>

    <head>
        <style>
            body {
                background-color: red;
            }
        </style>
    </head>
    
    <body>
        ...
    </body>

</html>
```

And this as the submission

```html
<html>

    <head>
        <style>
            #my_body {
                background-color: #FF0000;
            }
        </style>
    </head>
    
    <body id="my_body">
        ...
    </body>

</html>
```

Then the submission will be accepted, even though the solution and submission CSS rules differ quite a bit, they result in the same visual change and thus are accepted.


## DUMMY values

In a lot of cases you're going to want the students to write _something_ or to give _some value_ to an attribute, but you don't care what it is they write down. For that you can use the `DUMMY` keyword for attribute values and for text in your `solution.html` file.

### Examples

#### Example 1 (text)

If you have this as `solution.html`

```html
<p>DUMMY</p>
```

And this as the submission

```html
<p>Lorem ipsum</p>
```

Then the submission will be accepted. Remember that contents will only be compared if you set `contents` to `true` in the `config.json`.

#### Example 2 (attribute values)

If you have this as `solution.html`

```html
<html lang="DUMMY"></html>
```

And this as the submission

```html
<html lang="en"></html>
```

Then the submission will be accepted. Remember that attributes will only be compared if you set `attributes` or `minimal_attributes` to `true` in the `config.json`.
