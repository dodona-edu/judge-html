from ntpath import basename
from typing import TYPE_CHECKING, cast

import bs4
import tinycss2
from tinycss2.ast import IdentToken, LiteralToken, Node, WhitespaceToken

from validators.css_validator import Rule, Rules

if TYPE_CHECKING:
    from bs4.element import Tag


PREVIEW_ROOT = "#solution_rendering"


def _root_length(tokens: list[Node]) -> int:
    """number of leading tokens that select the page itself: html, body or :root"""
    if tokens and isinstance(tokens[0], IdentToken) and tokens[0].lower_value in ("html", "body"):
        return 1
    if (
        len(tokens) > 1
        and isinstance(tokens[0], LiteralToken)
        and tokens[0].value == ":"
        and isinstance(tokens[1], IdentToken)
        and tokens[1].lower_value == "root"
    ):
        return 2
    return 0


def scope_selector(selector: list[Node]) -> str:
    """scopes a selector to the preview: a leading html, body or :root selects the preview container itself,
    anything else selects its descendants"""
    rest = selector
    separator = " "
    while length := _root_length(rest):
        rest = rest[length:]
        separator = ""
        if rest and isinstance(rest[0], WhitespaceToken):
            rest = rest[1:]
            separator = " "
        if rest and isinstance(rest[0], LiteralToken) and rest[0].value == ">":
            after = rest[2:] if len(rest) > 1 and isinstance(rest[1], WhitespaceToken) else rest[1:]
            if _root_length(after):
                rest = after
                separator = ""
    return PREVIEW_ROOT + (separator if rest else "") + tinycss2.serialize(rest)


def prep_render(html_content: str, render_css: bool) -> tuple[str, str]:
    """prepares the html for rendering, returns the title and the preview html:
    if preparing fails, the preview is empty rather than the unprepared input
    * wraps the contents of body in a div with id='solution_rendering'
    * scopes every css rule to the div: a leading html, body or :root selects the div, anything else its descendants"""
    title_str = ""
    try:
        soup = bs4.BeautifulSoup(html_content, "html.parser")

        # remove title
        title = soup.find("title")
        if title is not None:
            title_str = title.text
            title.decompose()
        else:
            title_str = ""

        # wrap div around the contents of body
        div = soup.new_tag("div", attrs={"id": "solution_rendering"})

        body = soup.find("body")

        if body is not None:
            body.wrap(div)
            attrs = body.attrs
            body.unwrap()
            # body.dark has to match the div, which stands in for the body
            if "class" in attrs:
                div["class"] = attrs["class"]
            # bs4 types new_tag's attrs as Mapping[str, str], but Tag.attrs holds the
            # multi-valued ones (class, rel, ...) as lists, and new_tag takes those fine
            div.wrap(soup.new_tag("body", attrs=cast("dict[str, str]", attrs)))

        # Change all img src's to refer to the /media directory
        # find_all() is typed as yielding PageElement, which covers NavigableString
        # too. Searching by tag name only ever matches Tags.
        for img in cast("list[Tag]", soup.find_all("img", src=True)):
            # src=True in the search above already ruled out a missing attribute, and
            # src is not one of the attributes bs4 splits into a list
            src = cast("str", img.get("src"))

            # Ignore internet URLs, don't use some fancy package for this, this is good enough
            if not src.startswith(
                (
                    "http",
                    "www",
                )
            ):
                # Use ntpath.basename instead of os.path.basename
                # Because os.path can't handle Windows filepaths!
                filename = basename(src)

                img["src"] = f"media/{filename}"

        for style in soup.find_all("style"):
            # Css should not be rendered, remove it from the tree
            if not render_css:
                style.decompose()
            # An empty <style></style> has no string and nothing to scope
            elif style.string:
                try:
                    # edit the css-rules
                    rs = Rules(cast("str", style.string))
                    x: Rule
                    for x in rs.rules:
                        x.selector_str = scope_selector(x.selector)

                    new_style = ""
                    for r in rs.rules:
                        new_style += (
                            f"{r.selector_str}{{{r.name}:{r.value_str}{'!important' if r.important else ''};}}\n   "
                        )

                    style.string = new_style
                except Exception:
                    # A block that can't be scoped is dropped rather than shown unscoped
                    style.decompose()

        return title_str, str(soup.prettify())
    except Exception:
        # never fall back to the raw input: its styles are not scoped to the preview
        return title_str, ""
