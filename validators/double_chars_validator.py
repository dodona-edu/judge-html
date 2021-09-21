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
        self.convert = dict(
            (key, val) for key, val in [*zip(self.opening, self.closing), *zip(self.closing, self.opening)])

    def validate_content(self, text: str):
        """checks the text"""
        text_ls = list(text)
        stack = []
        pos_stack = []
        i, line, pos, end, inside_comment, length, c_line, c_pos = [0, 0, 0, len(text_ls), None, len(text), 0, 0]
        # loop text
        while i < end:
            char = text_ls[i]
            # comment?
            if not inside_comment:
                if char == "<" and i + 4 < length and text[i:i + 4] == "<!--":  # html comment
                    inside_comment = "-->"
                    c_line = line
                    c_pos = pos
                if char == "/" and i + 2 < length and text[i:i + 2] == "/*":  # css comment
                    inside_comment = "*/"
                    c_line = line
                    c_pos = pos
            if inside_comment:  # check with previous char
                if text_ls[i - 1] == inside_comment[-1]:
                    if i - 1 - len(inside_comment) >= 0 and text[i - len(inside_comment):i] == inside_comment:
                        inside_comment = None
            if not inside_comment:
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
                pos = 0
            else:
                pos += 1

        # the stack should be empty, if not print remaining things
        errors = MultipleMissingCharsError(self.translator)

        if inside_comment:
            errors.add(MissingClosingCharError(translator=self.translator, position=(c_line, c_pos), char=("<!--" if inside_comment == "-->" else "/*")))
        if stack:
            while stack:
                char = stack.pop()
                pos = pos_stack.pop()
                if char in self.opening:
                    errors.add(MissingClosingCharError(translator=self.translator, position=pos, char=char))
                else:
                    errors.add(MissingOpeningCharError(translator=self.translator, position=pos, char=char))
            raise errors
