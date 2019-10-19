"""
PyTest test file for grader.logs module.
"""
from logging import Logger

from external_grader.grader import logs


def test_get_logger():
    """
    Test grader.logs.get_logger function.
    """
    logger_name = "test"
    logger = logs.get_logger(logger_name)

    assert logger.__class__ == Logger
    assert logger.name == logger_name
    assert logger.hasHandlers()
