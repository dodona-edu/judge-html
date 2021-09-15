from enum import Enum

import tinycss2
from tinycss2.ast import *


# https://pythonhosted.org/tinycss2/
# https://pythonhosted.org/tinycss2/#term-component-values


class CssParsingError(Exception):
    pass


class LiteralTypes(Enum):
    ID = "#"
    CLASS = "."
    GROUPING = ","


class Css:
    """
    stylesheet is a list of
    * QualifiedRule
        * .prelude is a list of component values
    * AtRule
    * Comment
    * ParseError
    """

    def __init__(self, stylesheet):
        print(f"Input:{stylesheet}")
        self.rules = tinycss2.parse_stylesheet(stylesheet, skip_whitespace=True)
        self.flatten_rules()
        self.split_important_rules()

    def __str__(self):
        return f"Important rules  : {tinycss2.serialize(self.rules[0])}\n" \
               f"Normal rules     : {tinycss2.serialize(self.rules[1])}"

    def flatten_rules(self):
        """css selectors can be grouped
            ex:
                h1, h2, p {
                    text-align: center;
                    color: red;
                }
            this method separates the group-rule to individual-rules
            (with each the same content in between curly brackets off course)
        """

        def split_on_comma(prelude: [], start=0) -> [[]]:
            """splits a list on LiteralToken with a value of a comma"""
            ps = []
            index = start
            while index < len(prelude):
                if prelude[index].type == LiteralToken.type and prelude[index].value == ",":
                    ps.append(self.strip(prelude[start:index]))
                    start = index + 1  # +1 because we skip the comma
                index += 1
            if start < len(prelude):
                ps.append(self.strip(prelude[start: len(prelude)]))
            return [x for x in ps if x]  # remove empty sublist(s) and return

        new_rules = []  # the new rules list
        for qr in self.rules:
            if qr.type == QualifiedRule.type:
                qr: QualifiedRule
                flat_selectors = split_on_comma(qr.prelude)
                content = self.strip(qr.content)
                for s in flat_selectors:
                    new_rules.append(QualifiedRule(qr.source_line, qr.source_column, s, content))
            elif qr.type == AtRule.type:
                print("atrule encountered")  # don't know what this type of rule is
            elif qr.type == Comment.type:
                pass
            elif qr.type == ParseError.type:
                raise CssParsingError()
        self.rules = new_rules

    def split_important_rules(self) -> ([], []):
        qr: QualifiedRule
        important_rules, normal_rules = [], []
        for qr in self.rules:
            qr.content = tinycss2.parse_declaration_list(qr.content, skip_whitespace=True)
            d: Declaration
            important, normal = [], []
            for d in qr.content:
                print(d)
                important.append(d) if d.type == Declaration.type and d.important else normal.append(d)
            if normal:
                normal_rules.append(QualifiedRule(qr.source_line, qr.source_column, qr.prelude, normal))
            if important:
                important_rules.append(QualifiedRule(qr.source_line, qr.source_column, qr.prelude, important))
        self.rules = (important_rules, normal_rules)

    def find(self, path: []):
        """
        path:
            [h1]: the h1 selector
        """

    def strip(self, ls: []):
        """strips leading & trailing whitespace tokens"""
        while ls and ls[0].type == WhitespaceToken.type:
            ls.pop(0)
        while ls and ls[-1].type == WhitespaceToken.type:
            ls.pop()
        return ls


css = Css("""
a, {
color: green !important;
margin: 2px;
}
b, #h2 {
color: red;
}
""")
print("------------------------Parsed------------------------")
print(css)
