from enum import Enum

import tinycss2
from bs4 import BeautifulSoup
from bs4 import Tag
from tinycss2.ast import *
from lxml.etree import ElementBase
from lxml.etree import fromstring, ElementBase
# from lxml.html.soupparser import fromstring
from cssselect import GenericTranslator, SelectorError

"""
tinycss2 docs
    https://pythonhosted.org/tinycss2/
    https://pythonhosted.org/tinycss2/#term-component-values
lxml docs
    https://lxml.de/api/
"""

"""
css precedence rules:
a more specific selector takes precedence over a less specific one
    rules that appear later in the code override earlier rules if both have the same specificity.
    A css rule with !important always takes precedence.

Specificity for single selectors from highest to lowest:
    ids (example: #main selects <div id="main">)
    classes (ex.: .myclass), attribute selectors (ex.: [href=^https:]) and pseudo-classes (ex.: :hover)
    elements (ex.: div) and pseudo-elements (ex.: ::before)
    To compare the specificity of two combined selectors, compare the number of occurences of single selectors of each of the specificity groups above.

Example: compare #nav ul li a:hover to #nav ul li.active a::after

count the number of id selectors: there is one for each (#nav)
count the number of class selectors: there is one for each (:hover and .active)
count the number of element selectors: there are 3 (ul li a) for the first and 4 for the second (ul li a ::after), thus the second combined selector is more specific.
"""


def xpath_soup(element):
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
            )
        )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)


def strip(ls: []):
    """strips leading & trailing whitespace tokens"""
    while ls and ls[0].type == WhitespaceToken.type:
        ls.pop(0)
    while ls and ls[-1].type == WhitespaceToken.type:
        ls.pop()
    return ls


class CssParsingError(Exception):
    pass


def _get_xpath(qr: QualifiedRule) -> str:
    try:
        # todo filter out pseudo-elements (like or ::after)
        return GenericTranslator().css_to_xpath(tinycss2.serialize(qr.prelude))
    except SelectorError as e:
        raise CssParsingError()


class Rule:
    def __init__(self, xpath: str, selector: [], content: Declaration):
        self.xpath = xpath
        self.selector = strip(selector)
        self.selector_str = tinycss2.serialize(self.selector)
        self.name = content.name
        self.value = strip(content.value)
        self.important = content.important

    def __repr__(self):
        return f"(Rule: {self.selector_str} | {self.name} {self.value} {'important' if self.important else ''})"


class Rules:
    def __init__(self, rules: [Rule]):
        self.rules = rules

    def __repr__(self):
        return f"RULES({len(self.rules)}): {self.rules}"

    def __len__(self):
        return len(self.rules)

    def calc_specifity(self, r: Rule):
        # count selectors: ID
        a = len([x for x in r.selector if x.type == HashToken.type])
        # count selectors: CLASSES & PSEUDO-CLASSES & ATTRIBUTES
        b = 0
        prev = ""
        for x in r.selector_str:
            if x == "." or x == "[":
                b += 1
            elif x == ":" and prev != ":":
                b += 1
            prev = x
        # count selectors: ELEMENTS PSEUDO-ELEMENTS
        c = 0
        prev = ""
        for x in r.selector_str:
            if x.isalpha() and prev not in ".[:=\"'":
                c += 1
            elif x == ":" and prev == ":":
                c += 1
            prev = x
        # ignore pseudo-elements
        return a, b, c

    def find(self, root: ElementBase, solution_element: ElementBase, key: str, value: str = "") -> [None, Rule]:
        rs: [Rule] = []
        r: Rule
        # find all rules defined for the solution element for the specified key
        for r in self.rules:
            if r.name == key:
                for element in root.xpath(r.xpath):
                    if element == solution_element:
                        rs.append(r)

        # no rules found
        if not rs:
            return None

        # check if there are rules containing !important
        imp = [r for r in rs if r.important]
        if imp:
            rs = imp

        # get the most specific rule or the one that was defined the latest
        dom_rule = rs.pop()  # the dominating rule
        dom_specificity = self.calc_specifity(dom_rule)
        while rs:
            r = rs.pop()
            r_specificity = self.calc_specifity(r)
            # if   less  than: r is overruled by dom_rule because dom_rule has a higher specificity
            # if  equal  than: r is overruled by dom_rule because dom_rule was defined after r
            # if greater than: r overrules dom_rules because of higher specificity
            if r_specificity > dom_specificity:
                dom_rule = r
                dom_specificity = r_specificity

        return dom_rule


def _parse_css(css_content: str) -> Rules:
    """parses css to a list of rules
        each element in the list is a tuple containing:
            * xpath notation of the css selector
            * the rule itself
    """

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
                xpath = _get_xpath(x)
                selector = x.prelude
                content = tinycss2.parse_declaration_list(x.content)
                # flatten rules -> grouped selectors are seperated and then grouped rules are seperated
                nrs += [Rule(xpath, s, c) for s in split_on_comma(selector) for c in content if
                        c.type == Declaration.type]
            elif x.type == ParseError.type:
                raise CssParsingError
        return nrs

    return Rules(to_rules(tinycss2.parse_stylesheet(css_content, skip_whitespace=True)))


css = """
p{color:red;}
"""
html = """<!DOCTYPE html>
<html>
<body>

<p id="nav">Every paragraph will be affected by the style.</p>
<p id="para1">Me too!</p>
<p>And me!</p>

</body>
</html>
"""


class AmbiguousXpath(Exception):
    pass


class Matcher:
    def __init__(self, html, css):
        self.root: ElementBase = fromstring(html)
        self.rules = _parse_css(css)

    def find(self, element: Tag, key: str, value: str = ""):
        xpath_solution = xpath_soup(element)
        sols = self.root.xpath(xpath_solution)
        if not len(sols) == 1:
            raise AmbiguousXpath()
        solution_element = sols[0]
        return self.rules.find(self.root, solution_element, key, value)


print("------------------------------------")
bs: BeautifulSoup = BeautifulSoup(html, "html.parser")
m = Matcher(html, css)
res = m.find(bs.find("p", attrs={"id": "para1"}), "color")  # yellow
print(res)

r = Rules([])
