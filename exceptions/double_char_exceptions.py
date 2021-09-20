from dodona.translator import Translator
from exceptions.utils import DelayedExceptions


class DoubleCharError(Exception):
    """Base class for double char related exceptions in this module."""
    def __init__(self,  translator: Translator):
        self.translator = translator


class LocatableDoubleCharError(DoubleCharError):
    """Exceptions that can be located"""
    def __init__(self, translator: Translator, position: (int, int)):
        super(LocatableDoubleCharError, self).__init__(translator)
        self.position = position

    def __lt__(self, other):
        return self.position < other.position

    def __gt__(self, other):
        return self.position > other.position

    def __le__(self, other):
        return self.position <= other.position

    def __ge__(self, other):
        return self.position >= other.position

    def __eq__(self, other):
        return self.position == other.position

    def __ne__(self, other):
        return self.position != other.position

    def location(self) -> str:
        return f"{self.translator.translate(Translator.Text.LOCATED_AT)}: {self.fpos()}"

    def fpos(self) -> str:
        return f"{self.translator.translate(Translator.Text.LINE)} {self.position[0] + 1} " \
               f"{self.translator.translate(Translator.Text.POSITION)} {self.position[1] + 1} "


class MissingCharError(LocatableDoubleCharError):
    """Exception that indicates a missing character for a character"""
    def __init__(self, translator: Translator, char: str, position: (int, int)):
        super(MissingCharError, self).__init__(translator, position)
        self.char = char


class MissingOpeningCharError(MissingCharError):
    """Exception that indicates that an opening equivalent of a certain character is missing"""
    def __str__(self):
        return f"{self.translator.translate(Translator.Text.MISSING_OPENING_CHARACTER)} '{self.char}' {self.location()}"


class MissingClosingCharError(MissingCharError):
    """Exception that indicates that a closing equivalent of a certain character is missing"""
    def __str__(self):
        return f"{self.translator.translate(Translator.Text.MISSING_CLOSING_CHARACTER)} '{self.char}' {self.location()}"


class MultipleMissingCharsError(DelayedExceptions):
    def __init__(self, translator: Translator):
        super().__init__()
        self.translator = translator
        self.exceptions: [LocatableDoubleCharError]

    def __str__(self):
        self.exceptions.sort()
        return f"{self.translator.translate(Translator.Text.ERRORS)} ({len(self)}):\n{self._print_exceptions()}"
