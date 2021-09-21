import bs4
from bs4 import Tag

from validators.css_validator import Rules, Rule


def prep_render(html_content: str, render_css: bool) -> (str, str):
    """prepares the html for rendering:
        a body and a style tag must be present, if not returns the input html
        if both are present:
        * wraps the contents of body in a div with id='solution_rendering'
        * prepends '#solution_rendering ' to every css rule, so that every rule applies to descendants of the div"""
    title_str = ''
    try:
        soup = bs4.BeautifulSoup(html_content, "html.parser")

        # remove title
        title: Tag = soup.find("title")
        if title is not None:
            title_str = title.text
            title.contents = []  # bc unwrapping just leaves the content behind
            title.unwrap()
        else:
            title_str = ''

        # wrap div around the contents of body
        div = soup.new_tag("div", attrs={"id": "solution_rendering"})

        body = soup.find("body")
        body.wrap(div)
        attrs = body.attrs
        body.unwrap()
        div.wrap(soup.new_tag("body", attrs=attrs))

        style = soup.find("style")
        if style is not None:
            # Css should not be rendered, remove it from the tree
            if not render_css:
                style.decompose()
            else:
                # edit the css-rules
                rs = Rules(style.string)
                x: Rule
                for x in rs.rules:
                    x.selector_str = f"#solution_rendering {x.selector_str}"

                new_style = ""
                for r in rs.rules:
                    new_style += f"{r.selector_str}" + "{" + f"{r.name}:{r.value_str}{'!important' if r.important else ''}" + ";}\n   "

                style.string = new_style

        return title_str, str(soup.prettify())
    except Exception:
        return title_str, html_content
