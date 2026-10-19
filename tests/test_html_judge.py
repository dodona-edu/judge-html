import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

JUDGE_DIR = Path(__file__).resolve().parent.parent

LATIN1_LOCALES = ("en_US.ISO8859-1", "en_US.ISO-8859-1", "de_DE.ISO8859-1")

CHECKLIST_EVALUATOR = """
from validators import checks


def create_suites(content: str) -> list[checks.TestSuite]:
    suite = checks.HtmlSuite(content)
    suite.make_item("The page has a title", suite.element("head").get_child("title").exists())
    suite.make_item("The page has a heading", suite.element("body").get_child("h1").exists())
    return [suite]
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>{title}</title></head>
<body>{body}</body>
</html>
"""

NON_ASCII = "Café Ελληνικά 日本"


def page(title: str = "Home", body: str = "<h1>Hello</h1>") -> str:
    return PAGE.format(title=title, body=body)


def parse_commands(stdout: str) -> list[dict]:
    """Decode the stream of concatenated JSON objects the judge prints"""
    decoder = json.JSONDecoder()
    commands = []
    pos = 0
    while pos < len(stdout):
        if stdout[pos].isspace():
            pos += 1
            continue
        command, pos = decoder.raw_decode(stdout, pos)
        commands.append(command)
    return commands


def find_locale() -> str | None:
    """Return the first Latin-1 locale this machine has, probed in a subprocess so the test run keeps its own"""
    for name in LATIN1_LOCALES:
        probe = f"import locale; locale.setlocale(locale.LC_ALL, {name!r})"
        if subprocess.run([sys.executable, "-c", probe], capture_output=True, check=False).returncode == 0:  # noqa: S603
            return name
    return None


LATIN1_LOCALE = find_locale()


class JudgeRun:
    """The parsed output of one run of html_judge.py"""

    def __init__(self, commands: list[dict]):
        self.commands = commands

    @property
    def status(self) -> str:
        return next(c for c in self.commands if c["command"] == "close-judgement")["status"]["enum"]

    @property
    def accepted(self) -> bool | None:
        return next(c for c in self.commands if c["command"] == "close-judgement").get("accepted")

    def testcases(self) -> dict[str, bool]:
        """Map each testcase description to whether it was accepted"""
        result = {}
        description = ""
        for c in self.commands:
            if c["command"] == "start-testcase":
                description = c["description"]
            elif c["command"] == "close-testcase":
                result[description] = c["accepted"]
        return result

    def messages(self) -> list[dict]:
        return [c["message"] for c in self.commands if c["command"] == "append-message"]


class HtmlJudgeEndToEndTest(unittest.TestCase):
    """Runs html_judge.py as Dodona does: run config on stdin, an exercise directory, feedback on stdout"""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.resources = root / "evaluation"
        self.workdir = root / "workdir"
        self.resources.mkdir()
        self.workdir.mkdir()
        self.source = self.workdir / "submission.html"

    def run_judge(
        self,
        submission: str,
        evaluator: str | None = None,
        solution: str | None = None,
        env: dict[str, str] | None = None,
        natural_language: str = "en",
    ) -> JudgeRun:
        self.source.write_text(submission, encoding="utf-8")
        if evaluator is not None:
            (self.resources / "evaluator.py").write_text(evaluator, encoding="utf-8")
        if solution is not None:
            (self.resources / "solution.html").write_text(solution, encoding="utf-8")

        config = {
            "memory_limit": 100_000_000,
            "time_limit": 10,
            "programming_language": "html",
            "natural_language": natural_language,
            "resources": str(self.resources),
            "source": str(self.source),
            "judge": str(JUDGE_DIR),
            "workdir": str(self.workdir),
        }
        # json.dumps escapes non-ASCII, so the config reads the same under any locale
        result = subprocess.run(  # noqa: S603
            [sys.executable, str(JUDGE_DIR / "html_judge.py")],
            input=json.dumps(config),
            capture_output=True,
            text=True,
            cwd=self.workdir,
            env={**os.environ, **(env or {})},
            check=False,
            encoding="utf-8",
        )
        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        return JudgeRun(parse_commands(result.stdout))

    def test_checklist_correct_submission(self):
        run = self.run_judge(page(), evaluator=CHECKLIST_EVALUATOR)

        self.assertEqual("correct answer", run.status)
        self.assertEqual(
            {"The HTML is valid.": True, "The page has a title": True, "The page has a heading": True},
            run.testcases(),
        )

    def test_checklist_one_failing_item(self):
        run = self.run_judge(page(body="<p>No heading</p>"), evaluator=CHECKLIST_EVALUATOR)

        self.assertEqual("wrong", run.status)
        self.assertEqual(
            {"The HTML is valid.": True, "The page has a title": True, "The page has a heading": False},
            run.testcases(),
        )

    def test_comparison_matching_submission(self):
        run = self.run_judge(page(), solution=page())

        self.assertEqual("correct answer", run.status)
        self.assertTrue(run.testcases()["The submission resembles the solution."])

    def test_comparison_non_matching_submission(self):
        run = self.run_judge(page(body="<p>Other</p>"), solution=page())

        self.assertEqual("wrong", run.status)
        self.assertFalse(run.testcases()["The submission resembles the solution."])

    # RULE-016 (owner's note): unparseable submission CSS fails "The CSS is valid." and does not skip the comparison
    @unittest.expectedFailure
    def test_comparison_unparseable_submission_css_fails_css_item(self):
        solution = (
            page().replace("</head>", "<style>p { color: red }</style></head>").replace("<h1>Hello</h1>", "<p>x</p>")
        )
        submission = solution.replace("p { color: red }", "p { color: blue } p..x { margin: 0 }")
        run = self.run_judge(submission, solution=solution)

        self.assertIs(False, run.testcases().get("The CSS is valid."))
        self.assertNotEqual("correct answer", run.status)

    def test_broken_evaluator(self):
        run = self.run_judge(page(), evaluator="import module_that_does_not_exist\n")

        self.assertFalse(run.accepted)
        self.assertEqual("runtime error", run.status)
        staff = [m for m in run.messages() if m.get("permission") == "educator"]
        self.assertEqual(1, len(staff))
        self.assertIn("Traceback", staff[0]["description"])
        self.assertIn("ModuleNotFoundError: No module named 'module_that_does_not_exist'", staff[0]["description"])

    def assert_invalid_exercise(self, run: JudgeRun, staff_text: str):
        self.assertFalse(run.accepted)
        self.assertEqual("runtime error", run.status)
        self.assertEqual({}, run.testcases())
        staff = [m for m in run.messages() if m.get("permission") == "educator"]
        self.assertEqual(1, len(staff))
        self.assertIn(staff_text, staff[0]["description"])
        students = [m for m in run.messages() if m.get("permission") != "educator"]
        self.assertEqual(1, len(students))
        self.assertEqual(
            "Your submission could not be evaluated because of an error in the solution file.",
            students[0]["description"],
        )

    def test_missing_evaluator_and_solution(self):
        run = self.run_judge(page())

        self.assert_invalid_exercise(run, "The evaluator.py and solution.html files are missing.")

    def test_empty_solution_without_evaluator(self):
        run = self.run_judge(page(), solution="")

        self.assert_invalid_exercise(run, "The evaluator.py and solution.html files are missing.")

    def test_evaluator_without_create_suites(self):
        run = self.run_judge(page(), evaluator="x = 1\n")

        self.assert_invalid_exercise(run, "does not implement the 'create_suites(content)' method")

    def test_create_suites_returns_empty_list(self):
        run = self.run_judge(page(), evaluator="def create_suites(content):\n    return []\n")

        self.assert_invalid_exercise(run, "did not return any evaluation suites")

    def test_create_suites_returns_none(self):
        run = self.run_judge(page(), evaluator="def create_suites(content):\n    pass\n")

        self.assert_invalid_exercise(run, "did not return any evaluation suites")

    def test_create_suites_raises(self):
        run = self.run_judge(page(), evaluator="def create_suites(content):\n    raise ValueError('boom')\n")

        self.assert_invalid_exercise(run, "ValueError: boom")

    def test_evaluator_syntax_error(self):
        run = self.run_judge(page(), evaluator="def create_suites(content:\n")

        self.assert_invalid_exercise(run, "SyntaxError")

    def test_invalid_exercise_messages_follow_natural_language(self):
        run = self.run_judge(page(), natural_language="nl")

        self.assertEqual("runtime error", run.status)
        staff = [m for m in run.messages() if m.get("permission") == "educator"]
        self.assertEqual(["De evaluator.py en solution.html bestanden ontbreken."], [m["description"] for m in staff])
        students = [m for m in run.messages() if m.get("permission") != "educator"]
        self.assertEqual(
            ["Jouw indiening kon niet geëvalueerd worden door een fout in het oplossingsbestand."],
            [m["description"] for m in students],
        )

    def test_several_failing_items_give_plural_status(self):
        run = self.run_judge(
            "<html lang='en'><head></head><body><p>No heading</p></body></html>", evaluator=CHECKLIST_EVALUATOR
        )

        self.assertEqual("wrong answer", run.status)
        self.assertFalse(run.accepted)
        self.assertFalse(run.testcases()["The page has a title"])
        self.assertFalse(run.testcases()["The page has a heading"])

    def assert_non_ascii_survives(self, locale_name: str):
        evaluator = CHECKLIST_EVALUATOR.replace("The page has a title", f"Titel {NON_ASCII}")
        run = self.run_judge(
            page(title=NON_ASCII, body=f"<h1>{NON_ASCII}</h1>"),
            evaluator=evaluator,
            env={"LC_ALL": locale_name, "LANG": locale_name},
        )

        self.assertEqual("correct answer", run.status)
        self.assertIn(f"Titel {NON_ASCII}", run.testcases())
        rendered = [m["description"] for m in run.messages() if m["format"] == "html"]
        self.assertEqual(1, len(rendered))
        self.assertIn(f"<h1>\n    {NON_ASCII}\n   </h1>", rendered[0])

    def test_non_ascii_under_c_locale(self):
        self.assert_non_ascii_survives("C")

    @unittest.skipIf(LATIN1_LOCALE is None, "no Latin-1 locale available")
    def test_non_ascii_under_latin1_locale(self):
        self.assert_non_ascii_survives(LATIN1_LOCALE or "")
