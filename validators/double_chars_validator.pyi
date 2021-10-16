from typing import List, Dict

from exceptions.double_char_exceptions import *
from dodona.translator import Translator


class DoubleCharsValidator:
    translator: Translator
    opening: List[str]
    closing: List[str]
    convert: Dict[str, str]

    def __init__(self, translator: Translator): ...

    def parse_content(self, s: str) -> [str]: ...

    def validate_content(self, text: str): ...
