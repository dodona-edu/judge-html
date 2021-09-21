from typing import Optional, Union
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
