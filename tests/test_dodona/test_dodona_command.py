import contextlib
import io
import json
import unittest

from dodona.dodona_command import (
    Context,
    ErrorType,
    Judgement,
    Message,
    MessageFormat,
    MessagePermission,
    SafeAnnotation,
    Tab,
    TestCase,
)


def commands(output: str) -> list[dict]:
    decoder = json.JSONDecoder()
    result, pos = [], 0
    while pos < len(output):
        if output[pos].isspace():
            pos += 1
            continue
        command, pos = decoder.raw_decode(output, pos)
        result.append(command)
    return result


def _raise_value_error() -> None:
    msg = "boom"
    raise ValueError(msg)


class TestEnums(unittest.TestCase):
    def test_error_type_values(self):
        self.assertEqual(
            [member.value for member in ErrorType],
            [
                "internal error",
                "compilation error",
                "memory limit exceeded",
                "time limit exceeded",
                "output limit exceeded",
                "runtime error",
                "wrong",
                "wrong answer",
                "correct",
                "correct answer",
            ],
        )

    def test_message_values(self):
        self.assertEqual(MessagePermission.EDUCATOR, "educator")
        self.assertEqual([member.value for member in MessageFormat], ["text", "html", "code"])

    def test_str(self):
        self.assertEqual(str(ErrorType.WRONG_ANSWER), "wrong answer")
        self.assertEqual(str(MessageFormat.CODE), "code")
        self.assertEqual(str(MessagePermission.EDUCATOR), "educator")


class TestCommands(unittest.TestCase):
    def test_nested_commands(self):
        out = io.StringIO()
        message = {"permission": MessagePermission.EDUCATOR, "format": MessageFormat.CODE, "description": "msg"}
        with contextlib.redirect_stdout(out), Judgement() as judgement, Tab("Tab title", hidden=True) as tab:
            with Context() as context, TestCase("a test") as test_case:
                with Message(**message), SafeAnnotation(row=2, text="note", type="error"):
                    pass
                test_case.accepted = False
                context.accepted = False
            tab.badgeCount = 1
            judgement.status = {"enum": ErrorType.WRONG, "human": "wrong"}
            judgement.accepted = False

        self.assertEqual(
            commands(out.getvalue()),
            [
                {"command": "start-judgement"},
                {"command": "start-tab", "title": "Tab title", "hidden": True},
                {"command": "start-context"},
                {"command": "start-testcase", "description": "a test"},
                {
                    "command": "append-message",
                    "message": {"permission": "educator", "format": "code", "description": "msg"},
                },
                {"command": "annotate-code", "row": 2, "text": "note", "type": "error"},
                {"command": "close-testcase", "accepted": False},
                {"command": "close-context", "accepted": False},
                {"command": "close-tab", "badgeCount": 1},
                {"command": "close-judgement", "status": {"enum": "wrong", "human": "wrong"}, "accepted": False},
            ],
        )

    def test_output_format(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), Tab("t"):
            pass
        self.assertEqual(
            out.getvalue(),
            '{\n "command": "start-tab",\n "title": "t"\n}\n{\n "command": "close-tab"\n}\n',
        )

    def test_test_case_with_dict_description(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), TestCase({"format": MessageFormat.CODE, "description": "d"}):
            pass
        self.assertEqual(
            commands(out.getvalue())[0],
            {"command": "start-testcase", "description": {"format": "code", "description": "d"}},
        )

    def test_negative_row_annotation_prints_nothing(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), SafeAnnotation(row=-1, text="note"):
            pass
        self.assertEqual(out.getvalue(), "")

    def test_exception_propagates_and_close_is_printed(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(ValueError), Judgement():
            _raise_value_error()
        self.assertEqual(
            [command["command"] for command in commands(out.getvalue())],
            ["start-judgement", "close-judgement"],
        )
