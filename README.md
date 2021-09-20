# HTML&CSS judge for [Dodona](https://dodona.ugent.be/)

## Judge features

* Checklist (correct, fail, warning)
* Feedback in language of user (Dutch or English)
* HTML (TODO &CSS) render of student submission
* Support for partial exercises (exercises that focus on one tag)
* Extensive [customization possible in `config.json`](#optional-evaluation-settings-in-configjson)
* Elaborate [feedback](#feedback)

### Judge properties
* Tags are case-insensitive
* Inline CSS is not allowed (internal CSS is)
* `<script>` and `<noscript>` tag are not allowed
* Self-closing tags are not allowed
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
|   |   |   +-- solution.html            # ▶ The HTML model solution file
|   |   |   +-- solution.css             # ▶ The CSS model solution file
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

## Testing


## Contributors
* **S. De Clercq**
* **Q. Vervynck**
* T. Ramlot
* B. Willems

*Development funded by the [Faculty of Engineering and Architecture](https://www.ugent.be/ea/en) of [Ghent University](https://www.ugent.be/en)*
