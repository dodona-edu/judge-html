from bs4 import BeautifulSoup

from utils.emmet import emmet_to_check
import unittest

from validators.checks import TestSuite


def do(emmet, document) -> bool:
    return emmet_to_check(
        emmet,
        TestSuite("My test suite", document)
    ).callback(BeautifulSoup(document, "html.parser"))


class TestCompareContent(unittest.TestCase):

    def test_child(self):
        doc = """
            <div>
                <ul>
                    <li></li>
                </ul>
            </div>
        """
        self.assertTrue(do("div>ul>li", doc))

    def test_sibling(self):
        doc = """
            <div></div>
            <p></p>
            <blockquote></blockquote>
        """
        self.assertTrue(do("div+p+blockquote", doc))

    def test_climb_up(self):
        doc = """
            <div></div>
            <div>
                <p><span></span><em></em></p>
            </div>
        """
        self.assertTrue(do("div+div>p>span+em", doc))
        doc = """
            <div></div>
            <div>
                <p><span></span><em></em></p>
                <blockquote></blockquote>
            </div>
        """
        self.assertTrue(do("div+div>p>span+em^blockquote", doc))
        doc = """
            <div></div>
            <div>
                <p><span></span><em></em></p>
            </div>
            <blockquote></blockquote>
        """
        self.assertTrue(do("div+div>p>span+em^^^blockquote", doc), "I fail")

    def test_multiplication(self):
        doc = """
            <ul>
                <li></li>
                <li></li>
                <li></li>
                <li></li>
                <li></li>
            </ul>
        """
        self.assertTrue(do("ul>li*5", doc))

    def test_grouping(self):
        doc = """
            <div>
                <header>
                    <ul>
                        <li><a href=""></a></li>
                        <li><a href=""></a></li>
                    </ul>
                </header>
                <footer>
                    <p></p>
                </footer>
            </div>
        """
        self.assertTrue(do("div>(header>ul>li*2>a)+footer>p", doc))
        doc = """
            <div>
                <dl>
                    <dt></dt>
                    <dd></dd>
                    <dt></dt>
                    <dd></dd>
                    <dt></dt>
                    <dd></dd>
                </dl>
            </div>
            <footer>
                <p></p>
            </footer>
        """
        self.assertTrue(do("(div>dl>(dt+dd)*3)+footer>p", doc))

    def test_id_and_class(self):
        doc = """
            <div id="header"></div>
            <div class="page"></div>
            <div id="footer" class="class1 class2 class3"></div>
        """
        self.assertTrue(do("div#header+div.page+div#footer.class1.class2.class3", doc))

    def test_custom_attributes(self):
        doc = """
            <td title="Hello world!" colspan="3"></td>
        """
        self.assertTrue(do("td[title='Hello world!' colspan=3]", doc))

    def test_text(self):
        doc = """
            <a href="">Click me</a>
        """
        self.assertTrue(do("a{Click me}", doc))
        doc = """
            <a href="">click</a><b>here</b>
        """
        self.assertTrue(do("a{click}+b{here}", doc))
        doc = """
            <a href="">click<b>here</b></a>
        """
        self.assertTrue(do("a>{click}+b{here}", doc))
        doc = """
            <p>Click <a href="">here</a> to continue</p>
        """
        self.assertTrue(do("p>{Click }+a{here}+{ to continue}", doc))

    def test_table_rows(self):
        doc = """
            <body>
                <table>
                    <tr>
                        <td>test</td>
                    </tr>
                </table>
            </body>
        """
        self.assertTrue(do("body>table>tr", doc))
        self.assertFalse(do("body>table>tr*2", doc))
