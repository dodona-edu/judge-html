"""Basic checking library to create evaluation tests for exercises"""
import re
from collections import deque
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Deque, List, Optional, Callable, Union, Dict, TypeVar, Iterable
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString

from decorators import flatten_varargs
from dodona.dodona_command import Context, TestCase, Message, MessageFormat, Annotation
from dodona.dodona_config import DodonaConfig
from dodona.translator import Translator
from exceptions.double_char_exceptions import MultipleMissingCharsError, LocatableDoubleCharError
from exceptions.html_exceptions import Warnings, LocatableHtmlValidationError
from exceptions.utils import EvaluationAborted
from utils.flatten import flatten_queue
from utils.regexes import doctype_re
from utils.html_navigation import find_child, compare_content, match_emmet, find_emmet, contains_comment
from validators.css_validator import CssValidator, CssParsingError
from validators.html_validator import HtmlValidator


# Emmet string type
Emmet = TypeVar("Emmet", bound=str)
Checks = TypeVar("Checks", bound=Union["Check", Iterable["Check"]])


@dataclass
class Check:
    """Class that represents a single check

    Attributes:
        callback    The function to run in order to perform this test.
        on_success  A list of checks that will only be performed in case this
                    check succeeds. An example of how this could be useful is to
                    first test if an element exists and THEN perform extra checks
                    on its attributes and/or children. This avoids unnecessary spam
                    to the user, because an element that doesn't exist never has
                    the correct specifications.
    """
    callback: Callable[[BeautifulSoup], bool]
    on_success: List["Check"] = field(default_factory=list)
    abort_on_fail: bool = False

    def _find_deepest_nested(self) -> "Check":
        """Find the deepest Check nested with on_success chains"""
        current_deepest = self.on_success[-1]

        # Keep going until the current one no longer contains anything
        while current_deepest.on_success:
            current_deepest = current_deepest.on_success[-1]

        return current_deepest

    def or_abort(self) -> "Check":
        """Prevent the next tests from running if this one fails
        Can be used when a test is necessary for the rest to continue, for example
        the HTML-validation step.
        """
        self.abort_on_fail = True
        return self

    def is_crucial(self) -> "Check":
        """Alias to or_abort()"""
        return self.or_abort()

    @flatten_varargs
    def then(self, *args: Checks) -> "Check":
        """Register a list of checks to perform in case this check succeeds
        When this check already has checks registered, try to find the deepest check
        and append it to that check. The reasoning is that x.then(y).then(z) suggests y should
        complete for z to start. This makes the overall use more fluent and avoids
        a big mess of brackets when it's not necessary at all.

        Returns a reference to the last entry to allow a fluent interface.
        """
        if not self.on_success:
            self.on_success = list(args)
        else:
            # Find the deepest child check and add to that one
            deepest: "Check" = self._find_deepest_nested()
            deepest.on_success = list(args)

        return args[-1]


@dataclass
class Element:
    """Class for an HTML element used in testing

    Attributes:
        tag         The HTML tag of this element.
        id          An optional id to specify when searching for the element,
                    if not specified then the first result found will be used.
        _element    The inner HTML element that was matched in the document,
                    can be None if nothing was found.
    """
    tag: str
    id: Optional[str] = None
    _element: Optional[Tag] = None
    _css_validator: Optional[CssValidator] = None

    def __str__(self):
        if self.id is not None:
            return f"<{self.tag} id={self.id}>"

        return f"<{self.tag}>"

    # HTML utilities
    def get_child(self, tag: Optional[Union[str, Emmet]] = None, index: int = 0, direct: bool = True, **kwargs) -> "Element":
        """Find the child element that matches the specifications

        :param tag:     the tag to search for
        :param index:   in case multiple children are found, specify the index to fetch
                        if not enough children were found, return an EmptyElement
        :param direct:  indicate that only direct children should be considered
        """
        child = find_child(self._element, tag=tag, index=index, from_root=direct, **kwargs)

        if child is None:
            return EmptyElement()

        return Element(child.name, child.get("id", None), child, self._css_validator)

    def get_children(self, tag: Optional[Union[str, Emmet]] = None, direct: bool = True, **kwargs) -> "ElementContainer":
        """Get all children of this element that match the requested input"""
        # This element doesn't exist so it has no children
        if self._element is None:
            return ElementContainer([])

        # Emmet syntax requested
        if match_emmet(tag):
            # Index parameter is not relevant here & it won't be used anyways
            matches = find_emmet(self._element, tag, 0, from_root=direct, match_multiple=True, **kwargs)

            # Nothing found
            if matches is None:
                return ElementContainer([])
        elif tag is not None:
            # If a tag was specified, only search for those
            matches = self._element.find_all(tag, recursive=not direct, **kwargs)
        else:
            # Otherwise, use all children instead
            matches = self._element.children if direct else self._element.descendants

            # Filter out string content
            matches = list(filter(lambda x: isinstance(x, Tag), matches))

        return ElementContainer.from_tags(matches, self._css_validator)

    # HTML checks
    def exists(self) -> Check:
        """Check that this element was found"""

        def _inner(_: BeautifulSoup) -> bool:
            return self._element is not None

        return Check(_inner)

    def has_child(self, tag: str, direct: bool = True, **kwargs) -> Check:
        """Check that this element has a child with the given tag

        :param tag:     the tag to search for
        :param direct:  indicate that only direct children should be considered,
                        not children of children
        """

        def _inner(_: BeautifulSoup) -> bool:
            if self._element is None:
                return False

            return self._element.find(tag, recursive=not direct, **kwargs) is not None

        return Check(_inner)

    def has_content(self, text: Optional[str] = None, case_insensitive: bool = False) -> Check:
        """Check if this element has given text as content.
        In case no text is passed, any non-empty string will make the test pass

        Example:
        >>> suite = TestSuite("<p>This is some text</p>")
        >>> element = suite.element("p")
        >>> element.has_content()
        True
        >>> element.has_content("This is some text")
        True
        >>> element.has_content("Something else")
        False
        """

        def _inner(_: BeautifulSoup) -> bool:
            # Element doesn't exist
            if self._element is None:
                return False

            if self._element.text is None:
                return text is None

            if text is not None:
                return compare_content(self._element.text, text, case_insensitive)

            return len(self._element.text.strip()) > 0

        return Check(_inner)

    def _has_tag(self, tag: str) -> bool:
        """Internal function that checks if this element has the required tag"""
        return self._element is not None and self._element.name.lower() == tag.lower()

    def has_tag(self, tag: str) -> Check:
        """Check that this element has the required tag"""

        def _inner(_: BeautifulSoup) -> bool:
            return self._has_tag(tag)

        return Check(_inner)

    def no_loose_text(self) -> Check:
        """Check that there is no content floating around in this tag"""

        def _inner(_: BeautifulSoup) -> bool:
            # Even though a non-existent element has no text,
            # so it may seem as this should always pass,
            # the standard behaviour is that Checks for these elements
            # should always fail
            if self._element is None:
                return False

            children = self._element.children

            for child in children:
                # Child is a text instance which is not allowed
                # Empty tags shouldn't count as text, but for some reason bs4
                # still picks these up so they're filtered out as well
                if isinstance(child, NavigableString) and child.text.strip():
                    return False

            return True

        return Check(_inner)

    def _get_attribute(self, attr: str) -> Optional[Union[List[str], str]]:
        """Internal function that gets an attribute"""
        if self._element is None:
            return None

        attribute = self._element.get(attr.lower())

        return attribute

    def _compare_attribute_list(self, attribute: List[str], value: Optional[str] = None,
                                case_insensitive: bool = False,
                                mode: int = 0, flags: Union[int, re.RegexFlag] = 0) -> bool:
        """Attribute check for attributes that contain lists (eg. Class). Can handle all 3 modes.
        0: exact match (exists)
        1: substring (contains)
        2: regex match (matches)
        """
        # Attribute doesn't exist
        if not attribute:
            return False

        # Any value is good enough
        if value is None:
            return True

        if case_insensitive:
            value = value.lower()
            attribute = list(map(lambda x: x.lower(), attribute))

        # Exact match
        if mode == 0:
            return value in attribute

        # Contains substring
        if mode == 1:
            return any(value in v for v in attribute)

        # Match regex
        if mode == 2:
            for v in attribute:
                if re.search(value, v, flags) is not None:
                    return True

            return False

        # Possible future modes
        return False

    def attribute_exists(self, attr: str, value: Optional[str] = None, case_insensitive: bool = False) -> Check:
        """Check that this element has the required attribute, optionally with a value
        :param attr:                The name of the attribute to check.
        :param value:               The value to check. If no value is passed, this will not be checked.
        :param case_insensitive:    Indicate that the casing of the attribute does not matter.
        """

        def _inner(_: BeautifulSoup) -> bool:
            attribute = self._get_attribute(attr)

            # Attribute wasn't found
            if attribute is None:
                return False

            if isinstance(attribute, list):
                return self._compare_attribute_list(attribute, value, case_insensitive, mode=0)

            # No value specified
            if value is None:
                return True

            if case_insensitive:
                return attribute.lower() == value.lower()

            return attribute == value

        return Check(_inner)

    def attribute_contains(self, attr: str, substr: str, case_insensitive: bool = False) -> Check:
        """Check that the value of this attribute contains a substring"""

        def _inner(_: BeautifulSoup) -> bool:
            attribute = self._get_attribute(attr)

            # Attribute wasn't found
            if attribute is None:
                return False

            if isinstance(attribute, list):
                return self._compare_attribute_list(attribute, substr, case_insensitive, mode=1)

            if case_insensitive:
                return substr.lower() in attribute.lower()

            return substr in attribute

        return Check(_inner)

    def attribute_matches(self, attr: str, regex: str, flags: Union[int, re.RegexFlag] = 0) -> Check:
        """Check that the value of an attribute matches a regex pattern"""

        def _inner(_: BeautifulSoup) -> bool:
            attribute = self._get_attribute(attr)

            # Attribute wasn't found
            if attribute is None:
                return False

            if isinstance(attribute, list):
                return self._compare_attribute_list(attribute, regex, mode=2, flags=flags)

            return re.search(regex, attribute, flags) is not None

        return Check(_inner)

    def has_table_header(self, header: List[str]) -> Check:
        """If this element is a table, check that the header content matches up"""

        def _inner(_: BeautifulSoup) -> bool:
            # This element is either None or not a table
            if not self._has_tag("table"):
                return False

            # List of all headers in this table
            ths = self._element.find_all("th")

            # Not the same amount of headers
            if len(ths) != len(header):
                return False

            # Check if all headers have the same content in the same order
            for i in range(len(header)):
                if not compare_content(header[i], ths[i].text):
                    return False

            return True

        return Check(_inner)

    def has_table_content(self, rows: List[List[str]], has_header: bool = True, case_insensitive: bool = False) -> Check:
        """Check that a table's rows have the requested content
        :param rows:                The data of all the rows to check
        :param has_header:          Boolean that indicates that this table has a header,
                                    so the first row will be ignored (!)
        :param case_insensitive:    Indicate that comparison should ignore casing or not
        """

        def _inner(_: BeautifulSoup) -> bool:
            # This element is either None or not a table
            if not self._has_tag("table"):
                return False

            trs = self._element.find_all("tr")

            # No rows found
            if not trs:
                return False

            # Cut header out
            if has_header:
                trs = trs[1:]

                # Table only had a header, no actual content
                if not trs:
                    return False

            # Incorrect amount of rows
            if len(trs) != len(rows):
                return False

            # Compare tds (actual data)
            for i in range(len(rows)):
                data = trs[i].find_all("td")

                # Row doesn't have the same amount of tds
                if len(data) != len(rows[i]):
                    return False

                # Compare content
                for j in range(len(rows[i])):
                    # Content doesn't match
                    if not compare_content(data[j].text, rows[i][j], case_insensitive):
                        return False

            return True

        return Check(_inner)

    def table_row_has_content(self, row: List[str], case_insensitive: bool = False) -> Check:
        """Check the content of one row instead of the whole table"""

        def _inner(_: BeautifulSoup) -> bool:
            # Check that this element exists and is a <tr>
            if not self._has_tag("tr"):
                return False

            tds = self._element.find_all("td")

            # Amount of items doesn't match up
            if len(tds) != len(row):
                return False

            for i in range(len(row)):
                # Text doesn't match
                if not compare_content(row[i], tds[i].text, case_insensitive):
                    return False

            return True

        return Check(_inner)

    def has_url_with_fragment(self, fragment: Optional[str] = None) -> Check:
        """Check if a url has a fragment
        If no fragment is passed, any non-empty fragment will do
        """

        def _inner(_: BeautifulSoup) -> bool:
            if self._element is None or self.tag.lower() != "a":
                return False

            url = self._get_attribute("href")

            # No url present
            if url is None:
                return False

            split = urlsplit(url)

            # No fragment present
            if not split.fragment:
                return False

            # No value required
            if fragment is None:
                return True

            return fragment == split.fragment

        return Check(_inner)

    def has_outgoing_url(self, allowed_domains: Optional[List[str]] = None, attr: str = "href") -> Check:
        """Check if a tag has an outgoing link
        :param allowed_domains: A list of domains that should not be considered "outgoing",
                                defaults to ["dodona.ugent.be", "users.ugent.be"]
        :param attr:            The attribute the link should be in
        """
        if allowed_domains is None:
            allowed_domains = ["dodona.ugent.be", "users.ugent.be"]

        def _inner(_: BeautifulSoup) -> bool:
            if self._element is None:
                return False

            url = self._get_attribute(attr.lower())

            # No url present
            if url is None:
                return False

            spl = urlsplit(url)

            if spl.netloc:
                # Ignore www. in the start to allow the arguments to be shorter
                netloc = spl.netloc.lower().removeprefix("www.")
                return netloc not in list(map(lambda x: x.lower(), allowed_domains))

            return False

        return Check(_inner)

    def contains_comment(self, comment: Optional[str] = None) -> Check:
        """Check if the element contains a comment, optionally matching a value"""

        def _inner(_: BeautifulSoup) -> bool:
            return contains_comment(self._element, comment)

        return Check(_inner)

    # CSS checks
    def has_styling(self, prop: str, value: Optional[str] = None, important: Optional[bool] = None) -> Check:
        """Check that this element has a CSS property
        :param prop:        the required CSS property to check
        :param value:       an optional value to add that must be checked against,
                            in case nothing is supplied any value will pass
        :param important:   indicate that this must (or may not be) marked as important
        """

        def _inner(_: BeautifulSoup) -> bool:
            if self._element is None:
                return False

            # This shouldn't happen if the element exists, but just in case
            if self._css_validator is None:
                return False

            prop_value = self._css_validator.find(self._element, prop.lower())

            # Property not found
            if prop_value is None:
                return False

            # !important modifier is incorrect
            if important is not None and prop_value.important != important:
                return False

            # Value doesn't matter
            if value is None:
                return True

            return prop_value.value_str == value

        return Check(_inner)

    def has_color(self, prop: str, color: str, important: Optional[bool] = None) -> Check:
        """Check that this element has a given color
        More flexible version of has_styling because it also allows RGB(r, g, b), hex format, ...

        :param prop:        the required CSS property to check (background-color, color, ...)
        :param color:       the color to check this property's value against, in any format
        :param important:   indicate that this must (or may not be) marked as important
        """

        def _inner(_: BeautifulSoup) -> bool:
            if self._element is None or self._css_validator is None:
                return False

            # Find the CSS Rule
            prop_rule = self._css_validator.find(self._element, prop.lower())

            # !important modifier is incorrect
            if important is not None and prop_rule.important != important:
                return False

            return prop_rule.has_color(color)

        return Check(_inner)


@dataclass
class EmptyElement(Element):
    """Class that represents an element that could not be found"""

    def __init__(self):
        super().__init__("", None, None, None)


@dataclass
class ElementContainer:
    """Class used for collections of elements fetched from the HTML
    This class was made to avoid potential IndexErrors in the evaluation file
    when using indexing.

    The example below assumes that there are two <div>s in the solution in order
    to set up the checklist, but the student's current file may not have these.
    This would cause IndexErrors when parsing the file.

    By letting get_children() return this container class, we can just return an
    empty Element() object when the list doesn't have enough elements, and then
    other checks will just fail instead of crashing.
    Example:
    >>> suite = TestSuite("<body>"
    ...                     "<div id='div1'>"
    ...                         "..."
    ...                     "</div>"
    ...                     "<div id='div2'>"
    ...                         "..."
    ...                     "</div>"
    ...                   "</body>")
    >>> all_divs = suite.element("body").get_children("div")
    >>> all_divs[1].has_child("...")  # IndexError if student doesn't have this!

    Attributes:
        elements       the elements to add into this container
    """
    elements: List[Element]
    _size: int = field(init=False)

    def __post_init__(self):
        # Avoid calling len() all the time
        self._size = len(self.elements)

    def __getitem__(self, item) -> Union[Element, List[Element]]:
        if not isinstance(item, (int, slice)):
            raise TypeError(f"Key {item} was of type {item}, not int or slice.")

        # Out of range
        if isinstance(item, int) and item >= self._size:
            return EmptyElement()

        return self.elements[item]

    def __iter__(self):
        for el in self.elements:
            yield el

    def __len__(self):
        return self._size

    @classmethod
    def from_tags(cls, tags: List[Tag], css_validator: CssValidator) -> "ElementContainer":
        """Construct a container from a list of bs4 Tag instances"""
        elements = list(map(lambda x: Element(x.name, x.get("id", None), x, css_validator), tags))
        return ElementContainer(elements)

    def get(self, index: int) -> Element:
        """Get an item at a given index, same as []-operator"""
        return self[index]

    def at_most(self, amount: int) -> Check:
        """Check that a container has at most [amount] elements"""

        def _inner(_: BeautifulSoup):
            return self._size <= amount

        return Check(_inner)

    def at_least(self, amount: int) -> Check:
        """Check that a container has at least [amount] elements"""

        def _inner(_: BeautifulSoup):
            return self._size >= amount

        return Check(_inner)

    def exactly(self, amount: int) -> Check:
        """Check that a container has exactly [amount] elements"""

        def _inner(_: BeautifulSoup) -> bool:
            return self._size == amount

        return Check(_inner)

    def all(self, func: Callable[[Element], Check]) -> Check:
        """Check if all elements in this container match a Check
        Requires the container to be non-empty, fails otherwise
        """
        return self.at_least(1).then(all_of(func(el) for el in self.elements))

    def any(self, func: Callable[[Element], Check]) -> Check:
        """Check if one element in this container matches a Check
        Requires the container to be non-empty, fails otherwise
        """
        return self.at_least(1).then(any_of(func(el) for el in self.elements))


@dataclass(init=False)
class ChecklistItem:
    """An item to add to the checklist

    Attributes:
        message     The message displayed on the Dodona checklist for this item
        checklist   List of Checks to run, all of which should pass for this item
                    to be marked as passed/successful on the final list
    """
    message: str
    _checks: List[Check] = field(init=False)

    def __init__(self, message: str, *checks: Checks):
        self.message = message
        self._checks = []

        # Flatten the list of checks and store in internal list
        checks = flatten_queue(checks)
        self._checks = flatten_queue(checks)

    def evaluate(self, bs: BeautifulSoup) -> bool:
        """Evaluate all checks inside of this item"""
        for check in self._checks:
            if not check.callback(bs):
                # Abort testing if necessary
                if check.abort_on_fail:
                    raise EvaluationAborted()

                return False

        return True


@dataclass
class TestSuite:
    """Main test suite class

    Attributes:
        content     The HTML of the document to perform the tests on
        checklist   A list of all checks to perform on this document
    """
    name: str
    content: str
    check_recommended: bool = True
    checklist: List[ChecklistItem] = field(default_factory=list)
    translations: Dict[str, List[str]] = field(default_factory=dict)
    _bs: BeautifulSoup = field(init=False)
    _html_validator: HtmlValidator = field(init=False)
    _css_validator: Optional[CssValidator] = field(init=False)
    _html_validated: bool = field(init=False)
    _css_validated: bool = field(init=False)

    def __post_init__(self):
        self._bs = BeautifulSoup(self.content, "html.parser")
        self._html_validated = False

        try:
            self._css_validator = CssValidator(self.content)
            self._css_validated = True
        except CssParsingError:
            # Css is invalid, can't create the validator
            self._css_validator = None
            self._css_validated = False

    def create_validator(self, config: DodonaConfig):
        """Create the HTML validator from outside the Suite
        The Suite is created in the evaluation file by teachers, so we
        avoid passing extra arguments into the constructor as much as we can.
        """
        self._html_validator = HtmlValidator(config.translator, recommended=self.check_recommended)

    def html_is_valid(self) -> bool:
        """Return whether or not the HTML has been validated
        Avoids private property access
        """
        return self._html_validated

    def css_is_valid(self) -> bool:
        """Return if the CSS was valid
        Avoids private property access
        """
        return self._css_validated

    def add_item(self, check: ChecklistItem):
        """Add an item to the checklist
        This is a shortcut to suite.checklist.append(item)
        """
        self.checklist.append(check)

    @flatten_varargs
    def make_item(self, message: str, *args: Checks):
        """Create a new ChecklistItem
        This is a shortcut for suite.checklist.append(ChecklistItem(message, check))"""
        self.checklist.append(ChecklistItem(message, list(args)))

    def make_item_from_emmet(self, message: str, *emmets: Emmet):
        """Create a new ChecklistItem, the check will compare the submission to the emmet expression.
            The emmet expression is seen as the minimal required elements/attributes, so the submission may contain more
            or equal elements"""
        from utils.emmet import emmet_to_check

        emmet_checks = []

        # Add multiple emmet checks under one main item
        for e in emmets:
            emmet_checks.append(emmet_to_check(e, self))

        self.make_item(message, *emmet_checks)

    def validate_html(self, allow_warnings: bool = True) -> Check:
        """Check that the HTML is valid
        This is done in here so that all errors and warnings can be sent to
        Dodona afterwards by reading them out of here

        The CODE format is used because it preserves spaces & newlines
        """

        def _inner(_: BeautifulSoup) -> bool:
            try:
                self._html_validator.validate_content(self.content)
            except Warnings as war:
                with Message(description=str(war), format=MessageFormat.CODE):
                    for exc in war.exceptions:
                        with Annotation(row=exc.position[0], text=str(exc), type="warning"):
                            pass
                    self._html_validated = allow_warnings
                    return allow_warnings
            except LocatableHtmlValidationError as err:
                with Message(description=str(err), format=MessageFormat.CODE):
                    with Annotation(row=err.position[0], text=str(err), type="error"):
                        pass
                    return False
            except MultipleMissingCharsError as errs:
                with Message(description=str(errs), format=MessageFormat.CODE):
                    err: LocatableDoubleCharError
                    for err in errs.exceptions:
                        with Annotation(row=err.position[0], text=str(err), type="error"):
                            pass
                    return False
            # If no validation errors were raised, the HTML is valid
            self._html_validated = True
            return True

        return Check(_inner)

    def validate_css(self) -> Check:
        """Check that CSS was valid"""

        def _inner(_: BeautifulSoup) -> bool:
            return self._css_validated

        return Check(_inner)

    def add_check_validate_css_if_present(self):
        """Adds a check for CSS-validation only if there is some CSS supplied"""
        if self._css_validated and self._css_validator:
            self.add_item(ChecklistItem("The css is valid.", self.validate_css()))
            if "nl" in self.translations:
                self.translations["nl"].append("De CSS is geldig.")

    def compare_to_solution(self, solution: str, translator: Translator, **kwargs) -> Check:
        """Compare the submission to the solution html."""

        def _inner(_: BeautifulSoup):
            from validators.structure_validator import compare, NotTheSame
            try:
                compare(solution, self.content, translator, **kwargs)
            except NotTheSame as err:
                with Message(str(err)):
                    # Only add annotation if line number is positive
                    if err.line >= 0:
                        with Annotation(err.line, str(err)):
                            pass

                    return False
            return True

        return Check(_inner)

    def document_matches(self, regex: str, flags: Union[int, re.RegexFlag] = 0) -> Check:
        """Check that the document matches a regex"""

        def _inner(_: BeautifulSoup) -> bool:
            return re.search(regex, self.content, flags) is not None

        return Check(_inner)

    def contains_comment(self, comment: Optional[str] = None) -> Check:
        """Check if the document contains a comment, optionally matching a value"""
        def _inner(_: BeautifulSoup) -> bool:
            return contains_comment(self._bs, comment)

        return Check(_inner)

    def has_doctype(self) -> Check:
        """Check if the document starts with <!DOCTYPE HTML"""
        def _inner(_: BeautifulSoup) -> bool:
            # Do NOT use the BS Doctype for this, because it repairs
            # incorrect/broken HTML which invalidates this function
            return re.search(doctype_re.pattern, self.content, doctype_re.flags) is not None

        return Check(_inner)

    def element(self, tag: Optional[Union[str, Emmet]] = None, index: int = 0, from_root: bool = False, **kwargs) -> Element:
        """Create a reference to an HTML element
        :param tag:         the name of the HTML tag to search for
        :param index:       in case multiple elements match, specify which should be chosen
        :param from_root:   find the element as a child of the root node instead of anywhere
                            in the document
        """
        element = find_child(self._bs, tag=tag, index=index, from_root=from_root, **kwargs)

        if element is None:
            return EmptyElement()

        return Element(element.name, kwargs.get("id", None), element, self._css_validator)

    def all_elements(self, tag: Optional[Union[str, Emmet]] = None, from_root: bool = False, **kwargs) -> ElementContainer:
        """Get references to ALL HTML elements that match a query"""
        if match_emmet(tag):
            elements = find_emmet(self._bs, tag, 0, from_root=from_root, match_multiple=True, **kwargs)

            if elements is None:
                return ElementContainer([])
        else:
            elements = self._bs.find_all(tag, recursive=not from_root, **kwargs)

        return ElementContainer.from_tags(elements, self._css_validator)

    def _create_language_lists(self):
        """Init the lists of languages to avoid IndexErrors"""
        for language in ["en", "nl"]:
            if language not in self.translations:
                self.translations[language] = []

    def evaluate(self, translator: Translator) -> int:
        """Run the test suite, and print the Dodona output
        :returns:   the amount of failed tests
        :rtype:     int
        """
        aborted = -1
        failed_tests = 0

        lang_abr = translator.language.name.lower()

        # Run all items on the checklist & mark them as successful if they pass
        for i, item in enumerate(self.checklist):
            # Get translated version if possible, else use the message in the item
            message: str = item.message \
                if lang_abr not in self.translations or i >= len(self.translations[lang_abr]) \
                else self.translations[lang_abr][i]

            with Context(), TestCase(message) as test_case:
                # Make it False by default so crashing doesn't make it default to True
                test_case.accepted = False

                # Evaluation was aborted, print a message and skip this test
                if aborted >= 0:
                    with Message(description=translator.translate(translator.Text.TESTCASE_NO_LONGER_EVALUATED),
                                 format=MessageFormat.TEXT):
                        failed_tests += 1
                        continue

                # Can't set items on tuples so overwrite it
                try:
                    test_case.accepted = item.evaluate(self._bs)
                except EvaluationAborted:
                    # Crucial test failed, stop evaluation and let the next tests
                    # all be marked as wrong
                    aborted = i

                    with Message(description=translator.translate(translator.Text.TESTCASE_ABORTED),
                                 format=MessageFormat.TEXT):
                        pass

                # If the test wasn't marked as True above, increase the counter for failed tests
                if not test_case.accepted:
                    failed_tests += 1

        return failed_tests


class BoilerplateTestSuite(TestSuite):
    """Base class for TestSuites that handle some boilerplate things"""
    _default_translations: Optional[Dict[str, List[str]]] = None
    _default_checks: Optional[List[ChecklistItem]] = None

    def __init__(self, name: str,
                 content: str,
                 check_recommended: bool = True,
                 _default_translations: Optional[Dict[str, List[str]]] = None,
                 _default_checks: Optional[List[ChecklistItem]] = None):
        super().__init__(name, content, check_recommended)

    def _add_default_translations(self):
        self._create_language_lists()

        if self._default_translations is None:
            return

        # Add in reverse order so we can keep inserting at index 0
        for language, translations in self._default_translations.items():
            for entry in reversed(translations):
                self.translations[language].insert(0, entry)

    def _add_default_checks(self):
        if self._default_checks is None:
            return

        # Add in reverse order so we can keep inserting at index 0
        for item in reversed(self._default_checks):
            self.checklist.insert(0, item)

    def evaluate(self, translator: Translator) -> int:
        self._add_default_translations()
        self._add_default_checks()

        return super().evaluate(translator)


class HtmlSuite(BoilerplateTestSuite):
    """TestSuite that does HTML validation by default"""
    allow_warnings: bool

    def __init__(self, content: str, check_recommended: bool = True, allow_warnings: bool = True, abort: bool = True):
        super().__init__("HTML", content, check_recommended)

        # Only abort if necessary
        if abort:
            self._default_checks = [ChecklistItem("The HTML is valid.", self.validate_html(allow_warnings).or_abort())]
        else:
            self._default_checks = [ChecklistItem("The HTML is valid.", self.validate_html(allow_warnings))]

        self._default_translations = {"en": ["The HTML is valid."], "nl": ["De HTML is geldig."]}

        self.allow_warnings = allow_warnings


class CssSuite(BoilerplateTestSuite):
    """TestSuite that does HTML and CSS validation by default"""
    allow_warnings: bool

    def __init__(self, content: str, check_recommended: bool = True, allow_warnings: bool = True, abort: bool = True):
        super().__init__("CSS", content, check_recommended)

        # Only abort if necessary
        if abort:
            self._default_checks = [ChecklistItem("The HTML is valid.", self.validate_html(allow_warnings).or_abort()),
                                    ChecklistItem("The CSS is valid.", self.validate_css().or_abort())
                                    ]
        else:
            self._default_checks = [ChecklistItem("The HTML is valid.", self.validate_html(allow_warnings)),
                                    ChecklistItem("The CSS is valid.", self.validate_css())
                                    ]

        self._default_translations = {
            "en": ["The HTML is valid.", "The CSS is valid."],
            "nl": ["De HTML is geldig.", "De CSS is geldig."]
        }

        self.allow_warnings = allow_warnings


class _CompareSuite(HtmlSuite):
    """TestSuite that does:
     * HTML validation
     * CSS validation (if css is present)
     * evaluation by comparing to the solution.html"""

    def __init__(self, content: str, solution: str, config: DodonaConfig, check_recommended: bool = True,
                 allow_warnings: bool = True, abort: bool = True):
        super().__init__(content, check_recommended, allow_warnings, abort)

        # Adds a check for CSS-validation only if there is some CSS supplied
        if self._css_validated and self._css_validator:
            if abort:
                self._default_checks.append(ChecklistItem("The CSS is valid.", self.validate_css().or_abort()))
            else:
                self._default_checks.append(ChecklistItem("The CSS is valid.", self.validate_css()))
            # Translations
            self._default_translations["en"].append("The CSS is valid.")
            self._default_translations["nl"].append("De CSS is geldig.")

        # Adds a check for comparing to solution
        params = {"attributes": getattr(config, "attributes", False),
                  "minimal_attributes": getattr(config, "minimal_attributes", False),
                  "contents": getattr(config, "contents", False)}

        self._default_checks.append(
            ChecklistItem("The submission resembles the solution.",
                          self.compare_to_solution(solution, config.translator, **params)))
        # Translations
        self._default_translations["en"].append("The submission resembles the solution.")
        self._default_translations["nl"].append("De ingediende code lijkt op die van de oplossing.")


"""
UTILITY FUNCTIONS
"""


@flatten_varargs
def all_of(*args: Checks) -> Check:
    """Perform an AND-statement on a series of Checks
    Creates a new Check that requires every single one of the checks to pass,
    otherwise returns False.
    """
    # Flatten list of checks
    flattened = flatten_queue(deepcopy(list(args)))
    queue: Deque[Check] = deque(flattened)

    def _inner(bs: BeautifulSoup) -> bool:
        while queue:
            check = queue.popleft()

            # One check failed, return False
            if not check.callback(bs):
                return False

            # Try the other checks
            for sub in reversed(check.on_success):
                queue.appendleft(sub)

        return True

    return Check(_inner)


@flatten_varargs
def any_of(*args: Checks) -> Check:
    """Perform an OR-statement on a series of Checks
    Returns True if at least one of the tests succeeds, and stops
    evaluating the rest at that point.
    """
    # Flatten list of checks
    flattened = flatten_queue(deepcopy(list(args)))
    queue: Deque[Check] = deque(flattened)

    def _inner(bs: BeautifulSoup) -> bool:
        while queue:
            check = queue.popleft()

            # One check passed, return True
            if check.callback(bs):
                return True

            # Try the other checks
            for sub in reversed(check.on_success):
                queue.appendleft(sub)

        return False

    return Check(_inner)


@flatten_varargs
def at_least(amount: int, *args: Checks) -> Check:
    """Check that at least [amount] checks passed"""
    # Flatten list of checks
    flattened = flatten_queue(deepcopy(list(args)))
    queue: Deque[Check] = deque(flattened)

    def _inner(bs: BeautifulSoup) -> bool:
        passed = 0

        while queue:
            check = queue.popleft()

            if check.callback(bs):
                passed += 1

            if passed >= amount:
                return True

        return False

    return Check(_inner)


def fail_if(check: Check) -> Check:
    """Fail if the inner Check returns True
    Equivalent to the not-operator.
    """

    def _inner(bs: BeautifulSoup):
        return not check.callback(bs)

    return Check(_inner)
