from dodona.translator import Translator


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


class MissingClosingTagError(LocatableHtmlValidationError):
    """Exception that indicates that the closing tag is missing for a tag"""
    def __init__(self, translator: Translator, tag: str, tag_location: [str], position: (int, int)):
        super(MissingClosingTagError, self).__init__(translator, tag_location, position)
        self.tag = tag

    def __str__(self):
        return f"{self.translator.translate(Translator.Text.MISSING_CLOSING_TAG)} <{self.tag}> ({self.tag_location()})"


class InvalidTagError(LocatableHtmlValidationError):
    """Exception that indicates that a tag is invalid (tag doesn't exist or isn't allowed to be used"""
    def __init__(self, translator: Translator, invalid_tag: str, tag_location: [str], position: (int, int)):
        super(InvalidTagError, self).__init__(translator, tag_location, position)
        self.invalid_tag = invalid_tag

    def __str__(self):
        return f"{self.translator.translate(Translator.Text.INVALID_TAG)}: <{self.invalid_tag}> ({self.tag_location()})"


class NoSelfClosingTagError(LocatableHtmlValidationError):
    def __init__(self, translator: Translator, tag: str, tag_location: [str], position: (int, int)):
        super(NoSelfClosingTagError, self).__init__(translator, tag_location, position)
        self.tag = tag

    def __str__(self):
        return f"{self.translator.translate(Translator.Text.NO_SELF_CLOSING_TAG)}: <{self.tag}> ({self.tag_location()})"


class UnexpectedTagError(LocatableHtmlValidationError):
    """Exception that indicates that a certain tag was not expected
        ex: you don't expect a <html> tag inside of a <body> tag
    """
    def __init__(self, translator: Translator, unexpected_tag: str, tag_location: [str], position: (int, int)):
        super(UnexpectedTagError, self).__init__(translator, tag_location, position)
        self.unexpected_tag = unexpected_tag

    def __str__(self):
        return f"{self.translator.translate(Translator.Text.UNEXPECTED_TAG)}: <{self.unexpected_tag}> ({self.tag_location()})"


class InvalidAttributeError(LocatableHtmlValidationError):
    """Exception that indicates that an attribute is invalid for a tag"""
    def __init__(self, translator: Translator, tag: str, invalid_attribute: str, tag_location: [str], position: (int, int)):
        super(InvalidAttributeError, self).__init__(translator, tag_location, position)
        self.tag = tag
        self.invalid_attribute = invalid_attribute

    def __str__(self):
        return f"{self.translator.translate(Translator.Text.INVALID_ATTRIBUTE)} <{self.tag}>: " \
               f"{self.invalid_attribute} ({self.tag_location()})"


class MissingRequiredAttributeError(LocatableHtmlValidationError):
    """Exception that indicates that a required attribute for a tag is missing"""
    def __init__(self, translator: Translator, tag: str, missing_attributes: str, tag_location: [str], position: (int, int)):
        super(MissingRequiredAttributeError, self).__init__(translator, tag_location, position)
        self.tag = tag
        self.missing_attributes = missing_attributes

    def __str__(self):
        return f"{self.translator.translate(Translator.Text.MISSING_REQUIRED_ATTRIBUTE)} <{self.tag}>: " \
               f"{self.missing_attributes} ({self.tag_location()})"


class EvaluationAborted(RuntimeError):
    """Exception raised when evaluation is aborted because a crucial test did not pass"""
    def __init__(self, *args):
        super().__init__(*args)


class MissingRecommendedAttributesWarning(LocatableHtmlValidationError):
    """Exception that indicates that a recommended attribute is missing
            this is considered a warning, and all instances of this class will be
            gathered and thrown at the very end if no other exceptions appear
    """
    def __init__(self, translator: Translator, tag: str, missing_attributes: str, tag_location: [str], position: (int, int)):
        super(MissingRecommendedAttributesWarning, self).__init__(translator, tag_location, position)
        self.tag = tag
        self.missing_attributes = missing_attributes

    def __str__(self):
        return f"{self.translator.translate(Translator.Text.MISSING_RECOMMENDED_ATTRIBUTE)} <{self.tag}>: " \
               f"{self.missing_attributes} ({self.tag_location()})"


class Warnings(Exception):
    """class made to gather multiple warnings"""
    def __init__(self, translator: Translator):
        self.translator = translator
        self.warnings: [MissingRecommendedAttributesWarning] = []

    def __len__(self):
        return len(self.warnings)

    def __bool__(self):
        return bool(self.warnings)

    def add(self, warning: MissingRecommendedAttributesWarning):
        self.warnings.append(warning)

    def clear(self):
        self.warnings.clear()

    def __str__(self):
        return f"{self.translator.translate(Translator.Text.WARNINGS)} ({len(self)}):\n{self._print_warnings()}"

    def _print_warnings(self) -> str:
        return "\n".join([str(x) for x in self.warnings])
