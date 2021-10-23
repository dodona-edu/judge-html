from dodona.translator import Translator
from exceptions.utils import FeedbackException


class NotTheSame(FeedbackException):
    def __init__(self, trans: Translator, msg: str, line: int, pos: int, *args):
        super(NotTheSame, self).__init__(trans=trans, msg=msg, line=line, pos=pos, args=args)

