from dodona.translator import Translator
from utils.file_loaders import html_loader as _html_loader
from os import path

# Location of this test file
from validators.checks import TestSuite, Check, ChecklistItem, Checks

basepath = path.dirname(__file__)

# Location of html files
html_dir = path.abspath(path.join(basepath, "../tests/html_files"))


def html_loader(file: str) -> str:
    return _html_loader(path.join(html_dir, file))


class UnitTestSuite(TestSuite):
    """TestSuite with extra utility stuff for unittests"""

    def __init__(self, file: str, **kwargs):
        """
        :param file: The HTML file to run the test against. The file extension (.html) can be left out.
        """
        super().__init__(name="TEST", content=html_loader(file), **kwargs)
        self.translator = Translator(Translator.Language.EN)

    def check(self, c: Check) -> bool:
        return c.callback(self._bs)

    def checklist_item(self, c: ChecklistItem) -> bool:
        return c.evaluate(self._bs, self.translator)

    def item(self, *args: Checks) -> ChecklistItem:
        return ChecklistItem("TEST", *args)
