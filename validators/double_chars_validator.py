from exceptions.double_char_exceptions import *

class DoubleCharsValidator:
    def __init__(self):
        self.opening = ["(", "<", "{", "[", "'", '"']
        self.closing = [")", ">", "}", "]", "'", '"']
        self.convert = dict((key, val) for key, val in [*zip(self.opening, self.closing), *zip(self.closing, self.opening)])

    def validate_content(self, text: str):
        stack = []
        pos_stack = []
        convert = {
            "(": ")",
            "<": ">",
            "{": "}",
            "[": "]",
            "'": "'",
            '"': '"'
        }
        convert.update({val: key for key, val in convert.items()})  # put the inverse map in the map
        text = list(text)
        i = 0
        end = len(text)
        line, pos = [1, 1]
        # loop text
        while i < end:
            char = text[i]
            # closing
            if stack and convert[stack[-1]] == char:
                stack.pop()
                pos_stack.pop()
            # not closing
            elif char in convert:
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
            errors = MultipleMissingCharsError()
            while stack:
                char = stack.pop()
                pos = pos_stack.pop()
                if char in self.opening:
                    errors.add(MissingClosingCharError(char, pos))
                else:
                    errors.add(MissingOpeningCharError(char, pos))
            raise errors


