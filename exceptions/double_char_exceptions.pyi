from typing import Tuple

from dodona.translator import Translator
from exceptions.utils import DelayedExceptions, AnnotatedException


class DoubleCharError(AnnotatedException):
    """Base class for double char related exceptions in this module."""
    def __init__(self, trans: Translator, msg: str, line: int = -1, pos: int = -1, *args):
        ...


class LocatableDoubleCharError(DoubleCharError):

    def __init__(self, trans: Translator, msg: str, line: int, pos: int, *args):
        ...

    def __lt__(self, other) -> bool: ...

    def __gt__(self, other) -> bool: ...

    def __le__(self, other) -> bool: ...

    def __ge__(self, other) -> bool: ...

    def __eq__(self, other) -> bool: ...

    def __ne__(self, other) -> bool: ...


class MissingOpeningCharError(LocatableDoubleCharError):
    def __init__(self, trans: Translator, char: str, line: int, pos: int, *args):
        ...

class MissingClosingCharError(LocatableDoubleCharError):
    def __init__(self, trans: Translator, char: str, line: int, pos: int, *args):
        ...

class MultipleMissingCharsError(DelayedExceptions):
    translator: Translator

    def __init__(self, translator: Translator): ...

    def __str__(self) -> str: ...
