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
        self.stylesheet: [] = tinycss2.parse_stylesheet(stylesheet, skip_whitespace=True)
        self.make_paths()

    def make_paths(self):
        selector: []
        for selector in [x.prelude for x in self.stylesheet]:

            paths = []

            first, last = [0, len(selector)-1]
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
            for i in range(first, last+1):
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
#header .callout {
}
""")

print(str(LiteralTypes.ID))

