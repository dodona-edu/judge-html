from typing import Tuple, List

from dodona.translator import Translator
from exceptions.utils import DelayedExceptions, FeedbackException


class HtmlValidationError(FeedbackException):
    def __init__(self, trans: Translator, msg: str, line: int, pos: int, *args):
        ...

class LocatableHtmlValidationError(HtmlValidationError):
    _tag_location: List[str]
    position: Tuple[int, int]

    def __init__(self, trans: Translator, msg: str, line: int, pos: int, *args):
        ...

    def location(self) -> str: ...

    def fpos(self) -> str: ...

    def annotation(self) -> str: ...

    def __str__(self): ...



class MissingOpeningTagError(LocatableHtmlValidationError):
    def __init__(self, trans: Translator, tag: str, line: int, pos: int, *args):
        ...

class MissingClosingTagError(LocatableHtmlValidationError):
    def __init__(self, trans: Translator, tag: str, line: int, pos: int, *args):
        ...

class InvalidTagError(LocatableHtmlValidationError):
    def __init__(self, trans: Translator, tag: str, line: int, pos: int, *args):
        ...

class NoSelfClosingTagError(LocatableHtmlValidationError):
    def __init__(self, trans: Translator, tag: str, line: int, pos: int, *args):
        ...

class UnexpectedTagError(LocatableHtmlValidationError):
    def __init__(self, trans: Translator, tag: str, line: int, pos: int, *args):
        ...

class UnexpectedClosingTagError(LocatableHtmlValidationError):
    def __init__(self, trans: Translator, tag: str, line: int, pos: int, *args):
        ...



class InvalidAttributeError(LocatableHtmlValidationError):
    def __init__(self, trans: Translator, tag: str, attribute: str, line: int, pos: int, *args):
        ...

class MissingRequiredAttributesError(LocatableHtmlValidationError):
    def __init__(self, trans: Translator, tag: str, attribute: str, line: int, pos: int, *args):
        ...

class DuplicateIdError(LocatableHtmlValidationError):
    def __init__(self, trans: Translator, tag: str, attribute: str, line: int, pos: int, *args):
        ...

class AttributeValueError(LocatableHtmlValidationError):
    def __init__(self, translator: Translator, tag_location: [str], position: (int, int), message: str): ...
        ...

class MissingRecommendedAttributesWarning(LocatableHtmlValidationError):
    def __init__(self, trans: Translator, tag: str, attribute: str, line: int, pos: int, *args):
        ...

class Warnings(DelayedExceptions):
    translator: Translator
    exceptions: List[LocatableHtmlValidationError]

    def __init__(self, translator: Translator): ...

    def __str__(self): ...