from dodona.translator import Translator


class EvaluationAborted(RuntimeError):
    """Exception raised when evaluation is aborted because a crucial test did not pass"""
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

