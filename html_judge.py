import sys

from dodona.dodona_command import Judgement, Test, TestCase, Message, ErrorType, Tab, Context
from dodona.dodona_config import DodonaConfig
from dodona.translator import Translator


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

        with Tab("Tab 1"):
            with Context(), TestCase(description="Setup test description"):
                with Test("First arg", "Second arg") as test:
                    test.generated = "Generated"

                    test.status = config.translator.error_status(ErrorType.CORRECT)


if __name__ == "__main__":
    main()
