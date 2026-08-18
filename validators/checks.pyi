from collections.abc import Callable, Iterable, Iterator
from re import RegexFlag
from typing import TypeAlias, TypeVar

from bs4 import BeautifulSoup
from bs4.element import Tag

from dodona.dodona_config import DodonaConfig
from dodona.translator import Translator
from validators.css_validator import CssValidator, Rule
from validators.html_validator import HtmlValidator

# Custom type hints
Emmet = TypeVar("Emmet", bound=str)
Checks: TypeAlias = Check | Iterable[Check]

class Check:
    callback: Callable[[BeautifulSoup], bool]
    on_success: list[Check] = ...
    abort_on_fail: bool = False

    def __init__(self, callback: Callable[[BeautifulSoup], bool]): ...
    def _find_deepest_nested(self) -> Check: ...
    def or_abort(self) -> Check:
        """This function will cause the check's TestSuite to stop evaluating, and cause all future checks to fail. This should be used in case a first check is a necessary requirement for the following checks to succeed."""
        ...

    def is_crucial(self) -> Check:
        """This is an alias to or_abort, and can be used in the exact same way."""
        ...

    def then(self, *args: Checks) -> Check:
        """This function registers one or more checks that should only run if the current check succeeds."""
        ...

class Element:
    tag: str
    id: str | None = ...
    _element: Tag | None = ...
    _css_validator: CssValidator | None = None

    def __init__(
        self,
        tag: str,
        id: str | None = ...,
        _element: Tag | None = ...,
        css_validator: CssValidator | None = ...,
    ): ...
    def __str__(self) -> str: ...
    def get_child(self, tag: str | Emmet | None = ..., index: int = 0, direct: bool = True, **kwargs) -> Element:
        """This method finds a child element with tag tag, optionally with extra filters. Supports Emmet syntax through the tag parameter."""
        ...

    def get_children(self, tag: str | Emmet | None = ..., direct: bool = True, **kwargs) -> ElementContainer:
        """This method finds ALL child elements, optionally with tag tag and extra filters. Supports Emmet syntax through the tag parameter."""
        ...

    def exists(self) -> Check:
        """Check that an element exists, and is not empty."""
        ...

    def has_child(self, tag: str | Emmet | None = ..., direct: bool = True, **kwargs) -> Check:
        """Check that the element has a child that meets the specifications"""
        ...

    def has_parent(self, tag: str, direct: bool = True, **kwargs) -> Check:
        """Check that this element has a parent with the given tag"""
        ...

    def has_content(self, text: str | None = ..., case_insensitive: bool = False) -> Check:
        """Check that the element has specific content, or any content at all."""
        ...

    def _has_tag(self, tag: str) -> bool: ...
    def has_tag(self, tag: str) -> Check:
        """Check that this element has the required tag."""
        ...

    def no_loose_text(self) -> Check:
        """Check that there is no content floating around in this tag"""
        ...

    def _get_attribute(self, attr: str) -> list[str] | str | None: ...
    def _compare_attribute_list(
        self,
        attribute: list[str],
        value: str | None = None,
        case_insensitive: bool = False,
        mode: int = 0,
        flags: int | RegexFlag = 0,
    ) -> bool: ...
    def attribute_exists(self, attr: str, value: str | None = ..., case_insensitive: bool = False) -> Check:
        """Check that this element has a given attribute, optionally matching a specific value."""
        ...

    def attribute_contains(self, attr: str, substr: str, case_insensitive: bool = False) -> Check:
        """Check that this element has a given attribute, and that the attribute contains a substring. If the element doesn't exist, this check will fail as well."""
        ...

    def attribute_matches(self, attr: str, regex: str, flags: int | RegexFlag = ...) -> Check:
        """Check if an attribute exists, and if its value matches a regular expression. If the element doesn't exist, this check will fail as well."""
        ...

    def has_table_header(self, header: list[str]) -> Check:
        """This method checks if an Element with tag table has a header with content that matches a list of strings."""
        ...

    def has_table_content(
        self, rows: list[list[str]], has_header: bool = True, case_insensitive: bool = False
    ) -> Check:
        """This method checks if an Element with tag table has rows with the required content, excluding the header."""
        ...

    def table_row_has_content(self, row: list[str], case_insensitive: bool = False) -> Check:
        """This method checks if an Element with tag tr has the required content."""
        ...

    def has_url_with_fragment(self, fragment: str | None = ...) -> Check:
        """Check that this element has a url with a fragment (#), optionally comparing the fragment to a string that it should match exactly."""
        ...

    def has_outgoing_url(self, allowed_domains: list[str] | None = None, attr: str = "href") -> Check:
        """Check if an attribute has an outgoing link"""
        ...

    def contains_comment(self, comment: str | None = None) -> Check:
        """Check if the element contains a comment, optionally matching a value"""
        ...

    def _find_css_property(self, prop: str, inherit: bool, pseudo: str | None = None) -> Rule | None:
        """Find a css property recursively if necessary
        Properties by parent elements are applied onto their children, so
        an element can inherit a property from its parent
        """
        ...

    def has_styling(
        self,
        prop: str,
        value: str | None = ...,
        important: bool | None = ...,
        pseudo: str | None = None,
        allow_inheritance: bool = False,
        any_order: bool = True,
    ) -> Check:
        """Check that this element is matched by a CSS selector to give it a particular styling. A value can be passed to match the value of the styling exactly."""
        ...

    def has_color(
        self,
        prop: str,
        color: str,
        important: bool | None = None,
        pseudo: str | None = None,
        allow_inheritance: bool = False,
    ) -> Check:
        """Check that this element has a given color on a CSS property."""
        ...

class EmptyElement(Element):
    def __init__(self): ...
    def __str__(self) -> str: ...

class ElementContainer:
    elements: list[Element]
    _size: int = ...

    def __init__(self, elements: list[Element]): ...
    def __getitem__(self, item) -> Element | list[Element]: ...
    def __iter__(self) -> Iterator[Element]: ...
    def __len__(self) -> int: ...
    @classmethod
    def from_tags(cls, tags: list[Tag], css_validator: CssValidator) -> ElementContainer: ...
    def get(self, index: int) -> Element:
        """Get the Element at a specific index of the container. In case there aren't enough elements in the container this returns an empty element instead."""
        ...

    def at_most(self, amount: int) -> Check:
        """Check that a container has at most a certain amount of elements."""
        ...

    def at_least(self, amount: int) -> Check:
        """Check that a container has at least a certain amount of elements."""
        ...

    def exactly(self, amount: int) -> Check:
        """Check that a container has exactly a certain amount of elements."""
        ...

    def all(self, func: Callable[[Element], Check]) -> Check:
        """Check if all elements in this container match a Check
        Requires the container to be non-empty, fails otherwise
        """
        ...

    def any(self, func: Callable[[Element], Check]) -> Check:
        """Check if one element in this container matches a Check
        Requires the container to be non-empty, fails otherwise
        """
        ...

class ChecklistItem:
    message: str
    _checks: list[Check] = ...
    _is_verbose: bool = False

    def __init__(self, message: str, *checks: Checks): ...
    def __post_init__(self): ...
    def _process_one(self, check: Check, bs: BeautifulSoup, language: str) -> bool:
        """Process a single check inside of this item"""
        ...

    def evaluate(self, bs: BeautifulSoup, language: str) -> bool:
        """Evaluate all checks inside of this item"""
        ...

class TestSuite:
    name: str
    content: str
    check_recommended: bool = True
    checklist: list[ChecklistItem] = ...
    translations: dict[str, list[str]] = ...
    _bs: BeautifulSoup = ...
    _html_validator: HtmlValidator = ...
    _css_validator: CssValidator | None = ...
    _html_validated: bool = ...
    _css_validated: bool = ...

    def __init__(self, name: str, content: str, check_recommended: bool = ...): ...
    def __post_init__(self): ...
    def create_validator(self, config: DodonaConfig): ...
    def css_is_valid(self) -> bool: ...
    def html_is_valid(self) -> bool: ...
    def add_item(self, check: ChecklistItem):
        """Shortcut for TestSuite.checklist.append(item)"""
        ...

    def make_item(self, message: str, *args: Checks):
        """Shortcut for suite.checklist.append(ChecklistItem(message, checks))"""
        ...

    def make_item_from_emmet(self, message: str, *emmets: Emmet):
        """Create a new ChecklistItem, the check will compare the submission to the emmet expression.
        The emmet expression is seen as the minimal required elements/attributes, so the submission may contain more
        or equal elements"""
        ...

    def validate_html(self, allow_warnings: bool = True) -> Check:
        """Check that the student's submitted code is valid HTML without syntax errors. The errors will not be reported to the student as to not reveal the answer."""
        ...

    def validate_css(self) -> Check:
        """Check that the code between the <style>-tag of the submission is valid CSS. If no style tag is present, this Check will also pass."""
        ...

    def add_check_validate_css_if_present(self):
        """Adds a check for CSS-validation only if there is some CSS supplied"""
        ...

    def compare_to_solution(self, solution: str, translator: Translator, **kwargs) -> Check:
        """Compare the submission to the solution html."""
        ...

    def document_matches(self, regex: str, flags: int | RegexFlag = ...) -> Check:
        """Check that the student's submitted code matches a regex string."""
        ...

    def contains_comment(self, comment: str | None = None) -> Check:
        """Check if the document contains a comment, optionally matching a value."""
        ...

    def contains_css(
        self,
        css_selector: str,
        prop: str,
        value: str | None = None,
        important: bool | None = None,
        any_order: bool = False,
    ) -> Check:
        """Check if the given css rule exists for the given css selector"""
        ...

    def has_doctype(self) -> Check:
        """Check if the document has a DOCTYPE tag, optionally matching a value"""
        ...

    def element(self, tag: str | Emmet | None = ..., index: int = 0, from_root: bool = False, **kwargs) -> Element:
        """Create a reference to an HTML element. Supports Emmet syntax through the tag parameter."""
        ...

    def all_elements(self, tag: str | Emmet | None = ..., from_root: bool = False, **kwargs) -> ElementContainer:
        """Get references to ALL HTML elements that match a query. Supports Emmet syntax through the tag parameter."""
        ...

    def _create_language_lists(self): ...
    def evaluate(self, translator: Translator) -> int: ...

class BoilerplateTestSuite(TestSuite):
    _default_translations: dict[str, list[str]]
    _default_checks: list[ChecklistItem]

    def __init__(self, name: str, content: str, check_recommended: bool = True, check_minimal: bool = False): ...

class HtmlSuite(BoilerplateTestSuite):
    allow_warnings: bool

    def __init__(
        self,
        content: str,
        check_recommended: bool = True,
        allow_warnings: bool = True,
        abort: bool = True,
        check_minimal: bool = False,
    ): ...

class CssSuite(BoilerplateTestSuite):
    allow_warnings: bool

    def __init__(
        self,
        content: str,
        check_recommended: bool = True,
        allow_warnings: bool = True,
        abort: bool = True,
        check_minimal: bool = False,
    ): ...

class _CompareSuite(HtmlSuite):
    def __init__(
        self,
        content: str,
        solution: str,
        config: DodonaConfig,
        check_recommended: bool = True,
        allow_warnings: bool = True,
        abort: bool = True,
    ): ...

def all_of(*args: Checks) -> Check:
    """The all_of function takes a series of Checks, and will only pass if all of these checks passed too. Once one check fails, all other checks in the list will no longer be evaluated."""
    ...

def any_of(*args: Checks) -> Check:
    """The any_of function takes a series of checks, and will pass if at least one of these checks passes as well. Once one check passes, all other checks in the list will no longer evaluated."""
    ...

def at_least(amount: int, *args: Checks) -> Check:
    """The at_least function takes the amount of checks required, and a series of checks to evaluate. The function will pass once at least amount checks have passed, and further checks will no longer be evaluated."""
    ...

def fail_if(check: Check) -> Check:
    """The fail_if function takes a check, and will fail if the check passes."""
    ...
