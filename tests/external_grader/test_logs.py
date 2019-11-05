"""
PyTest test file for logs module.
"""
from external_grader import logs


def test_get_logger():
    """
    Test logs.get_logger function.
    """
    logger_name = "test"
    logger = logs.get_logger(logger_name)

    assert logger.name == logger_name
    assert logger.hasHandlers()
