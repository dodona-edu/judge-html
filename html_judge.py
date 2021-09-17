import sys
from typing import List

from dodona.dodona_command import Judgement, Test, Message, ErrorType, Tab, MessageFormat
from dodona.dodona_config import DodonaConfig
from dodona.translator import Translator
from exceptions.html_exceptions import Warnings, HtmlValidationError
from utils.evaluation_module import EvaluationModule
from utils.file_loaders import html_loader
from validators.checks import TestSuite
from validators.html_validator import HtmlValidator
from utils.render_ready import prep_render


def main():
    """
    Main judge method
    """
    # Read config JSON from stdin
    config = DodonaConfig.from_json(sys.stdin)

    with Judgement() as judge:
        # Counter for failed tests because this judge works a bit differently
        # Allows nicer feedback on Dodona (displays amount of failed tests)
        failed_tests = 0

        # Perform sanity check
        config.sanity_check()
        # Initiate translator
        config.translator = Translator.from_str(config.natural_language)

        # Compile evaluator code
        evaluator: EvaluationModule = EvaluationModule.build(config)

        # Load HTML
        html_content: str = html_loader(config.source, shorted=False)
        test_suites: List[TestSuite] = evaluator.create_suites(html_content)

        # Has HTML been validated at least once?
        # Same HTML is used every time so once is enough
        html_validated: bool = False
        css_validated: bool = False

        # Run all test suites
        for suite in test_suites:
            suite.create_validator(config)

            with Tab(suite.name):
                failed_tests += suite.evaluate(config.translator)

            # This suite validated the HTML
            if suite.html_is_valid():
                html_validated = True

            # This suite validated the CSS
            if suite.css_is_valid():
                css_validated = True

        # Only render out valid HTML on Dodona
        if html_validated:
            with Tab("Rendered"):
                with Message(format=MessageFormat.HTML, description=prep_render(html_content, render_css=css_validated)):
                    pass

        status = ErrorType.CORRECT_ANSWER if failed_tests == 0 else ErrorType.WRONG_ANSWER
        judge.status = config.translator.error_status(status, amount=failed_tests)


if __name__ == "__main__":
    main()
