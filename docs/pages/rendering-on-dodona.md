# Rendering HTML and CSS on Dodona

The HTML Judge is capable of rendering the student's code in Dodona. HTML will **only** be shown if their HTML code was valid, and CSS will **only** be shown if **both** HTML **and** CSS were valid.

This means it is required to check for validity at least _once_ when using the `TestSuite`. In order to do this, the `validate_html` and `validate_css` checks can be used.

```python
suite = TestSuite("HTML", content)

valid = ChecklistItem("The HTML and CSS are valid.", [
    suite.validate_html(),
    suite.validate_css()
])
suite.add_item(valid)
```

Keep in mind that there may be artifacts from Dodona's own CSS that are applied onto the student's submission. This _can_ result in the rendering not being 100% accurate, but has no influence on the tests being correct or not.