from dodona.translator import Translator


class NotTheSame(Exception):
    def message_str(self) -> str: ...

    def annotation_str(self) -> str: ...


def compare(solution: str, submission: str, trans: Translator, **kwargs): ...
