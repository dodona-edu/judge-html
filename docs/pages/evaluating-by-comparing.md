# Evaluating by Comparing

Another way of evaluating an exercise is by comparing it to the `solution.html file`. This is the default if no `evaluator.py` file is present.

## Options

In the `config.json` file of the exercise you can give some options as to how the comparison should happen.
- `attributes`: (default: False) check whether attributes are exactly the same in solution and submission
- `minimal_attributes`: (default: False) check whether **at least** the attributes in the solution are supplied in the submission, extra attributes are **allowed**
- `contents`: (default: False) check whether the contents of each tag in the solution are exactly the same as in the submission
- `css`: (default: True) if there are css rules defined in the solution, check if the submission can match these rules. We don't compare the css rules itself, but rather whether every element in the submission has at least the css-rules defined in the solution.


To do this, simply add `option`: true to the key-value pairs which are the values of the `evaluation` key.

#### Example 1 (config.json)

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

#### Example 2 (css rules)

If you have this as solution.html
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
Then the submission will be accepted, even tho the solution and submission css rules differ quite a bit, they result in the same visual change and thus are accepted.

## Dummy values

In a lot of cases you're going to want the students to write _something_ or to give _some value_ to an attribute, but you don't care what it is they write down. For that you can use the `DUMMY` keyword for attribute values and for text.

#### Example 1 (text)

If you have this as solution.html
```html
<p>DUMMY</p>
```
And this as the submission
```html
<p>Lorem ipsum</p>
```
Then the submission will be accepted. Remember that contents will only be compared if you set `contents` to `true` in the config.json.


#### Example 2 (attribute values)

If you have this as solution.html
```html
<html lang="DUMMY"></html>
```
And this as the submission
```html
<html lang="en"></html>
```
Then the submission will be accepted. Remember that attributes will only be compared if you set `attributes` or `minimal_attributes` to `true` in the config.json.