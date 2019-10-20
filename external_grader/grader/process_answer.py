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

from external_grader.grader.logs import get_logger
from external_grader.grader.exceptions import FailedFilesLoadException, \
    InvalidSubmissionException, InvalidResponseException
from external_grader.config.config import PATH_DATA_DIRECTORY, PATH_GRADER_SCRIPTS_DIRECTORY, \
    EPICBOX_SETTINGS


def process_answer(
        submission: dict
) -> dict:
    """
    Function which receives answers, proceeds them, and returns results.

    :param submission: Student submission received from message broker.

    :raises ValueError: Invalid student submission.
    :raises FailedFilesLoadException: Failed to load required files.
    :raises ModuleNotFoundError: Failed to find required grading script.
    """
    logger: Logger = get_logger("process_answer")

    submission_validate(submission)
    logger.debug("Student submission is valid")

    script_name: str = submission["xqueue_body"]["grader_payload"]
    logger.debug("Script name: %s", script_name)

    # Load settings from file
    settings: dict = settings_load(script_name)
    logger.debug("Settings: %s", settings)

    # Load required files and raise FailedFilesLoadException if loading failed
    prepared_files, docker_image, docker_limits = settings_parse(script_name, settings)
    logger.debug("Docker image: %s", docker_image)
    logger.debug("Prepared files: %s", prepared_files)

    # Run code in a more-or-less secure Docker container
    grade: dict = grade_epicbox(submission, script_name, prepared_files, docker_image, docker_limits)
    logger.debug("Grade: %s", grade)

    return grade


def submission_validate(
        submission: dict
) -> None:
    """
    Validate received student submission.

    :param submission: Student submission received from message broker.
    :return: True if submission is valid.

    :raises InvalidSubmissionException: Submission is not valid
    """
    # Check the existence of body field
    if "xqueue_body" not in submission.keys():
        raise InvalidSubmissionException("Submission doesn't have xqueue_body: %s", submission)

    # Check grader payload
    if "grader_payload" not in submission["xqueue_body"].keys():
        raise InvalidSubmissionException("Submission doesn't have grader_payload: %s", submission)

    try:
        script_name: str = submission["xqueue_body"]["grader_payload"]

        if not Path(PATH_GRADER_SCRIPTS_DIRECTORY / script_name / "grade.py").is_file():
            raise Exception
    except Exception:
        raise InvalidSubmissionException("Submission has invalid grader_payload: %s", submission)

    # Check the existence of student answer
    if not (
            "student_response" in submission["xqueue_body"].keys()
            and submission["xqueue_body"]["student_response"]
    ) or (
            "xqueue_files" in submission.keys()
            and "student_submission" in submission["xqueue_files"].keys()
            and submission["xqueue_files"]["student_submission"]
    ):
        raise InvalidSubmissionException("Submission has invalid student response: %s", submission)


def submission_get_response(
        submission: dict
) -> str:
    """
    Get student response from submission.

    :param submission: Student submission received from message broker.
    :return: Student response.
    """
    if "student_response" in submission["xqueue_body"].keys():
        response: str = submission["xqueue_body"]["student_response"]
    else:
        local_filename, _ = urllib.request.urlretrieve(
            submission["xqueue_files"]["student_submission"]
        )

        with open(local_filename) as file:
            response: str = file.read()

    return response


def settings_load(
        script_name: str
) -> dict:
    """
    Load settings for grading script.

    :param script_name: Name of the grading script.
    :return: Settings dictionary.
    """
    logger: Logger = get_logger("process_answer")

    settings_file: Path = PATH_GRADER_SCRIPTS_DIRECTORY / script_name / "settings.json"
    logger.debug("Settings file path: %s", settings_file)

    # Load settings
    with settings_file.open() as file:
        settings = json.load(file)

    return settings


def settings_parse(
        script_name: str,
        settings: dict
) -> (list, str, dict):
    """
    Parse settings for grading script and load required files.

    :param script_name: Name of the grading script.
    :param settings: Settings dictionary.
    :return: List of prepared files, name of the docker image, and container limits.

    :raises FailedFilesLoadException: Failed to load or find required file.
    """
    logger: Logger = get_logger("process_answer")

    # Create directory for the script files in data directory
    data_directory: Path = PATH_DATA_DIRECTORY / "grader_scripts" / script_name
    data_directory.mkdir(parents=True, exist_ok=True)
    logger.debug("Data directory path: %s", data_directory)

    script_directory: Path = PATH_GRADER_SCRIPTS_DIRECTORY / script_name
    logger.debug("Script directory path: %s", script_directory)

    docker_image: str = EPICBOX_SETTINGS["profile"]["docker_image"]
    docker_limits: dict = EPICBOX_SETTINGS["container_limits"]
    prepared_files: list = []

    # Docker image
    if "docker_image" in settings.keys():
        docker_image = settings["docker_image"]

    # Docker container limits
    if "docker_limits" in settings.keys():
        docker_limits = settings["docker_limits"]

    # Files
    if "files" in settings.keys():
        all_files = settings["files"]

        # Check existence of external files
        if "external" in all_files.keys():
            files = all_files["external"]

            for f in files:
                file_path: Path = data_directory / f["name"]
                prepared_files.append({"type": "external","name": f["name"],"path": file_path})

                if file_path.is_file():
                    logger.debug("File already downloaded: %s", file_path)
                else:
                    try:
                        urllib.request.urlretrieve(f["link"], file_path)
                        logger.debug("File downloaded: %s", file_path)
                    except Exception:
                        raise FailedFilesLoadException("Failed to download file: %s", f["link"])

        # Check existence of local files
        if "local" in all_files.keys():
            files = all_files["local"]

            for f in files:
                file_path = script_directory / f["path"]
                prepared_files.append({"type": "local","name": f["name"],"path": file_path})

                if file_path.is_file():
                    logger.debug("Local file exists: %s", file_path)
                else:
                    raise FailedFilesLoadException("Failed to find local file: %s", file_path)

    return prepared_files, docker_image, docker_limits


def grade_epicbox(
        submission: dict,
        script_name: str,
        prepared_files: list,
        docker_image: str,
        docker_limits: dict
) -> dict:
    """
    Running grading script in a separate Docker container.
    https://github.com/StepicOrg/epicbox

    :param submission: Student submission received from message broker.
    :param script_name: Name of the grading script.
    :param prepared_files: List of files and their paths.
    :param docker_image: Name of the docker image.
    :param docker_limits: Docker container limits.
    :return: Results of grading.
    """
    logger: Logger = get_logger("process_answer")

    epicbox.configure(
        profiles=[
            epicbox.Profile(
                name="python",
                docker_image=docker_image,
                user="guest"
            )
        ]
    )

    # Get all files used during grading
    # Content field should be bytes
    files = []

    # Grading script
    with Path(PATH_GRADER_SCRIPTS_DIRECTORY / script_name / "grade.py").open("rb") as f:
        files.append({
            "name": "grade.py",
            "content": f.read()
        })

    # Required files
    for file in prepared_files:
        with Path(file["path"]).open("rb") as f:
            files.append({
                "name": file["name"],
                "content": f.read()
            })

    # Student submission
    files.append({
        "name": "student_submission.txt",
        "content": submission_get_response(submission).encode()
    })

    result = epicbox.run("python", "python3 grade.py", files=files, limits=docker_limits)
    logger.debug("Result: %s", result)

    score: str = result["stdout"].decode().replace("\n", "")
    msg: str = result["stderr"].decode()
    correct: bool = bool(score) and int(score) == 100

    grade: dict = {
        "correct": correct,
        "score": score,
        "msg": msg
    }

    return grade
