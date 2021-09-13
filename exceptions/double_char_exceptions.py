from dodona.translator import Translator


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
        return f"{self.translator.translate(Translator.Text.LINE)} {self.position[0]} " \
               f"{self.translator.translate(Translator.Text.POSITION)} {self.position[1]} "


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


class MultipleMissingCharsError(Exception):
    """class made to gather multiple missing chars errors"""
    def __init__(self, translator: Translator):
        self.translator = translator
        self.errors: [MissingCharError] = []

    def __len__(self):
        return len(self.errors)

    def __bool__(self):
        return bool(self.errors)

    def add(self, error: MissingCharError):
        self.errors.append(error)

    def clear(self):
        self.errors.clear()

    def __str__(self):
        self.errors.sort()
        return f"{self.translator.translate(Translator.Text.ERRORS)} ({len(self)}):\n{self._print_errors()}"

    def _print_errors(self):
        return "\n".join([str(x) for x in self.errors])
