from dodona.translator import Translator


class NotTheSame(Exception):
    def __init__(self, msg: str, line: int, trans: Translator):
        self.msg = msg
        self.line = line - 1
        self.trans = trans

    def annotation(self):
        return self.msg

    def __repr__(self):
        return f"{self.msg} {self.trans.translate(Translator.Text.AT_LINE)} {self.line + 1}"

    def __str__(self):
        return self.__repr__()
