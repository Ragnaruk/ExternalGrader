"""
Custom exceptions.
"""


class FailedFilesLoadException(Exception):
    """
    Exception which is called when grader failed to load files required for grading.
    """


class InvalidSubmissionException(Exception):
    """
    Exception which is called when either xqueue_body or grader_payload fields don't exist
    """


class InvalidGraderScriptException(Exception):
    """
    Exception which is called when grader script returns invalid answer.
    """
