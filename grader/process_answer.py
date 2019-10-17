import importlib
import os
import shutil

from config.config import PATH_HOME_DIRECTORY
from grader.logs import get_logger
from utils.decorators import log_exceptions


@log_exceptions
def process_answer(message: dict) -> dict:
    """
    Function which receives answers, proceeds them, and returns results.

    :param message: Message received from broker.
    """
    logger = get_logger("process_answer")

    logger.debug("Received message: %s", message)

    response = {}

    grader_script = importlib.import_module(
        "grader_scripts."
        + str(message["xqueue_body"]["grader_payload"])
        + ".grade"
    )

    try:
        score, msg = grader_script.main(
            message["xqueue_body"]["student_response"],
            message["xqueue_files"] if message["xqueue_files"] else None
        )

        # clear_working_directory()

        response["correct"] = True
        response["score"] = score if score else 0
        response["msg"] = msg if msg else ""
    except AssertionError as exception:
        logger.error("Grading failed with message: %s", exception)

        response["msg"] = str(exception)

    logger.debug("Response: %s", response)

    return response


# @log_exceptions
# def clear_working_directory():
#     """
#     Clears the working directory.
#     """
#     for root, dirs, files in os.walk(PATH_HOME_DIRECTORY):
#         for f in files:
#             os.unlink(os.path.join(root, f))
#         for d in dirs:
#             shutil.rmtree(os.path.join(root, d))
