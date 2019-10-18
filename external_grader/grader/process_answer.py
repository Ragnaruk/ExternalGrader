import importlib
import os
import shutil

from external_grader.config.config import PATH_EXECUTION_DIRECTORY
from external_grader.grader.logs import get_logger


def process_answer(
        message: dict
) -> dict:
    """
    Function which receives answers, proceeds them, and returns results.

    :param message: Message received from broker.
    """
    logger = get_logger("process_answer")

    response = {}

    grader_script_name = str(message["xqueue_body"]["grader_payload"])

    try:
        grader_script = importlib.import_module(
            "external_grader.grader_scripts."
            + grader_script_name
            + ".grade"
        )

        score, msg = grader_script.main(
            message["xqueue_body"]["student_response"],
            message["xqueue_files"] if "xqueue_files" in message.keys() else None
        )

        # clear_working_directory()

        response["correct"] = True
        response["score"] = score if score else 0
        response["msg"] = msg if msg else ""
    except AssertionError as exception:
        logger.error("Grading failed with message: %s", exception)

        response["msg"] = str(exception)
    except ModuleNotFoundError as exception:
        logger.error("Unknown grader script with name: %s", grader_script_name)

        raise exception

    logger.debug("Response: %s", response)

    return response


def clear_working_directory():
    """
    Clears the working directory.
    """
    for root, dirs, files in os.walk(PATH_EXECUTION_DIRECTORY):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
