from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Concatenate, Protocol, cast

if TYPE_CHECKING:
    from collections.abc import Callable

    from bs4 import BeautifulSoup
    from bs4.element import Tag

    from validators.css_validator import CssValidator


# Deliberately left without a `-> Check` return annotation. validators/checks.pyi sits next
# to checks.py, so an annotation here resolves Check to the stub, and ty then reads that as a
# different type from the class checks.py defines. checks.py returns fail() itself, and the
# annotation would turn that into an error about two types with the same name.
def fail():
    """Return a Check that always fails"""
    # Local import to avoid circular dependencies
    from validators.checks import Check  # noqa: PLC0415

    def _inner(_: BeautifulSoup) -> bool:
        return False

    return Check(_inner)


class _HasElement(Protocol):
    """The part of Element that html_check needs to see

    Spelled as a protocol instead of importing Element, because validators.checks
    imports this module and the type would be a circular reference.
    """

    _element: Tag | None


class _HasCssValidator(_HasElement, Protocol):
    """The part of Element that css_check needs to see"""

    _css_validator: CssValidator | None


def html_check[S: _HasElement, **P, R](
    func: Callable[Concatenate[S, P], R],
) -> Callable[Concatenate[S, P], R]:
    """Decorator that checks if an HTML element is not None"""

    @functools.wraps(func)
    def wrapper(self: S, *args: P.args, **kwargs: P.kwargs) -> R:
        if self._element is None:
            return cast("R", fail())

        return func(self, *args, **kwargs)

    return wrapper


def css_check[S: _HasCssValidator, **P, R](
    func: Callable[Concatenate[S, P], R],
) -> Callable[Concatenate[S, P], R]:
    """Decorator that checks if an element's HTML tag and CSS validator are not None"""

    @functools.wraps(func)
    def wrapper(self: S, *args: P.args, **kwargs: P.kwargs) -> R:
        if self._element is None or self._css_validator is None:
            return cast("R", fail())

        return func(self, *args, **kwargs)

    return wrapper
