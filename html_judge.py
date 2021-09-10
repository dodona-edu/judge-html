import sys

from dodona.dodona_command import Judgement, Test, TestCase, Message, ErrorType, Tab, Context
from dodona.dodona_config import DodonaConfig
from dodona.translator import Translator
from validators.html_validator import HtmlValidator
from exceptions.htmlExceptions import HtmlValidationError, MissingRecommendedAttributeError


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

        # valid html
        with Tab("checklist"):
            with Context(), TestCase("HTML validation"):
                with Test("Checking tags and attributes", "Valid") as test:
                    try:
                        HtmlValidator(config.judge).validate(config.source)
                    except MissingRecommendedAttributeError as err:
                        with Message(str(err)):
                            test.status = config.translator.error_status(ErrorType.CORRECT)
                            test.generated = "Valid"
                    except HtmlValidationError as err:
                        test.generated = str(err)
                        test.status = config.translator.error_status(ErrorType.WRONG)
                    else:
                        test.generated = "Valid"
                        test.status = config.translator.error_status(ErrorType.CORRECT)

        with Tab("Tab 1"):
            with Context(), TestCase("Setup test description"):
                with Test("First arg", "Second arg") as test:
                    test.generated = "Generated"
                    test.status = config.translator.error_status(ErrorType.CORRECT)


if __name__ == "__main__":
    main()
