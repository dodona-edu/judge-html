import unittest
from unittest import mock

from bs4 import BeautifulSoup, Tag

from utils.render_ready import prep_render

ONE_STYLE = (
    "<html><head><title>My title</title><style>p{color:red;} h1,h2{margin:0 !important;}</style></head>"
    "<body class='a b'><h1>Hi</h1><p>text</p></body></html>"
)

TWO_STYLES = (
    "<html><head><style>p{color:red;}</style></head>"
    "<body><p>x</p></body>"
    "<head><style>b{color:blue;}</style></head></html>"
)


def scoped(selectors: str, body_attrs: str = "") -> str:
    html = f"<html><head><style>{selectors}{{color:red;}}</style></head><body{body_attrs}><p>x</p></body></html>"
    return prep_render(html, True)[1]


class TestPrepRender(unittest.TestCase):
    def test_style_rules_are_scoped_to_preview_container(self):
        title, html = prep_render(ONE_STYLE, True)
        self.assertEqual("My title", title)
        self.assertIn("#solution_rendering p{color:red;}", html)
        self.assertIn("#solution_rendering h1{margin:0!important;}", html)
        self.assertIn("#solution_rendering h2{margin:0!important;}", html)

    def test_body_contents_are_wrapped_and_body_attributes_kept(self):
        _, html = prep_render(ONE_STYLE, True)
        self.assertIn('<body class="a b">', html)
        self.assertIn('<div class="a b" id="solution_rendering">', html)
        self.assertNotIn("<title>", html)

    def test_body_with_many_children_is_wrapped_in_order(self):
        count = 2000
        html = "<html><body class='a'>" + "".join(f"<p>{i}</p>" for i in range(count)) + "</body></html>"
        _, out = prep_render(html, True)
        soup = BeautifulSoup(out, "html.parser")
        body = soup.find("body")
        assert isinstance(body, Tag)
        wrapper = body.find("div", id="solution_rendering")
        self.assertEqual([wrapper], body.find_all(True, recursive=False))
        assert isinstance(wrapper, Tag)
        self.assertEqual(
            [str(i) for i in range(count)], [p.get_text(strip=True) for p in wrapper.find_all("p", recursive=False)]
        )

    def test_style_removed_without_render_css(self):
        title, html = prep_render(ONE_STYLE, False)
        self.assertEqual("My title", title)
        self.assertNotIn("<style>", html)
        self.assertNotIn("color:red", html)

    def test_page_without_style(self):
        title, html = prep_render("<html><head><title>T</title></head><body><p>x</p></body></html>", True)
        self.assertEqual("T", title)
        self.assertNotIn("<style>", html)
        self.assertIn('<div id="solution_rendering">', html)

    def test_relative_image_sources_point_to_media(self):
        html = "<html><body><img src='img/a.png'><img src='C:\\dir\\b.png'><img src='c.png'></body></html>"
        _, out = prep_render(html, True)
        self.assertIn('src="media/a.png"', out)
        self.assertIn('src="media/b.png"', out)
        self.assertIn('src="media/c.png"', out)

    def test_absolute_image_sources_are_left_as_they_are(self):
        html = (
            "<html><body><img src='http://example.com/a.png'><img src='https://example.com/b.png'>"
            "<img src='www.example.com/c.png'></body></html>"
        )
        _, out = prep_render(html, True)
        self.assertIn('src="http://example.com/a.png"', out)
        self.assertIn('src="https://example.com/b.png"', out)
        self.assertIn('src="www.example.com/c.png"', out)
        self.assertNotIn("media/", out)

    def test_every_style_block_is_scoped(self):
        _, html = prep_render(TWO_STYLES, True)
        self.assertIn("#solution_rendering p{color:red;}", html)
        self.assertIn("#solution_rendering b{color:blue;}", html)
        self.assertNotIn("\n   b{color:blue;}", html)

    def test_non_empty_style_after_empty_style_is_scoped(self):
        html = "<html><head><style></style><style>p{color:red;}</style></head><body><p>x</p></body></html>"
        _, out = prep_render(html, True)
        self.assertIn("#solution_rendering p{color:red;}", out)

    def test_every_style_block_removed_without_render_css(self):
        _, html = prep_render(TWO_STYLES, False)
        self.assertNotIn("<style>", html)

    def test_style_block_that_cannot_be_parsed_is_dropped_and_preview_still_wrapped(self):
        html = (
            "<html><head><style>p{color:red;} }</style><style>b{color:blue;}</style></head><body><p>x</p></body></html>"
        )
        _, out = prep_render(html, True)
        self.assertNotIn("color:red", out)
        self.assertIn("#solution_rendering b{color:blue;}", out)
        self.assertIn('<div id="solution_rendering">', out)

    def test_failed_preparation_returns_title_and_empty_preview(self):
        with mock.patch("utils.render_ready.bs4.BeautifulSoup", side_effect=RuntimeError):
            title, html = prep_render(ONE_STYLE, True)
        self.assertEqual("", title)
        self.assertEqual("", html)


class TestPageSelectors(unittest.TestCase):
    def assert_scoped(self, selector: str, expected: str):
        self.assertIn(f"{expected}{{color:red;}}", scoped(selector))

    def test_body_selects_the_preview_itself(self):
        self.assert_scoped("body", "#solution_rendering")

    def test_body_descendant_and_child(self):
        self.assert_scoped("body p", "#solution_rendering p")
        self.assert_scoped("body > p", "#solution_rendering > p")

    def test_html_and_root_select_the_preview_itself(self):
        self.assert_scoped("html", "#solution_rendering")
        self.assert_scoped(":root", "#solution_rendering")
        self.assert_scoped("html body", "#solution_rendering")
        self.assert_scoped("html > body", "#solution_rendering")
        self.assert_scoped(":root body", "#solution_rendering")

    def test_html_body_descendant(self):
        self.assert_scoped("html body p", "#solution_rendering p")

    def test_compound_on_body_keeps_its_parts(self):
        self.assert_scoped("body.dark", "#solution_rendering.dark")
        self.assert_scoped("body:hover", "#solution_rendering:hover")

    def test_body_class_is_also_on_the_preview_container(self):
        out = scoped("body.dark", " class='dark wide'")
        self.assertIn('<div class="dark wide" id="solution_rendering">', out)
        self.assertIn('<body class="dark wide">', out)

    def test_selector_list_with_body(self):
        out = scoped("h1, body")
        self.assertIn("#solution_rendering h1{color:red;}", out)
        self.assertIn("#solution_rendering{color:red;}", out)

    def test_body_selector_is_case_insensitive(self):
        self.assert_scoped("BODY", "#solution_rendering")
        self.assert_scoped("HTML P", "#solution_rendering P")

    def test_non_leading_body_keeps_the_prefix(self):
        self.assert_scoped(".x body", "#solution_rendering .x body")

    def test_other_selectors_are_prefixed(self):
        self.assert_scoped("*", "#solution_rendering *")
        self.assert_scoped("p.x", "#solution_rendering p.x")
        self.assert_scoped("bodyguard", "#solution_rendering bodyguard")

    def test_issue_309_page_gets_a_selector_that_matches(self):
        html = (
            '<!DOCTYPE html><html lang="en"><head><title>x</title><meta charset="UTF-8">'
            "<style>p { color: red }</style></head><body><p>hello</p></body>"
            "<head><style>body { background: yellow }</style></head></html>"
        )
        _, out = prep_render(html, True)
        self.assertIn("#solution_rendering{background:yellow;}", out)
        self.assertIn("#solution_rendering p{color:red;}", out)
