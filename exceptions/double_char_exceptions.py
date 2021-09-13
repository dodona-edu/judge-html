class DoubleCharError(Exception):
    """Base class for HTML related exceptions in this module."""
    pass


class LocatableDoubleCharError(DoubleCharError):
    def __init__(self, position: (int, int)):
        self.position = position

    def location(self) -> str:
        return f"located at: {self.fpos()}"

    def fpos(self) -> str:
        return f"line {self.position[0]} position {self.position[1]}"


class MissingCharError(LocatableDoubleCharError):
    def __init__(self, char: str, position: (int, int)):
        super(MissingCharError, self).__init__(position)
        self.char = char


class MissingOpeningCharError(MissingCharError):
    def __str__(self):
        return f"Missing opening character for '{self.char}' at {self.location()}"


class MissingClosingCharError(MissingCharError):
    def __str__(self):
        return f"Missing opening character for '{self.char}' at {self.location()}"

