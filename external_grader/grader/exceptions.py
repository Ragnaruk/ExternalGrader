"""
Custom exceptions.
"""


class FailedFilesLoadException(Exception):
    """
    Exception which is called when grader failed to load files required for grading.
    """
    pass


class InvalidSubmissionException(Exception):
    """
    Exception which is called when either xqueue_body or grader_payload fields don't exist
    """


class InvalidResponseException(Exception):
    """
    Exception which is called when either student asnwer doesn't exist or is empty.
    """
    pass
