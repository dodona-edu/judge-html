import unittest

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
        self.assertIn('<div id="solution_rendering">', html)
        self.assertNotIn("<title>", html)

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

    @unittest.expectedFailure
    def test_every_style_block_is_scoped(self):
        # intended: the rules of both style blocks are scoped, no unscoped rule remains
        _, html = prep_render(TWO_STYLES, True)
        self.assertIn("#solution_rendering p{color:red;}", html)
        self.assertIn("#solution_rendering b{color:blue;}", html)
        self.assertNotIn("\n   b{color:blue;}", html)

    @unittest.expectedFailure
    def test_non_empty_style_after_empty_style_is_scoped(self):
        # intended: an empty first style does not stop the next one from being scoped
        html = "<html><head><style></style><style>p{color:red;}</style></head><body><p>x</p></body></html>"
        _, out = prep_render(html, True)
        self.assertIn("#solution_rendering p{color:red;}", out)

    @unittest.expectedFailure
    def test_every_style_block_removed_without_render_css(self):
        # intended: with render_css=False no style block is left, not only the first
        _, html = prep_render(TWO_STYLES, False)
        self.assertNotIn("<style>", html)
