from dodona.translator import Translator


class NotTheSame(Exception): pass


def compare(solution: str, submission: str, trans: Translator, **kwargs): ...
