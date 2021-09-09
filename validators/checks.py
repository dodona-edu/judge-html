"""Basic checking library to create evaluation tests for exercises"""
from bs4 import BeautifulSoup
from bs4.element import Tag
from copy import deepcopy
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, List, Optional, Callable, Union, Tuple


# TODO extend Translator functionality for error messages to allow NL


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
    message: str
    callback: Callable[[BeautifulSoup], bool]
    on_success: List["Check"] = field(default_factory=list)
    hidden: bool = True

    def display(self) -> "Check":
        """Make the message of this check visible in the checklist"""
        self.hidden = False

        return self


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

    def get_child(self, tag: str, direct: bool = True, **kwargs) -> "Element":
        """Find the child element with the given tag

        :param tag:     the tag to search for
        :param direct:  indicate that only direct children should be considered,
                        no elements of children
        """
        child = self._element.find(tag, recursive=not direct, **kwargs)
        return Element(tag, kwargs.get("id", None), child)

    def exists(self) -> Check:
        """Check that this element was found"""
        def _inner(_: BeautifulSoup) -> bool:
            return self._element is not None

        message = f"Element {str(self)} is missing."
        return Check(message, _inner)

    def has_child(self, tag: str, direct: bool = True, **kwargs) -> Check:
        """Check that this element has a child with the given tag

        :param tag:     the tag to search for
        :param direct:  indicate that only direct children should be considered,
                        no elements of children
        """
        def _inner(_: BeautifulSoup) -> bool:
            return self._element.find(tag, recursive=not direct, **kwargs) is not None

        message = f"Element {str(self)} is missing child with tag {tag}."
        return Check(message, _inner)

    def has_content(self, text: Optional[str] = None) -> Check:
        """Check if this element has given text as content.
        In case no text is passed, any non-empty string will make the test pass
        """
        def _inner(_: BeautifulSoup) -> bool:
            if text is not None:
                return self._element.text == text

            return len(self._element.text) > 0

        if text:
            message = f"Content of element {str(self)} ({self._element.text}) did not match required content ({text})."
        else:
            message = f"Element {str(self)} does not contain any text."

        return Check(message, _inner)


@dataclass
class TestSuite:
    """Main test suite class

    Attributes:
        content     The HTML of the document to perform the tests on
        checklist   A list of all checks to perform on this document
    """
    content: str
    checklist: List[Check] = field(default_factory=list)
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
        messages = []
        queue: Deque[Check] = deque(deepcopy(self.checklist))

        # Keep running every check until the queue is exhausted
        while queue:
            check = queue.popleft()

            # Run checks
            success = check.callback(self._bs)

            # If the message should be shown on the checklist,
            if not check.hidden:
                messages.append((success, check.message))

            # Check failed, don't perform subtests
            if not success:
                continue

            # Add all on_success checks to the BEGINNING of the queue
            # because they should run next
            for sub in reversed(check.on_success):
                queue.appendleft(sub)

        return messages


def grouped_checks(message: str, args: List[Check]) -> Check:
    """Perform multiple checks at once, and show the given message in case one fails
    This method can be used to perform checks that require one another, without revealing
    the answer by accident.

    For example:
    - Check 1: does <body> exist?
    - Check 2: is there a <div> inside the body?
    - Check 3: is there an <a> inside that div?

    In case the first check fails, it would reveal part of the answer. If the checklist should
    only tell the student that there should be an <a>, and not that it should also be inside of
    a <div>, then this function can do that by ALWAYS displaying the message passed as an argument,
    no matter which check failed. That way the user won't get a "missing <div>" message.
    """
    queue: Deque[Check] = deque(deepcopy(args))

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

    return Check(message, _inner)
