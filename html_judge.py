import sys
from dodona.dodona_command import Judgement, Test, TestCase, Message, ErrorType, Tab, Context, MessageFormat, \
    DodonaException, MessagePermission
from validators.html_validator import HtmlValidator
from exceptions.html_exceptions import HtmlValidationError, Warnings
from os import path
from dodona.dodona_config import DodonaConfig
from dodona.translator import Translator
from types import ModuleType


def build_evaluator_module(config: DodonaConfig) -> ModuleType:
    """Compile the evaluation code & create a new module"""
    # Create filepath
    custom_evaluator_path = path.join(config.resources, "./evaluator.py")

    # Evaluator doesn't exist, throw an exception
    if not path.exists(custom_evaluator_path):
        raise DodonaException(
            config.translator.error_status(ErrorType.INTERNAL_ERROR),
            permission=MessagePermission.STAFF,
            description="Could not find evaluator.py script. ",
            format=MessageFormat.TEXT,
        )

    # Read raw content of .py file
    with open(custom_evaluator_path, "r") as fp:
        # Compile the code into bytecode
        evaluator_script = compile(fp.read(), "<string>", "exec")

    # Create a new module
    evaluator_module = ModuleType("evaluation")

    # Build the bytecode & add to the new module
    exec(evaluator_script, evaluator_module.__dict__)

    return evaluator_module


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
        # evaluator = build_evaluator_module(config)

        # validate html
        with Tab("checklist"):
            with Context(), TestCase("HTML validation"):

                with Test("Checking tags and attributes", "") as test:
                    try:
                        HtmlValidator(config.translator).validate_file(config.source)
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
