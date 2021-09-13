class DoubleCharError(Exception):
    """Base class for HTML related exceptions in this module."""
    pass


class LocatableDoubleCharError(DoubleCharError):
    def __init__(self, position: (int, int)):
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
        return f"Missing closing character for '{self.char}' at {self.location()}"


class MultipleMissingCharsError(Exception):
    def __init__(self):
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
        return f"Errors ({len(self)}):\n{self._print_errors()}"

    def _print_errors(self):
        return "\n".join([str(x) for x in self.errors])
