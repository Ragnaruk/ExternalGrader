"""
General config.
"""
from logging import DEBUG, INFO, ERROR
from pathlib import Path
import importlib
from os import getenv

PATH_HOME_DIRECTORY = Path("/home/")
PATH_VERIFICATION_FILES = Path("/root/")
PATH_LOG_DIRECTORY = Path(__file__).parent.parent / "logs"

# Possible log levels: DEBUG, INFO, ERROR
LOG_LEVEL = DEBUG
LOG_FORMAT = "%(asctime)s - %(levelname)-5s - %(filename)s:%(lineno)d - %(message)s"

# Number of seconds to wait between connections attempts to message broker
CONNECTION_RETRY_TIME = 10

# Name of the python file with message broker config
MESSAGE_BROKER = importlib.import_module("config_queue." + getenv("QUEUE_CONFIG_NAME", "rabbitmq"))
