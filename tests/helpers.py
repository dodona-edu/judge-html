from utils.file_loaders import html_loader as _html_loader
from os import path

# Location of this test file
basepath = path.dirname(__file__)

# Location of html files
html_dir = path.abspath(path.join(basepath, "../tests/html_files"))


def html_loader(file: str) -> str:
    return _html_loader(path.join(html_dir, file))
