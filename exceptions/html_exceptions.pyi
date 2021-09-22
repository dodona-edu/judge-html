from typing import Tuple, List

from dodona.translator import Translator
from exceptions.utils import DelayedExceptions


class HtmlValidationError(Exception):
    translator: Translator

    def __init__(self, translator: Translator): ...


class LocatableHtmlValidationError(HtmlValidationError):
    _tag_location: List[str]
    position: Tuple[int, int]

    def __init__(self, translator: Translator, tag_location: List[str], position: Tuple[int, int]): ...

    def tag_location(self) -> str: ...

    def fpos(self) -> str: ...


class TagError(LocatableHtmlValidationError):
    tag: str

    def __init__(self, translator: Translator, tag_location: [str], position: (int, int), tag: str): ...

class MissingClosingTagError(TagError):
    def __str__(self) -> str: ...


class InvalidTagError(TagError):
    def __str__(self) -> str: ...


class NoSelfClosingTagError(TagError):
    def __str__(self) -> str: ...


class UnexpectedTagError(TagError):
    def __str__(self) -> str: ...


class UnexpectedClosingTagError(TagError):
    def __str__(self): ...


class TagAttributeError(LocatableHtmlValidationError):
    tag: str
    attribute: str

    def __init__(self, translator: Translator, tag: str, tag_location: List[str], position: Tuple[int, int], attribute: str): ...


class InvalidAttributeError(TagAttributeError):
    def __str__(self) -> str: ...


class MissingRequiredAttributesError(TagAttributeError):
    def __str__(self) -> str: ...


class MissingRecommendedAttributesWarning(TagAttributeError):
    def __str__(self) -> str: ...


class Warnings(DelayedExceptions):
    translator: Translator
    exceptions: List[LocatableHtmlValidationError]

    def __init__(self, translator: Translator): ...

    def __str__(self) -> str: ...
