class DoubleCharsValidator:
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
                pos_stack.append(i + 1)  # humans count from 1 not from 0
            i += 1
        print(len(stack))
        print(stack)
        print(pos_stack)
