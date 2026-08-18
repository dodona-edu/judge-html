import re
from typing import NamedTuple


class Regex(NamedTuple):
    pattern: str
    flags: re.RegexFlag


# Has to be the first non-empty line, ignoring comments
doctype_re = Regex(r"^\s*(<\!--.*-->\s*)*<\!doctype html", re.IGNORECASE | re.MULTILINE)
