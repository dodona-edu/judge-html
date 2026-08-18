from typing import Any, cast

import tinycss2
import tinycss2.nth
from bs4.element import Tag
from cssselect import GenericTranslator, SelectorError
from lxml.etree import _Element
from lxml.html import fromstring
from tinycss2.ast import (
    Declaration,
    LiteralToken,
    Node,
    ParseError,
    QualifiedRule,
    WhitespaceToken,
)

from utils.color_converter import Color

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
    To compare the specificity of two combined selectors, compare the number of occurrences of single selectors of
    each of the specificity groups above.

Example: compare #nav ul li a:hover to #nav ul li.active a::after

count the number of id selectors: there is one for each (#nav)
count the number of class selectors: there is one for each (:hover and .active)
count the number of element selectors: there are 3 (ul li a) for the first and 4 for the second (ul li a ::after),
thus the second combined selector is more specific.

USAGE:
>>> validator = CssValidator(html_content)
>>> import bs4
>>> element = BeautifulSoup(html_content, "html.parser").find("div", attrs={"id":"div_you_want_to_query_on"})
>>> validator.find(element, "color")  # will return None if no rules for "color" are defined for that element
"green"
"""


def strip(ls: list) -> list:
    """strips leading & trailing whitespace tokens"""
    while ls and ls[0].type == WhitespaceToken.type:
        ls.pop(0)
    while ls and ls[-1].type == WhitespaceToken.type:
        ls.pop()
    return ls


class CssParsingError(Exception):
    """Thrown when the css is not in a correct format"""


def _get_xpath(selector: str) -> str:
    """converts a css selector string to an xpath string"""
    try:
        # TODO filter out pseudo-elements (like or ::after)
        return GenericTranslator().css_to_xpath(selector)
    except SelectorError as err:
        raise CssParsingError from err


class Rule:
    """represents a single css rule"""

    def __init__(self, selector: list[Node], content: Declaration):
        self.selector = strip(selector)
        self.selector_str = tinycss2.serialize(self.selector)
        self.xpath = _get_xpath(self.selector_str)
        if ":" in self.selector_str:
            self.pseudo = self.selector_str.split(":")[1]
            if self.xpath.endswith("[0]"):
                self.xpath = self.xpath[: len(self.xpath) - 3]
        else:
            self.pseudo = None
        self.name = content.name
        self.value: list[Node] = strip(content.value)
        self.important = content.important
        self.specificity = calc_specificity(self.selector_str)
        self.value_str = tinycss2.serialize(self.value)
        self.color = None
        if self.is_color():
            try:
                self.color = Color(self.value_str)
            except (IndexError, ValueError) as err:
                raise CssParsingError from err

    def __repr__(self):
        return f"(Rule: {self.selector_str} | {self.name} {self.value} {'important' if self.important else ''})"

    def is_color(self) -> bool:
        return "color" in self.name.lower()

    def has_color(self, color: str) -> bool:
        """Check that this element has a given color
        :param color:       the color to check this property's value against, in any format
        """
        if not self.is_color():
            return False

        try:
            other = Color(color)
        except ValueError:
            return False  # if the other color is not-parsable than it is the programmers fault
        return self.color == other

    def compare_to(self, value: str | None = None, important: bool | None = None, any_order: bool = False):
        """Compares this Rule to a given value string and or important specifier,
        any_order can be used when value string may contain multiple values"""
        # !important modifier is incorrect
        if important is not None and self.important != important:
            return False

        # Value doesn't matter
        if value is None:
            return True

        # Any order should be allowed, so just split the values on spaces
        # and sort them alphabetically
        if any_order:
            prop_value_sorted = sorted(self.value_str.split(" "))
            value_sorted = sorted(value.split(" "))
            return prop_value_sorted == value_sorted

        return self.value_str == value


def calc_specificity(selector_str: str) -> tuple[int, int, int]:  # see https://specificity.keegan.st/
    """calculates how specific a css-selector is"""
    # count selectors: ID
    a = selector_str.count("#")
    # count selectors: CLASSES & PSEUDO-CLASSES & ATTRIBUTES
    b = 0
    prev = ""
    for x in selector_str:
        if x in {".", "["} or (x == ":" and prev != ":"):
            b += 1
        prev = x
    # count selectors: ELEMENTS PSEUDO-ELEMENTS
    c = 0
    prev = ""
    for x in selector_str:
        if (x.isalpha() and prev not in ".[:=\"'") or (x == ":" and prev == ":"):
            c += 1
        prev = x
    # ignore pseudo-elements
    return a, b, c


class Rules:
    """represents a set of css rules"""

    root: _Element

    def __init__(self, css_content: str):
        """parses css to individual Rules"""
        self.rules: list[Rule] = []
        self.map: dict[str, Any] = {}

        def split_on_comma(prelude: list[Node], start: int = 0) -> list[list[Node]]:
            """splits a list on LiteralToken with a value of a comma"""
            ps = []
            index = start
            while index < len(prelude):
                # tinycss2's Node base class declares neither type nor value, but it is
                # never instantiated: every node in a prelude is a subclass that has both
                node = cast("LiteralToken", prelude[index])

                if node.type == LiteralToken.type and node.value == ",":
                    ps.append(strip(prelude[start:index]))
                    start = index + 1  # +1 because we skip the comma
                index += 1
            if start < len(prelude):
                ps.append(strip(prelude[start : len(prelude)]))
            return [y for y in ps if y]  # remove empty sublist(s) and return

        """convert a 'rule' made by tinycss2 to the Rule class I made"""
        for x in tinycss2.parse_stylesheet(css_content, skip_whitespace=True):
            if x.type == QualifiedRule.type:
                content = [x for x in tinycss2.parse_declaration_list(x.content) if x.type == Declaration.type]
                # flatten rules -> grouped selectors are seperated and then grouped rules are seperated
                for selector in split_on_comma(x.prelude):
                    for declaration in content:
                        self.rules.append(Rule(selector, declaration))
            elif x.type == ParseError.type:
                raise CssParsingError

    def __repr__(self):
        return f"RULES({len(self.rules)}): {self.rules}"

    def __len__(self):
        return len(self.rules)

    # of doing serialize() at the end, to access the !important property
    def find(self, root: _Element, solution_element: _Element, key: str, pseudo: str | None = None) -> Rule | None:
        """find the css rule for key (ex: color) for the solution_element,
        root is the root of the html-document (etree)"""
        rs: list[Rule] = []
        imp: list[Rule] = []
        r: Rule
        # find all rules defined for the solution element for the specified key
        for r in reversed(self.rules):
            if r.name == key and r.pseudo == pseudo:
                for element in cast("list[_Element]", root.xpath(r.xpath)):
                    if element == solution_element:
                        if r.important:
                            imp.append(r)
                        else:
                            rs.append(r)

        # check if there are rules containing !important
        if imp:
            rs = imp

        # no rules found
        if not rs:
            return None
        # get the most specific rule or the one that was defined the latest if multiple with the same specificity
        dom_rule = rs[0]  # the dominating rule
        for r in rs:
            # if   less  than: r is overruled by dom_rule because dom_rule has a higher specificity
            # if  equal  than: r is overruled by dom_rule because dom_rule was defined after r
            # if greater than: r overrules dom_rules because of higher specificity
            if r.specificity > dom_rule.specificity:
                dom_rule = r

        return dom_rule

    def find_all(self, root: _Element, solution_element: _Element) -> dict[str, Rule]:
        """find all the css rule for the solution_element,
        root is the root of the html-document (etree)"""
        dom_css = {}
        by_keyword: dict[str, tuple[list[Rule], list[Rule]]] = {}
        r: Rule
        # find all rules defined for the solution element for the specified key
        for r in reversed(self.rules):
            for element in cast("list[_Element]", root.xpath(r.xpath)):
                if element == solution_element:
                    if r.name not in by_keyword:
                        by_keyword[r.name] = ([], [])
                    if r.important:
                        by_keyword[r.name][0].append(r)
                    else:
                        by_keyword[r.name][1].append(r)

        for imp, rs in by_keyword.values():
            # check if there are rules containing !important
            if imp:
                rs = imp
            # get the most specific rule or the one that was defined the latest if multiple with the same specificity
            dom_rule = rs[0]  # the dominating rule
            for r in rs:
                # if   less  than: r is overruled by dom_rule because dom_rule has a higher specificity
                # if  equal  than: r is overruled by dom_rule because dom_rule was defined after r
                # if greater than: r overrules dom_rules because of higher specificity
                if r.specificity > dom_rule.specificity:
                    dom_rule = r
            dom_css[dom_rule.name] = dom_rule
        return dom_css

    def find_by_css_selector(self, css_selector: str, key: str) -> Rule | None:
        dom_rule: Rule | None = None
        rule: Rule
        for rule in self.rules:
            if rule.selector_str == css_selector and rule.name == key:
                if dom_rule is None or rule.specificity > dom_rule.specificity:
                    dom_rule = rule
        return dom_rule


class AmbiguousXpath(Exception):
    """Thrown when an xpath can select multiple elements when it should only select one element"""


class ElementNotFound(Exception):
    """Thrown when an xpath expects to find something, but it wasn't able to"""


class CssValidator:
    """interface for using the classes / functions defined above
        USAGE (html_content is a string containing the html itself):
        >> validator = CssValidator(html_content)
        >> import bs4
        >> element = BeautifulSoup(html_content, "html.parser").find("div", attrs={"id":"div_you_want_to_query_on"})
        >> validator.find(element, "color")  # will return None if no rules for "color" are defined for that element
    "green"
    """

    def __init__(self, html: str):
        # Invalid HTML makes fromstring() crash, so it can be None
        self.root: _Element | None = None
        try:
            self.root = fromstring(html)

            # A document without a <style> makes find() return None, and the AttributeError
            # that follows is what the except below is there to swallow
            style = cast("_Element", self.root.find(".//style"))

            # An empty <style></style> has no text, which is the same as having no CSS
            css = style.text or ""
        except Exception:
            css = ""

        self.rules = Rules(css)

        if self.root is not None:
            self.rules.root = self.root

        self.xpaths = {}

    def __bool__(self):
        return bool(self.rules.rules)

    def get_xpath_soup(self, element: Tag) -> str:
        """converts an element from bs4 soup to an xpath expression
        this is the memorization of the private function (makes it a lot faster)"""
        # memorization of the xpath_soup method
        if id(element) not in self.xpaths:
            self.xpaths.update({id(element): self._get_xpath_soup(element)})
        return self.xpaths[id(element)]

    @staticmethod
    def _get_xpath_soup(element: Tag) -> str:
        """converts an element from bs4 soup to an xpath expression"""
        components = []

        child = element

        for parent in child.parents:
            siblings = parent.find_all(child.name, recursive=False)
            components.append(
                child.name
                if len(siblings) == 1
                else f"{child.name}[{next(i for i, s in enumerate(siblings, 1) if s is child)}]"
            )
            child = parent
        components.reverse()
        return "/{}".format("/".join(components))

    def find(self, element: Tag, key: str, pseudo: str | None = None) -> Rule | None:
        """find the css rule for key (ex: color) for the solution_element
        the element should be a BeautifulSoup Tag"""
        # Tree couldn't be parsed so can't perform searching
        if self.root is None:
            return None

        xpath_solution = self.get_xpath_soup(element)

        # LXML adds a root HTML tag if there is none present, which results in
        # root.xpath(path) failing because our parsed solution technically doesn't exist
        # If nothing was found, try again with "/html" as a prefix
        sols = cast("list[_Element]", self.root.xpath(xpath_solution) or self.root.xpath("/html" + xpath_solution))

        # Found nothing
        if not sols:
            raise ElementNotFound

        # Found more than one match
        if not len(sols) == 1:
            raise AmbiguousXpath

        return self.rules.find(self.root, sols[0], key, pseudo)

    def find_by_css_selector(self, css_selector: str, key: str) -> Rule | None:
        if self.root is None:
            return None
        return self.rules.find_by_css_selector(
            css_selector.replace("\n", "").replace(" ", "").lower(), key.replace(" ", "").lower()
        )
