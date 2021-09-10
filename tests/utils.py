from os import path

# Location of this test file
basepath = path.dirname(__file__)

# Location of html files
html_dir = path.abspath(path.join(basepath, "html_files"))


def load_html_file(filename: str) -> str:
    """Utility function to load an HTML file in order to use the content in tests
    This way, we don't have to have big blocks of HTML strings in every test.
    """
    # Allow only the name to be passed (shorter)
    if not filename.endswith(".html"):
        filename += ".html"

    with open(path.join(html_dir, filename), "r") as file:
        return file.read()
