"""Basic checking library to create evaluation tests for exercises"""
from bs4 import BeautifulSoup
from bs4.element import Tag
from copy import deepcopy
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, List, Optional, Callable, Union, Tuple


# TODO extend Translator functionality for error messages to allow NL
# TODO find a solution for potential index errors when strict-checking order of children
#   wrapper class for containers?


@dataclass
class Check:
    """Class that represents a single check

    Attributes:
        message     Message to display to the user in the checklist.
        callback    The function to run in order to perform this test.
        on_success  A list of checks that will only be performed in case this
                    check succeeds. An example of how this could be useful is to
                    first test if an element exists and THEN perform extra checks
                    on its attributes and/or children. This avoids unnecessary spam
                    to the user, because an element that doesn't exist never has
                    the correct specifications.
        hidden      Indicate that the message from this check should NOT be shown
                    in the final checklist. Again avoids unnecessary spam and can
                    help hide checks that would reveal the answer to the student.
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

    def then(self, *args: "Check") -> "Check":
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

    def __str__(self):
        if self.id is not None:
            return f"<{self.tag} id={self.id}>"

        return f"<{self.tag}>"

    def get_child(self, tag: str, index: int = 0, direct: bool = True, **kwargs) -> "Element":
        """Find the child element with the given tag

        :param tag:     the tag to search for
        :param index:   in case multiple children are found, specify the index to fetch
                        if not enough children were found, still return the first
        :param direct:  indicate that only direct children should be considered
        """
        # This element was not found, so the children don't exist either
        if self._element is None:
            return Element(tag, kwargs.get("id", None), None)

        # No index specified, first child requested
        if index == 0:
            child = self._element.find(tag, recursive=not direct, **kwargs)
        else:
            all_children = self._element.find_all(tag, recursive=not direct, **kwargs)

            # No children found
            if len(all_children) == 0:
                child = None
            else:
                # Not enough children found (index out of range)
                if index >= len(all_children):
                    index = 0

                child = all_children[index]

        return Element(tag, child.get("id", None), child)

    def get_children(self, tag: str = "", direct: bool = True, **kwargs) -> List["Element"]:
        """Get all children of this element that match the requested input"""
        # This element doesn't exist so it has no children
        if self._element is None:
            return []

        # If a tag was specified, only search for those
        # Otherwise, use all children instead
        if tag:
            matches = self._element.find_all(tag, recursive=not direct, **kwargs)
        else:
            matches = self._element.children if direct else self._element.descendants

            # Filter out string content
            matches = list(filter(lambda x: isinstance(x, Tag), matches))

        return list(map(lambda x: Element(x.name, x.get("id", None), x), matches))

    def exists(self) -> Check:
        """Check that this element was found"""
        def _inner(_: BeautifulSoup) -> bool:
            return self._element is not None

        return Check(_inner)

    def has_child(self, tag: str, direct: bool = True, **kwargs) -> Check:
        """Check that this element has a child with the given tag

        :param tag:     the tag to search for
        :param direct:  indicate that only direct children should be considered,
                        no elements of children
        """
        def _inner(_: BeautifulSoup) -> bool:
            return self._element.find(tag, recursive=not direct, **kwargs) is not None

        return Check(_inner)

    def has_content(self, text: Optional[str] = None) -> Check:
        """Check if this element has given text as content.
        In case no text is passed, any non-empty string will make the test pass
        """
        def _inner(_: BeautifulSoup) -> bool:
            if text is not None:
                return self._element.text == text

            return len(self._element.text) > 0

        return Check(_inner)

    def count_children(self, tag: str, amount: int, direct: bool = True, **kwargs) -> Check:
        """Check that this element has exactly [amount] children matching the requirements"""
        def _inner(_: BeautifulSoup) -> bool:
            return len(self._element.find_all(tag, recursive=not direct, **kwargs)) == amount

        return Check(_inner)

    def has_tag(self, tag: str) -> Check:
        """Check that this element has the required tag"""
        def _inner(_: BeautifulSoup) -> bool:
            if self._element is None:
                return False

            return self.tag == tag

        return Check(_inner)


def _flatten_queue(queue: List) -> List[Check]:
    """Flatten the queue to allow nested lists to be put it"""
    flattened: List[Check] = []

    while queue:
        el = queue.pop(0)

        # This entry is a list too, unpack it
        # & add to front of the queue
        if isinstance(el, list):
            # Iterate in reverse to keep the order of checks!
            for nested_el in reversed(el):
                queue.insert(0, nested_el)
        else:
            flattened.append(el)

    return flattened


@dataclass
class ChecklistItem:
    """An item to add to the checklist

    Attributes:
        message     The message displayed on the Dodona checklist for this item
        checklist   List of Checks to run, all of which should pass for this item
                    to be marked as passed/successful on the final list
    """
    message: str
    # People can pass nested lists into this, so the type is NOT List[Check] yet
    checks: List = field(default_factory=list)
    _checks: List[Check] = field(init=False)

    def __post_init__(self):
        # Flatten the list of checks and store in internal list
        for item in self.checks:
            if isinstance(item, Check):
                self._checks.append(item)
            elif isinstance(item, list):
                # Group the list into one main check and add that one
                self._checks.append(all_of(item))

    def evaluate(self, bs: BeautifulSoup) -> bool:
        """Evaluate all checks inside of this item"""
        for check in self._checks:
            if not check.callback(bs):
                # TODO create Aborted exception if check requests it & raise if necessary
                return False

        return True


@dataclass
class TestSuite:
    """Main test suite class

    Attributes:
        content     The HTML of the document to perform the tests on
        checklist   A list of all checks to perform on this document
    """
    content: str
    checklist: List[ChecklistItem] = field(default_factory=list)
    _bs: BeautifulSoup = field(init=False)
    _root: Tag = field(init=False)

    def __post_init__(self):
        self._bs = BeautifulSoup(self.content, "html.parser")

        # Assume HTML validation has been done beforehand, and every document
        # correctly starts/ends with <html> tags
        self._root = self._bs.html

    def element(self, tag: str, from_root=True, **kwargs) -> Element:
        """Create a reference to an HTML element
        :param tag:         the name of the HTML tag to search for
        :param from_root:   find the element as a child of the root node instead of anywhere
                            in the document
        """
        start: Union[BeautifulSoup, Tag] = self._root if from_root else self._bs

        element = start.find(tag, **kwargs)
        return Element(tag, kwargs.get("id", None), element)

    def evaluate(self) -> List[Tuple[bool, str]]:
        """Run the test suite, returns a list of messages (being the checklist)
        Every message is of the format (bool, str). The boolean indicates that
        the check was successful, the string contains the message itself.
        """
        # Create an initial list with only False's so when we abort the checks
        # all future checks on the list are already marked as failed
        messages = list((False, item.message,) for item in self.checklist)

        # Run all items on the checklist & mark them as successful if applicable
        # TODO try-catch aborted exception
        for i, item in enumerate(self.checklist):
            # Can't set items on tuples so overwrite it
            messages[i] = (item.evaluate(self._bs), item.message,)

        return messages


def all_of(args: List[Check]) -> Check:
    """Perform an AND-statement on a list of checks
    Creates a new Check that requires every single one of the checks to pass,
    otherwise returns False.
    """
    # Flatten list of checks
    flattened = _flatten_queue(deepcopy(args))
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


def has_count(elements: List, amount: int) -> Check:
    """Check that a list of elements has a certain amount of entries"""
    def _inner(_: BeautifulSoup) -> bool:
        return len(elements) == amount

    return Check(_inner)
