# HTML&CSS judge for [Dodona](https://dodona.ugent.be/)

> The HTML judge has two ways to evaluate a student's submitted solution. In *comparison mode*, the structure of the submitted solution is compared to a model solution based on generic comparison criteria. The teacher can set how strictly that comparison should be done.
>
> *Checklist mode* offers even more possibilities because the submitted solution is checked against the criteria explicitly set up for the exercise by the teacher. The feedback that students get to see shows which criteria have or have not been met.  
>
> In both modes, the submitted code is checked against a number of conditions for valid HTML code. In addition, the result of the submitted HTML and CSS code in Dodona is also shown in a separate tab of the feedback page.
>
> ![judge-html](docs/media/judge-html.png)
>
> This Dodona course contains some sample exercises that were used in developing the HTML judge:
>
> * https://dodona.ugent.be/en/courses/941/
>
> There are a number of sample exercises on Dodona's sample exercises repository to demonstrate the use of the judge:
>
> * https://github.com/dodona-edu/example-exercises
>

## Judge features

* Checklist (correct, fail, warning, error)
* Feedback in language of user (Dutch or English)
* HTML and CSS render of student submission
* Support for partial exercises (exercises that focus on one tag)
* Elaborate [feedback](#feedback)
* Two evaluation methods:
  1. [**Comparison mode**](#quick-start-guide-for-comparison-mode-with-solutionhtml) with `solution.html` file (fast, easy, [limited configuration options](#optional-evaluation-settings-in-configjson))
  2. [**Checklist mode**](#quick-start-guide-for-checklist-mode-with-evaluatorpy) with `evaluator.py` (a lot of flexibility, support for [Emmet syntax](https://docs.emmet.io/abbreviations/syntax/))

### Judge properties

* Tags are case-insensitive.
* Inline CSS is not allowed (internal CSS is).
* `<script>` and `<noscript>` tag are not allowed.
* Self-closing (non-void) tags are not allowed (e.g. `<p/>`, `<div/>`).
* Default TestSuite for HTML and/or CSS (in different tabs with automatic validation).
* Absolute file paths are not allowed.

## Feedback

### HTML&CSS

* Syntax errors
  * Check if brackets/quotes open and close (`(`, `<`, `{`, `[`, `'`, `"`)
  * Each tag that opens must have a corresponding closing tag.
  * Checks if all tags are valid
* Check if all id's are unique
* Check if the tag is permitted in the parent tag
* Check for required (and recommended) attributes
* Check for invalid attributes (e.g. style attribute is not allowed)

### HTML
* Check if required attributes are present.
* Warning if recommended attributes are missing.

### CSS
* Automatic color conversion (`name`, `#RRGGBB`, `rgb(R,G,B)`, `rgb(R%,G%,B%)`, `#RGB`, `hsl(H,S%,L%)`, `rgba(R,G,B,a)`, `rgba(R%,G%,B%,a)`, `hsla(H,S%,L%,a)`)

## Table of Contents
- [Recommended exercise directory structure](#recommended-exercise-directory-structure)
- [Recommended `dirconfig.json`](#recommended-dirconfigjson)
- [Recommended `config.json` (example with default settings)](#recommended-configjson-example-with-default-settings)
- [Quick start guide for **comparison mode** (with `solution.html`)](#quick-start-guide-for-comparison-mode-with-solutionhtml)
  - [Optional `evaluation` settings in `config.json`](#optional-evaluation-settings-in-configjson)
  - [`DUMMY` values](#dummy-values)
- [Quick start guide for **checklist mode** (with `evaluator.py`)](#quick-start-guide-for-checklist-mode-with-evaluatorpy)
  - [Minimal example](#minimal-example)
- [Testing](#testing)
- [Contributors](#contributors)

## Recommended exercise directory structure

> [More info about repository directory structure](https://docs.dodona.be/en/references/repository-directory-structure/#example-of-a-valid-repository-structure)

Add your solution/evaluator file (`solution.html` for comparison mode or `evaluator.py` for checklist mode) to the **`evaluation`** folder. Absolute necessary files are marked with `▶` in the tree structure below.

```text
+-- README.md                            # Optional: Describes the repository
+-- dirconfig.json                       # Shared config for all exercises in subdirs
+-- 📂public                            # Optional: Contains files that belong to the course or series
|   +-- my_picture.png                   # Optional: An image to reuse throughout the course
+-- 📂validators                        # ▶ Folder that needs to be imported in every evaluator.py
|   +-- checks.pyi                       # ▶ File needed for autocomplete (explained later)
+-- 📂html-exercises                    # We could group exercises in a folder
|   +-- 📂first_html_exercise           # Folder name for the exercise
|   |   +-- config.json                  # ▶ Configuration of the exercise
|   |   +-- 📂evaluation                # -- 🔽️ ADD YOUR FILES HERE 🔽 --
|   |   |   +-- solution.html            # ▶ The HTML model solution for comparison mode
|   |   |   +-- evaluator.py             # ▶ The Python code for checklist mode
|   |   +-- 📂solution                  # Optional: This will be visible in Dodona
|   |   |   +-- solution.html            # Optional: The HTML model solution file
|   |   +-- 📂preparation               # Optional folder
|   |   |   +-- generator.py             # Optional: Script to generate data
|   |   +-- 📂description               #
|   |       +-- description.nl.md        # ▶ The description in Dutch
|   |       +-- description.en.md        # Optional: The description in English
|   |       +-- 📂media                 # Optional folder
|   |       |   +-- some_image.png       # Optional: An image used in the description and/or exercise
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
  "access": "public",
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

## Quick start guide for **comparison mode** (with `solution.html`)

> [Full documentation for **comparison mode**](/docs/pages/evaluating-by-comparing.md)

The **easiest** and **fastest** way of evaluating an exercise is by comparing it to the `solution.html` file in the `evaluation` folder. This is the default if no `evaluator.py` file is present. In this case, the structure of the student's submission will be compared to your solution, and you can provide extra options to specify how strict this comparison should be. If submission and solution don't match, a similarity percentage is shown.

It does have to be noted that this way of evaluation allows for a lot less freedom. **For flexible tests, consider using the [checklist mode](#quick-start-guide-for-checklist-mode-with-evaluatorpy).**

### Optional `evaluation` settings in `config.json`

In the `config.json` file of the exercise you can give some options as to how the comparison should happen. If these settings are not defined, the default value is chosen. By default, only the HTML-structure and CSS is checked.

| Evaluation setting | Description | Possible values | Default |
| ------------------ | ----------- | --------------  | ------- |
| `attributes` |  Check whether attributes are exactly the same in solution and submission.* | `true`/`false` | `false`  |
| `minimal_attributes`| Check whether **at least** the attributes in the solution are supplied in the submission, extra attributes are **allowed**. | `true`/`false` | `false` |
| `recommended`| Check whether **all recommended** attributes are present, these are warnings, the check won't fail if some of them are missing | `true`/`false` | `true` |
| `contents`| Check whether the contents of each tag in the solution are exactly the same as in the submission. | `true`/`false` | `false` |
| `css` | If there are CSS rules defined in the solution, check if the submission can match these rules. We don't compare the CSS rules themselves, but rather whether every element in the submission has at least the CSS-rules defined in the solution. | `true`/`false` | `true` |
| `comments` | Check whether the submission has the same comments as the solution. | `true`/`false` | `false` |

*\*Note: when both `attributes` and `minimal_attributes` are supplied, `attributes` will take preference as it is stricter.*

#### Example of modified settings

````json
{
  ...
  "evaluation": {
    "handler": "html",
    "minimal_attributes": true,
    "contents": true
  },
  ...
}
````

### `DUMMY` values

In a lot of cases you're going to want the students to write _something_ or to give _some value_ to an attribute, but you don't care what it is they write down. For that you can use the `DUMMY` keyword for attribute values and for text in your `solution.html` file.

## Quick start guide for checklist mode (with `evaluator.py`)

> [Full documentation for **checklist mode**](/docs)

1. For autocomplete you need to add the folder `validator` with the [`checks.pyi`](validators/checks.pyi) file at the root of your project in which you write the evaluators.

2. Create an `evaluator.py` file in the `evaluation` folder with the following code:

    > `evaluator.py` (Python 3.9+ **required**)
    >
    > ```python
    > from validators.checks import HtmlSuite, CssSuite, TestSuite, ChecklistItem
    > 
    > 
    > def create_suites(content: str) -> list[TestSuite]:
    >     html = HtmlSuite(content)
    >     css = CssSuite(content)
    >
    >     # Add checks here
    > 
    >     return [html, css]
    > ```

4. Make a `ChecklistItem` (in regular or Emmet syntax) and append it to a TestSuite. Combine several Checks in one ChecklistItem if you want to.

    **Regular syntax**

    ```python
    body = html.element("body")
    table = body.get_child('table', direct=True)

    html.make_item("The body has a table. (regular)", table.exists())
    html.make_item("The table has two rows. (regular)", table.get_children('tr').at_least(2))
    ```

    **Emmet syntax**

    ```python
    html.make_item_from_emmet("The body has a table.", "body>table")
    html.make_item_from_emmet("The table has two rows.", "body>table>tr*2")
    ```

5. *Optional*: Add translations for the checklist just before the `return` keyword. Available languages: `nl` (Dutch, **n**eder**l**ands) and `en` (English, **en**glish). The language code needs to be lower case.

    ```python
    # Add Dutch translation
    html.translations["nl"] = [
        "De body heeft een tabel.",
        "De tabel heeft twee rijen."
    ]
    ```

6. *Optional*: Add boilerplate HTML to the boilerplate file. The contents of this file is loaded automatically in the submission text area of the users. You can use this to provide some starting code or structure to your students.

**Final checks:**

1. Make sure at least one TestSuite is returned (`html` and/or `css`).
2. Don't use `print()` in the `evaluator.py` file!

### Minimal example

> `evaluator.py`
>
> ```python
> from validators.checks import HtmlSuite, TestSuite
> 
> 
> def create_suites(content: str) -> list[TestSuite]:
>    html = HtmlSuite(content)
>
>    body = html.element("body")
>    table = body.get_child('table', direct=True)
>
>    html.make_item("The body has a table. (regular)", table.exists())
>    html.make_item("The table has two rows. (regular)", table.get_children('tr').at_least(2))
>
>    html.make_item_from_emmet("The body has a table. (Emmet)", "body>table")
>    html.make_item_from_emmet("The table has two rows. (Emmet)", "body>table>tr*2")
>
>    html.translations["nl"] = [
>        "De body heeft een tabel. (normaal)",
>        "De tabel heeft twee rijen. (normaal)",
>        "De body heeft een tabel. (Emmet)",
>        "De tabel heeft twee rijen. (Emmet)"
>    ]
> 
>     return [html]
> ```

## Testing

## Contributors

* **S. De Clercq**
* **Q. Vervynck**
* T. Ramlot
* B. Willems

*Development funded by the [Faculty of Engineering and Architecture](https://www.ugent.be/ea/en) of [Ghent University](https://www.ugent.be/en)*
