from dodona.translator import Translator


class AnnotatedException(Exception):
    msg: str
    line: int
    trans: Translator

    def __init__(self, msg: str, line: int, trans: Translator, *args):
        super().__init__(msg, *args)

        self.msg = msg
        self.line = line - 1  # 1-based to 0-based
        self.trans = trans

    def message_str(self):
        """Create the message that should be displayed in the Dodona Tab"""
        # Line number < 0 means no line number should be shown (eg. empty submission)
        # (#137)
        if self.line < 0:
            return self.msg

        return f"{self.msg} {self.trans.translate(Translator.Text.AT_LINE)} {self.line + 1}"

    def annotation_str(self):
        """Create the message that should be displayed in the annotation in the Code Tab"""
        # Don't show line number in annotations (#137)
        return self.msg


class EvaluationAborted(RuntimeError):
    """Exception raised when evaluation is aborted because a crucial test did not pass"""
    def __init__(self, *args):
        super().__init__(*args)


class InvalidTranslation(ValueError):
    """Exception raised when the length of a translation doesn't match the checklist"""
    def __init__(self, *args):
        super().__init__(*args)


class DelayedExceptions(Exception):
    """class made to gather multiple exceptions"""
    def __init__(self):
        self.exceptions: [Exception] = []

    def __len__(self):
        return len(self.exceptions)

    def __bool__(self):
        return bool(self.exceptions)

    def add(self, exception: Exception):
        self.exceptions.append(exception)

    def clear(self):
        self.exceptions.clear()

    def _print_exceptions(self) -> str:
        return "\n".join([str(x) for x in self.exceptions])

