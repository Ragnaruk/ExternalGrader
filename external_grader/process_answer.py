"""
Process student submissions.

To execute untrusted code there are several options:
0. Nothing
    - Haha. No.
1. Chroot Jail
    + Pretty easy
    + No overhead
    - Insecure
2. Lxc or Docker
    + Easy
    * Insecure?
    - Some overhead
3. VM
    + Secure
    * Hard?
    - Big overhead
    - Slow
4. edX CodeJail
    + Easy
    * Probably pretty good?
    - Uses AppArmor which is not fully supported by Alpine Linux

In the end, I decided to run code inside Docker via epicbox python module created by stepic team.
"""
import json
import urllib.request
from pathlib import Path
from logging import Logger

import epicbox

from external_grader.logs import get_logger
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


def process_answer(submission: dict) -> dict:
    """
    Function which receives answers, proceeds them, and returns results.

    :param submission: Student submission received from message broker.

    :raises ValueError: Invalid student submission.
    :raises FailedFilesLoadException: Failed to load required files.
    :raises ModuleNotFoundError: Failed to find required grading script.
    """
    logger: Logger = get_logger("process_answer")

    submission: dict = submission_validate(submission)
    logger.info("Student submission: %s", submission)

    script_name: str = submission_get_grader_payload(submission)
    logger.debug("Script name: %s", script_name)

    # Load settings from file
    settings: dict = settings_load(script_name)
    logger.debug("Settings: %s", settings)

    # Load required files and raise FailedFilesLoadException if loading failed
    prepared_files, docker_profile, docker_limits = settings_parse(
        script_name, settings
    )
    logger.debug("Docker profile: %s", docker_profile)
    logger.debug("Docker limits: %s", docker_limits)
    logger.debug("Prepared files: %s", prepared_files)

    # Run code in a more-or-less secure Docker container
    grade: dict = grade_epicbox(
        submission, script_name, prepared_files, docker_profile, docker_limits
    )
    logger.info("Grade: %s", grade)

    return grade


def submission_validate(submission: dict) -> dict:
    """
    Validate received student submission.

    :param submission: Student submission received from message broker.
    :return: True if submission is valid.

    :raises InvalidSubmissionException: Submission is not valid
    """
    # Check the existence of body field
    if "xqueue_body" not in submission.keys():
        raise InvalidSubmissionException(
            "Submission doesn't have xqueue_body:", submission
        )

    if isinstance(submission["xqueue_body"], str):
        submission["xqueue_body"]: dict = json.loads(submission["xqueue_body"])

    # Check grader payload
    if "grader_payload" not in submission["xqueue_body"].keys():
        raise InvalidSubmissionException(
            "Submission doesn't have grader_payload:", submission
        )

    if isinstance(submission["xqueue_body"]["grader_payload"], str) and submission[
        "xqueue_body"
    ]["grader_payload"].startswith("{"):
        submission["xqueue_body"]["grader_payload"]: dict = json.loads(
            submission["xqueue_body"]["grader_payload"]
        )

    # Check for grading script id
    if (
        isinstance(submission["xqueue_body"]["grader_payload"], dict)
        and "script_id" in submission["xqueue_body"]["grader_payload"]
    ):
        script_name: str = submission["xqueue_body"]["grader_payload"]["script_id"]
    elif isinstance(submission["xqueue_body"]["grader_payload"], str):
        script_name: str = submission["xqueue_body"]["grader_payload"]
    else:
        raise InvalidSubmissionException(
            "Submission doesn't have script id:", submission
        )

    if not Path(PATH_GRADER_SCRIPTS_DIRECTORY / script_name / "grade.py").is_file():
        raise InvalidSubmissionException(
            "Submission has invalid grader_payload:", submission
        )

    # Check the existence of student answer
    if not (
        "student_response" in submission["xqueue_body"].keys()
        and submission["xqueue_body"]["student_response"]
    ):
        if "xqueue_files" in submission.keys() and isinstance(
            submission["xqueue_files"], str
        ):
            submission["xqueue_files"]: dict = json.loads(submission["xqueue_files"])

        if not (
            "xqueue_files" in submission.keys()
            and "student_response.txt" in submission["xqueue_files"].keys()
            and submission["xqueue_files"]["student_response.txt"]
        ):
            raise InvalidSubmissionException(
                "Submission has invalid student response:", submission
            )

    return submission


def submission_get_response(submission: dict) -> str:
    """
    Get student response from submission.

    :param submission: Student submission received from message broker.
    :return: Student response.
    """
    if "student_response" in submission["xqueue_body"].keys():
        response: str = submission["xqueue_body"]["student_response"]
    else:
        local_filename, _ = urllib.request.urlretrieve(
            submission["xqueue_files"]["student_response.txt"]
        )

        with open(local_filename) as file:
            response: str = file.read()

    return response


def submission_get_grader_payload(submission: dict) -> str:
    """
    Get grader payload from submission.

    :param submission: Student submission received from message broker.
    :return: Grader payload.
    """
    if (
        isinstance(submission["xqueue_body"]["grader_payload"], dict)
        and "script_id" in submission["xqueue_body"]["grader_payload"]
    ):
        script_name: str = submission["xqueue_body"]["grader_payload"]["script_id"]
    else:
        script_name: str = submission["xqueue_body"]["grader_payload"]

    return script_name


def settings_load(script_name: str) -> dict:
    """
    Load settings for grading script.

    :param script_name: Name of the grading script.
    :return: Settings dictionary.
    """
    logger: Logger = get_logger("process_answer")

    settings_file: Path = PATH_GRADER_SCRIPTS_DIRECTORY / script_name / "settings.json"
    logger.debug("Settings file path: %s", settings_file)

    # Load settings
    if settings_file.is_file():
        with settings_file.open() as file:
            settings = json.load(file)
    else:
        raise InvalidGraderScriptException(
            "Grading script has no settings file: %s", script_name
        )

    return settings


def settings_parse(script_name: str, settings: dict) -> (list, dict, dict):
    """
    Parse settings for grading script and load required files.

    :param script_name: Name of the grading script.
    :param settings: Settings dictionary.
    :return: List of prepared files, epicbox profile, and container limits.

    :raises FailedFilesLoadException: Failed to load or find required file.
    """
    logger: Logger = get_logger("process_answer")

    # Create directory for the script files in data directory
    data_directory: Path = PATH_DATA_DIRECTORY / "grader_scripts" / script_name
    data_directory.mkdir(parents=True, exist_ok=True)
    logger.debug("Data directory path: %s", data_directory)

    script_directory: Path = PATH_GRADER_SCRIPTS_DIRECTORY / script_name
    logger.debug("Script directory path: %s", script_directory)

    docker_profile: dict = EPICBOX_SETTINGS["profile"]
    docker_limits: dict = EPICBOX_SETTINGS["container_limits"]
    prepared_files: list = []

    # Docker container limits
    if "container_limits" in settings.keys():
        docker_limits = settings["container_limits"]

    # Docker profile
    if "profile" in settings.keys():
        docker_profile = settings["profile"]

    # Files
    if "files" in settings.keys():
        all_files = settings["files"]

        # Check existence of external files
        if "external" in all_files.keys():
            files = all_files["external"]

            for f in files:
                file_path: Path = data_directory / f["name"]
                prepared_files.append(
                    {"type": "external", "name": f["name"], "path": file_path}
                )

                if file_path.is_file():
                    logger.debug("File already downloaded: %s", file_path)
                else:
                    try:
                        urllib.request.urlretrieve(f["link"], file_path)
                        logger.debug("File downloaded: %s", file_path)
                    except Exception:
                        raise FailedFilesLoadException(
                            "Failed to download file: %s", f["link"]
                        )

        # Check existence of local files
        if "local" in all_files.keys():
            files = all_files["local"]

            for f in files:
                file_path = script_directory / f["path"]
                prepared_files.append(
                    {"type": "local", "name": f["name"], "path": file_path}
                )

                if file_path.is_file():
                    logger.debug("Local file exists: %s", file_path)
                else:
                    raise FailedFilesLoadException(
                        "Failed to find local file: %s", file_path
                    )

    return prepared_files, docker_profile, docker_limits


def grade_epicbox(
    submission: dict,
    script_name: str,
    prepared_files: list,
    docker_profile: dict,
    docker_limits: dict,
) -> dict:
    """
    Running grading script in a separate Docker container.
    https://github.com/StepicOrg/epicbox

    :param submission: Student submission received from message broker.
    :param script_name: Name of the grading script.
    :param prepared_files: List of files and their paths.
    :param docker_profile: Epicbox profile.
    :param docker_limits: Docker container limits.
    :return: Results of grading.
    """
    logger: Logger = get_logger("process_answer")

    epicbox.configure(
        profiles=[
            epicbox.Profile(
                name="python",
                docker_image=docker_profile["docker_image"],
                user=docker_profile["user"],
                read_only=docker_profile["read_only"],
                network_disabled=docker_profile["network_disabled"],
            )
        ]
    )

    # Get all files used during grading
    # Content field should be bytes
    files: list = []

    # Grading script
    with Path(PATH_GRADER_SCRIPTS_DIRECTORY / script_name / "grade.py").open("rb") as f:
        files.append({"name": "grade.py", "content": f.read()})

    # Required files
    for file in prepared_files:
        with Path(file["path"]).open("rb") as f:
            files.append({"name": file["name"], "content": f.read()})

    # Student submission
    files.append(
        {
            "name": "student_response.txt",
            "content": submission_get_response(submission).encode(),
        }
    )

    result: dict = epicbox.run(
        "python", "python3 grade.py", files=files, limits=docker_limits
    )
    logger.debug("Result: %s", result)

    try:
        score: int = int(result["stdout"].decode().split("\n")[-2])
        msg: str = result["stderr"].decode()  # .split("\n")[-2]
        correct: bool = bool(score)
    except ValueError:
        raise InvalidGraderScriptException(
            "Grading script returned invalid results: %s", result
        )

    grade: dict = {"correct": correct, "score": score, "msg": msg}

    return grade
