"""
General config.
"""
from logging import DEBUG, INFO, ERROR
from pathlib import Path

PATH_LOG_DIRECTORY = Path.cwd() / "logs"
PATH_DATA_DIRECTORY = Path.cwd() / "data"
PATH_GRADER_SCRIPTS_DIRECTORY = Path.cwd() / "grader_scripts"

# Possible log levels: DEBUG, INFO, ERROR
LOG_LEVEL = INFO
LOG_FORMAT = "%(asctime)s - %(levelname)-5s - %(filename)s:%(lineno)-3d - %(message)s"

# Number of seconds to wait between connections attempts to message broker
CONNECTION_RETRY_TIME = 10

# Name of the python file with default message broker config
QUEUE_CONFIG_NAME = "rabbitmq_example"

# https://github.com/StepicOrg/epicbox
EPICBOX_SETTINGS = {
    "container_limits": {
        # CPU time in seconds, None for unlimited
        "cputime": 30,
        # Real time in seconds, None for unlimited
        "realtime": 150,
        # Memory in megabytes, None for unlimited
        "memory": 512,
        # Limit the max processes the sandbox can have
        # -1 or None for unlimited(default)
        "processes": -1
    },
    "profile": {
        "docker_image": "ragnaruk/python:latest",
        "user": "student",
        "read_only": False,
        "network_disabled": True
    }
}

