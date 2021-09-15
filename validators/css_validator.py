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
        self.rules = tinycss2.parse_stylesheet(stylesheet, skip_whitespace=True)
        self.flatten_rules()
        # self.make_paths()

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
        def strip(ls: []):
            """strips leading & trailing whitespace tokens"""
            while ls and ls[0].type == WhitespaceToken.type:
                ls.pop(0)
            while ls and ls[-1].type == WhitespaceToken.type:
                ls.pop()
            return ls

        def split_on_comma(prelude: [], start=0) -> [[]]:
            """splits a list on LiteralToken with a value of a comma"""
            ps = []
            index = start
            while index < len(prelude):
                if prelude[index].type == LiteralToken.type and prelude[index].value == ",":
                    ps.append(strip(prelude[start:index]))
                    start = index + 1  # +1 because we skip the comma
                index += 1
            if start < len(prelude):
                ps.append(strip(prelude[start: len(prelude)]))
            return ps

        new_rules = []  # the new rules list
        for qr in self.rules:
            if qr.type == QualifiedRule.type:
                qr: QualifiedRule
                flat_selectors = split_on_comma(qr.prelude)
                for s in flat_selectors:
                    new_rules.append(QualifiedRule(qr.source_line, qr.source_column, s, qr.content))
            elif qr.type == AtRule.type:
                print("atrule encountered")  # don't know what this type of rule is
            elif qr.type == Comment.type:
                pass
            elif qr.type == ParseError.type:
                raise CssParsingError()
        print(self.rules)
        print(new_rules)




    def make_paths(self):
        selector: []
        for selector in [x.prelude for x in self.rules]:

            paths = []

            first, last = [0, len(selector) - 1]
            # remove leading & trailing whitespace
            while selector[first].type == WhitespaceToken.type:
                first += 1
            while selector[last].type == WhitespaceToken.type:
                last -= 1

            handlers = {
                ParseError.type: self._handle_error,
                WhitespaceToken.type: self._handle_whitespace,
                LiteralToken.type: self._handle_literal,
                IdentToken.type: self._handle_ident,
                AtKeywordToken.type: self._handle_at_keyword,
                HashToken.type: self._handle_hash,
                StringToken.type: self._handle_string,
                URLToken.type: self._handle_url,
                NumberToken.type: self._handle_number,
                PercentageToken.type: self._handle_percentage,
                DimensionToken.type: self._handle_dimension,
                UnicodeRangeToken.type: self._handle_unicode_range,
                ParenthesesBlock.type: self._handle_parentheses,
                SquareBracketsBlock.type: self._handle_square_brackets,
                CurlyBracketsBlock.type: self._handle_curly_brackets,
                FunctionBlock.type: self._handle_function,
                Comment.type: self._handle_comment
            }
            for i in range(first, last + 1):
                node = selector[i]
                if node.type in handlers:
                    handlers[node.type](node)

    def _handle_error(self, node):
        raise CssParsingError()

    def _handle_whitespace(self, node: WhitespaceToken):
        print("whitespace")

    def _handle_literal(self, node: LiteralToken):
        print("literal " + node.value)

    def _handle_ident(self, node: IdentToken):
        print("ident " + node.value)

    def _handle_at_keyword(self, node: AtKeywordToken):
        pass

    def _handle_hash(self, node: HashToken):
        print("hash " + node.value)

    def _handle_string(self, node: StringToken):
        pass

    def _handle_url(self, node: URLToken):
        pass

    def _handle_number(self, node: NumberToken):
        pass

    def _handle_percentage(self, node: PercentageToken):
        pass

    def _handle_dimension(self, node: DimensionToken):
        pass

    def _handle_unicode_range(self, node: UnicodeRangeToken):
        pass

    def _handle_parentheses(self, node: ParenthesesBlock):
        pass

    def _handle_square_brackets(self, node: SquareBracketsBlock):
        pass

    def _handle_curly_brackets(self, node: CurlyBracketsBlock):
        pass

    def _handle_function(self, node: FunctionBlock):
        pass

    def _handle_comment(self, node: Comment):
        pass


css = Css("""
a, b, #h2 {
}
""")
