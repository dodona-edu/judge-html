from dodona.translator import Translator


class NotTheSame(Exception):
    msg: str
    line: int
    trans: Translator

    def message_str(self) -> str: ...

    def annotation_str(self) -> str: ...


def compare(solution: str, submission: str, trans: Translator, **kwargs): ...
