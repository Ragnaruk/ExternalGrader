"""
PyTest test file for process_answer module.
"""
import pytest

from external_grader import process_answer
from external_grader.exceptions import (
    FailedFilesLoadException,
    InvalidSubmissionException,
    InvalidGraderScriptException,
)
from external_grader.config import (
    PATH_DATA_DIRECTORY,
    PATH_GRADER_SCRIPTS_DIRECTORY,
    EPICBOX_SETTINGS,
)


def test_submission_validate_valid_body_payload_str():
    """
    Test process_answer.submission_validate function.
    """
    submission: dict = {"xqueue_body": {"student_response": "5", "grader_payload": "1"}}

    process_answer.submission_validate(submission)


def test_submission_validate_valid_body_payload_dict():
    """
    Test process_answer.submission_validate function.
    """
    submission: dict = {
        "xqueue_body": {"student_response": "5", "grader_payload": {"script_id": "1"}}
    }

    process_answer.submission_validate(submission)


def test_submission_validate_valid_file():
    """
    Test process_answer.submission_validate function.
    """
    submission: dict = {
        "xqueue_files": {"student_response.txt": "http://captive.apple.com"},
        "xqueue_body": {"grader_payload": "1"},
    }

    process_answer.submission_validate(submission)


def test_submission_validate_invalid_no_body():
    """
    Test process_answer.submission_validate function.
    """
    submission: dict = {
        "xqueue_files": {"student_response.txt": "http://captive.apple.com"}
    }

    with pytest.raises(InvalidSubmissionException):
        process_answer.submission_validate(submission)


def test_submission_validate_invalid_no_payload_str():
    """
    Test process_answer.submission_validate function.
    """
    submission: dict = {
        "xqueue_files": {"student_response.txt": "http://captive.apple.com"},
        "xqueue_body": {"student_response": "5"},
    }

    with pytest.raises(InvalidSubmissionException):
        process_answer.submission_validate(submission)


def test_submission_validate_invalid_no_payload_dict():
    """
    Test process_answer.submission_validate function.
    """
    submission: dict = {
        "xqueue_files": {"student_response.txt": "http://captive.apple.com"},
        "xqueue_body": {"student_response": "5", "grader_payload": {"test": "1"}},
    }

    with pytest.raises(InvalidSubmissionException):
        process_answer.submission_validate(submission)


def test_submission_validate_invalid_no_grading_script():
    """
    Test process_answer.submission_validate function.
    """
    submission: dict = {
        "xqueue_files": {"student_response.txt": "http://captive.apple.com"},
        "xqueue_body": {"student_response": "5", "grader_payload": "some_script_name"},
    }

    with pytest.raises(InvalidSubmissionException):
        process_answer.submission_validate(submission)


def test_submission_validate_invalid_no_answer_body():
    """
    Test process_answer.submission_validate function.
    """
    submission: dict = {"xqueue_body": {"grader_payload": "1"}}

    with pytest.raises(InvalidSubmissionException):
        process_answer.submission_validate(submission)

    submission: dict = {"xqueue_body": {"student_response": "", "grader_payload": "1"}}

    with pytest.raises(InvalidSubmissionException):
        process_answer.submission_validate(submission)


def test_submission_validate_invalid_no_answer_file():
    """
    Test process_answer.submission_validate function.
    """
    submission: dict = {"xqueue_files": {}, "xqueue_body": {"grader_payload": "1"}}

    with pytest.raises(InvalidSubmissionException):
        process_answer.submission_validate(submission)

    submission: dict = {
        "xqueue_files": {"student_response.txt": ""},
        "xqueue_body": {"grader_payload": "1"},
    }

    with pytest.raises(InvalidSubmissionException):
        process_answer.submission_validate(submission)


def test_submission_get_response_body():
    """
    Test process_answer.submission_get_response function.
    Submission is expected to be valid, since this function is called after submission_validate.
    """
    submission: dict = {"xqueue_body": {"student_response": "5", "grader_payload": "1"}}

    expected_response: str = "5"

    assert process_answer.submission_get_response(submission) == expected_response


def test_submission_get_response_file():
    """
    Test process_answer.submission_get_response function.
    Submission is expected to be valid, since this function is called after submission_validate.
    """
    submission: dict = {
        "xqueue_files": {"student_response.txt": "http://captive.apple.com"},
        "xqueue_body": {"grader_payload": "1"},
    }

    expected_response: str = "<HTML><HEAD><TITLE>Success</TITLE></HEAD><BODY>Success</BODY>" "</HTML>"

    assert process_answer.submission_get_response(submission) == expected_response


def test_submission_get_grader_payload_string():
    """
    Test process_answer.submission_get_grader_payload function.
    Submission is expected to be valid, since this function is called after submission_validate.
    """
    submission: dict = {"xqueue_body": {"grader_payload": "1"}}

    expected_response: str = "1"

    assert process_answer.submission_get_grader_payload(submission) == expected_response


def test_submission_get_grader_payload_dict():
    """
    Test process_answer.submission_get_grader_payload function.
    Submission is expected to be valid, since this function is called after submission_validate.
    """
    submission: dict = {"xqueue_body": {"grader_payload": {"script_id": "1"}}}

    expected_response: str = "1"

    assert process_answer.submission_get_grader_payload(submission) == expected_response


def test_submission_settings_load_valid():
    """
    Test process_answer.settings_load function.
    """
    script_name: str = "1"

    expected_response: dict = {
        "files": {
            "external": [
                {"name": "test-external.txt", "link": "http://captive.apple.com"}
            ],
            "local": [{"name": "test-local.txt", "path": "settings.json"}],
        },
        "container_limits": {
            "cputime": 1,
            "realtime": 3,
            "memory": 64,
            "processes": -1,
        },
        "profile": {
            "docker_image": "ragnaruk/python:latest",
            "user": "guest",
            "read_only": False,
            "network_disabled": True,
        },
    }

    assert process_answer.settings_load(script_name) == expected_response


def test_submission_settings_load_invalid():
    """
    Test process_answer.settings_load function.
    """
    script_name: str = "some_script_name"

    with pytest.raises(InvalidGraderScriptException):
        assert process_answer.settings_load(script_name)


def test_submission_settings_parse_valid_empty():
    """
    Test process_answer.settings_parse function.
    """
    script_name: str = "1"
    settings: dict = {}

    expected_response: tuple = (
        [],
        EPICBOX_SETTINGS["profile"],
        EPICBOX_SETTINGS["container_limits"],
    )

    assert process_answer.settings_parse(script_name, settings) == expected_response


def test_submission_settings_parse_valid_container_limits():
    """
    Test process_answer.settings_parse function.
    """
    script_name: str = "1"
    settings: dict = {
        "container_limits": {"cputime": 1, "realtime": 3, "memory": 64, "processes": -1}
    }

    expected_response: tuple = (
        [],
        EPICBOX_SETTINGS["profile"],
        settings["container_limits"],
    )

    assert process_answer.settings_parse(script_name, settings) == expected_response


def test_submission_settings_parse_valid_profile():
    """
    Test process_answer.settings_parse function.
    """
    script_name: str = "1"
    settings: dict = {
        "profile": {
            "docker_image": "ragnaruk/python:latest",
            "user": "guest",
            "read_only": False,
            "network_disabled": True,
        }
    }

    expected_response: tuple = (
        [],
        settings["profile"],
        EPICBOX_SETTINGS["container_limits"],
    )

    assert process_answer.settings_parse(script_name, settings) == expected_response


def test_submission_settings_parse_valid_external():
    """
    Test process_answer.settings_parse function.
    """
    script_name: str = "1"
    settings: dict = {
        "files": {
            "external": [
                {"name": "test-external.txt", "link": "http://captive.apple.com"}
            ]
        }
    }

    expected_response: tuple = (
        [
            {
                "type": "external",
                "name": "test-external.txt",
                "path": PATH_DATA_DIRECTORY / "grader_scripts/1/test-external.txt",
            }
        ],
        EPICBOX_SETTINGS["profile"],
        EPICBOX_SETTINGS["container_limits"],
    )

    assert process_answer.settings_parse(script_name, settings) == expected_response


def test_submission_settings_parse_valid_all():
    """
    Test process_answer.settings_parse function.
    """
    script_name: str = "1"
    settings: dict = {
        "files": {
            "external": [
                {"name": "test-external.txt", "link": "http://captive.apple.com"}
            ],
            "local": [{"name": "test-local.txt", "path": "settings.json"}],
        },
        "container_limits": {
            "cputime": 1,
            "realtime": 3,
            "memory": 64,
            "processes": -1,
        },
        "profile": {
            "docker_image": "ragnaruk/python:latest",
            "user": "guest",
            "read_only": False,
            "network_disabled": True,
        },
    }

    expected_response: tuple = (
        [
            {
                "type": "external",
                "name": "test-external.txt",
                "path": PATH_DATA_DIRECTORY / "grader_scripts/1/test-external.txt",
            },
            {
                "type": "local",
                "name": "test-local.txt",
                "path": PATH_GRADER_SCRIPTS_DIRECTORY / "1/settings.json",
            },
        ],
        settings["profile"],
        settings["container_limits"],
    )

    assert process_answer.settings_parse(script_name, settings) == expected_response


def test_submission_settings_parse_invalid_external():
    """
    Test process_answer.settings_parse function.
    """
    script_name: str = "1"
    settings: dict = {
        "files": {"external": [{"name": "abcdef.txt", "link": "http://abc.def"}]}
    }

    with pytest.raises(FailedFilesLoadException):
        process_answer.settings_parse(script_name, settings)


def test_submission_settings_parse_invalid_local():
    """
    Test process_answer.settings_parse function.
    """
    script_name: str = "1"
    settings: dict = {"files": {"local": [{"name": "abcdef.txt", "path": "abc.def"}]}}

    with pytest.raises(FailedFilesLoadException):
        process_answer.settings_parse(script_name, settings)
