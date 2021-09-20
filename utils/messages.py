from types import SimpleNamespace

from dodona.dodona_command import Message, MessageFormat, ErrorType, MessagePermission
from dodona.dodona_config import DodonaConfig
from dodona.translator import Translator
import traceback


def invalid_suite(judge: SimpleNamespace, config: DodonaConfig):
    with Message(
            description=config.translator.translate(Translator.Text.INVALID_TESTSUITE_STUDENTS),
            format=MessageFormat.TEXT
    ):
        pass

    judge.status = config.translator.error_status(ErrorType.RUNTIME_ERROR)


def invalid_evaluator_file(exception: Exception):
    with Message(
            permission=MessagePermission.STAFF,
            description=traceback.format_exc(),
            format=MessageFormat.CODE
    ):
        pass
