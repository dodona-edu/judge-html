from typing import List

from dodona.translator import Translator


class AnnotatedException(Exception):
    msg: str
    line: int
    trans: Translator

    def __init__(self, msg: str, line: int, trans: Translator, *args): ...

    def message_str(self):
        """Create the message that should be displayed in the Dodona Tab"""
        ...

    def annotation_str(self):
        """Create the message that should be displayed in the annotation in the Code Tab"""
        ...


class EvaluationAborted(RuntimeError):
    def __init__(self, *args): ...

class InvalidTranslation(ValueError):
    def __init__(self, *args): ...


class DelayedExceptions(Exception):
    exceptions: List[Exception]

    def __init__(self): ...

    def __len__(self) -> int: ...

    def __bool__(self) -> bool: ...

    def add(self, exception: Exception): ...

    def clear(self): ...

    def _print_exceptions(self) -> str: ...

