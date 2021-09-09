import sys
from os import path, getcwd, listdir
from dodona.dodona_command import Judgement, Test, TestCase, Message, ErrorType, Tab, Context
from dodona.dodona_config import DodonaConfig
from dodona.translator import Translator
from importlib import import_module
from inspect import getmembers, isfunction


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

        custom_evaluator_path = path.join(config.resources, "evaluator.py")
        print(listdir(getcwd()))
        # If a custom evaluator exists, try to import and use it
        if path.exists(custom_evaluator_path):
            m = import_module(custom_evaluator_path)
            print(getmembers(m, isfunction))

        with Tab("Tab 1"):
            with Context(), TestCase("Setup test description"):
                with Test("First arg", "Second arg") as test:
                    test.generated = "Generated"

                    test.status = config.translator.error_status(ErrorType.CORRECT)


if __name__ == "__main__":
    main()
