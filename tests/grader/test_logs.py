"""
PyTest test file for grader.logs module.
"""
from external_grader.grader import logs


def test_get_logger():
    """
    Test grader.logs.get_logger function.
    """
    logger_name = "test"
    logger = logs.get_logger(logger_name)

    assert logger.name == logger_name
    assert logger.hasHandlers()
