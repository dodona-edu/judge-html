import sys

from dodona.dodona_command import Judgement, Test, TestCase, Message, ErrorType, Tab, Context, MessageFormat
from dodona.dodona_config import DodonaConfig
from dodona.translator import Translator
from exceptions.htmlExceptions import HtmlValidationError, Warnings
from utils.file_loaders import html_loader
from utils.evaluation_module import EvaluationModule
from validators.checks import TestSuite
from validators.html_validator import HtmlValidator


def main():
    """
    Main judge method
    """
    # Read config JSON from stdin
    config = DodonaConfig.from_json(sys.stdin)

    with Judgement():
        # Perform sanity check
        config.sanity_check()
        # Initiate translator
        config.translator = Translator.from_str(config.natural_language)

        # Compile evaluator code
        evaluator: EvaluationModule = EvaluationModule.build(config)

        # Load HTML
        html_content: str = html_loader(config.source, shorted=False)
        test_suite: TestSuite = evaluator.create_suite(html_content)

        # validate html
        with Tab("checklist"):
            print(test_suite.evaluate())
            with Context(), TestCase("HTML validation"):

                with Test("Checking tags and attributes", "") as test:
                    try:
                        HtmlValidator().validate_file(config.source)
                    except Warnings as war:
                        with Message(description=str(war), format=MessageFormat.CODE):  # code preserves spaces&newlines
                            test.status = config.translator.error_status(ErrorType.CORRECT)
                            test.generated = ""
                    except HtmlValidationError as err:
                        test.generated = str(err)
                        test.status = config.translator.error_status(ErrorType.WRONG)
                    else:
                        test.generated = ""
                        test.status = config.translator.error_status(ErrorType.CORRECT)

        with Tab("Tab 1"):
            with Context(), TestCase("Setup test description"):
                with Test("First arg", "Second arg") as test:
                    test.generated = "Generated"
                    test.status = config.translator.error_status(ErrorType.CORRECT)


if __name__ == "__main__":
    main()
