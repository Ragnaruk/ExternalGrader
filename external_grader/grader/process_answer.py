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

    if not submission_validate(submission):
        raise ValueError("Invalid student submission: %s", submission)

    script_name: str = str(submission["xqueue_body"]["grader_payload"])

    # Check the existence of grader script
    script_file: Path = PATH_GRADER_SCRIPTS_DIRECTORY / script_name / "grade.py"
    logger.debug("Grading script file path: %s", script_file)

    if not script_file.is_file():
        raise ModuleNotFoundError(
            "Failed to find grader script: %s", script_file
        )

    # Load required files and raise FailedFilesLoadException if loading failed
    loaded_settings = load_settings(script_name)
    logger.debug("Loaded files results: %s", loaded_settings)

    if not loaded_settings["success"]:
        raise FailedFilesLoadException(
            "Failed to load required files: %s", loaded_settings
        )

    # Run code in a more-or-less secure Docker container
    grade: dict = grade_epicbox(submission, script_name, loaded_settings)

    logger.debug("Grade: %s", grade)

    return grade


def submission_validate(
        submission: dict
) -> bool:
    """
    Validate received student submission.

    :param submission: Student submission received from message broker.
    :return: True if submission is valid.

    :raises InvalidSubmissionException: Either xqueue_body or grader_payload don't exist.
    """
    if "xqueue_body" not in submission.keys():
        raise InvalidSubmissionException("Submission doesn't have xqueue_body: %s", submission)
    if "grader_payload" not in submission["xqueue_body"].keys():
        raise InvalidSubmissionException("Submission doesn't have grader_payload: %s", submission)

    return True


def submission_get_response(
        submission: dict
) -> str:
    """
    Get student response from submission.

    :param submission: Student submission received from message broker.
    :return: Student response.

    :raises ValueError: Submission doesn't have a valid student answer.
    """
    logger: Logger = get_logger("process_answer")

    if "student_response" in submission["xqueue_body"].keys() \
            and submission["xqueue_body"]["student_response"]:
        response: str = submission["xqueue_body"]["student_response"]
    elif "xqueue_files" in submission.keys() \
            and "student_submission" in submission["xqueue_files"].keys() \
            and submission["xqueue_files"]["student_submission"]:
        local_filename, _ = urllib.request.urlretrieve(
            submission["xqueue_files"]["student_submission"]
        )

        with open(local_filename) as file:
            response: str = file.read()
    else:
        raise InvalidResponseException(
            "Submission doesn't have a valid student answer: %s", submission
        )

    logger.debug("Student response: %s", response)

    return response


def load_settings(
        script_name: str
) -> dict:
    """
    Load settings for grading script.

    :param script_name: Name of the grading script.
    :return: Dictionary with file names and load results.
    """
    logger: Logger = get_logger("process_answer")

    settings_file: Path = PATH_GRADER_SCRIPTS_DIRECTORY / script_name / "settings.json"
    logger.debug("Requirements file path: %s", settings_file)

    data_directory: Path = PATH_DATA_DIRECTORY / "grader_scripts" / script_name
    data_directory.mkdir(parents=True, exist_ok=True)
    logger.debug("Data directory path: %s", data_directory)

    loaded_settings: dict = {
        "success": True,
        "files": []
    }

    # Load settings
    if settings_file.is_file():
        with settings_file.open() as file:
            settings = json.load(file)
            logger.debug("Settings file: %s", settings)

            # Docker image
            if "docker_image" in settings.keys():
                loaded_settings["docker_image"] = settings["docker_image"]
            else:
                loaded_settings["docker_image"] = EPICBOX_SETTINGS["profile"]["docker_image"]

            # Files
            if "files" in settings.keys():
                all_files = settings["files"]

                # Loading external files
                if "external" in all_files.keys():
                    files = all_files["external"]

                    for f in files:
                        try:
                            file_path: Path = data_directory / f["name"]

                            if file_path.is_file():
                                logger.debug("File already downloaded: %s", file_path)

                                loaded_settings["files"].append({
                                    "type": "external",
                                    "name": f["name"],
                                    "path": file_path,
                                    "result": True
                                })
                            else:
                                try:
                                    urllib.request.urlretrieve(f["link"], file_path)

                                    logger.debug("File downloaded: %s", file_path)

                                    loaded_settings["files"].append({
                                        "type": "external",
                                        "name": f["name"],
                                        "path": file_path,
                                        "result": True
                                    })
                                except Exception as exception:
                                    logger.error("Failed to download required file: %s", f["link"])
                                    logger.error(exception, exc_info=True)

                                    loaded_settings["files"].append({
                                        "type": "external",
                                        "name": f["name"],
                                        "path": file_path,
                                        "result": False
                                    })
                        except Exception as exception:
                            logger.error(exception, exc_info=True)

                # Check existence of local files
                if "local" in all_files.keys():
                    files = all_files["local"]

                    for f in files:
                        try:
                            file_path = PATH_GRADER_SCRIPTS_DIRECTORY / script_name / f["path"]

                            if file_path.is_file():
                                logger.debug("Local file exists: %s", file_path)

                                loaded_settings["files"].append({
                                    "type": "local",
                                    "name": f["name"],
                                    "path": file_path,
                                    "result": True
                                })
                            else:
                                logger.error("Failed to find required local file: %s", file_path)

                                loaded_settings["files"].append({
                                    "type": "local",
                                    "name": f["name"],
                                    "path": file_path,
                                    "result": False
                                })
                        except Exception as exception:
                            logger.error(exception, exc_info=True)

    loaded_settings["success"] = False not in [x["result"] for x in loaded_settings["files"]]

    return loaded_settings


def grade_epicbox(
    submission: dict,
    script_name: str,
    loaded_settings: dict
) -> dict:
    """
    Running grading script in a separate Docker container.
    https://github.com/StepicOrg/epicbox

    :param submission: Student submission received from message broker.
    :param script_name: Name of the grading script.
    :param loaded_settings: Settings loaded from settings.json file.
    :return: Results of grading.
    """
    logger: Logger = get_logger("process_answer")

    epicbox.configure(
        profiles=[
            epicbox.Profile(
                name="python",
                docker_image=loaded_settings["docker_image"],
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

    # Loaded files
    for file in loaded_settings["files"]:
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

    limits = EPICBOX_SETTINGS["container_limits"]
    logger.debug("Container limits: %s", limits)

    result = epicbox.run("python", "python3 grade.py", files=files, limits=limits)

    logger.debug("Result: %s", result)

    grade: dict = {
        "correct": True,
        "score": result["stdout"].decode().replace("\n", ""),
        "msg": result["stderr"].decode()
    }

    return grade
