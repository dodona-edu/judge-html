from pathlib import Path

from dodona.translator import Translator
from utils.file_loaders import html_loader as _html_loader

# Location of this test file
from validators.checks import Check, ChecklistItem, Checks, TestSuite

basepath = Path(__file__).parent

# Location of html files
html_dir = (basepath / "../tests/html_files").resolve()


def html_loader(file: str) -> str:
    return _html_loader(str(html_dir / file))


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
        # evaluate() wants the language abbreviation, the same one TestSuite.evaluate
        # derives from its translator, not the translator itself
        return c.evaluate(self._bs, self.translator.language.name.lower())

    def item(self, *args: Checks) -> ChecklistItem:
        return ChecklistItem("TEST", *args)
