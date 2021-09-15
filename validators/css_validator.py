from enum import Enum

import tinycss2
from tinycss2.ast import *
from lxml.etree import fromstring, ElementBase
from cssselect import GenericTranslator, SelectorError

"""
tinycss2 docs
    https://pythonhosted.org/tinycss2/
    https://pythonhosted.org/tinycss2/#term-component-values
lxml docs
    https://lxml.de/api/
"""


class CssParsingError(Exception):
    pass


class Match:
    def __init__(self, rule: QualifiedRule, element: ElementBase):
        self.rule = rule
        self.element = element

    def __repr__(self):
        return f"\nMATCH:\n" \
               f"\tCSS SELECTOR: {tinycss2.serialize(self.rule.prelude)}\n" \
               f"\tCSS RULES: {[(tinycss2.serialize([x]), str(x.important)) for x in self.rule.content]}\n" \
               f"\tELEMENT: {self.element.tag} {self.element.keys()} {self.element.values()}\n"


class Matches:
    def __init__(self, ms: ([Match], [Match])):
        self.important = ms[0]
        self.normal = ms[1]

    def __repr__(self):
        return f"IMPORTANT: {self.important}\n" \
               f"NORMAL:    {self.normal}"


class Rule:
    def __init__(self, rule_data: (str, QualifiedRule)):
        self.xpath = rule_data[0]
        self.css: QualifiedRule = rule_data[1]

    def __repr__(self):
        return f"<Rule: {self.css.serialize()}>"


class Rules:
    def __init__(self, ls: ([(str, QualifiedRule)], [(str, QualifiedRule)])):
        self.important = [Rule(x) for x in ls[0]]
        self.normal = [Rule(x) for x in ls[1]]

    def __repr__(self):
        return f"IMPORTANT: {self.important}\n" \
               f"NORMAL:    {self.normal}"


class Style:
    """
    stylesheet is a list of
    * QualifiedRule
        * .prelude is a list of component values
    * AtRule
    * Comment
    * ParseError
    """

    def __init__(self, css: str, html: str):
        # html
        self.document = fromstring(html)
        # css
        self.rules = Rules(self._parse_css(css))
        print(self.rules)
        # matches
        self.matches = self.find_matches()

    def _parse_css(self, css: str):
        """parses css to a list of rules
            each element in the list is a tuple containing:
                * xpath notation of the css selector
                * the rule itself
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
            return [x for x in ps if x]  # remove empty sublist(s) and return

        def flatten_rules(rules: []):
            """css selectors can be grouped
                ex:
                    h1, h2, p {
                        text-align: center;
                        color: red;
                    }
                this method separates the group-rule to individual-rules
                (with each the same content in between curly brackets off course)
            """
            new_rules = []  # the new rules list
            for qr in rules:
                if qr.type == QualifiedRule.type:
                    qr: QualifiedRule
                    flat_selectors = split_on_comma(qr.prelude)
                    content = strip(qr.content)
                    for s in flat_selectors:
                        new_rules.append(QualifiedRule(qr.source_line, qr.source_column, s, content))
                elif qr.type == AtRule.type:
                    print("atrule encountered")  # don't know what this type of rule is
                elif qr.type == Comment.type:
                    pass
                elif qr.type == ParseError.type:
                    raise CssParsingError()
            return new_rules

        def split_important_rules(rules: []) -> ([], []):
            """splits the rules containing an !important indicator from the normal ones"""
            qr: QualifiedRule
            important_rules, normal_rules = [], []
            for qr in rules:
                qr.content = tinycss2.parse_declaration_list(qr.content, skip_whitespace=True)
                d: Declaration
                important, normal = [], []
                for d in qr.content:
                    important.append(d) if d.type == Declaration.type and d.important else normal.append(d)
                if normal:
                    normal_rules.append(QualifiedRule(qr.source_line, qr.source_column, qr.prelude, normal))
                if important:
                    important_rules.append(QualifiedRule(qr.source_line, qr.source_column, qr.prelude, important))
            return important_rules, normal_rules

        def add_xpaths(rules: ([], [])) -> ([()], [()]):
            def do(rs):
                r: QualifiedRule
                ns: [str] = []  # new selectors (xpaths)
                for r in rs:
                    try:
                        ns.append(GenericTranslator().css_to_xpath(tinycss2.serialize(r.prelude)))
                    except SelectorError:
                        raise CssParsingError()
                return ns
            return list(zip(do(rules[0]), rules[0])), list(zip(do(rules[1]), rules[1]))

        return add_xpaths(split_important_rules(flatten_rules(tinycss2.parse_stylesheet(css, skip_whitespace=True))))

    def find_matches(self) -> [Match]:
        """
        path:
            [h1]: the h1 selector
        searches first in the important rules, if not found, search backwards in the other rules
        """
        matches_imp = []
        matches_nor = []
        for x in self.rules.important:
            matches_imp += [Match(x.css, e) for e in self.document.xpath(x.xpath)]
        for x in self.rules.normal:
            matches_nor += [Match(x.css, e) for e in self.document.xpath(x.xpath)]
        matches = Matches((matches_imp, matches_nor))
        return matches


css = """
.body {
color: red !important
}
div #inner, #outer{
color: red;
margin: 2px;
}
"""
html = """
           <div>
             <div id="inner" class="content body CHECK">text</div>
           </div>
         """

print("------------------------Parsing------------------------")
style = Style(css, html)
print("------------------------Matches------------------------")
# print matches
print(style.matches.important)  # important
print(style.matches.normal)  # normal

