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


def _get_xpath(qr: QualifiedRule) -> str:
    try:
        return GenericTranslator().css_to_xpath(tinycss2.serialize(qr.prelude))
    except SelectorError:
        raise CssParsingError()


class Rule:
    def __init__(self, qr: QualifiedRule):
        self.xpath: str = _get_xpath(qr)
        self.css: QualifiedRule = qr

    def __repr__(self):
        return f"<Rule: {self.css.serialize()}>"


class Rules:
    def __init__(self, rules: [Rule]):
        # split list of rules onto importance
        qr: QualifiedRule
        important_rules, normal_rules = [], []
        for r in rules:
            qr: QualifiedRule = r.css
            qr.content = tinycss2.parse_declaration_list(qr.content, skip_whitespace=True)
            d: Declaration
            important, normal = [], []
            for d in qr.content:
                important.append(d) if d.type == Declaration.type and d.important else normal.append(d)
            if normal:
                normal_rules.append(Rule(QualifiedRule(qr.source_line, qr.source_column, qr.prelude, normal)))
            if important:
                important_rules.append(Rule(QualifiedRule(qr.source_line, qr.source_column, qr.prelude, important)))
        self.important = important_rules
        self.normal = normal_rules

    def __repr__(self):
        return f"IMPORTANT: {self.important}\n" \
               f"NORMAL:    {self.normal}"


def _parse_css(css_content: str) -> Rules:
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

    def to_rules(rules: []) -> [Rule]:
        """converts from 'rule' to Rule, which also has an xpath value"""
        nrs = []
        for x in rules:
            if x.type == QualifiedRule.type:
                nrs.append(Rule(x))
            elif x.type == ParseError.type:
                raise CssParsingError
        return nrs

    def flatten_rules(rules: [Rule]) -> [Rule]:
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
        r: Rule
        for r in rules:
            qr: QualifiedRule = r.css
            flat_selectors = split_on_comma(qr.prelude)
            content = strip(qr.content)
            for s in flat_selectors:
                new_rules.append(Rule(QualifiedRule(qr.source_line, qr.source_column, s, content)))
        return new_rules

    return Rules(flatten_rules(to_rules(tinycss2.parse_stylesheet(css_content, skip_whitespace=True))))


class Match:
    def __init__(self, rule: Rule, element: ElementBase):
        self.rule = rule
        self.element = element

    def __repr__(self):
        return f"\nMATCH:\n" \
               f"\tCSS SELECTOR: {tinycss2.serialize(self.rule.css.prelude)}\n" \
               f"\tCSS RULES: {[(tinycss2.serialize([x]), str(x.important)) for x in self.rule.css.content]}\n" \
               f"\tELEMENT: {self.element.tag} {self.element.keys()} {self.element.values()}"

    def get_path(self) -> [str]:
        path = [self.element]
        while path[-1].getparent() is not None:
            path.append(path[-1].getparent())
        return [x.tag for x in reversed(path)]


class Matches:
    important: [Match] = []
    normal: [Match] = []

    def __init__(self, css, html):
        rules, document = _parse_css(css), fromstring(html)
        for x in rules.important:
            self.important += [Match(x, e) for e in document.xpath(x.xpath)]
        for x in rules.normal:
            self.normal += [Match(x, e) for e in document.xpath(x.xpath)]

    def __repr__(self):
        return f"*************** IMPORTANT *************** {self.important}\n" \
               f"***************  NORMAL   *************** {self.normal}"


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
        <body>
           <div id="outer">
             <div id="inner" class="content body CHECK">text</div>
           </div>
        </body>
         """
ms: Matches = Matches(css, html)
print(ms)
