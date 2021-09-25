from dodona.translator import Translator


class NotTheSame(Exception):
    line: int


def compare(solution: str, submission: str, trans: Translator, **kwargs): ...
