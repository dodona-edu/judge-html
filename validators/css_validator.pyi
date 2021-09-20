from typing import Optional

from bs4.element import Tag
from lxml.etree import ElementBase
from tinycss2.ast import Declaration

from utils.color_converter import Color


def strip(ls: []) -> []: ...


class CssParsingError(Exception):
    pass


def _get_xpath(selector: str) -> str: ...


class Rule:
    selector: []
    selector_str: str
    xpath: str
    name: str
    value: []
    important: bool
    specificity: (int, int, int)
    value_str: str

    def __init__(self, selector: [], content: Declaration): ...

    def __repr__(self) -> str: ...

    def get_color(self) -> Optional[Color]: ...


def calc_specificity(selector_str: str) -> (int, int, int):  ...

class Rules:
    root: ElementBase
    rules: []
    map: {}

    def __init__(self, css_content: str): ...

    def __repr__(self) -> str: ...

    def __len__(self) -> int: ...

    def find(self, root: ElementBase, solution_element: ElementBase, key: str) -> Optional[Rule]: ...


class AmbiguousXpath(Exception):
    pass


class CssValidator:
    root: Optional[ElementBase]
    rules: Rules
    xpaths: {}

    def __init__(self, html: str): ...

    def get_xpath_soup(self, element: Tag) -> str: ...

    def _get_xpath_soup(self, element: Tag) -> str: ...

    def find(self, element: Tag, key: str) -> Optional[Rule]: ...
