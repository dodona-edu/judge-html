# HTML&CSS judge for [Dodona](https://dodona.ugent.be/)

## Judge features

* Checklist (correct, fail, warning)
* Feedback in language of user (Dutch or English)
* HTML (TODO &CSS) render of student submission
* Support for partial exercises (exercises that focus on one tag)
* Two evaluation methods
  * **Comparison mode** with `solution.html` file (fast and easy)
  * **Checklist mode** (a lot of flexibility)
* Extensive [customization possible in `config.json`](#optional-evaluation-settings-in-configjson)
* Elaborate [feedback](#feedback)

### Judge properties

* Tags are case-insensitive
* Inline CSS is not allowed (internal CSS is)
* `<script>` and `<noscript>` tag are not allowed
* Self-closing (non-void) tags are not allowed (e.g. `<p/>`, `<div/>`)
* TestSuite for HTML and/or CSS (in different tabs)

## Feedback

### HTML&CSS
* Syntax errors
  * Check if brackets/quotes open and close (`(`, `<`, `{`, `[`, `'`, `"`)
  * Each tag that opens must have a corresponding closing tag
  * Checks if all tags are valid

### HTML
* Check if required attributes are present
* Warning if recommended attributes are missing

### CSS



## Recommended exercise directory structure

> [More info about repository directory structure](https://docs.dodona.be/en/references/repository-directory-structure/#example-of-a-valid-repository-structure)

Add your solution (`solution.html` and `solution.css` file) to the **`evaluation`** folder. Absolute necessary files are marked with `▶` in the tree structure below.

```text
+-- README.md                            # Optional: Describes the repository
+-- 📂public                            # Optional: Contains files that belong to the course or series
|   +-- my_picture.png                   # Optional: An image to reuse throughout the course
+-- dirconfig.json                       # Shared config for all exercises in subdirs
+-- 📂html-exercises                    # We could group exercises in a folder
|   +-- 📂first_html_exercise           # Folder name for the exercise
|   |   +-- config.json                  # ▶ Configuration of the exercise
|   |   +-- 📂evaluation                # -- 🔽️ ADD YOUR SOLUTION FILES HERE 🔽 --
|   |   |   +-- solution.html            # ▶ The HTML model solution for comparison mode
|   |   |   +-- evaluator.py             # ▶ The Python code for checklist mode
|   |   +-- 📂solution                  # Optional: This will be visible in Dodona
|   |   |   +-- solution.html            # Optional: The HTML model solution file
|   |   |   +-- solution.css             # Optional: The CSS model solution file
|   |   +-- 📂preparation               # Optional folder
|   |   |   +-- generator.py             # Optional: Script to generate data
|   |   +-- 📂description               #
|   |       +-- description.nl.md        # ▶ The description in Dutch
|   |       +-- description.en.md        # Optional: The description in English
|   |       +-- 📂media                 # Optional folder
|   |       |   +-- some_image.png       # Optional: An image used in the description
|   |       +-- 📂boilerplate           # Optional folder
|   |           +-- boilerplate          # Optional: loaded automatically in submission text area
|   :
:
```

## Recommended `dirconfig.json`

> [More info about exercise directory structure](https://docs.dodona.be/en/references/exercise-directory-structure/)

````json
{
  "type": "exercise",
  "programming_language": "html",
  "access": "private",
  "evaluation": {
    "handler": "html",
    "time_limit": 10,
    "memory_limit": 50000000
  },
  "labels": [
    "website",
    "html",
    "css"
  ],
  "author": "Firstname Lastname <firstname_lastname@ugent.be>",
  "contact": "firstname_lastname@ugent.be"
}
````

## Recommended `config.json` (example with default settings)

````json
{
  "description": {
    "names": {
      "nl": "Mijn eerste HTML oefening",
      "en": "My first HTML exercise"
    }
  },
  "type": "exercise",
  "programming_language": "html",
  "labels": [
    "website",
    "html"
  ],
  "evaluation": {
    "handler": "html"
  }
}
````

## Optional `evaluation` settings in `config.json`

If these settings are not defined, the default value is chosen.

| Evaluation setting | Description | Possible values | Default |
| ------------------ | ----------- | --------------- | ------- |
| `???`              | ???         | ???             | `???`   |

### Example of modified settings

````json
{
  "evaluation": {
    "???": "???",
  }
}
````

## Teacher manual for direct comparison mode

Another way of evaluating an exercise is by comparing it to the `solution.html` file in the `evaluation` folder (this is the default if no `evaluator.py` file is present). In this case, the structure of the student's submission will be compared to your solution, and you can provide extra options to specify how strict this comparison should be.

It does have to be noted that this way of evaluation allows for a lot less freedom. For flexible tests, consider using the checklist mode.

## Teacher manual for checklist mode (evaluating with `evaluator.py` script)

1. For autocomplete you need to add the folder `validator` with the `checks.pyi` at the root of your project in which you write the evaluators.
2. Create an `evaluator.py` file in the `evaluation` folder with the following code:
  
  > `evaluator.py` (Python 3.9+ recommended)
  >
  > ```python
  > from validators.checks import HtmlSuite, CssSuite, TestSuite, ChecklistItem
  > 
  > 
  > def create_suites(content: str) -> list[TestSuite]:
  >     html = HtmlSuite(content)
  >     css = CssSuite(content)
  > 
  >     return [html, css]
  > ```

3. Check if the HTML and/or CSS is valid

```python
html_valid = ChecklistItem("The HTML is valid.", suite.validate_html().or_abort())
```

5. Select the desired element

TODO: add example

5. Make a ChecklistItem

TODO: add example

6. Combine several ChecklistItems in one check



8. Add ChecklistItem to suite.checklist

TODO: add example

7. *Optional*: Add translations for the checklist just before the `return` keyword. Available languages: `nl` (Dutch, **n**eder**l**ands) and `en` (English, **en**glish). Language code needs to be lower case.

  ```python
  # Add Dutch translation
  your_suite.translations["nl"] = [
      "YOUR FIRST CHECKLIST ITEM DESCRIPTION",
      "YOUR SECOND CHECKLIST ITEM DESCRIPTION",
      "YOUR THIRD CHECKLIST ITEM DESCRIPTION"
      ]
  ```

8. *Optional*: Add boilerplate HTML to the boilerplate file. The contents of this file is loaded automatically in the submission text area of the users. You can use this to provide some starting code or structure to your students.

**Final checks:**

1. Make sure at least one TestSuite is returned (`html` and/or `css`).
2. Don't use `print()` in the `evaluator.py` file!

## Testing

## Contributors
* **S. De Clercq**
* **Q. Vervynck**
* T. Ramlot
* B. Willems

*Development funded by the [Faculty of Engineering and Architecture](https://www.ugent.be/ea/en) of [Ghent University](https://www.ugent.be/en)*
