from dodona.translator import Translator
from exceptions.utils import DelayedExceptions


class HtmlValidationError(Exception):
    """Base class for HTML related exceptions in this module."""
    def __init__(self, translator: Translator):
        self.translator = translator


class LocatableHtmlValidationError(HtmlValidationError):
    """Exceptions that can be located"""
    def __init__(self, translator: Translator, tag_location: [str], position: (int, int)):
        self._tag_location = tag_location
        self.position = position
        self.translator = translator

    def tag_location(self) -> str:
        if self._tag_location:
            return f"{self.translator.translate(Translator.Text.LOCATED_AT)}: " \
                   f"{self.fpos()} | {' -> '.join([f'<{x}>' for x in self._tag_location])}"
        else:
            return f"{self.translator.translate(Translator.Text.LOCATED_AT)}: {self.fpos()}"

    def fpos(self) -> str:
        return f"{self.translator.translate(Translator.Text.LINE)} {self.position[0]} " \
               f"{self.translator.translate(Translator.Text.POSITION)} {self.position[1]}"


"""
EXCEPTIONS FOR TAGS
"""


class TagError(LocatableHtmlValidationError):
    """Exception that contains a tag"""
    def __init__(self, translator: Translator, tag_location: [str], position: (int, int), tag: str):
        super(TagError, self).__init__(translator, tag_location, position)
        self.tag = tag


class MissingClosingTagError(TagError):
    """Exception that indicates that the closing tag is missing for a tag"""
    def __str__(self):
        return f"{self.translator.translate(Translator.Text.MISSING_CLOSING_TAG)} <{self.tag}> ({self.tag_location()})"


class InvalidTagError(TagError):
    """Exception that indicates that a tag is invalid (tag doesn't exist or isn't allowed to be used"""
    def __str__(self):
        return f"{self.translator.translate(Translator.Text.INVALID_TAG)}: <{self.tag}> ({self.tag_location()})"


class NoSelfClosingTagError(TagError):
    def __str__(self):
        return f"{self.translator.translate(Translator.Text.NO_SELF_CLOSING_TAG)}: <{self.tag}> ({self.tag_location()})"


class UnexpectedTagError(TagError):
    """Exception that indicates that a certain tag was not expected
        ex: you don't expect a <html> tag inside of a <body> tag
    """
    def __str__(self):
        return f"{self.translator.translate(Translator.Text.UNEXPECTED_TAG)}: <{self.tag}> ({self.tag_location()})"


"""
EXCEPTIONS FOR ATTRIBUTES
"""


class TagAttributeError(LocatableHtmlValidationError):
    def __init__(self, translator: Translator, tag: str, tag_location: [str], position: (int, int), attribute: str):
        super(TagAttributeError, self).__init__(translator, tag_location, position)
        self.tag = tag
        self.attribute = attribute


class InvalidAttributeError(TagAttributeError):
    """Exception that indicates that an attribute is invalid for a tag"""
    def __str__(self):
        return f"{self.translator.translate(Translator.Text.INVALID_ATTRIBUTE)} <{self.tag}>: " \
               f"{self.attribute} ({self.tag_location()})"


class MissingRequiredAttributesError(TagAttributeError):
    """Exception that indicates that a required attribute for a tag is missing"""
    def __str__(self):
        return f"{self.translator.translate(Translator.Text.MISSING_REQUIRED_ATTRIBUTE)} <{self.tag}>: " \
               f"{self.attribute} ({self.tag_location()})"


class MissingRecommendedAttributesWarning(TagAttributeError):
    """Exception that indicates that a recommended attribute is missing
            this is considered a warning, and all instances of this class will be
            gathered and thrown at the very end if no other exceptions appear
    """
    def __str__(self):
        return f"{self.translator.translate(Translator.Text.MISSING_RECOMMENDED_ATTRIBUTE)} <{self.tag}>: " \
               f"{self.attribute} ({self.tag_location()})"


class Warnings(DelayedExceptions):
    def __init__(self, translator: Translator):
        super(Warnings, self).__init__()
        self.translator = translator
        self.exceptions: LocatableHtmlValidationError  # makes them sortable

    def __str__(self):
        self.exceptions.sort()
        return f"{self.translator.translate(Translator.Text.WARNINGS)} ({len(self)}):\n{self._print_exceptions()}"
