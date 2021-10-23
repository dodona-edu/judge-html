from dodona.translator import Translator
from exceptions.utils import DelayedExceptions, FeedbackException


class DoubleCharError(FeedbackException):
    """Base class for double char related exceptions in this module."""
    def __init__(self, trans: Translator, msg: str, line: int, pos: int, *args):
        super(DoubleCharError, self).__init__(trans=trans, msg=msg, line=line, pos=pos, args=args)


class LocatableDoubleCharError(DoubleCharError):
    """Exceptions that can be located"""

    def __init__(self, trans: Translator, msg: str, line: int, pos: int, *args):
        super(LocatableDoubleCharError, self).__init__(trans=trans, msg=msg, line=line, pos=pos, args=args)

    def __lt__(self, other):
        return (self.line, self.pos) < (other.line, other.pos)

    def __gt__(self, other):
        return (self.line, self.pos) > (other.line, other.pos)

    def __le__(self, other):
        return (self.line, self.pos) <= (other.line, other.pos)

    def __ge__(self, other):
        return (self.line, self.pos) >= (other.line, other.pos)

    def __eq__(self, other):
        return (self.line, self.pos) == (other.line, other.pos)

    def __ne__(self, other):
        return (self.line, self.pos) != (other.line, other.pos)


class MissingOpeningCharError(LocatableDoubleCharError):
    """Exception that indicates that an opening equivalent of a certain character is missing"""
    def __init__(self, trans: Translator, char: str, line: int, pos: int, *args):
        msg = f"{trans.translate(Translator.Text.MISSING_OPENING_CHARACTER)} '{char}'"
        super(MissingOpeningCharError, self).__init__(trans=trans, msg=msg, line=line, pos=pos, args=args)


class MissingClosingCharError(LocatableDoubleCharError):
    """Exception that indicates that a closing equivalent of a certain character is missing"""
    def __init__(self, trans: Translator, char: str, line: int, pos: int, *args):
        msg = f"{trans.translate(Translator.Text.MISSING_CLOSING_CHARACTER)} '{char}'"
        super(MissingOpeningCharError, self).__init__(trans=trans, msg=msg, line=line, pos=pos, args=args)


class MultipleMissingCharsError(DelayedExceptions):
    def __init__(self, translator: Translator):
        super().__init__()
        self.translator = translator
        self.exceptions: [LocatableDoubleCharError]

    def __str__(self):
        self.exceptions.sort()
        return f"{self.translator.translate(Translator.Text.ERRORS)} ({len(self)}):\n{self._print_exceptions()}"
