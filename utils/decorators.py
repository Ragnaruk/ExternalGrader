"""
Decorators.
"""
from logging import Logger
from grader.logs import get_logger


def log_exceptions_custom(logger: Logger = None,
                          logger_name: str = "exceptions"):
    """
    Decorator which logs all exceptions.

    :param logger: Logger object.
    :param logger_name: Logger name.
    """
    def decorator(function):
        """
        Decorator around the function.
        """
        def wrapper(*args, **kwargs):
            """
            Wrapper around the function.
            """
            try:
                return function(*args, **kwargs)
            except Exception as exception:
                if logger:
                    logger.error(exception, exc_info=True)
                else:
                    get_logger(logger_name).error(exception, exc_info=True)
        return wrapper
    return decorator


def log_exceptions(function):
    """
    Decorator which logs all exceptions.

    :param logger_name: Logger name.
    """
    def wrapper(*args, **kwargs):
        """
        Wrapper around the function.
        """
        try:
            return function(*args, **kwargs)
        except Exception as exception:
            get_logger("exceptions").error(exception, exc_info=True)

    return wrapper
