import re
from typing import NamedTuple


class Regex(NamedTuple):
    pattern: str
    flags: re.RegexFlag


def _skip_whitespace(line: str, i: int) -> int:
    while i < len(line) and line[i].isspace():
        i += 1
    return i


def has_leading_doctype(content: str) -> bool:
    """True if some line starts with `<!doctype html` after whitespace and single-line `<!-- -->` comments."""
    for line in content.split("\n"):
        i = _skip_whitespace(line, 0)
        while line.startswith("<!--", i) and (end := line.find("-->", i + 4)) != -1:
            i = _skip_whitespace(line, end + 3)
        if line[i : i + 14].lower() == "<!doctype html":
            return True
    return False
