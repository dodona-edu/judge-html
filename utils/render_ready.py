from ntpath import basename
from typing import TYPE_CHECKING, cast

import bs4

from validators.css_validator import Rule, Rules

if TYPE_CHECKING:
    from bs4.element import Tag


def prep_render(html_content: str, render_css: bool) -> tuple[str, str]:
    """prepares the html for rendering:
    a body and a style tag must be present, if not returns the input html
    if both are present:
    * wraps the contents of body in a div with id='solution_rendering'
    * prepends '#solution_rendering ' to every css rule, so that every rule applies to descendants of the div"""
    title_str = ""
    try:
        soup = bs4.BeautifulSoup(html_content, "html.parser")

        # remove title
        # find() and find_all() are typed as yielding PageElement, which covers
        # NavigableString too. Searching by tag name only ever matches Tags.
        title = cast("Tag | None", soup.find("title"))
        if title is not None:
            title_str = title.text
            title.decompose()
        else:
            title_str = ""

        # wrap div around the contents of body
        div = soup.new_tag("div", attrs={"id": "solution_rendering"})

        body = cast("Tag | None", soup.find("body"))

        if body is not None:
            body.wrap(div)
            attrs = body.attrs
            body.unwrap()
            # bs4 types new_tag's attrs as Mapping[str, str], but Tag.attrs holds the
            # multi-valued ones (class, rel, ...) as lists, and new_tag takes those fine
            div.wrap(soup.new_tag("body", attrs=cast("dict[str, str]", attrs)))

        # Change all img src's to refer to the /media directory
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

        style = cast("Tag | None", soup.find("style"))
        if style is not None:
            # Css should not be rendered, remove it from the tree
            if not render_css:
                style.decompose()
            else:
                # edit the css-rules
                # An empty <style></style> gives string None, and Rules() then raises a
                # TypeError. The except below catches it and returns the html unchanged,
                # so keep it that way rather than growing a branch for it here
                rs = Rules(cast("str", style.string))
                x: Rule
                for x in rs.rules:
                    x.selector_str = f"#solution_rendering {x.selector_str}"

                new_style = ""
                for r in rs.rules:
                    new_style += (
                        f"{r.selector_str}{{{r.name}:{r.value_str}{'!important' if r.important else ''};}}\n   "
                    )

                style.string = new_style

        return title_str, str(soup.prettify())
    except Exception:
        return title_str, html_content
