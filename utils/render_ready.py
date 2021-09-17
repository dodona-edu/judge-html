import bs4
from bs4 import Tag, PageElement


def prep_render(html_content: str) -> str:
    soup = bs4.BeautifulSoup(html_content, "html.parser")

    # wrap div around the contents of body
    body = soup.find("body")
    div = soup.new_tag("div", attrs={"id": "solution_rendering"})
    body.wrap(div)
    attrs = body.attrs
    body.unwrap()
    div.wrap(soup.new_tag("body", attrs=attrs))

    # edit the css-rules
    style = soup.find("style")

    return str(soup.prettify())



html = """
<!DOCTYPE html>
<html>
  <head>
<style>
    #solution_rendering body {
        color:red;
    }
    #solution_rendering div {
        color: green;
        background_color: green;
    }
</style>
  </head>
  <body>
      AAAAA
  </body>
</html>
"""

# print(prep_render(html))
