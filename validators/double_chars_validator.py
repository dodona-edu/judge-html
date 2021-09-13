from exceptions.double_char_exceptions import *
from dodona.translator import Translator


class DoubleCharsValidator:
    """"
    parses some text & checks that every opening char has an equivalent closing char later in the text
    checks for:
        * ( )
        * < >
        * { }
        * [ ]
        * ' '
        * " "
    """
    def __init__(self, translator: Translator):
        self.translator = translator
        self.opening = ["(", "<", "{", "[", "'", '"']
        self.closing = [")", ">", "}", "]", "'", '"']
        self.convert = dict((key, val) for key, val in [*zip(self.opening, self.closing), *zip(self.closing, self.opening)])

    def validate_content(self, text: str):
        text = list(text)
        stack = []
        pos_stack = []
        i, line, pos, end = [0, 1, 1, len(text)]
        # loop text
        while i < end:
            char = text[i]
            # closing
            if stack and self.convert[stack[-1]] == char:
                stack.pop()
                pos_stack.pop()
            # not closing
            elif char in self.convert:
                stack.append(char)
                pos_stack.append((line, pos))  # humans count from 1 not from 0
            i += 1
            # update position
            if char == "\n":
                line += 1
                pos = 1
            else:
                pos += 1

        # the stack should be empty, if not print remaining things
        if stack:
            errors = MultipleMissingCharsError(self.translator)
            while stack:
                char = stack.pop()
                pos = pos_stack.pop()
                if char in self.opening:
                    errors.add(MissingClosingCharError(self.translator, char, pos))
                else:
                    errors.add(MissingOpeningCharError(self.translator, char, pos))
            raise errors
