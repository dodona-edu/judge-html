import re
from typing import Any, TypeGuard, cast

from bs4 import BeautifulSoup
from bs4.element import Comment, Tag


def match_emmet(tag: str | None) -> TypeGuard[str]:
    """Check whether a tag is written in emmet syntax instead of a plain tag name

    A TypeGuard rather than a bool: emmet syntax is always a string, so callers that
    branch on this can pass the tag straight into find_emmet.
    """
    return tag is not None and tag != "" and re.match(r"^[a-zA-Z0-9]+$", tag) is None


def find_child(
    element: BeautifulSoup | Tag | None, tag: str | None, index: int = 0, from_root: bool = False, **kwargs
) -> Tag | None:
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
    if match_emmet(tag):
        try:
            emmet_match = find_emmet(element, tag, index, from_root, match_multiple=False, **kwargs)
        except IndexError:
            # IndexError can happen when negative indexes are supplied which are too
            # small to fit in the list, and this is too ugly to check so just catch it here
            return None

        # Nothing found
        if emmet_match is None or not emmet_match:
            return None

        # Index is already applied in the find_emmet method so safely take the first element
        return emmet_match[0]

    # Tags should be lowercase
    if tag is not None:
        tag = tag.lower()

    # No index specified, first child requested
    if index == 0:
        # find() and find_all() are typed as yielding PageElement, which covers
        # NavigableString too. Searching by tag name only ever matches Tags.
        return cast("Tag | None", element.find(tag, recursive=not from_root, **kwargs))

    all_children = cast("list[Tag]", element.find_all(tag, recursive=not from_root, **kwargs))

    # No children found
    if len(all_children) == 0:
        return None
    # Not enough children found (index out of range)
    if index >= len(all_children):
        return None

    return all_children[index]


def find_emmet(
    element: BeautifulSoup | Tag | None,
    path: str,
    ind: int,
    from_root: bool = False,
    match_multiple: bool = False,
    **kwargs,
) -> list[Tag] | None:
    """Find an element using emmet syntax"""
    if element is None:
        return None

    # Tag must always be in the beginning, otherwise we can't parse it out
    tag_regex = re.compile(r"^[a-zA-Z0-9]+")
    id_regex = re.compile(r"#([a-zA-Z0-9_-]+)")
    index_regex = re.compile(r"\[(-?)([0-9]+)\]$")

    # Cannot start with a digit, two hyphens or a hyphen followed by a number.
    illegal_class_regex = re.compile(r"\.([0-9]|--|-[0-9])")
    class_regex = re.compile(r"\.([a-zA-Z0-9_-]+)")

    path_stack: list[str] = path.split(">")

    # the from_root should only be done once, afterwards it's always True to support this syntax
    moved = False
    current_element: BeautifulSoup | Tag | None = element

    # Keep going until path is empty
    while path_stack:
        if current_element is None:
            return None

        # Take first entry from stack
        current_entry = path_stack.pop(0)

        # Element is empty, so return all children
        if not current_entry:
            # .children is a generator that also yields NavigableStrings, but every other
            # branch (and every caller) expects a list of Tags, so match that here too
            return [child for child in current_element.children if isinstance(child, Tag)]

        # Illegal class name
        if illegal_class_regex.search(current_entry) is not None:
            return None

        tag = tag_regex.search(current_entry)
        id_match = id_regex.search(current_entry)
        # Multiple class names allowed
        class_names = class_regex.findall(current_entry)
        index = index_regex.search(current_entry)

        # Kwargs to filter on. find_all() takes attribute filters of assorted types
        # through **kwargs, so this can't be narrowed to dict[str, str]
        filter_kwargs: dict[str, Any] = {}

        # Parse matches out
        # Tag doesn't use a capture group so take match 0 instead of 1,
        # the others need to use 1
        if tag is not None:
            filter_kwargs["name"] = tag.group(0).lower()

        if id_match is not None:
            filter_kwargs["id"] = id_match.group(1)

        if class_names:
            filter_kwargs["class"] = " ".join(class_names)

        # Parse index out
        # First match is an optional -
        # Second match is the number
        if index is not None:
            sign = 1
            if index.group(1):
                sign = -1

            index = int(index.group(2)) * sign
        else:
            # Take the first arg, but if an index was specified as a parameter
            # and this is the last part of the path, then use that index
            index = 0 if path_stack else ind

        # Apply kwargs to the end of the path only,
        # and the path takes priority so it overrides the others
        if not path_stack:
            filter_kwargs = kwargs | filter_kwargs

        # Apply filters & find a matching element
        # Only use from_root if we haven't moved at least once, otherwise never go recursive
        # find_all() is typed as yielding PageElement, but filtering on a name only matches Tags
        matches = cast(
            "list[Tag]", current_element.find_all(recursive=not from_root if not moved else False, **filter_kwargs)
        )

        # No matches found, or not enough
        if not matches or len(matches) <= index:
            return None

        # End of path reached
        if not path_stack:
            # Return all matches
            if match_multiple:
                return matches

            # Only return the match at the specific index
            return [matches[index]]

        # Set current node to the one at the requested index & keep going
        current_element = matches[index]
        moved = True

    # Unreachable: path.split(">") always yields at least one entry, so the loop runs at
    # least once, and every path through its body returns
    return None


def compare_content(first: str, second: str, case_insensitive: bool = False) -> bool:
    """Check if content of two strings is equal, ignoring all whitespace"""
    # Remove all leading/trailing whitespace, and replace all other whitespace by single spaces
    # in both argument and content
    element_text = first.strip()
    arg_text = second.strip()

    element_text = re.sub(r"\s+", " ", element_text)
    arg_text = re.sub(r"\s+", " ", arg_text)

    if case_insensitive:
        element_text = element_text.lower()
        arg_text = arg_text.lower()

    return element_text == arg_text


def contains_comment(element: BeautifulSoup | Tag | None, comment: str | None = None) -> bool:
    """Check if an element contains a comment, optionally with a specific value"""
    if element is None:
        return False

    # The filter only lets Comments through, and a Comment is a str subclass
    comments = cast("list[Comment]", element.find_all(string=lambda text: isinstance(text, Comment)))

    # No comments found
    if not comments:
        return False

    # No specific value requested
    if comment is None:
        return True

    # Check if at least one matches
    # Ignore whitespace again
    return any(compare_content(c, comment) for c in comments)
