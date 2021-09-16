from re import RegexFlag

from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import Callable, List, Optional, Union

from dodona.dodona_config import DodonaConfig
from dodona.translator import Translator
from validators.html_validator import HtmlValidator


class Check:
    callback: Callable[[BeautifulSoup], bool]
    on_success: List["Check"] = ...
    abort_on_fail: bool = ...

    def __init__(self, callback: Callable[[BeautifulSoup], bool]): ...

    def _find_deepest_nested(self) -> "Check": ...

    def or_abort(self) -> "Check": ...

    def is_crucial(self) -> "Check": ...

    def then(self, *args: "Check") -> "Check": ...


class Element:
    tag: str
    id: Optional[str] = ...
    _element: Optional[Tag] = ...

    def __init__(self, tag: str, id: Optional[str] = ..., _element: Optional[Tag] = ...): ...

    def __str__(self) -> str: ...

    def get_child(self, tag: str, index: int = ..., direct: bool = ..., **kwargs) -> "Element": ...

    def get_children(self, tag: Optional[str] = ..., direct: bool = ..., **kwargs) -> "ElementContainer": ...

    def exists(self) -> Check: ...

    def has_child(self, tag: str, direct: bool = ..., **kwargs) -> Check: ...

    def has_content(self, text: Optional[str] = ...) -> Check: ...

    def _has_tag(self, tag: str) -> bool: ...

    def has_tag(self, tag: str) -> Check: ...

    def _get_attribute(self, attr: str) -> Optional[str]: ...

    def attribute_exists(self, attr: str, value: Optional[str] = ..., case_insensitive: bool = ...) -> Check: ...

    def attribute_contains(self, attr: str, substr: str, case_insensitive: bool = ...) -> Check: ...

    def attribute_matches(self, attr: str, regex: str, flags: Union[int, RegexFlag] = ...) -> Check: ...

    def has_table_header(self, header: List[str]) -> Check: ...

    def has_table_content(self, rows: List[List[str]], has_header: bool = True) -> Check: ...

    def table_row_has_content(self, row: List[str]) -> Check: ...


class EmptyElement(Element):
    def __init__(self): ...


class ElementContainer:
    elements: List[Element]
    _size: int = ...

    def __init__(self, elements: List[Element]): ...

    def __getitem__(self, item) -> Element: ...

    def __len__(self) -> int: ...

    @classmethod
    def from_tags(cls, tags: List[Tag]) -> "ElementContainer": ...

    def get(self, index: int) -> Element: ...

    def at_most(self, amount: int) -> Check: ...

    def at_least(self, amount: int) -> Check: ...

    def exactly(self, amount: int) -> Check: ...

def _flatten_queue(queue: List) -> List[Check]: ...


class ChecklistItem:
    message: str
    checks: Union[List, Check] = ...
    _checks: List[Check] = ...

    def __init__(self, message: str, checks: Union[List, Check]): ...

    def __post_init__(self): ...

    def evaluate(self, bs: BeautifulSoup) -> bool: ...


class TestSuite:
    name: str
    content: str
    check_recommended: bool = ...
    checklist: List[ChecklistItem] = ...
    _bs: BeautifulSoup = ...
    _validator: HtmlValidator = ...

    def __init__(self, name: str, content: str, check_recommended: bool = ...): ...

    def __post_init__(self): ...

    def create_validator(self, config: DodonaConfig): ...

    def add_check(self, check: ChecklistItem): ...

    def validate_html(self, allow_warnings: bool = ...) -> Check: ...

    def document_matches(self, regex: str, flags: Union[int, RegexFlag] = ...) -> Check: ...

    def element(self, tag: str, from_root: bool = ..., **kwargs) -> Element: ...

    def all_elements(self, tag: str, from_root: bool = ..., **kwargs) -> ElementContainer: ...

    def evaluate(self, translator: Translator) -> int: ...


def all_of(args: List[Check]) -> Check: ...


def any_of(args: List[Check]) -> Check: ...


def at_least(amount: int, args: List[Check]) -> Check: ...


def fail_if(check: Check) -> Check: ...