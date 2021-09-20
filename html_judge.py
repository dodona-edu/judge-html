import sys
from typing import List, Optional

from dodona.dodona_command import Judgement, Message, ErrorType, Tab, MessageFormat
from dodona.dodona_config import DodonaConfig
from dodona.translator import Translator
from exceptions.utils import InvalidTranslation
from utils.evaluation_module import EvaluationModule
from utils.file_loaders import html_loader
from validators.checks import TestSuite
from utils.render_ready import prep_render
from utils.messages import invalid_suite, invalid_evaluator_file


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
        try:
            evaluator: Optional[EvaluationModule] = EvaluationModule.build(config)
        except Exception as e:
            invalid_evaluator_file(e)
            invalid_suite(judge, config)
            return

        # An error message is shown for this in build(), stop evaluating
        if evaluator is None:
            # TODO later allow this to run against the solution file instead
            invalid_suite(judge, config)
            return

        # Load HTML
        html_content: str = html_loader(config.source, shorted=False)

        try:
            test_suites: List[TestSuite] = evaluator.create_suites(html_content)
        except NotImplementedError:
            # Evaluator.py file doesn't implement create_suites
            # Tell students why evaluation failed
            invalid_suite(judge, config)
            return
        except Exception as e:
            # Something else is wrong in the create_suites function
            invalid_evaluator_file(e)
            invalid_suite(judge, config)
            return

        # Has HTML been validated at least once?
        # Same HTML is used every time so once is enough
        html_validated: bool = False
        css_validated: bool = False
        aborted: bool = False

        # Run all test suites
        for suite in test_suites:
            suite.create_validator(config)

            with Tab(suite.name):
                try:
                    failed_tests += suite.evaluate(config.translator)
                except InvalidTranslation:
                    # One of the translations was invalid
                    with Message(
                        description=config.translator.translate(Translator.Text.INVALID_TESTSUITE_STUDENTS),
                        format=MessageFormat.TEXT
                    ):
                        pass

                    aborted = True
                    continue

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

        if aborted:
            judge.status = config.translator.error_status(ErrorType.RUNTIME_ERROR)
        else:
            status = ErrorType.CORRECT_ANSWER if failed_tests == 0 else ErrorType.WRONG_ANSWER
            judge.status = config.translator.error_status(status, amount=failed_tests)


if __name__ == "__main__":
    main()
