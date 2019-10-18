import logging
from sys import stdout

from external_grader.config.config import PATH_LOG_DIRECTORY, LOG_LEVEL, LOG_FORMAT


def get_logger(logger_name: str) -> logging.Logger:
    """
    Get a logger object that writes to logs directory and to stdout.

    :param logger_name: Name of the logger.
    :param logger_file_name: Name of the log file.
    :return: Logger object.
    """
    PATH_LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(logger_name)

    logger.setLevel(LOG_LEVEL)

    if len(logger.handlers) == 0:
        logger_handler = logging.FileHandler(PATH_LOG_DIRECTORY / "{0}.log".format(logger_name))
        logger_handler.setFormatter(
            logging.Formatter(LOG_FORMAT)
        )

        logger.addHandler(logger_handler)

        logger_handler = logging.StreamHandler(stdout)
        logger_handler.setFormatter(
            logging.Formatter(LOG_FORMAT)
        )

        logger.addHandler(logger_handler)

    return logger
