"""translate judge output towards Dodona"""

from enum import Enum, auto
from typing import Dict

from dodona.dodona_command import ErrorType


class Translator:
    """a class for translating all user feedback
    The Translator class provides translations for a set of Text
    messages and for the Dodona error types.
    """

    class Language(Enum):
        """Language"""

        EN = auto()
        NL = auto()

    class Text(Enum):
        """Text message content enum"""

        UNCLOSED_HTML_TAG = auto()
        MISSING_EVALUATION_FILE = auto()
        MISSING_CREATE_SUITE = auto()
        TESTCASE_ABORTED = auto()
        TESTCASE_NO_LONGER_EVALUATED = auto()
        FAILED_TESTS = auto()

    def __init__(self, language: Language):
        self.language = language

    @classmethod
    def from_str(cls, language: str) -> "Translator":
        """created a Translator instance
        If the language is not detectected correctly or not supported
        the translator defaults to English (EN).
        :param language: Dodona language string "nl" or "en"
        :return: translator
        """
        if language == "nl":
            return cls(cls.Language.NL)

        # default value is EN
        return cls(cls.Language.EN)

    def human_error(self, error: ErrorType) -> str:
        """translate an ErrorType enum into a human-readable string
        :param error: ErrorType enum
        :return: translated human-readable string
        """
        return self.error_translations[self.language][error]

    def error_status(self, error: ErrorType) -> Dict[str, str]:
        """translate an ErrorType enum into a status object
        :param error: ErrorType enum
        :return: Dodona status object
        """
        return {
            "enum": error,
            "human": self.human_error(error),
        }

    def translate(self, message: Text, **kwargs) -> str:
        """translate a Text enum into a string
        :param message: Text enum
        :param kwargs: parameters for message
        :return: translated text
        """
        return self.text_translations[self.language][message].format(**kwargs)

    error_translations = {
        Language.EN: {
            ErrorType.INTERNAL_ERROR: "Internal error",
            ErrorType.COMPILATION_ERROR: "The code is not valid",
            ErrorType.MEMORY_LIMIT_EXCEEDED: "Memory limit exceeded",
            ErrorType.TIME_LIMIT_EXCEEDED: "Time limit exceeded",
            ErrorType.OUTPUT_LIMIT_EXCEEDED: "Output limit exceeded",
            ErrorType.RUNTIME_ERROR: "Crashed while testing",
            ErrorType.WRONG: "Test failed",
            ErrorType.WRONG_ANSWER: "Test failed",
            ErrorType.CORRECT: "All tests succeeded",
            ErrorType.CORRECT_ANSWER: "All tests succeeded",
        },
        Language.NL: {
            ErrorType.INTERNAL_ERROR: "Interne fout",
            ErrorType.COMPILATION_ERROR: "Ongeldige code",
            ErrorType.MEMORY_LIMIT_EXCEEDED: "Geheugenlimiet overschreden",
            ErrorType.TIME_LIMIT_EXCEEDED: "Tijdslimiet overschreden",
            ErrorType.OUTPUT_LIMIT_EXCEEDED: "Outputlimiet overschreden",
            ErrorType.RUNTIME_ERROR: "Gecrasht bij testen",
            ErrorType.WRONG: "Test gefaald",
            ErrorType.WRONG_ANSWER: "Test gefaald",
            ErrorType.CORRECT: "Alle testen geslaagd",
            ErrorType.CORRECT_ANSWER: "Alle testen geslaagd",
        },
    }

    text_translations = {
        Language.EN: {
            Text.UNCLOSED_HTML_TAG: "An HTML-tag was opened but not closed",
            Text.MISSING_EVALUATION_FILE: "The evaluator.py file is missing",
            Text.MISSING_CREATE_SUITE: "The evaluator.py file does not implement the 'create_suites(content)' method.",
            Text.TESTCASE_ABORTED: "Evaluation was aborted because this test failed. All subsequent tests were not executed.",
            Text.TESTCASE_NO_LONGER_EVALUATED: "This test was not evaluated.",
            Text.FAILED_TESTS: "{amount} test(s) failed."
        },
        Language.NL: {
            Text.UNCLOSED_HTML_TAG: "Er is een HTML-tag geopend die niet gesloten werd",
            Text.MISSING_EVALUATION_FILE: "Het evaluator.py-bestand ontbreekt",
            Text.MISSING_CREATE_SUITE: "Het evaluator.py-bestand bevat de 'create_suites(content)' methode niet.",
            Text.TESTCASE_ABORTED: "Het evalueren is onderbroken omdat deze test faalde. De hierop volgende tests werden niet uitgevoerd.",
            Text.TESTCASE_NO_LONGER_EVALUATED: "Deze test werd niet uitgevoerd.",
            Text.FAILED_TESTS: "{amount} test(en) gefaald."
        },
    }
