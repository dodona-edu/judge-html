import re
from typing import Optional, Union, List
from bs4 import BeautifulSoup
from bs4.element import Tag


def find_child(element: Optional[Union[BeautifulSoup, Tag]],
               tag: str, index: int = 0, from_root: bool = False, **kwargs) -> Optional[Tag]:
    """Shortcut to find a child node with a given tag
    :param element:     the parent element to start searching from
    :param tag:         the name of the HTML tag to search for
    :param index:       in case multiple elements match, specify which should be chosen
    :param from_root:   find the element as a child of the root node instead of anywhere
                        in the document
    """
    # Element doesn't exist, so neither do the children
    if element is None:
        return None

    # Doesn't match only text, so emmet syntax was used
    if tag and re.match(r"^[a-zA-Z]+$", tag) is None:
        return _find_emmet(element, tag, from_root)

    # Tags should be lowercase
    tag = tag.lower()

    # No index specified, first child requested
    if index == 0:
        return element.find(tag, recursive=not from_root, **kwargs)

    all_children = element.find_all(tag, recursive=not from_root, **kwargs)

    # No children found
    if len(all_children) == 0:
        return None
    else:
        # Not enough children found (index out of range)
        # Default to first
        if index >= len(all_children):
            index = 0

        return all_children[index]


def _find_emmet(element: Optional[Union[BeautifulSoup, Tag]], path: str, from_root: bool = False) -> Optional[Tag]:
    """Find an element using emmet syntax"""
    if element is None:
        return None

    # Tag must always be in the beginning, otherwise we can't parse it out
    tag_regex = re.compile(r"^[a-zA-Z]+")
    id_regex = re.compile(r"#([a-zA-Z0-9_-]+)")
    index_regex = re.compile(r"\[([0-9]+)\]$")

    # Cannot start with a digit, two hyphens or a hyphen followed by a number.
    illegal_class_regex = re.compile(r"\.([0-9]|--|-[0-9])")
    class_regex = re.compile(r"\.([a-zA-z0-9_-]+)")

    path_stack: List[str] = path.split(">")

    current_element = element

    # Keep going until path is empty
    while path_stack:
        if current_element is None:
            return None

        # Take first entry from stack
        current_entry = path_stack.pop(0)

        # Illegal class name
        if illegal_class_regex.search(current_entry) is not None:
            # TODO raise exception to show an error message to the teacher?
            return None

        tag = tag_regex.search(current_entry)
        id = id_regex.search(current_entry)
        class_name = class_regex.search(current_entry)
        index = index_regex.search(current_entry)

        # Parse matches out
        # Tag doesn't use a capture group so take match 0 instead of 1,
        # the others need to use 1
        if tag is not None:
            tag = tag.group(0)

        if id is not None:
            id = id.group(1)

        if class_name is not None:
            class_name = class_name.group(1)

        # Parse index out
        if index is not None:
            index = int(index.group(1))
        else:
            index = 0

        # Apply filters & find a matching element
        # None is ignored by bs4 by default which makes this a lot cleaner
        matches = current_element.find_all(name=tag, id=id, class_=class_name)

        # No matches found, or not enough
        if not matches or len(matches) <= index:
            return None

        current_element = matches[index]

    return current_element


def compare_content(first: str, second: str) -> bool:
    """Check if content of two strings is equal, ignoring all whitespace"""
    # Remove all leading/trailing whitespace, and replace all other whitespace by single spaces
    # in both argument and content
    element_text = first.strip()
    arg_text = second.strip()

    element_text = re.sub(r"\s+", " ", element_text, re.MULTILINE)
    arg_text = re.sub(r"\s+", " ", arg_text, re.MULTILINE)

    return element_text == arg_text
