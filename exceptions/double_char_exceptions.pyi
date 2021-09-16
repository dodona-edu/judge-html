from typing import Tuple

from dodona.translator import Translator
from exceptions.utils import DelayedExceptions


class DoubleCharError(Exception):
    translator: Translator

    def __init__(self,  translator: Translator): ...


class LocatableDoubleCharError(DoubleCharError):
    position: Tuple[int, int]

    def __init__(self, translator: Translator, position: Tuple[int, int]): ...

    def __lt__(self, other) -> bool: ...

    def __gt__(self, other) -> bool: ...

    def __le__(self, other) -> bool: ...

    def __ge__(self, other) -> bool: ...

    def __eq__(self, other) -> bool: ...

    def __ne__(self, other) -> bool: ...

    def location(self) -> str: ...

    def fpos(self) -> str: ...


class MissingCharError(LocatableDoubleCharError):
    char: str

    def __init__(self, translator: Translator, char: str, position: Tuple[int, int]): ...


class MissingOpeningCharError(MissingCharError):
    def __str__(self) -> str: ...


class MissingClosingCharError(MissingCharError):
    def __str__(self) -> str: ...


class MultipleMissingCharsError(DelayedExceptions):
    translator: Translator

    def __init__(self, translator: Translator): ...

    def __str__(self) -> str: ...
