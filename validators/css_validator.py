from enum import Enum

import tinycss2
from tinycss2.ast import *
from lxml.etree import fromstring, ElementBase

"""
tinycss2 docs
    https://pythonhosted.org/tinycss2/
    https://pythonhosted.org/tinycss2/#term-component-values
lxml docs
    https://lxml.de/api/
"""


class CssParsingError(Exception):
    pass


class LiteralTypes(Enum):
    ID = "#"
    CLASS = "."
    GROUPING = ","


class Match:
    def __init__(self, rule: QualifiedRule, element: ElementBase):
        self.rule = rule
        self.element = element

    def __str__(self):
        return f"\nMATCH:\n" \
               f"\tRULE: {tinycss2.serialize(self.rule.prelude)}\n" \
               f"\tELEMENT: {self.element.tag} {self.element.keys()} {self.element.values()}\n"

    def __repr__(self):
        return str(self)


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
        xpaths = self.selectors_to_xpaths()
        self.rules = (list(zip(xpaths[0], self.rules[0])), list(zip(xpaths[1], self.rules[1])))

    def __str__(self):
        return f"Important rules  : {tinycss2.serialize([x[1] for x in self.rules[0]])}\n" \
               f"  selectors      : {[x[0] for x in self.rules[0]]}\n" \
               f"Normal rules     : {tinycss2.serialize([x[1] for x in self.rules[1]])}\n" \
               f"  selectors      : {[x[0] for x in self.rules[1]]}"

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
                important.append(d) if d.type == Declaration.type and d.important else normal.append(d)
            if normal:
                normal_rules.append(QualifiedRule(qr.source_line, qr.source_column, qr.prelude, normal))
            if important:
                important_rules.append(QualifiedRule(qr.source_line, qr.source_column, qr.prelude, important))
        self.rules = (important_rules, normal_rules)

    def selectors_to_xpaths(self):
        from cssselect import GenericTranslator, SelectorError

        def do(rs):
            r: QualifiedRule
            ns: [str] = []  # new selectors (xpaths)
            for r in rs:
                try:
                    ns.append(GenericTranslator().css_to_xpath(tinycss2.serialize(r.prelude)))
                except SelectorError:
                    raise CssParsingError()
            return ns

        return do(self.rules[0]), do(self.rules[1])

    def strip(self, ls: []):
        """strips leading & trailing whitespace tokens"""
        while ls and ls[0].type == WhitespaceToken.type:
            ls.pop(0)
        while ls and ls[-1].type == WhitespaceToken.type:
            ls.pop()
        return ls

    def find_matches(self, path: str, html_content: str) -> [Match]:
        """
        path:
            [h1]: the h1 selector
        searches first in the important rules, if not found, search backwards in the other rules
        """
        matches_imp = []
        matches_nor = []
        document = fromstring(html_content)
        for x in self.rules[0]:
            matches_imp += [Match(x[1], e) for e in document.xpath(x[0])]
        for x in self.rules[1]:
            matches_nor += [Match(x[1], e) for e in document.xpath(x[0])]
        matches = (matches_imp, matches_nor)
        return matches




css = Css("""
div #inner, #outer{
color: red
}
""")
print("------------------------Matches------------------------")
ms = css.find_matches("", '''
           <div id="outer">
             <div id="inner" class="content body">text</div>
           </div>
         ''')
# print matches
print(ms[0])  # important
print(ms[1])  # normal
